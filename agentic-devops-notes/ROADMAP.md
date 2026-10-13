# Agentic DevOps: Day 1–10

We will follow the same deployment or container incident through the series. The order moves from concepts to a bounded investigator, then to production concerns. The companion lab stays deterministic where possible; model calls and AWS access are optional additions, never a prerequisite for understanding the lesson.

| Day | Topic | Learning outcome |
|---|---|---|
| 1 | Agentic DevOps foundations | Tell a chatbot, fixed automation, and tool-using agent apart; define a safe incident problem and draw the system map. |
| 2 | Tools and evidence | Describe tool schemas, validation, read-only permissions, and trustworthy evidence. |
| 3 | Model and investigation loop | Understand model selection and a bounded observe → decide → act → verify loop; keep the current incident state separate from long-term knowledge. |
| 4 | LangGraph | Model investigation steps, state, routing, retries, checkpoints, and approval. |
| 5 | RAG and runbooks | Follow ingestion and retrieval, then ground a response in cited passages. |
| 6 | Security and governance | Threat-model prompt injection, secrets, identity, tenant boundaries, and writes; define when the agent must pause or hand control to an engineer. |
| 7 | AWS architecture | Trace the request through networking, API delivery, compute, model, and search services. |
| 8 | Evaluation | Test diagnosis, evidence, retrieval, tool choice, follow-up handling, abstention, and unsafe behavior with labeled synthetic cases. |
| 9 | Operations and CI/CD | Observe latency, failures, cost, and quality; safely test and promote changes. |
| 10 | End-to-end release | Explain a production-style design, its trade-offs, limits, recovery, and operating guide. |

## Recommended reading order

Start with [fundamentals](01-fundamentals/README.md), then [LangGraph](02-langgraph/README.md), [RAG](03-rag/README.md), [model selection](04-model-selection/README.md), and [the reference architecture](05-reference-architecture/README.md). The remaining pages explain AWS implementation options and operational practices. Not every example requires every AWS service.

## Boundaries

- **Concept notes:** this folder; explanations and architecture diagrams.
- **Hands-on code:** the separate lab; simulated incidents and tests first.
- **Production use:** requires an explicit threat model, least-privilege review, evaluation, observability, and human approval for changes.

Day numbers describe a teaching sequence, not a claim that a production system should be built in ten days.

## Optional advanced lesson after Day 10

### Stateful, incremental incident investigation

The ten-day path teaches the core system. This optional lesson extends it to incidents where evidence arrives over time and an engineer asks follow-up questions in the same investigation. It connects to [conversation memory](03-rag/conversation-memory.md), [LangGraph state and checkpoints](02-langgraph/README.md), [security and governance](10-security-and-governance/README.md), and the [end-to-end project](14-end-to-end-project/README.md).

**Example:** a deployment starts failing, new container events and log windows arrive, and the engineer asks, “What changed in the last release?” The investigator keeps a scoped incident state, collects only approved read-only evidence, retrieves relevant runbook guidance, and explains what it knows, what is missing, and when it will stop.

**Deliverable:** a state-flow diagram, synthetic event fixtures, and follow-up evaluation cases in the separate lab. The lesson explains how to design this flow; it does not require a hosted queue, a model API, or an AWS account.

Keep four kinds of data distinct while building it: conversation turns, workflow state/checkpoints, chronological event or log records, and chunks of runbook documents indexed for RAG. They solve different problems and should not be mixed into one generic “memory” store.
