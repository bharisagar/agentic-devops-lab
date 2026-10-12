# 13. Reliability and disaster recovery (introductory notes)

The agent should degrade safely when a dependency fails. If the model is unavailable, return collected evidence and say the diagnosis is incomplete. If retrieval fails, do not pretend a runbook was consulted. If a tool fails, report that gap and stop or continue only when policy permits.

## Reliability patterns

- **Timeouts:** set per-tool and overall deadlines. Bound model response time and queue wait.
- **Retries:** retry transient failures with limits and backoff; do not retry invalid requests or authorization denials. Use idempotency for effects.
- **Throttling:** cap concurrency and respect provider/service quotas. Queue work when asynchronous buffering is appropriate.
- **Circuit breaker:** temporarily stop calls to a dependency that is repeatedly failing, then probe recovery carefully.
- **Autoscaling and high availability:** scale across Availability Zones and use health checks where justified. Protect downstream APIs from a sudden scale-out by limiting concurrency.
- **Graceful degradation:** offer deterministic checks, partial reports, or manual runbooks when model/search services are unavailable.
- **Cost controls:** cap steps, tokens, retrieval size, concurrency, and investigation duration; alarm on spend anomalies.

### Example: model provider throttles during an incident

The API accepts an incident but the model endpoint returns a throttling response. The application should not spin in an unbounded retry loop. It can retry a small number of times with backoff if the deadline permits, then return collected read-only evidence and mark the generated diagnosis unavailable. For an asynchronous job, the worker can release/retry the message under the queue’s visibility and redrive policy. A circuit breaker can stop flooding a dependency that remains unhealthy. The operator sees a partial report plus a clear next action, such as using the linked manual runbook.

### Timeouts, retries, and budgets together

Use an overall deadline plus shorter per-call deadlines. For example, if a job has a 90-second total budget, each diagnostic and model call must fit inside the remaining time; do not grant every step 90 seconds. Retry only transient errors, use bounded exponential delays with jitter, and ensure retry count is included in the total tool/token budget. A timeout is an expected workflow result that should be recorded, not silently hidden.

## Backup and recovery terms

**RTO** (Recovery Time Objective) is the target time to restore service after disruption. **RPO** (Recovery Point Objective) is the acceptable amount of data loss measured in time. Set these from business requirements, not from a template.

Back up authoritative documents, application configuration, Terraform state, and any irreplaceable workflow state. A derived search index may be rebuilt from sources, but test rebuild time and validate embeddings/index compatibility. Decide whether in-flight investigations can be restarted or need persisted checkpoints. Test restore procedures.

### Define objectives with an example

If the internal support team says it can tolerate losing the most recent 15 minutes of investigation status and wants the service restored within two hours, those are candidate RPO/RTO targets to validate with owners and architecture tests—not universal defaults. A rebuilt OpenSearch index may be acceptable if source documents and ingestion versions are durable and rebuild completes within the target. If approval records are authoritative audit evidence, they need a stronger persistence/backup plan than a disposable cache.

Test at least: model endpoint unavailable, OpenSearch unavailable, diagnostic API denied/throttled, one Availability Zone unhealthy, queue backlog, and restore from backup. Record whether the assistant returns a partial report, queues work, or fails closed. Never respond to uncertainty by widening IAM or skipping authorization.

## Interview questions

**Should every error be retried?** No. Retry only transient failures and bounded safe operations; permission and validation errors need correction, not repetition.

**What does graceful degradation look like?** A partial, honest report with known evidence and an explicit unavailable dependency, plus a manual next step.

## Official references

- [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Amazon SQS dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [AWS Backup](https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html)
- [AWS Well-Architected: test reliability](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/test-reliability.html)
