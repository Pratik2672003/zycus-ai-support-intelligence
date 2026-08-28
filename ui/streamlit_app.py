import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
from app.account_health import build_account_brief
from app.data_loader import load_accounts
from app.triage import triage_ticket

st.set_page_config(page_title="Support Intelligence", page_icon="🛟", layout="wide")
st.title("Support Intelligence Workspace")
st.caption("Deterministic ticket triage and TAM account briefing using only the supplied synthetic dataset.")
triage_tab, tam_tab = st.tabs(["Ticket Triage", "TAM Account Brief"])

with triage_tab:
    subject = st.text_input("Ticket subject", "Production login failing for all users")
    body = st.text_area("Ticket body", "SecureVault SSO authentication is failing in production. All users are blocked with an invalid SAML assertion error.", height=170)
    if st.button("Triage ticket", type="primary"):
        out = triage_ticket({"subject": subject, "body": body})
        a, b, c, d = st.columns(4)
        a.metric("Urgency", out.urgency); b.metric("Product", out.product); c.metric("Category", out.issue_category); d.metric("Team", out.responder_team)
        st.subheader("Reasoning"); st.write(out.reasoning)
        st.subheader("Knowledge match"); st.json(out.knowledge_match.model_dump())
        st.subheader("Draft response"); st.code(out.first_response)

with tam_tab:
    accounts = load_accounts()
    labels = {f"{a['account_id']} — {a['company']}": a["account_id"] for a in accounts}
    selected = st.selectbox("Account", list(labels))
    if st.button("Generate account brief", type="primary"):
        brief = build_account_brief(labels[selected])
        st.subheader("Executive summary"); st.write(brief.executive_summary)
        st.subheader("Open risks and flagged issues")
        if brief.open_risks:
            for risk in brief.open_risks:
                st.warning(f"{risk.severity.upper()} · {risk.source}: {risk.reason}\n\nEvidence: “{risk.quote}”")
        else: st.success("No explicit churn or escalation signals found.")
        st.subheader("Recommended talking points"); st.write(brief.recommended_talking_points)

