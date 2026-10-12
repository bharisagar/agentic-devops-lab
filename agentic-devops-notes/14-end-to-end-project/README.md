# 14. End-to-end project: deployment incident assistant

## Problem statement

An engineer needs help investigating a failed deployment, restarting container, or Kubernetes workload incident. The assistant gathers a bounded set of read-only evidence, searches approved runbooks, and returns a report with sources and uncertainty. It does not perform remediation in the initial version.

## Example incident from request to report

An authorized developer submits: “Investigate why deployment `orders-api-42` is unhealthy in staging.” The request identifies the environment and deployment; it does not include credentials or ask the model to choose an account.

1. The API authenticates the developer and checks access to staging.
2. The application creates an investigation ID and validates the request against a strict schema.
3. LangGraph inspects the deployment status. It sees task starts followed by exits and records source IDs/timestamps.
4. The workflow calls a read-only log tool with bounded time range and byte limit. It detects `DATABASE_URL` is not configured, but does not retrieve or display secret values.
5. RAG retrieves the current “required application configuration” runbook section, filtered to documents the developer may access.
6. The selected model drafts a structured report. It can only cite evidence IDs and retrieved source IDs present in the workflow state.
7. A validator checks the schema, redacts sensitive patterns, verifies citations, and labels unsupported conclusions as hypotheses.
8. The developer receives findings, evidence, confidence/limitations, and suggested checks. No ECS deployment is changed.

An example finding could read: “Likely cause: the container exits during startup because the required `DATABASE_URL` configuration reference is absent. Evidence: startup log event `log-3`; task stopped at `time-1`; service deployment `orders-api-42`. The secret value was not read. Check that the staging task definition references the intended secret and that its execution role can retrieve it.” In the actual project, only real observed evidence may be reported; these identifiers here are illustrative.

## Reference flow

The [reference architecture](../05-reference-architecture/README.md) contains request and ingestion diagrams. The core request crosses identity and API boundaries, enters an application runtime, follows an explicit LangGraph workflow, calls scoped diagnostic tools and authorized retrieval, invokes the chosen model, validates the result, and returns a report. The knowledge pipeline extracts and indexes versioned runbooks separately.

## Component responsibilities

| Component | Responsibility | Important boundary |
|---|---|---|
| API and identity layer | Authenticate caller, authorize incident/environment scope, rate-limit | Request data cannot grant its own privilege |
| Agent application | Validate input, own state, budgets, and report schema | Model output is untrusted until checked |
| LangGraph | Coordinate nodes, routes, state, and optional pause/resume | It does not grant AWS permissions |
| Diagnostic tools | Read a defined resource set and return structured evidence | Narrow role, validated identifiers, audit record |
| Retrieval service | Find allowed runbook passages with source metadata | Filter tenant/access scope before returning text |
| Model endpoint | Interpret supplied context and return structured proposal/report | No direct credentials; prompts and outputs may be sensitive |
| Safety/validation layer | Check schema, provenance, redaction, policy, limits | Reject missing or unsupported claims |
| Observability | Correlate tool/model/retrieval calls and quality checks | Redact contents and apply retention |

## Build sequence

1. Write a data-flow and threat model. Decide exact users, incident types, read scope, and stop conditions.
2. Create sanitized labeled fixtures and a deterministic baseline.
3. Define a typed read-only tool registry and validate every argument.
4. Add a bounded model-assisted loop behind a replaceable provider interface and keep deterministic CI tests.
5. Add runbook ingestion, authorization-aware retrieval, provenance, and retrieval evaluation.
6. Add an AWS deployment only when required: networking, identity, runtime, search, and inference choices should each have a reason.
7. Add security tests, operational dashboards/alerts, load/recovery tests, deployment automation, and a runbook.

## Operational questions to answer before production

- Which accounts, clusters, namespaces, and log groups may each user inspect?
- What sensitive data can logs or manifests contain, and where may it be sent?
- What is the maximum investigation duration, number of tool calls, and model budget?
- How does the service behave if model, retrieval, or an operational API is unavailable?
- How are prompt, model, tool, corpus, embedding, and index changes evaluated and rolled back?
- Who owns false diagnoses, security events, and approval of future remediation features?

## Example architecture trade-off decisions

- **Need to deploy a concept lesson today?** Run locally on fixtures; do not provision VPC, Bedrock, or OpenSearch just to teach the workflow.
- **Need a small internal HTTP service?** ECS/Fargate behind an internal ALB may be enough. Add API Gateway when its API-level features, integrations, or policies solve a named requirement.
- **Need current runbook search?** RAG is useful when the corpus is larger or changes often; a few fixed troubleshooting rules can stay in code or simple files initially.
- **Need a long-running investigation?** Use an asynchronous job pattern with durable status. For short, bounded checks, a synchronous request may be simpler.
- **Need to call a model privately?** Evaluate supported Bedrock connectivity and the selected model/Region; a VPC endpoint is a networking choice, not a guarantee of availability or authorization.

Each decision should be recorded with its requirement, alternative considered, security impact, cost/operations impact, and a condition that would make us revisit it.

## Architecture trade-offs

Use synchronous HTTP for short work and a queue/job status pattern for long investigations. Use OpenSearch when indexed search needs justify it; use simpler retrieval for a small fixed corpus. Use Fargate for a continuously available container API, Lambda for suitable short event work, or Step Functions for AWS service orchestration where it fits. Bedrock is one managed model access option. The appropriate design follows tested requirements and current service capabilities.

## Interview questions

**What is the safest MVP?** A read-only, bounded investigation on sanitized fixtures with deterministic tests, evidence provenance, and a clear partial-result path.

**How do you prevent the model from running destructive actions?** Do not expose destructive tools in the MVP; enforce tool authorization in application/cloud permissions, independently validate arguments, and require a separate approval path for any future writes.

**How do you know the system helps?** Compare against a baseline using labeled incidents and measures for diagnosis correctness, evidence support, tool quality, time, cost, and unsafe behavior.
