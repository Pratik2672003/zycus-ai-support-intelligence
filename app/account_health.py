import re
from app.data_loader import account_and_recent_tickets
from app.models import AccountBrief, RiskFlag

RISK_SIGNALS = {
    "churn": ["cancel", "churn", "competitor", "switching vendor", "not renew", "terminate"],
    "escalation": ["escalat", "executive", "legal", "unacceptable", "frustrated", "urgent"],
    "business impact": ["production down", "blocked", "data loss", "critical", "cannot operate"],
}


def _quote(text: str, term: str, limit: int = 220) -> str:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    match = next((s.strip() for s in sentences if term in s.lower()), text.strip())
    return match[:limit]


def build_account_brief(account_id: str) -> AccountBrief:
    account, tickets, as_of = account_and_recent_tickets(account_id)
    flags: list[RiskFlag] = []
    for note in account.get("escalation_notes") or []:
        lower = note.lower()
        term = next((x for terms in RISK_SIGNALS.values() for x in terms if x in lower), None)
        if term:
            flags.append(RiskFlag(source="account escalation note", severity="high", reason="Commercial or relationship risk signal", quote=note))
    for ticket in tickets:
        combined = f"{ticket['subject']} {ticket['body']}"
        lower = combined.lower()
        found = next(((kind, term) for kind, terms in RISK_SIGNALS.items() for term in terms if term in lower), None)
        if found:
            kind, term = found
            severity = "high" if kind in {"churn", "business impact"} or ticket.get("urgency") == "P1" else "medium"
            flags.append(RiskFlag(source=ticket["ticket_id"], severity=severity, reason=f"Detected {kind} signal", quote=_quote(combined, term)))
    flags = flags[:8]

    utilization = round(100 * account["seats_active"] / max(account["seats_licensed"], 1))
    p1 = sum(t.get("urgency") == "P1" for t in tickets)
    unresolved = sum(t.get("status") not in {"Resolved", "Closed"} for t in tickets)
    summary = (
        f"{account['company']} is a {account['plan_tier']} account with ${account['arr_usd']:,} ARR and is currently marked {account['health_status']}. "
        f"Seat utilization is {utilization}% ({account['seats_active']} of {account['seats_licensed']}) and usage is {account['usage_trend'].lower()}. "
        f"In the dataset-relative last 90 days, {len(tickets)} tickets were recorded, including {p1} P1 tickets and {unresolved} unresolved tickets. "
        f"The account has {len(flags)} evidence-backed risk signal(s); the TAM should validate ownership and recovery actions before the renewal on {account['renewal_date']}."
    )
    talking = [
        f"Confirm business outcomes and adoption across {', '.join(account['products'])}.",
        f"Review the recovery plan and owners for {unresolved} unresolved recent ticket(s).",
        f"Discuss the {account['usage_trend'].lower()} usage trend and agree on an adoption target above the current {utilization}% utilization.",
        f"Confirm renewal priorities and success criteria before {account['renewal_date']}.",
    ]
    if flags:
        talking.insert(0, "Acknowledge the flagged concerns directly and agree on dated follow-up actions.")
    return AccountBrief(
        account_id=account_id, company=account["company"], as_of_date=as_of.date().isoformat(),
        executive_summary=summary, open_risks=flags,
        recommended_talking_points=talking, tickets_reviewed=len(tickets),
    )

