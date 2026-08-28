# 10-minute Loom walkthrough

## 0:00-0:45 - Introduction

Hello, I am Pratik Naikwade. This is my Support Intelligence project for the AI Engineer - Product Support Intern assignment. It covers ticket triage, TAM account health summaries, systematic evaluation, and a Streamlit interface.

## 0:45-2:00 - Architecture and data

Show the folder structure. Explain that only the supplied 500 synthetic tickets, 50 accounts, and knowledge-base Markdown files are used. Show `data_loader.py`, and explain that the latest dataset timestamp is the fixed reference date for deterministic 90-day filtering.

## 2:00-4:00 - Task 1 live demo

Open the Streamlit Ticket Triage tab. Use a production SSO outage example. Show the product, area, category, P1 urgency, reasoning, responder team, retrieved document, and draft response. Explain TF-IDF retrieval and structured Pydantic output.

## 4:00-6:00 - Task 2 live demo

Select an at-risk account. Show the executive summary, direct evidence quotes, risk severity, and talking points. Explain that every flag retains its source ticket ID or escalation note and that results remain identical for the same account.

## 6:00-7:30 - API and implementation

Open `/docs` at `http://localhost:8000/docs`. Demonstrate POST `/triage` and GET `/accounts/{account_id}/brief`. Briefly show the separation between retrieval, triage, summarisation, models, and data loading.

## 7:30-8:30 - Evaluation

Run `python evals/run_evals.py`. Show the ten cases, pass/fail, per-case 0-1 score, adversarial ambiguous ticket, missing account case, and `eval_report.json`. Mention the GitHub Actions quality gate.

## 8:30-9:30 - Design decisions

Explain the deterministic local baseline, data privacy benefit, explainability, dataset-relative time window, and the trade-off: TF-IDF plus rules is faster and reproducible but less flexible than a large generative model.

## 9:30-10:00 - Closing

Summarize the outcomes and show the README run commands. Thank the reviewer.

