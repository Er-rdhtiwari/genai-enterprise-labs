You are OpenAI Codex acting as a Senior Cloud/DevOps Architect + Terraform + Kubernetes platform engineer.

GOAL
Create a COMPLETE, production-minded Git repository called: rdh-platform-eks
This repo provisions and manages a shared “platform” EKS cluster on AWS and installs cluster add-ons so that many PoC repos can deploy into it via Helm.

CONSTRAINTS / STYLE
- Explain WHY before HOW in docs (short, clear).
- Production-minded: least privilege IAM, safe defaults, auditability, cost awareness, failure analysis.
- NO secrets or real identifiers in code. Use placeholders and environment variables.
- Do NOT hardcode: root domain, hosted zone IDs, state bucket/table names, account IDs.
- Must be runnable from Jenkins on EC2 and also runnable locally.
- Assume AWS Region default: ap-south-1 (configurable).
- Environment default: dev (configurable).
- Platform name_prefix default: platform (configurable).
- Domain strategy: create/manage hosted zone for poc.<ROOT_DOMAIN> (default POC_SUBDOMAIN=poc, ROOT_DOMAIN=rdhcloudlab.com but MUST remain variable-driven).
- Use Terraform for infrastructure and Helm for addons.
- Pin Terraform + provider versions and use stable module versions.
- Include debug/verification commands and checkpoints so user won’t get stuck.

DELIVERABLE
Generate the full repo with:
1) Terraform code (bootstrap + env) to provision:
   - VPC (public/private subnets, NAT, tags for EKS/ALB)
   - EKS cluster + managed node group(s)
   - IAM OIDC/IRSA enabled
   - CloudWatch control-plane logs enabled
   - (Optional but recommended) ECR shared repos (toggle var)
   - Route53 hosted zone for poc.<ROOT_DOMAIN> (toggle var)
   - Optional delegation NS record into parent hosted zone when PARENT_HOSTED_ZONE_ID provided
   - IAM roles/policies for add-ons (IRSA):
       - AWS Load Balancer Controller
       - ExternalDNS (Route53 changes scoped to zone)
       - cert-manager (Route53 DNS01) if enabled
2) Bootstrap Terraform to create remote state backend:
   - S3 bucket (versioning, encryption, block public access)
   - DynamoDB lock table
   - Outputs showing bucket/table names
   - Clear workflow to run bootstrap first, then env/dev
   - Backend config MUST be passed via -backend-config file generated from environment (because Terraform backend can’t use normal vars).
3) Cluster add-ons installation (Helm) with pinned chart versions and verification steps:
   - aws-load-balancer-controller
   - external-dns
   - cert-manager (optional toggle)
   - metrics-server
   Provide scripts to:
   - update kubeconfig
   - install/upgrade addons
   - uninstall addons (optional)
   - verify cluster health (pods, nodes, ingress controller readiness)
4) Jenkins pipelines:
   - Jenkinsfile.platform: terraform fmt/validate/plan/apply/destroy with manual approval gates
   - Jenkinsfile.addons: install/upgrade addons using helm + kubectl
   Requirements:
   - Pipeline parameters (ACTION=plan/apply/destroy, ENV=dev, AUTO_APPROVE=false, INSTALL_ADDONS=true)
   - Safe: “apply” and “destroy” require a manual confirmation step (input gate)
   - Store terraform plan output as artifact if possible
   - Use AWS credentials from:
       a) Jenkins environment variables or Jenkins credentials binding OR
       b) EC2 instance profile (assume-role optional)
   - Never echo secrets in logs
5) Documentation:
   - README.md: architecture, file purpose, execution flow, prerequisites, setup steps, and “how PoC repos will deploy into this cluster”
   - docs/runbook.md: step-by-step runbook with checkpoints and debug commands
   - docs/troubleshooting.md: common failures (IAM auth to EKS, IRSA, ALB controller, ExternalDNS, cert-manager), how to diagnose
   - docs/security.md: how secrets are handled, least privilege, logging notes
6) Tooling:
   - scripts/require_tools.sh (checks aws/terraform/kubectl/helm/jq/envsubst versions)
   - Makefile with targets: bootstrap-init/bootstrap-apply, tf-init, fmt, validate, plan, apply, destroy, kubeconfig, addons, status
   - .gitignore, .env.example (ONLY placeholders), LICENSE (optional)
   - Use bash scripts with: set -euo pipefail and clear error messages
7) Output formatting requirement:
   - Return a “FILE TREE” first.
   - Then for EACH file, output:
       ### FILE: <relative/path>
       ```<language>
       <content>
       ```
   - Ensure scripts that should be executable are marked in docs (and include `chmod +x` note).
   - Avoid huge walls of text; keep docs readable and structured.

TECHNICAL DECISIONS (implement)
- Use terraform-aws-modules/vpc/aws and terraform-aws-modules/eks/aws (pinned versions).
- Use EKS managed node group; default instance type t3.medium (configurable).
- Use private subnets for nodes; public subnets for ALB.
- Tags required for ALB discovery must be applied to subnets.
- Use IRSA for addon permissions; do NOT use node IAM broad policies.
- ExternalDNS should be scoped to only manage records in the specific hosted zone ID created/used for poc.<ROOT_DOMAIN>.
- cert-manager DNS01 role should be similarly scoped.
- Include outputs: cluster_name, cluster_endpoint, region, hosted_zone_id, nameservers, OIDC provider ARN, addon role ARNs.

VARIABLES (must exist)
- aws_region (default ap-south-1)
- environment (default dev)
- name_prefix (default platform)
- root_domain (no default in code; allow via env or tfvars; docs show example rdhcloudlab.com)
- poc_subdomain (default poc)
- create_poc_hosted_zone (default true)
- parent_hosted_zone_id (optional)
- cluster_version (default stable)
- node_instance_types (default ["t3.medium"])
- node_desired_size/min/max
- enable_cert_manager (default true)
- enable_external_dns (default true)
- enable_metrics_server (default true)

SECURITY / COST NOTES
- Add cost notes in docs: NAT, node group size, ALB usage.
- Provide “safe destroy” steps and warnings.

NOW GENERATE THE REPO.
Remember: do not ask questions. Make safe defaults and clearly list assumptions at top of README.

