import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache
def load_tickets() -> list[dict]:
    return json.loads((ROOT / "data" / "tickets.json").read_text(encoding="utf-8"))


@lru_cache
def load_accounts() -> list[dict]:
    return json.loads((ROOT / "data" / "accounts.json").read_text(encoding="utf-8"))


def dataset_as_of() -> datetime:
    """Use the dataset's latest timestamp so results never change with wall-clock time."""
    return max(datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")) for t in load_tickets())


def account_and_recent_tickets(account_id: str, days: int = 90) -> tuple[dict, list[dict], datetime]:
    account = next((a for a in load_accounts() if a["account_id"] == account_id), None)
    if not account:
        raise KeyError(f"Account '{account_id}' was not found")
    as_of = dataset_as_of()
    cutoff = as_of - timedelta(days=days)
    tickets = [
        t for t in load_tickets()
        if t.get("account_id") == account_id
        and cutoff <= datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")) <= as_of
    ]
    tickets.sort(key=lambda t: (t["created_at"], t["ticket_id"]), reverse=True)
    return account, tickets, as_of

