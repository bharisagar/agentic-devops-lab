# 6. AWS networking (introductory notes)

Networking defines reachability, not application permission. A private subnet is a routing classification; a security group, network ACL, IAM policy, and application authorization each answer different questions.

## Core concepts

- **VPC:** an isolated virtual network in an AWS Region.
- **CIDR:** an IP address range, such as `10.20.0.0/16`. Plan ranges to avoid overlap with connected networks.
- **Subnet:** an address range in one Availability Zone. A public subnet has a route to an Internet Gateway; a private subnet has no direct route to that gateway. A private subnet may use a NAT route for outbound internet access.
- **Route table:** rules that direct traffic to a local VPC route, Internet Gateway, NAT Gateway, transit gateway, or endpoint.
- **Internet Gateway (IGW):** VPC attachment that enables internet routing for resources with appropriate routes and public addressing.
- **NAT Gateway:** managed outbound translation for private-subnet clients. It is not an inbound access path and is not a firewall. Consider per-AZ placement, resilience, data processing charges, and alternatives such as VPC endpoints.
- **Security group:** stateful, resource-associated allow rules. Use narrow source/destination and port rules.
- **Network ACL (NACL):** stateless subnet-level allow/deny rules; return traffic needs its own rule. Use it when subnet-level controls are required, not as a substitute for security groups.
- **VPC endpoint:** private connectivity to supported AWS services. Gateway endpoints and interface endpoints differ in service support and network behavior. An endpoint does not by itself authorize API actions; IAM and endpoint policies still matter.
- **DNS:** name resolution. VPC DNS attributes, private hosted zones, and resolver rules affect private service discovery. DNS resolution is not authorization.

## Example placement

The web edge and API entry can be public-facing according to the design, while ECS tasks and data services use private subnets. The ECS role calls only required AWS APIs. Interface endpoints may provide private paths to supported services such as Bedrock or CloudWatch. A NAT Gateway may be needed for other outbound destinations, but do not route all egress there without considering allowlists, monitoring, and cost.

## Follow one packet through the network

Suppose the VPC range is `10.20.0.0/16`. It can be divided into subnets such as public `10.20.1.0/24` and `10.20.2.0/24` in two Availability Zones, plus private application subnets `10.20.11.0/24` and `10.20.12.0/24`. A subnet is located in one Availability Zone; using more than one zone can help availability. These ranges are examples only and must not overlap with connected office/VPN/VPC ranges.

The public route table has the VPC-local route plus `0.0.0.0/0 → Internet Gateway`. A private app route table may have a default route through a NAT Gateway for required outbound internet access, or no general internet route if the app uses only private endpoints and internal resources. The Internet Gateway does not make every resource public: an internet-routable path, public address, and permissive security rules are all relevant.

Example inbound path: API Gateway reaches a private integration through a VPC Link to an internal ALB. The ECS task security group permits TCP `8080` only from the ALB security group. The ALB security group permits HTTPS/TCP `443` only from the VPC Link security group or supported source range configured for the integration. The task role separately allows only required AWS API calls. Network reachability does not equal IAM permission.

Example outbound path: ECS calls a supported AWS service over an interface endpoint on TLS port `443`; endpoint DNS resolves the service name to private endpoint addresses. If it calls a public model provider instead, the subnet may need controlled NAT egress and the application still uses TLS and provider authentication. A NAT route alone does not restrict which websites the application can contact.

## Security groups, NACLs, and DNS in the example

Security groups are **stateful**: when an allowed connection is established, return traffic is tracked. A useful rule is “task SG: allow inbound 8080 from ALB SG,” rather than “allow inbound from the whole VPC.” Network ACLs are **stateless** and applied at subnet boundaries; a custom NACL allowing inbound TCP 443 may also need outbound ephemeral ports for response traffic. Start with security groups for workload boundaries; add NACL restrictions only when there is a clear subnet-level requirement and the return path has been tested.

Route 53 can point `agent.example.com` to CloudFront for a browser interface. A private hosted zone can resolve an internal service name only for associated VPCs. Private DNS for an interface endpoint lets a normal AWS service hostname resolve to the endpoint addresses, but endpoint policy and IAM still determine whether the request is allowed.

## VPC endpoints and private connectivity

Gateway endpoints are used for supported services such as S3 and DynamoDB and are associated with route tables. Interface endpoints use AWS PrivateLink and elastic network interfaces in selected subnets for supported services. A VPC peering connection, Transit Gateway, VPN, and Direct Connect solve different VPC/on-premises connectivity patterns; they are not interchangeable with an endpoint to one AWS service. Choose the narrowest connectivity model that meets the need.

## Security and trade-offs

Use non-overlapping IP ranges, restrict ingress and egress, and log relevant network flows. Multi-AZ resources improve availability but add cost. NAT centralization can reduce gateway count but creates routing dependencies and cross-AZ traffic. Endpoints can reduce internet-path dependence, but endpoint policies, DNS, security groups, and IAM need correct configuration.

## Interview questions

**What makes a subnet public?** Its route table provides a route to an Internet Gateway. A resource also needs suitable addressing and security rules for public reachability.

**Does a NAT Gateway permit inbound connections?** No. It supports outbound-initiated connections and their responses; it is not an inbound publishing mechanism.

**Does a VPC endpoint grant access?** No. It provides a network path. Identity and resource policies still decide which API actions are allowed.

## Official references

- [Amazon VPC user guide](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [Subnets](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html)
- [Security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [VPC endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
- [Route tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
- [NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
- [Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
