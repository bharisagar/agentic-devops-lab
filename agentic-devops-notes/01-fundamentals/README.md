# 1. Agentic DevOps fundamentals

## What is Agentic DevOps?

Agentic DevOps applies an AI system that can select from explicitly permitted tools to a DevOps task. The system receives a goal, gathers evidence, uses a model to help choose or interpret the next step, and returns a result for an engineer. The word *agentic* describes a degree of delegated decision-making; it does not mean the system has human judgment or should receive broad access.

For our example, the goal is: “Investigate why this deployment failed and explain the evidence.” The assistant may inspect a deployment status, read sanitized logs, and search approved runbooks. It may recommend a rollback, but the initial design does not execute it.

### Walk through one incident

Suppose release `orders-api-42` starts, then its container exits. A fixed script might check only the exit code. An agent-style investigation can first inspect deployment status, notice repeated container restarts, then call the allowed log-reading tool, find `DATABASE_URL is required`, and finally retrieve the runbook section for missing application configuration. The report should say the deployment is unhealthy, quote or summarize the relevant evidence with source and time, and recommend checking the secret/configuration reference. It must not reveal the variable value or change the service.

This example also shows the division of responsibility: the model may choose “read logs”; the application checks that the request is allowed; the tool fetches the logs; the report validator checks that claims refer to returned evidence.

| System | How it behaves | Incident example |
|---|---|---|
| Chatbot | Responds to the prompt from its learned patterns and supplied context. It does not inherently inspect the environment. | Explains what `CrashLoopBackOff` usually means. |
| Deterministic script | Runs the branches and checks its author specified. Same inputs and version produce predictable checks. | If restart count is high, print the supplied logs and test a known rule. |
| Tool-using agent | A model selects among an allowlisted set of tools; the application validates requests, supplies results, and bounds the loop. | Inspect pod events, then logs, then retrieve the relevant runbook before reporting. |

An agent is not automatically more accurate than a script. Use a fixed script for a stable, known procedure. Use a model-assisted agent when the evidence and next useful inspection vary, and verify that it improves measured outcomes enough to justify extra complexity.

## Core terms

- **LLM (large language model):** a model that generates or transforms text based on input and learned patterns. It can make mistakes and does not automatically know current cluster state.
- **Tool:** an application function with a defined name, input schema, permission boundary, and output. Examples are `get_deployment_status` and `read_pod_events`.
- **Workflow:** the allowed sequence and branching rules around work. A workflow can be fixed, model-directed, or a mix.
- **State:** the structured facts collected for one investigation, such as incident ID, tool results, current hypothesis, and step count.
- **Planning:** selecting a sequence of actions toward a goal. In an AI system, a plan is a proposal that must remain bounded and checked.
- **Reasoning:** the model's generated explanation or intermediate decision. Treat it as a hypothesis, not as proof. Tool output and validation provide evidence.
- **Memory:** information carried between steps or sessions. Keep durable memory explicit, scoped, expiring, and access-controlled; do not assume chat history is a reliable operational database.

### The terms in our incident example

| Term | Example |
|---|---|
| Goal | “Explain why deployment `orders-api-42` failed.” |
| Tool | `read_task_events(service, task_id)` returns a bounded, sanitized set of events. |
| Workflow | Validate request → inspect deployment → choose another check → write report. |
| State | `investigation_id`, step count, evidence references, and current status. |
| Planning | The model proposes checking task logs after status shows the task exited. The proposal is validated before use. |
| Reasoning | “A missing configuration reference may explain the startup exit.” This is a hypothesis until checked against logs/config evidence. |
| Memory | A saved checkpoint lets a long-running investigation resume after an engineer reviews it; store it with access controls and retention. |
| Guardrail | Application code refuses an unknown tool or an out-of-scope cluster, even if the model requests it. |

The model’s internal generated rationale is not an audit source. For auditing, record observable facts such as the tool name, validated arguments, result status, evidence IDs, model/prompt version, and route taken.

## A safe starting problem

Keep the first task narrow: investigate one simulated deployment failure and create a report. Define which data the system may read, which tools it may call, how many steps it may take, what evidence is required, and when it must stop or ask an engineer. Separate diagnosis from remediation. This creates a testable baseline before adding a model or cloud integration.

Write down a success condition before implementation. For example: “Given a fixture with a missing required variable, the investigator identifies the missing variable name, includes the startup log as evidence, does not expose any variable value, and stops after the available checks.” This is testable; “use AI to fix DevOps” is too broad to evaluate safely.

## Why it fits DevOps

Operations work often combines structured state (deployment status, events, metrics) with text (logs, change notes, runbooks). A model can help route between inspections and summarize findings, while ordinary code enforces identity, schemas, limits, redaction, and approval. A useful report says what was observed, where it came from, what remains uncertain, and what a human could check next.

## Security and trade-offs

Logs, ticket text, manifests, and retrieved documents are untrusted input. They can contain instructions aimed at the model. Tool permissions should be narrow and server-enforced; never allow model text to become arbitrary shell, SQL, or infrastructure commands. Read-only investigation still needs access control, audit records, data minimization, and tenant checks. If a deterministic check solves the problem, it is simpler to operate than an agent.

**Example of a boundary:** allow `get_pod_events(cluster_id, namespace, pod_name)` only after checking the caller’s access to that cluster and namespace. Do not offer `run_command(command_text)` and hope the prompt prevents destructive commands. The first interface is narrow enough to validate; the second gives the model an open-ended execution surface.

## Interview questions

**How is an agent different from automation?** A script follows a predefined path; an agent can choose among approved tools based on observed evidence. Both should be bounded and tested.

**Does an agent need to change infrastructure?** No. Read-only investigation is a useful first capability. Any later write action needs separate authorization, validation, and often human approval.

**What is the model responsible for?** It can interpret context and propose the next allowed action or a summary. The application remains responsible for authentication, authorization, tool execution, validation, and safety controls.

## Further reading

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
- [Amazon Bedrock overview](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
