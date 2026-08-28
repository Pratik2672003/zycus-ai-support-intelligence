from fastapi.testclient import TestClient
from app.main import app
from app.account_health import build_account_brief
from app.data_loader import load_accounts
from app.triage import triage_ticket

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_triage_p1_outage():
    result = triage_ticket({"subject": "SecureVault outage", "body": "Production down. All users cannot operate due to login error."})
    assert result.urgency == "P1"
    assert result.product == "SecureVault"


def test_brief_is_deterministic():
    account_id = load_accounts()[0]["account_id"]
    assert build_account_brief(account_id).model_dump() == build_account_brief(account_id).model_dump()


def test_missing_account_is_404():
    assert client.get("/accounts/ACC-NOT-REAL/brief").status_code == 404

