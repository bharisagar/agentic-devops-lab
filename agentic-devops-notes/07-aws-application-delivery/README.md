# 7. AWS application delivery (introductory notes)

This page introduces common entry and routing services. DNS, edge delivery, web filtering, API routing, load balancing, authentication, and authorization are separate concerns.

## Service roles

- **Route 53:** DNS hosting and routing policies. It maps names to destinations; it does not inspect application identity.
- **CloudFront:** content delivery network and edge proxy. Often useful for static UI assets and global delivery; dynamic API caching should be explicitly designed and usually disabled for sensitive responses.
- **AWS WAF:** web request filtering attached to supported services such as CloudFront and API Gateway REST APIs. It can block patterns and rate-limit, but does not replace application-level authorization or secure code; check current integration support when choosing an API type.
- **API Gateway:** managed API front door for routing, quotas, authorization integrations, and request handling. Choose REST API or HTTP API based on required features, integrations, protocol, and cost; verify the current feature matrix rather than assuming they are interchangeable.
- **Application Load Balancer (ALB):** Layer 7 HTTP/HTTPS routing, host/path rules, and target groups; common with ECS web services.
- **Network Load Balancer (NLB):** Layer 4 TCP/UDP/TLS load distribution and static-address use cases. Choose by protocol, client behavior, and required load-balancer features.
- **TLS certificates:** AWS Certificate Manager certificates can terminate TLS at supported AWS endpoints. Use valid certificate names and maintain end-to-end encryption where required.
- **Authentication:** establishes who the caller is (for example, a signed token or Cognito user pool).
- **Authorization:** decides what that caller may do to a specific incident, environment, tenant, or tool. Authentication alone is not authorization.

## Typical request path

Route 53 may resolve a public application name to CloudFront; CloudFront can serve the UI and forward API paths to an API endpoint. API Gateway can authenticate/authorize and route requests. A private integration can connect API Gateway to a VPC service; an ALB can then distribute requests to ECS tasks. This chain is optional and each hop should have a clear purpose.

### Example: browser asks for an incident report

1. The browser resolves `agent.example.com`. Route 53 returns the configured CloudFront destination.
2. CloudFront serves cached static JavaScript/CSS from S3. For `/api/investigations`, it forwards the request according to an explicit behavior; incident responses should not be cached as public content.
3. AWS WAF, if attached at the selected supported edge/API layer, evaluates configured web request rules. It is not the place to decide whether this particular user may inspect production cluster `prod-1`.
4. API Gateway validates/routes the API request and may validate a token. The application verifies that the authenticated subject can access the requested environment and incident.
5. API Gateway sends the request through a configured private integration/VPC Link to the internal ALB. The ALB routes to healthy ECS task targets. The task security group accepts traffic from the ALB path only.

The API response returns along the managed path. TLS certificates configure trusted HTTPS at the relevant custom domains/load balancers. If TLS terminates at one layer and continues internally, document where encryption ends and whether the internal hop must also use TLS.

### REST API and HTTP API selection

Both are API Gateway products for HTTP APIs. AWS’s current comparison lists more features for REST APIs; HTTP APIs target a smaller feature set and lower price. For example, REST API may be needed for API Gateway WAF integration, private API endpoints, API keys/per-client throttling, or request validation. HTTP API may suit a JWT/Cognito-authorized service that needs straightforward routing and supported private ALB/NLB integration without those extra features. Check the current feature matrix and region/service constraints before deciding; requirements can change.

| Question | If yes, investigate |
|---|---|
| Do we need an API Gateway private endpoint, API key/usage plan, request validation, or WAF directly on API Gateway? | REST API |
| Do we need simple HTTP routing, JWT authorization, and lower-priced minimal API features? | HTTP API |
| Do we need HTTP host/path routing to ECS targets? | ALB may be sufficient, or it may sit behind API Gateway when API features justify both. |
| Do we need TCP/UDP or static network-layer addresses? | Evaluate NLB. |

API keys identify/measure a client usage plan; they should not be treated as user authentication or authorization for sensitive incident data.

### ALB versus NLB example

An ALB can route `/api/*` to an API target group and `/health` to a health handler, or route hostnames to separate services. An NLB can distribute TCP connections where the application needs network-layer behavior, protocols beyond HTTP, or supported static IP patterns. If the only requirement is ordinary HTTP routing to ECS, evaluate ALB first. Do not place both behind each other by habit.

### TLS, authentication, and authorization

TLS protects data in transit and proves the server’s identity to the client; it does not prove the API caller may use a tool. Authentication may validate a signed JWT from Cognito or another identity provider. Authorization then checks the token’s subject/claims and application policy against the requested account, cluster, namespace, or tenant. Recheck permission in the backend even if an edge layer has authenticated the caller.

## Example decision

For an internal tool used by one team, a private ALB and an identity-aware application may be sufficient. For a public API with API-specific throttling or managed authorization integration, API Gateway may help. If static web delivery needs a global edge cache, CloudFront may help. Avoid adding API Gateway and an ALB automatically; confirm why both layers are needed.

## Interview questions

**ALB or NLB?** ALB routes HTTP at the application layer, including host/path rules; NLB distributes supported network-layer traffic. Match the protocol and behavior requirements.

**CloudFront or API Gateway?** CloudFront is edge content delivery/proxy; API Gateway manages API entry and routing concerns. They may be composed, but they are not substitutes in all cases.

**Authentication or authorization?** Authentication proves identity; authorization grants a scoped action. An authenticated user still may not inspect a given production account.

## Official references

- [Route 53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)
- [CloudFront](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
- [AWS WAF](https://docs.aws.amazon.com/waf/latest/developerguide/what-is-aws-waf.html)
- [API Gateway REST and HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html)
- [Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Network Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html)
- [AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html)
- [API Gateway private integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-private-integration.html)
