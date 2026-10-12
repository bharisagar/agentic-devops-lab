# 9. Data and retrieval (introductory notes)

Choose storage from access patterns, consistency, query needs, scale, and operating skills. A vector database is not a general replacement for a relational database or object store.

## Services in the example

- **Amazon S3:** durable object storage for source runbooks, reports, and ingestion artifacts. Keep access policies and lifecycle rules aligned to data sensitivity and retention.
- **Amazon OpenSearch Service:** search and analytics engine; it can support full-text and vector search. Use an index mapping to define fields, types, and vector dimensions.
- **PostgreSQL:** relational database for structured records, transactions, constraints, and joins. PostgreSQL with the `pgvector` extension can also support vector similarity search when that fits the workload.
- **Amazon ElastiCache:** managed in-memory data stores, often used for caching or low-latency ephemeral data. Cache authorization-sensitive content carefully and set TTL/invalidation rules.

## OpenSearch concepts

An **index** groups searchable documents. A **mapping** declares field types, analyzers, vector dimensions, and whether a field can be filtered or sorted. **Shards** partition an index; **replicas** provide additional copies that can improve read capacity and availability. Too many shards waste resources; sizing depends on dataset and workload.

### Example document and mapping decisions

A runbook chunk could be stored as one search document with fields for `chunk_id`, `document_id`, `title`, `section`, `body`, `team`, `version`, `effective_date`, and `embedding`. Map `body` as analyzed text for word search, `team` and `version` as exact-match keyword fields for filters, dates as date fields, and `embedding` as a vector field with the dimension required by the chosen embedding model. Do not guess the vector dimension: use the model’s documented output and keep it compatible across indexed chunks and query vectors.

Example query: the operator’s identity is authorized for `team=payments`; the retrieval query filters to `team=payments` and `version=current`, then searches for passages about “tasks exiting during startup.” A separate keyword clause can match an exact `ExitCode=1` or error string. Results carry `document_id` and `section` so the report can cite the actual source.

### Shards, replicas, and index lifecycle in practice

If an index has primary shards, documents are partitioned across them. Replicas copy primary shards and can support reads and resilience according to the deployment configuration. Replicas consume storage/compute and do not replace backups. Choose shard count from expected data size and query/load needs; oversharding makes cluster management harder. For a new runbook corpus, start with the simplest index layout supported by the selected OpenSearch offering, then measure before tuning.

An index lifecycle policy can roll over an index when it reaches a condition and later delete or transition old data if the deployment supports that policy. For example, versioned runbook chunks may be rebuilt into `runbooks-v8` while `runbooks-v7` stays available for rollback. Do not delete the old index until access, recall, citations, and rollback have been verified.

## Choosing among S3, OpenSearch, PostgreSQL, and ElastiCache

| Need | Candidate | Example |
|---|---|---|
| Original documents and durable files | S3 | Keep the approved PDF/Markdown runbook and ingestion source version. |
| Full-text plus vector search | OpenSearch | Find relevant incident troubleshooting passages at query time. |
| Transactions, relational constraints, structured entities | PostgreSQL | Store investigation records, approvals, and foreign-key relationships. |
| Low-latency temporary cache | ElastiCache | Cache a short-lived non-sensitive lookup result, with TTL and careful tenant scoping. |

Do not store the only source copy of a runbook in a derived search index. Do not use a cache as the authorization source. If pgvector is sufficient for the project’s scale and query needs, it may avoid operating a separate vector system; evaluate expected workload and supported extension/version.

For vector retrieval, store the embedding plus text reference and metadata. Apply tenant/product/version filters as part of retrieval. Use text fields for exact terms and vector fields for semantic similarity; hybrid ranking can combine both. Index lifecycle policies can roll over, retain, or delete indices, but only after the retention and re-indexing requirements are understood.

## Data lifecycle and governance

Maintain source provenance, document version, parser/chunker version, embedding model ID, and index schema version. Re-index intentionally when content, embeddings, or schema changes. Define deletion propagation: removing a source may require deleting chunks and cached copies too. Back up source documents and evaluate whether the search index can be rebuilt within the required recovery objective.

## Interview questions

**Why keep source documents in S3 if chunks are in OpenSearch?** Object storage is a durable source of truth; the search index is a derived retrieval structure that can be rebuilt.

**What is the difference between a shard and a replica?** A shard partitions index data; a replica is a copy of a shard. Replicas can improve availability/read capacity at additional storage and resource cost.

**When might PostgreSQL be a better fit than OpenSearch?** When relational integrity, transactions, and joins dominate, or when pgvector satisfies the retrieval need without operating a separate search system.

## Official references

- [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [OpenSearch index concepts](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html)
- [OpenSearch vector search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vector-search.html)
- [RDS for PostgreSQL extensions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.Extensions.html) — verify the supported extension/version in the target Region.
- [Amazon ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.html)
- [OpenSearch mappings](https://docs.opensearch.org/latest/field-types/)
- [Choosing the number of OpenSearch shards](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp-sharding.html)
- [OpenSearch storage and replicas](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp-storage.html)
- [Managing OpenSearch indexes and lifecycle](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/managing-indices.html)
