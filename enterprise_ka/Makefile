# Makefile — standardizes developer + CI commands for this repo.
# Usage:
#   make help
#   make venv
#   make install
#   make run
#   make test
#   make lint
#   make fmt
#
# Notes:
# - Works best on macOS/Linux. On Windows, use WSL or Git Bash.
# - The app reads .env automatically via pydantic-settings (config.py),
#   so you usually just need to copy .env.example -> .env and fill keys.

SHELL := /bin/bash
PYTHON ?= python3
VENV_DIR ?= .venv
PIP := $(VENV_DIR)/bin/pip
PY := $(VENV_DIR)/bin/python

APP_MODULE := app.main:app
HOST ?= 0.0.0.0
PORT ?= 8000

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show available make targets
	@awk 'BEGIN {FS = ":.*##"; printf "\nTargets:\n"} /^[a-zA-Z0-9_\-]+:.*##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ---------------------------
# Environment / Installation
# ---------------------------

.PHONY: venv
venv: ## Create a local virtual environment
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(PIP) install --upgrade pip setuptools wheel
	@echo "✅ venv created at $(VENV_DIR). Activate: source $(VENV_DIR)/bin/activate"

.PHONY: install
install: ## Install runtime dependencies (uses requirements.txt)
	@$(PIP) install -r requirements.txt
	@echo "✅ runtime deps installed"

.PHONY: install-dev
install-dev: install ## Install dev tooling (ruff/mypy/pytest)
	@$(PIP) install -U ruff mypy pytest pytest-asyncio
	@echo "✅ dev tools installed (ruff, mypy, pytest)"

.PHONY: clean
clean: ## Remove caches and local build artifacts
	@rm -rf .pytest_cache .mypy_cache .ruff_cache
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "🧹 cleaned"

# ---------------------------
# Run / Build
# ---------------------------

.PHONY: run
run: ## Run API in dev mode (reload)
	@$(PY) -m uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

.PHONY: run-prod
run-prod: ## Run API in prod-like mode (no reload)
	@$(PY) -m uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)

.PHONY: build-index
build-index: ## Build/refresh the embeddings index (calls embeddings API)
	@$(PY) scripts/build_index.py

# ---------------------------
# Quality Gates (CI-friendly)
# ---------------------------

.PHONY: fmt
fmt: ## Auto-format code (ruff formatter)
	@$(PY) -m ruff format .
	@echo "✅ formatted"

.PHONY: lint
lint: ## Lint code (ruff)
	@$(PY) -m ruff check .
	@echo "✅ lint OK"

.PHONY: lint-fix
lint-fix: ## Lint + auto-fix safe issues (ruff)
	@$(PY) -m ruff check . --fix
	@echo "✅ lint fixed where safe"

.PHONY: type
type: ## Type-check (mypy)
	@$(PY) -m mypy app
	@echo "✅ typecheck OK"

.PHONY: test
test: ## Run tests (pytest)
	@$(PY) -m pytest

.PHONY: check
check: ## Run formatting check + lint + typecheck + tests (recommended for CI)
	@$(PY) -m ruff format . --check
	@$(PY) -m ruff check .
	@$(PY) -m mypy app
	@$(PY) -m pytest
	@echo "✅ all checks passed"

# ---------------------------
# Docker
# ---------------------------

IMAGE_NAME ?= enterprise-ka
IMAGE_TAG ?= 0.1

.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: docker-run
docker-run: ## Run Docker image (expects env vars passed in)
	docker run --rm -p $(PORT):8000 $(IMAGE_NAME):$(IMAGE_TAG)
