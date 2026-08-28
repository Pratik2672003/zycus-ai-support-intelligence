from typing import Literal
from pydantic import BaseModel, Field


class TicketInput(BaseModel):
    subject: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=10000)


class KnowledgeMatch(BaseModel):
    matched: bool
    document: str | None
    title: str | None
    score: float = Field(ge=0, le=1)
    excerpt: str | None


class TriageOutput(BaseModel):
    product: str
    product_area: str
    issue_category: str
    urgency: Literal["P1", "P2", "P3", "P4"]
    reasoning: list[str]
    knowledge_match: KnowledgeMatch
    responder_team: str
    first_response: str
    prompt_version: str = "triage-v1.0"


class RiskFlag(BaseModel):
    source: str
    severity: Literal["high", "medium", "low"]
    reason: str
    quote: str


class AccountBrief(BaseModel):
    account_id: str
    company: str
    as_of_date: str
    executive_summary: str
    open_risks: list[RiskFlag]
    recommended_talking_points: list[str]
    tickets_reviewed: int
    prompt_version: str = "account-health-v1.0"

