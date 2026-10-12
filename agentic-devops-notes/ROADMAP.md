# Agentic DevOps: Day 1–10

We will follow the same deployment or container incident through the series. The order moves from concepts to a bounded investigator, then to production concerns. The companion lab stays deterministic where possible; model calls and AWS access are optional additions, never a prerequisite for understanding the lesson.

| Day | Topic | Learning outcome |
|---|---|---|
| 1 | Agentic DevOps foundations | Tell a chatbot, fixed automation, and tool-using agent apart; define a safe incident problem and draw the system map. |
| 2 | Tools and evidence | Describe tool schemas, validation, read-only permissions, and trustworthy evidence. |
| 3 | Model and investigation loop | Understand model selection and a bounded observe → decide → act → verify loop. |
| 4 | LangGraph | Model investigation steps, state, routing, retries, checkpoints, and approval. |
| 5 | RAG and runbooks | Follow ingestion and retrieval, then ground a response in cited passages. |
| 6 | Security and governance | Threat-model prompt injection, secrets, identity, tenant boundaries, and writes. |
| 7 | AWS architecture | Trace the request through networking, API delivery, compute, model, and search services. |
| 8 | Evaluation | Measure diagnosis, evidence, retrieval, tool choice, and unsafe behavior with labeled cases. |
| 9 | Operations and CI/CD | Observe latency, failures, cost, and quality; safely test and promote changes. |
| 10 | End-to-end release | Explain a production-style design, its trade-offs, limits, recovery, and operating guide. |

## Recommended reading order

Start with [fundamentals](01-fundamentals/README.md), then [LangGraph](02-langgraph/README.md), [RAG](03-rag/README.md), [model selection](04-model-selection/README.md), and [the reference architecture](05-reference-architecture/README.md). The remaining pages explain AWS implementation options and operational practices. Not every example requires every AWS service.

## Boundaries

- **Concept notes:** this folder; explanations and architecture diagrams.
- **Hands-on code:** the separate lab; simulated incidents and tests first.
- **Production use:** requires an explicit threat model, least-privilege review, evaluation, observability, and human approval for changes.

Day numbers describe a teaching sequence, not a claim that a production system should be built in ten days.
