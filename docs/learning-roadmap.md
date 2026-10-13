# Agentic DevOps Lab: 10-day roadmap

We already have DevOps learning paths for Docker, Terraform, Kubernetes, AWS, and CI/CD. We’ve also introduced AI incident summaries, evaluation, and runbook retrieval. This lab moves to the next question: **how can an AI system gather operational evidence with approved tools and help an engineer investigate an incident?**

We’ll follow the same simulated container-restart incident through all ten days. Each lesson adds one piece to the investigator.

| Day | Topic | What we build |
|---|---|---|
| 1 | [Foundation: chatbot, script, and agent](../days/day-01-foundation/README.md) | Incident fixture, architecture, deterministic investigation and tests |
| 2 | [Tools: schemas and validation](../days/day-02-safe-tools/README.md) | Fixture-backed diagnostic tool registry; strict input validation; no shell commands |
| 3 | Investigation loop | Model-assisted tool selection, evidence collection, bounded steps and a mock mode for tests |
| 4 | LangGraph orchestration | Triage, evidence, diagnosis, verification, and report nodes with clear stop conditions |
| 5 | Runbook retrieval | Local search across selected DevOps notes, with citations in the report |
| 6 | Safety | Secret redaction, untrusted input tests, tool allowlist and approval boundary |
| 7 | AWS evidence | Optional read-only ECS checks based on the ECS Deployment Readiness project |
| 8 | Evaluation | At least ten labeled incidents and repeatable quality measurements |
| 9 | Operations | Investigation IDs, tool-call logs, timing, failures, and CI tests without paid model calls |
| 10 | Release v0.1 | CLI or local UI, setup guide, demo, limitations, and evaluation results |

## We set the safety rules before AWS

The Day 2 tools work on local fixtures. We’ll add safety tests before the optional AWS connection on Day 7, and that connection will use a read-only role. Version 0.1 can recommend a fix; it cannot run it or change infrastructure.

## Model/API plan

Day 1 has no model API call. On Day 3, we can add an optional model provider for tool selection. The rest of the project—including tests and CI—will work with a local mock, so learners can follow along without an API key or paid inference. Free-tier availability and limits depend on the provider and can change. Never put an API key in browser code or Git.
