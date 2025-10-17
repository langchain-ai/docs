.PHONY: dev-install prod-install config-status build serve-clean-docs serve-docs
# .PHONY: build-docs serve-clean-docs serve-docs format-docs lint-docs tests

# ---------------------------------------
# Python reference documentation Makefile
# ---------------------------------------

all: help

# Install dependencies using local editable packages (for development)
dev-install:
	@./switch-config.sh dev
	@echo "Installing dependencies..."
	uv sync

# Install dependencies using git sources (for production/CI)
prod-install:
	@./switch-config.sh prod
	@echo "Installing dependencies..."
	uv sync

# Show current configuration
config-status:
	@./switch-config.sh status

# Build files for deployment (uses current venv)
build:
	uv run python -m mkdocs build -c -f mkdocs.yml

# To preview what the docs will look like when built
serve-clean-docs:
	uv run python -m mkdocs serve -c -f mkdocs.yml --strict

# For local development; uses --dirty to avoid rebuilding unchanged files
serve-docs:
	uv run python -m mkdocs serve -f mkdocs.yml --dirty

# format-docs:
# 	uv run ruff format docs
# 	uv run ruff check --fix docs

# lint-docs:
# 	uv run ruff format --check docs
# 	uv run ruff check docs

# tests:
# 	uv run pytest tests/unit_tests

help:
	@echo "Available targets:"
	@echo ""
	@echo "Setup:"
	@echo "  dev-install      - Switch to dev config & install with local editable packages"
	@echo "  prod-install     - Switch to prod config & install from git sources"
	@echo "  config-status    - Show current configuration (dev or prod)"
	@echo ""
	@echo "Building & Serving:"
	@echo "  build            - Build the documentation for deployment"
	@echo "  serve-clean-docs - Serve the documentation with a clean build (for previewing)"
	@echo "  serve-docs       - Serve the documentation for local development (faster)"
	@echo ""
	@echo "Typical workflows:"
	@echo "  Development:  make dev-install && make serve-docs"
	@echo "  Production:   make prod-install && make build"
