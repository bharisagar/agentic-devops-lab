# Agentic DevOps Notes

Hi, I’m Bhari. This is the concept guide for my **Agentic DevOps: Day 1–10** learning series. We’ll start with the ideas, understand how the parts fit together, and then build the hands-on lab in the separate [Agentic DevOps Lab](../README.md).

The notes use one example throughout: an assistant that investigates a failed deployment or a container/Kubernetes incident. It gathers evidence through approved tools, finds relevant runbook guidance, and prepares a report for an engineer. It does not make a production change on its own.

## Learning path

- [Roadmap: Day 1–10](ROADMAP.md)
- [1. Fundamentals](01-fundamentals/README.md)
- [2. LangGraph](02-langgraph/README.md)
- [3. Retrieval-augmented generation (RAG)](03-rag/README.md)
- [4. Model selection](04-model-selection/README.md)
- [5. Reference architecture](05-reference-architecture/README.md)
- [6. AWS networking](06-aws-networking/README.md)
- [7. AWS application delivery](07-aws-application-delivery/README.md)
- [8. Agent runtime](08-agent-runtime/README.md)
- [9. Data and retrieval](09-data-and-retrieval/README.md)
- [10. Security and governance](10-security-and-governance/README.md)
- [11. LLM operations and observability](11-llmops-and-observability/README.md)
- [12. CI/CD and infrastructure as code](12-cicd-and-iac/README.md)
- [13. Reliability and disaster recovery](13-reliability-and-disaster-recovery/README.md)
- [14. End-to-end project](14-end-to-end-project/README.md)
- [Glossary](glossary/README.md)
- [Diagram index](diagrams/README.md)

## How to use these notes

Read the first five topics in order before choosing an AWS design. Each page explains terms before using them and separates a core responsibility from optional services. AWS diagrams are examples, not a claim that this system has been deployed. Service choice depends on requirements, account limits, region availability, security review, and current pricing.

When a topic is central, the notes answer: what it is, why it is useful, how it works, where it fits, an incident example, security considerations, alternatives/trade-offs, and interview questions. We reuse a failed `orders-api` deployment so each concept connects back to one understandable problem.

These pages explain concepts only. Runnable code, experiments, and tests belong in the [lab repository](../README.md). We will not put credentials, real incident data, or customer information in either project.

## Sources

The primary references are the [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview) and official [AWS documentation](https://docs.aws.amazon.com/). Links to topic-specific references appear on each page. Service details and pricing can change, so check the linked docs when implementing.
