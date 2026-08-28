"""Deterministic evaluation harness for both assignment tasks."""
import json
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.account_health import build_account_brief
from app.data_loader import load_accounts
from app.triage import triage_ticket


def score_checks(name: str, task: str, checks: dict[str, bool], adversarial: bool = False) -> dict:
    score = sum(checks.values()) / len(checks)
    return {"name": name, "task": task, "adversarial": adversarial, "passed": score == 1.0, "score": round(score, 3), "checks": checks}


def run() -> dict:
    results = []
    triage_cases = [
        ("P1 SSO outage", {"subject": "SecureVault SSO outage", "body": "Complete outage in production. All users cannot login due to SAML error."}, {"urgency": "P1", "category": "Bug", "product": "SecureVault"}, False),
        ("Billing question", {"subject": "Incorrect invoice charge", "body": "We were charged twice on our Enterprise invoice. Please review the billing payment."}, {"category": "Billing", "team": "Billing Operations"}, False),
        ("Integration failure", {"subject": "CloudSync Salesforce integration", "body": "The Salesforce integration is failing with an API error in production."}, {"category": "Integration", "product": "CloudSync"}, False),
        ("Feature request", {"subject": "Request: bulk archive", "body": "Please add a bulk archive feature to DataBridge Pro. Current workaround is manual."}, {"category": "Feature Request", "urgency": "P4"}, False),
        ("Ambiguous ticket", {"subject": "Something seems different", "body": "The page changed yesterday. Please advise when possible."}, {"urgency": "P4"}, True),
    ]
    for name, payload, expected, adversarial in triage_cases:
        out = triage_ticket(payload)
        checks = {
            "structured_fields": all([out.product_area, out.issue_category, out.urgency, out.reasoning, out.responder_team, out.first_response]),
            "expected_category": expected.get("category", out.issue_category) == out.issue_category,
            "expected_urgency": expected.get("urgency", out.urgency) == out.urgency,
            "expected_product": expected.get("product", out.product) == out.product,
            "expected_team": expected.get("team", out.responder_team) == out.responder_team,
            "safe_response": "API key" not in out.first_response and len(out.first_response) > 80,
        }
        results.append(score_checks(name, "ticket_triage", checks, adversarial))

    accounts = load_accounts()
    selected = [accounts[0], accounts[1], accounts[2], accounts[3]]
    for idx, account in enumerate(selected, 1):
        first = build_account_brief(account["account_id"])
        second = build_account_brief(account["account_id"])
        checks = {
            "three_sections": bool(first.executive_summary and first.recommended_talking_points and isinstance(first.open_risks, list)),
            "summary_length": 3 <= len([x for x in first.executive_summary.split(". ") if x]) <= 6,
            "direct_quotes": all(r.quote and len(r.quote) >= 8 for r in first.open_risks),
            "deterministic": first.model_dump() == second.model_dump(),
            "ninety_day_metadata": first.tickets_reviewed >= 0 and bool(first.as_of_date),
        }
        results.append(score_checks(f"Account brief {idx}: {account['account_id']}", "account_health", checks))

    try:
        build_account_brief("ACC-DOES-NOT-EXIST")
        missing_handled = False
    except KeyError:
        missing_handled = True
    results.append(score_checks("Missing account ID", "account_health", {
        "graceful_error": missing_handled,
        "no_fabricated_brief": missing_handled,
    }, adversarial=True))

    overall = sum(r["score"] for r in results) / len(results)
    report = {
        "suite": "Support Intelligence Evaluation v1.0",
        "method": "Rule-based acceptance criteria with deterministic regression checks",
        "total_cases": len(results),
        "passed_cases": sum(r["passed"] for r in results),
        "overall_quality_score": round(overall, 3),
        "results": results,
    }
    (ROOT / "eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed_cases"] == report["total_cases"] else 1)

