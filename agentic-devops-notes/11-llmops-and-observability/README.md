# 11. LLM operations and observability (introductory notes)

Observability answers what the service did and how it performed. For an AI workflow, measure operational health and answer quality separately. A fast, healthy service can still produce a wrong diagnosis.

## What to observe

- **Logs:** structured, correlated records for request ID, workflow node, tool name, status, duration, and safe error class. Redact secrets and avoid raw sensitive prompts by default.
- **Metrics:** request volume, error/throttle rate, queue depth, tool failures, model failures, retrieval latency, and resource saturation.
- **Distributed traces:** follow one investigation across API, workflow, tools, retrieval, and model calls. Do not put sensitive content in span attributes.
- **Token use and cost:** record input/output tokens and provider/model identifiers where available; estimate cost from current rates. Include retries and guardrails in cost accounting.
- **Latency:** separate API, retrieval, tool, model, and total duration. Track percentiles and timeout rates.
- **Retrieval quality:** evaluate source relevance and citation support with a labeled set; online signals alone can be misleading.
- **Agent evaluation:** diagnosis correctness, evidence sufficiency, tool precision, unnecessary calls, policy violations, and abstention behavior.
- **Hallucination monitoring:** sample reports for claims without tool or retrieved evidence; use checks and human review rather than assuming an automatic detector is definitive.

CloudWatch can collect AWS logs, metrics, and alarms. OpenTelemetry-compatible tracing can help connect components. Select tools that fit the deployment and privacy requirements; do not log more simply because a platform can.

## Example investigation trace

Give each request an `investigation_id`, for example `inv-2026-0042`. One trace can contain spans for API authorization, LangGraph nodes, `describe_service_deployment`, log retrieval, OpenSearch query, Bedrock invocation, and response validation. Each span records start/end time, outcome, and safe identifiers. A trace makes it possible to see that the investigation spent time waiting on a model call or that log retrieval failed, without copying full log contents into the trace.

Example metric names for a dashboard might be `investigations_started`, `investigations_completed`, `tool_calls_by_tool_and_status`, `model_latency_ms`, `retrieval_latency_ms`, `input_tokens`, `output_tokens`, and `reports_rejected_by_validation`. These are proposed measurements, not production results. Avoid labels such as raw user ID, full incident text, or pod name if they create sensitive/high-cardinality data.

## Measure quality with labeled cases

For each sanitized case, label the expected root cause, evidence sources, permitted tools, and whether the correct outcome is to abstain. A repeatable evaluation can calculate root-cause accuracy, fraction of key claims supported by cited evidence, correct tool-selection rate, unnecessary calls, secret leaks, and unsafe tool proposals. Sample borderline cases for human review. Keep this evaluation dataset separate from test prompts when measuring generalization; otherwise, the model may simply memorize examples.

Retrieval quality and final answer quality should be measured separately. If the correct runbook never appears in the top results, changing the generation model may not solve the root issue. Likewise, good retrieval does not guarantee the generator uses the evidence correctly.

## Alerting and response

Alert on service symptoms that require action: sustained failures, throttling, queue age, latency objective breach, unexpected spend, or a rise in unsafe tool requests. Route alerts to an owner and runbook. Define severity and avoid paging on normal model uncertainty. Track evaluation regressions in CI before deploying prompt, model, retriever, or tool changes.

For example, an alert can fire when the agent API’s error rate breaches its agreed threshold over a sustained window, or when the oldest SQS job exceeds its response objective. A separate quality gate can block release if evaluation finds a new secret leak or an unauthorized tool call, even if service availability is healthy. Set actual thresholds from baseline/load testing and business needs; this guide does not assume production measurements.

## Interview questions

**What is an AI quality metric that infrastructure metrics miss?** Whether the diagnosis is correct and supported by the evidence, and whether the selected tools were appropriate.

**Should full prompts be logged?** Only if there is a clear need, approved data handling, access control, redaction, and retention. Usually structured metadata is safer.

## Official references

- [Amazon CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)
- [Bedrock invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)
- [CloudWatch guardrail metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-guardrails-cw-metrics.html)
- [OpenTelemetry](https://opentelemetry.io/docs/)
