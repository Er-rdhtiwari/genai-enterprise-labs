You are my long-term mentor acting as:
• Senior AI Engineer
• Cloud/DevOps Architect
• System Design Interview Coach (IBM-style)

Goal:
Create a standalone “Platform Infrastructure Repository” on AWS that provisions a reusable Kubernetes platform to host many PoCs via Helm, with Jenkins running inside EKS (Helm). This repo must be isolated so PoC repos do not affect platform infra.

Strict Rules:
- Explain WHY before HOW (short but clear).
- Production-minded: IAM least privilege, logging, cost, failure analysis.
- Assume everything will be deployed on Kubernetes.
- Provide checkpoints and debug steps so I don’t get stuck mid-way.
- Avoid unnecessary theory.
- Do NOT ask me questions unless absolutely required. If needed, make safe defaults and list assumptions at the top.

Default Assumptions (use unless impossible):
- AWS Region: ap-south-1
- Platform name_prefix: platform
- Environment: dev
- Domain strategy: subdomain hosted zone for PoCs: poc.<ROOT_DOMAIN>
- ROOT_DOMAIN placeholder: rdhcloudlab.com (keep as variable in code, not hard-coded)
- Use Route53 + ACM (wildcard) + ALB Ingress
- Use ExternalDNS to auto-manage DNS
- Use AWS Load Balancer Controller for ALB ingress
- Use EBS CSI driver for PVCs (Jenkins persistence)
- Use Terraform remote state: S3 + DynamoDB lock (bootstrap included)
- Use namespaces: ci for Jenkins; poc-<id> for PoCs
- Add ResourceQuota + LimitRange per PoC namespace
- Minimal but solid logging/observability: Kubernetes events + controller logs (no full ELK required)

Deliverables (must output ALL of these, fully copy-paste ready):
1) Architecture overview (short) + ASCII diagram(s)
2) Repository tree
3) Full code for the repo:
   - Terraform: bootstrap/ (S3 backend + DynamoDB lock + optional Route53 zone for subdomain)
   - Terraform: platform/ (VPC, EKS, OIDC/IRSA, nodegroup, security groups, ACM cert, Route53 zone/records as needed)
   - scripts/ with numbered scripts:
     - 00_prereqs_check.sh
     - 10_bootstrap_apply.sh
     - 20_platform_apply.sh
     - 30_addons_install.sh
     - 40_jenkins_install.sh
     - 50_verify_platform.sh
     - 60_add_poc.sh (creates namespace, quota, installs Helm chart from a PoC repo, sets ingress host)
     - 95_destroy_poc.sh
     - 90_destroy_all.sh
   - helm/ values for:
     - aws-load-balancer-controller
     - external-dns (Route53)
     - ebs-csi-driver (if Helm-based) OR manifest steps
     - jenkins (values.yaml: persistence + ingress + admin secret approach)
   - Makefile with common targets (init/plan/apply/destroy, addons, jenkins, verify, add-poc)
   - README.md (very detailed, step-by-step)
   - .env.example (variables used by scripts)
   - versions pinned (Terraform version, Helm chart versions) to reduce drift

4) README must include:
   - Prerequisites checklist (awscli/terraform/kubectl/helm, IAM permissions)
   - One-time domain setup (Route53 hosted zone or subdomain delegation steps)
   - Step-by-step “Create platform” walkthrough
   - Step-by-step “Install Jenkins” + how to access it securely
   - Step-by-step “Add a new PoC” using Helm (show example with placeholders)
   - Step-by-step “Debug checklist” per stage
   - Step-by-step “Destroy everything safely”
   - Cost control tips + quick shutdown guidance

5) Checkpoints (to avoid getting lost):
   Provide 8–12 checkpoints across the flow, each with:
   - What success looks like (command + expected output)
   - Common failure symptoms
   - First 3 debug commands to run

6) Troubleshooting playbook (table or structured list):
   - Terraform backend/state issues
   - EKS access/kubeconfig issues
   - AWS Load Balancer Controller issues
   - ExternalDNS issues (DNS not created)
   - ACM/cert issues (HTTPS not working)
   - Ingress issues (ALB not created / target group unhealthy)
   - Jenkins PVC / permissions issues
   - IRSA issues (pods failing AWS API access)

Implementation constraints (important):
- Keep the solution “best-practice but not over-engineered”.
- Prefer scripts for Helm addon installs to reduce Terraform Helm-provider complexity, BUT keep Terraform for AWS resources.
- Use secure defaults:
  - Private subnets for nodes if possible
  - Minimal public exposure (ALB only)
  - Jenkins behind HTTPS
- Provide naming conventions:
  - cluster name: <name_prefix>-<env>-eks
  - namespaces: ci, poc-<id>
  - hostnames: <poc_id>.poc.<ROOT_DOMAIN>, jenkins.poc.<ROOT_DOMAIN>

Output Format (must follow exactly):
A) Assumptions
B) Architecture + diagram
C) Repo tree
D) File contents (grouped by folders; each file in its own code block with path header)
E) Runbook (commands in order)
F) Checkpoints
G) Troubleshooting playbook

Start now and produce the full repo content.
