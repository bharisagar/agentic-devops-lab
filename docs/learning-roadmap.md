# Agentic DevOps Lab: 10-day roadmap

We already have DevOps learning paths for Docker, Terraform, Kubernetes, AWS, and CI/CD. We’ve also introduced AI incident summaries, evaluation, and runbook retrieval. This lab moves to the next question: **how can an AI system gather operational evidence with approved tools and help an engineer investigate an incident?**

We’ll follow the same simulated container-restart incident through all ten days. Each lesson adds one piece to the investigator.

| Day | Topic | What we build |
|---|---|---|
| 1 | [Foundation: chatbot, script, and agent](../days/day-01-foundation/README.md) | Incident fixture, architecture, deterministic investigation and tests |
| 2 | [Tools: schemas and validation](../days/day-02-safe-tools/README.md) | Fixture-backed diagnostic tool registry; strict input validation; no shell commands |
| 3 | [Investigation loop](../days/day-03-investigation-loop/README.md) | Evidence-driven tool selection, bounded steps, explicit stop conditions, and a readable trace; no model API required |
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

The early lessons use local, deterministic decisions so every learner can run the project without an API key. Day 3 introduces a replaceable selector interface; a model-backed provider can be added after the workflow and safety boundaries are clear. Tests and CI will continue to work without paid model calls. Free-tier availability and limits depend on the provider and can change. Never put an API key in browser code or Git.
