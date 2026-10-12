# 8. Agent runtime (introductory notes)

The runtime hosts the application and coordinates work. It is separate from the model, which performs inference, and separate from the infrastructure tools the assistant may call.

## Common choices

- **Amazon ECS:** orchestrates containers. With EC2 capacity, the team manages host capacity; with Fargate, AWS manages the underlying compute hosts.
- **AWS Fargate:** serverless compute for containers used with ECS or EKS. It can suit a continuously available API without direct host management.
- **AWS Lambda:** event-driven functions with managed execution. Often suits short event handlers, lightweight ingestion steps, or glue code; check duration, packaging, concurrency, and state needs.
- **Amazon ECR:** stores container images. Use immutable tags/digests for releases and scan images as part of delivery.
- **Amazon SQS:** durable queue that decouples producers and consumers. Useful for asynchronous investigations or ingestion jobs that need buffering/retries.
- **Amazon SNS:** pub/sub notifications and fan-out to subscribers.
- **Amazon EventBridge:** event bus and rules for routing events between producers and consumers.
- **AWS Step Functions:** managed state-machine orchestration, especially useful for service workflows, retries, and long-running orchestration. It can complement application-level LangGraph; decide which layer owns each transition.

## Synchronous request or asynchronous job?

Use synchronous HTTP when the task has a predictable short duration and can finish within the end-to-end client and gateway deadlines. Return a report directly. Use an asynchronous pattern when work may take longer, needs a queue, should survive client disconnects, or must be retried independently: accept the request, authorize it, enqueue a job, return an ID, then let the client poll or receive a notification. Do not hold an API request open through an unbounded agent loop.

### Example flows

**Synchronous:** `POST /investigations` validates a short fixture, performs two quick read-only checks, and returns a report with `200 OK`. The client waits only within configured limits. If an upstream model times out, the response can contain a partial evidence report with an explicit status.

**Asynchronous:** the same request is authenticated and stored with an investigation ID, then queued to SQS. The API returns `202 Accepted` and the ID. An ECS/Fargate worker consumes one job, runs a bounded graph, stores the result under access-controlled storage, and updates job status. The UI polls `GET /investigations/{id}` or receives an authorized notification. Configure a dead-letter queue and idempotency so a redelivered job does not create duplicate reports/actions.

SNS can fan out a completion event to multiple subscribers. EventBridge can route a `DeploymentFailed` event to the investigation service. Step Functions can orchestrate AWS service tasks and durable waits; LangGraph can orchestrate agent-specific nodes and model/tool turns. One workflow should clearly own retries and state transitions at each boundary to avoid retry multiplication.

## How to choose a runtime

| Workload | Possible fit | Example and trade-off |
|---|---|---|
| Always-available HTTP API or worker | ECS on Fargate | Runs a containerized Python service without managing EC2 hosts; service, task, network, and scaling configuration remain your responsibility. |
| Short event handler or ingestion transform | Lambda | Process an S3 notification or normalize one small document; check execution, dependency size, concurrency, and retry semantics. |
| Buffered work | SQS plus ECS worker or Lambda consumer | Queue incident investigations during a burst; adds queue visibility, redelivery, and poison-message handling. |
| Container image storage | ECR | Store the versioned agent image and deploy by immutable digest. |
| Fan-out event notification | SNS or EventBridge | Notify separate reporting consumers or route deployment events based on event fields. |
| AWS service state machine | Step Functions | Coordinate an approval wait or multiple AWS tasks; avoid duplicating agent reasoning/control flow. |

Fargate removes host management; it does not mean “no servers to think about.” Plan task CPU/memory, subnet paths, security groups, task IAM role, logs, scaling, deployment health, and container patching.

## Safety and operations

Run each task with a dedicated IAM role. Limit CPU, memory, concurrency, execution time, and outbound connectivity. Make queue consumers idempotent, use a dead-letter queue where appropriate, and record correlation IDs. Store only necessary state and keep model/tool call logs redacted. Containerized agent services still need patching, image provenance, health checks, and deployment controls.

## Interview questions

**ECS Fargate or Lambda?** Choose based on workload duration, packaging, scaling, network and runtime needs, and operational model; either can be appropriate for parts of an assistant.

**SQS or EventBridge?** SQS is a queue for work delivery and buffering; EventBridge routes events to targets. They can be combined, but solve different jobs.

**LangGraph or Step Functions?** LangGraph manages application agent state/control flow; Step Functions orchestrates AWS service tasks and durable state machines. Avoid duplicating orchestration responsibility without a reason.

## Official references

- [Amazon ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- [AWS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html)
- [Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html)
- [AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)
- [SQS visibility timeout and message processing](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
