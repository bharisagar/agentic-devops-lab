# 12. CI/CD and infrastructure as code (introductory notes)

Treat prompts, model configuration, tools, application code, retrieval data, and infrastructure as versioned release inputs. A prompt or index mapping change can change system behavior even when application code is unchanged.

## A safe delivery path

1. Pull request checks run unit tests, schema checks, security tests, and deterministic evaluation fixtures without paid model calls.
2. Build a container image and scan dependencies/image contents. Publish to ECR using an immutable digest and provenance controls.
3. Plan infrastructure changes with Terraform and review the plan. Keep state protected and environment-specific.
4. Promote the same tested artifact through development, staging, and production; use environment-specific configuration and least-privilege roles.
5. Deploy gradually using an appropriate strategy such as rolling, blue/green, or canary. Check health and evaluation signals, then roll back on defined failures.

GitHub Actions can automate workflow jobs using scoped credentials, ideally short-lived federation rather than long-lived keys. Protect deployment environments and approval rules. Never print secrets or prompt payloads in CI logs.

### Worked release example

Suppose a change updates the LangGraph prompt and adds a `read_service_events` tool. A pull request can:

1. Run Python unit tests with a local/mock model and sanitized incident fixtures.
2. Assert the tool schema rejects an unknown cluster and that no shell command is possible.
3. Run a small labeled evaluation and compare diagnosis/evidence/tool behavior to the baseline.
4. Scan dependencies and the built container image; create an image digest.
5. Run `terraform fmt` and `terraform validate`; produce a plan for review without applying production changes.
6. On approval, deploy the same image digest to a test environment, run smoke and safety checks, then promote it with a controlled deployment strategy.

The model call in CI can be a deterministic stub so tests are repeatable and do not incur paid inference. A separate scheduled or manually approved evaluation can compare real providers where policy permits, but it must use sanitized cases and budget controls.

## Version and compatibility

Version prompts and tool schemas. Version source corpus snapshots, parsers, chunking rules, embedding model, index mapping, and retrieval parameters. Roll out a new index side-by-side when compatibility or re-indexing risk warrants it; switch traffic only after validation. Keep a route back to the previous prompt/model/index combination where feasible.

An investigation result should be traceable to a release manifest such as: application image digest, prompt ID/revision, tool-schema revision, model/provider ID, corpus version, embedding model, OpenSearch mapping/index version, and evaluator version. This tells an engineer what changed when behavior shifts. Store non-secret version identifiers; never put credentials in the manifest.

### Deployment strategy examples

- **Rolling:** replace tasks gradually; simple for compatible changes, but old and new versions may run at the same time.
- **Blue/green:** send traffic to a new task set, validate, then shift; rollback can shift traffic back if the old environment remains available.
- **Canary:** send a small share of traffic to the new version and compare operational and quality signals before increasing it.

The strategy depends on the runtime and release risk. A model/prompt or retrieval change also needs quality checks because a healthy HTTP response alone does not prove equivalent behavior.

## Interview questions

**What should run in CI without model calls?** Deterministic unit, security, schema, policy, fixture-based evaluation, and infrastructure validation tests.

**Why deploy the same image digest?** It means staging and production use the artifact that passed prior checks, rather than rebuilding potentially different bytes.

## Official references

- [GitHub Actions documentation](https://docs.github.com/actions)
- [Terraform documentation](https://developer.hashicorp.com/terraform/docs)
- [Amazon ECR image scanning](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html)
- [ECS deployment types](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html)
- [GitHub Actions: OpenID Connect in AWS](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform test](https://developer.hashicorp.com/terraform/cli/commands/test)
