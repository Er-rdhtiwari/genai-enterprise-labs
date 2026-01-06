You are OpenAI Codex acting as a Senior AI Engineer + Cloud/DevOps Architect who builds production-minded PoC repos that deploy into a shared Kubernetes platform (EKS).

GOAL
Generate a COMPLETE Git repository called: rdhtiwari-profile
This PoC repo contains:
- FastAPI backend
- Next.js frontend
- Dockerfiles for both
- Helm chart to deploy both services to an EXISTING shared EKS cluster (“platform cluster”)
- Jenkinsfile CI/CD pipeline to build, push to ECR, and deploy/upgrade/rollback via Helm
- Scripts + docs + runbook + troubleshooting

IMPORTANT CONTEXT (assume these exist in the platform repo)
- A shared EKS cluster already exists (created by platform repo).
- Cluster add-ons exist:
  - AWS Load Balancer Controller (Ingress class ALB)
  - ExternalDNS (auto Route53 records from Ingress)
  - cert-manager (TLS, optional)
- There is a hosted zone like: poc.<ROOT_DOMAIN> (e.g., poc.rdhcloudlab.com), but DO NOT hardcode it.

CONSTRAINTS / STYLE
- Keep it minimal but real (not toy). Make it “deployable on day 1”.
- Production-oriented defaults: health checks, readiness/liveness, structured logging, sane resource requests/limits.
- No secrets committed. Use .env.example and Kubernetes Secret values injected at deploy time.
- Do NOT hardcode domain, cluster name, AWS region, ECR account/repo, or any credentials.
- Must work with Jenkins running on EC2 (using either instance profile or Jenkins credentials binding).
- Assume Kubernetes deployment (no docker-compose required, but local run steps are helpful).
- Explain WHY before HOW in docs (short, clear).
- Provide checkpoints and debug commands so I don’t get stuck.

DELIVERABLE REQUIREMENT (output format)
1) Return a “FILE TREE” first.
2) Then for EACH file, output:
   - <relative/path>
   - <language>
   - <content>
3. Do not skip any essential file. Include all needed configs, scripts, and docs.

REPO CONTENT REQUIREMENTS

A) BACKEND (FastAPI)

* Python 3.11+.
* Minimal clean architecture:

  * app/main.py
  * app/api/routes.py (or routers/)
  * app/core/config.py (env config via pydantic-settings)
  * app/core/logging.py (structured logs + request_id middleware)
* Endpoints:

  * GET /healthz  -> returns status
  * GET /version  -> returns git_sha/build metadata (from env)
  * GET /v1/profile -> returns dummy JSON profile payload (for frontend)
* Add basic unit test for /healthz.
* Add logging, error handler, and request-id correlation middleware.

B) FRONTEND (Next.js)

* Node 20+, Next.js (App Router preferred).
* A minimal UI that:

  * shows a profile card
  * fetches data from backend
* Avoid CORS headaches:

  * Implement a Next.js server-side route (e.g., /api/profile) that proxies to backend using BACKEND_BASE_URL env var at runtime.
  * UI calls same-origin /api/profile (so no browser CORS issues).
* Add /healthz page or route for readiness.

C) DOCKERFILES

* backend/Dockerfile: slim, non-root user, installs deps, runs uvicorn
* frontend/Dockerfile: multi-stage, builds Next.js, runs in production mode
* Include .dockerignore files.

D) HELM CHART (deploy backend + frontend)

* Chart path: helm/
* Deployments:

  * backend Deployment + Service (ClusterIP)
  * frontend Deployment + Service (ClusterIP)
* Ingress:

  * Use ALB ingress annotations (generic, not account-specific)
  * Hostnames must be configurable via values:

    * frontend host: <app>.<POC_SUBDOMAIN>.<ROOT_DOMAIN>
    * backend host: <app>-api.<POC_SUBDOMAIN>.<ROOT_DOMAIN> (optional but supported)
  * ExternalDNS annotation should be supported.
  * TLS via cert-manager should be toggleable (enable_tls true/false).
* Probes:

  * backend: /healthz
  * frontend: /api/healthz (implement this route)
* Values must include:

  * image repos + tags for backend and frontend
  * replicas
  * resources
  * ingress settings (enabled, className, hosts, annotations)
  * backend env config (LOG_LEVEL, etc)
  * frontend env config (BACKEND_BASE_URL)
* Add NOTES.txt in Helm chart to show how to get URLs and check status.

E) JENKINSFILE (CI/CD pipeline)
Provide a Jenkinsfile at repo root with:

* Parameters:

  * ACTION = build|deploy|rollback (default deploy)
  * AWS_REGION
  * EKS_CLUSTER_NAME
  * NAMESPACE (default: poc-rdhtiwari-profile)
  * RELEASE_NAME (default: rdhtiwari-profile)
  * ROOT_DOMAIN
  * POC_SUBDOMAIN (default: poc)
  * FRONTEND_HOST_PREFIX (default: profile)
  * BACKEND_HOST_PREFIX (default: profile-api) OR derive from app name
  * ENABLE_TLS (true/false)
  * ROLLBACK_REVISION (optional)
* Stages:

  1. Checkout
  2. Tool checks (aws/terraform not needed here; require aws/kubectl/helm/docker/jq)
  3. Unit tests (backend)
  4. Build images (backend + frontend)
  5. Push images to ECR

     * Determine AWS_ACCOUNT_ID using sts get-caller-identity
     * Ensure ECR repos exist (create if not)
     * Tag images with GIT_SHA (short) and BUILD_NUMBER
  6. Configure kubeconfig:

     * aws eks update-kubeconfig --region $AWS_REGION --name $EKS_CLUSTER_NAME
  7. Deploy/Upgrade via Helm:

     * helm upgrade --install $RELEASE_NAME ./helm -n $NAMESPACE --create-namespace
     * set image repos/tags
     * set ingress hosts using ROOT_DOMAIN and POC_SUBDOMAIN
     * set ENABLE_TLS toggle
  8. Verify:

     * kubectl rollout status deploy/<backend>
     * kubectl rollout status deploy/<frontend>
     * helm status
* Rollback behavior:

  * If ACTION=rollback:

    * if ROLLBACK_REVISION provided, helm rollback to that revision
    * else rollback to previous revision (helm rollback release 0 is not valid; implement logic to find previous revision via helm history)
* Safety:

  * Never echo secrets
  * Use Jenkins credentials binding OR instance profile; document both options.
* Output:

  * Print the final expected URLs.

F) SCRIPTS + TOOLING

* scripts/require_tools.sh: checks aws/kubectl/helm/docker/jq versions and exits with helpful messages
* scripts/local_run_backend.sh and local_run_frontend.sh (optional)
* scripts/helm_deploy.sh: local deploy helper (reads env vars)
* Makefile:

  * test-backend
  * build
  * push
  * kubeconfig
  * deploy
  * rollback
  * status

G) DOCUMENTATION (must be included)

* README.md

  * What this repo is
  * Architecture diagram (ASCII)
  * Local dev quickstart
  * CI/CD flow (why/how)
  * Required Jenkins parameters
  * How it integrates with the platform EKS cluster
* docs/runbook.md

  * Step-by-step deployment runbook
  * Checkpoints + expected outputs
* docs/troubleshooting.md

  * Common issues: ECR auth, kubectl auth, helm failures, ingress/dns/tls issues
  * Debug commands
* docs/security.md

  * How secrets are handled
  * No hardcoded credentials
  * Principle of least privilege suggestions for Jenkins role

IMPLEMENTATION DETAILS (use these decisions)

* Default service names:

  * backend: rdhtiwari-profile-backend
  * frontend: rdhtiwari-profile-frontend
* Kubernetes labels must include: app.kubernetes.io/name, app.kubernetes.io/instance, app.kubernetes.io/component
* Backend runs on port 8000, frontend on 3000
* Use resource requests/limits modestly for PoC (cost-aware).
* Include readiness/liveness probes with reasonable initial delays.
* Frontend must proxy to backend using env var (runtime) to avoid rebuilding images per environment.
* Ensure Helm chart supports both “frontend only ingress” and “frontend+backend ingress” via values.

NOW GENERATE THE REPO.
Do not ask questions. Make safe defaults and list assumptions at the top of README.
Return the file tree first, then each file with full content.


