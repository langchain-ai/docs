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
	@echo "Syncing dependencies..."
	@uv sync
	@./install-mkdocs.sh
	@if [ "$$VERCEL" = "1" ] && [ -n "$$MKDOCS_INSIDERS" ]; then \
		echo "Building with Insiders plugins enabled..."; \
		ENABLE_INSIDERS_PLUGINS=true uv run --no-sync python -m mkdocs build -c -f mkdocs.yml; \
	else \
		echo "Building without Insiders plugins..."; \
		uv run --no-sync python -m mkdocs build -c -f mkdocs.yml; \
	fi

# To preview what the docs will look like when built
serve-clean-docs:
	@./install-mkdocs.sh
	@port=8000; \
	while lsof -ti:$$port > /dev/null 2>&1; do \
		port=$$((port + 1)); \
	done; \
	echo "Starting MkDocs server on port $$port..."; \
	if [ "$$VERCEL" = "1" ] && [ -n "$$MKDOCS_INSIDERS" ]; then \
		ENABLE_INSIDERS_PLUGINS=true uv run --no-sync python -m mkdocs serve -c -f mkdocs.yml --strict -a 127.0.0.1:$$port; \
	else \
		uv run --no-sync python -m mkdocs serve -c -f mkdocs.yml --strict -a 127.0.0.1:$$port; \
	fi

# For local development; uses --dirty to avoid rebuilding unchanged files
serve-docs:
	@./install-mkdocs.sh
	@port=8000; \
	while lsof -ti:$$port > /dev/null 2>&1; do \
		port=$$((port + 1)); \
	done; \
	echo "Starting MkDocs server on port $$port..."; \
	if [ "$$VERCEL" = "1" ] && [ -n "$$MKDOCS_INSIDERS" ]; then \
		ENABLE_INSIDERS_PLUGINS=true uv run --no-sync python -m mkdocs serve -f mkdocs.yml --dirty -a 127.0.0.1:$$port; \
	else \
		uv run --no-sync python -m mkdocs serve -f mkdocs.yml --dirty -a 127.0.0.1:$$port; \
	fi

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
