from fastapi import FastAPI, HTTPException

from app.account_health import build_account_brief
from app.models import AccountBrief, TicketInput, TriageOutput
from app.triage import triage_ticket


app = FastAPI(
    title="Support Intelligence API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Zycus AI Support Intelligence API is running",
        "documentation": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triage", response_model=TriageOutput)
def triage(payload: TicketInput):
    return triage_ticket(payload)


@app.get(
    "/accounts/{account_id}/brief",
    response_model=AccountBrief
)
def account_brief(account_id: str):
    try:
        return build_account_brief(account_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc