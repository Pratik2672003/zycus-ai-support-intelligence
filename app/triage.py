import re
from app.models import TicketInput, TriageOutput
from app.retrieval import retrieve

PRODUCTS = ["DataBridge Pro", "CloudSync", "AnalyticsHub", "SecureVault", "WorkflowEngine"]
AREA_TERMS = {
    "Authentication & SSO": ["sso", "saml", "login", "authentication", "mfa", "password"],
    "Data Ingestion": ["ingest", "import", "upload", "pipeline", "connector"],
    "Reporting & Dashboards": ["report", "dashboard", "chart", "analytics"],
    "Integrations": ["integration", "salesforce", "slack", "snowflake", "api", "webhook"],
    "Billing & Plans": ["invoice", "billing", "payment", "charge", "plan", "subscription"],
    "Performance": ["slow", "latency", "timeout", "performance", "throughput"],
}
CATEGORY_TERMS = {
    "Data Loss": ["data loss", "deleted", "missing data", "corrupted", "cannot recover"],
    "Billing": ["invoice", "billing", "payment", "charged", "refund", "subscription"],
    "Feature Request": ["feature request", "request:", "would like", "please add", "bulk", "enhancement"],
    "Integration": ["integration", "connect to", "salesforce", "slack", "snowflake", "webhook"],
    "Performance": ["slow", "latency", "timeout", "performance", "takes minutes"],
    "Onboarding": ["onboarding", "new account", "getting started", "setup users"],
    "How-To": ["how do", "how to", "guidance", "documentation", "where can i"],
    "Bug": ["error", "fails", "failing", "broken", "unexpected", "exception", "not working"],
}
TEAM_BY_CATEGORY = {
    "Billing": "Billing Operations", "Integration": "Integrations Support",
    "Onboarding": "Customer Onboarding", "Feature Request": "Product Support",
    "Performance": "Tier 2 Performance", "Data Loss": "Incident Response",
    "Bug": "Tier 2 Product Support", "How-To": "Tier 1 Support",
}


def _first_match(text: str, mapping: dict[str, list[str]], default: str) -> tuple[str, str | None]:
    for label, terms in mapping.items():
        for term in terms:
            if term in text:
                return label, term
    return default, None


def triage_ticket(ticket: TicketInput | dict | str) -> TriageOutput:
    if isinstance(ticket, str):
        ticket = TicketInput(subject=ticket[:300], body=ticket)
    elif isinstance(ticket, dict):
        ticket = TicketInput(**ticket)
    text = f"{ticket.subject} {ticket.body}".lower()

    product = next((p for p in PRODUCTS if p.lower() in text), "Platform / Unknown")
    area, area_signal = _first_match(text, AREA_TERMS, "General")
    category, category_signal = _first_match(text, CATEGORY_TERMS, "Bug")

    p1 = ["business stopped", "complete outage", "all users", "production down", "security breach", "data loss", "cannot operate"]
    p2 = ["critical", "urgent", "production", "many users", "no workaround", "major impact", "blocked"]
    p4 = ["cosmetic", "minor", "suggestion", "when possible", "nice to have"]
    if any(x in text for x in p1): urgency, signal = "P1", next(x for x in p1 if x in text)
    elif any(x in text for x in p2): urgency, signal = "P2", next(x for x in p2 if x in text)
    elif any(x in text for x in p4) or category == "Feature Request": urgency, signal = "P4", "low-impact request"
    else: urgency, signal = "P3", "moderate impact; no outage signal"

    kb = retrieve(f"{product} {area} {ticket.subject} {ticket.body}")
    reasoning = [
        f"Product identified from ticket text: {product}.",
        f"Issue category '{category}' selected" + (f" from signal '{category_signal}'." if category_signal else "."),
        f"Urgency {urgency} selected from impact signal '{signal}'.",
    ]
    if area_signal:
        reasoning.append(f"Product area matched signal '{area_signal}'.")
    greeting = "Hello,\n\nThank you for contacting Support."
    response = (
        f"{greeting} We have classified this as a {urgency} {category.lower()} issue for {product} "
        f"and routed it to {TEAM_BY_CATEGORY[category]}. "
        + (f"We are reviewing the guidance in '{kb['title']}'. " if kb["matched"] else "We are investigating the details provided. ")
        + "Please share the affected environment, product version, approximate start time, and any recent changes if they were not included. "
        "We will update you with the next step as soon as possible.\n\nRegards,\nSupport Team"
    )
    return TriageOutput(
        product=product, product_area=area, issue_category=category, urgency=urgency,
        reasoning=reasoning, knowledge_match=kb, responder_team=TEAM_BY_CATEGORY[category],
        first_response=response,
    )

