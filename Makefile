.PHONY: all dev build format lint test install clean lint_md lint_md_fix broken-links build-references preview-references format-check code-snippets test-code-samples

# Default target
all: help

dev:
	@echo "Starting development mode..."
	PYTHONPATH=$(CURDIR) uv run pipeline dev

build:
	@echo "Building documentation..."
	PYTHONPATH=$(CURDIR) uv run pipeline build

# Define a variable for the test file path.
TEST_FILE ?= tests/unit_tests

# Define a variable for Python and notebook files.
PYTHON_FILES=.

lint:
	uv run ruff format $(PYTHON_FILES) --diff
	uv run ruff check $(PYTHON_FILES) --diff
	uv run mypy $(PYTHON_FILES)

format:
	uv run ruff format $(PYTHON_FILES)
	uv run ruff check --fix $(PYTHON_FILES)

# Check formatting without applying changes (for CI)
format-check:
	uv run ruff format $(PYTHON_FILES) --check --diff
	uv run ruff check $(PYTHON_FILES)

lint_md:
	@echo "Linting markdown files..."
	@if command -v markdownlint >/dev/null 2>&1; then \
		find src -name "*.md" -o -name "*.mdx" | xargs markdownlint; \
	else \
		echo "markdownlint not found. Install with: npm install -g markdownlint-cli or VSCode extension"; \
		exit 1; \
	fi

lint_md_fix:
	@echo "Linting and fixing markdown files..."
	@if command -v markdownlint >/dev/null 2>&1; then \
		find src -name "*.md" -o -name "*.mdx" | xargs markdownlint --fix; \
	else \
		echo "markdownlint not found. Install with: npm install -g markdownlint-cli or VSCode extension"; \
		exit 1; \
	fi

test:
	uv run pytest --disable-socket --allow-unix-socket $(TEST_FILE) -vv

install:
	@echo "Installing all dependencies"
	uv sync --all-groups
	npm install -g mint@latest

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf __pycache__/
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "*.pyd" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} +

# Mintlify commands (run from build directory where final docs are generated)
# broken-links: Checks for broken links, excluding OpenAPI-generated pages and snippet files
# (snippets use relative paths that resolve when inlined; /oss/langchain/agents uses redirect)
# Excluded: /langsmith/agent-server-api/, /api-reference/ (Mintlify-generated at deploy, not in local build)
# Excluded: ../langchain/agents (snippet preprocessing: /oss/langchain/agents → relative path, resolves when inlined)
# Failure: only when filtered output still has indented link lines (real broken links we care about)
# Run mint, capture output, filter exclusions. Only show output when failing.
broken-links: build
	@command -v mint >/dev/null 2>&1 || { echo "Error: mint not installed. Run 'npm install -g mint@4.2.126'"; exit 1; }
	@cd build && mint broken-links 2>&1 | tee /tmp/broken-links.txt > /dev/null; \
		filtered=$$(grep -v '/langsmith/agent-server-api/' /tmp/broken-links.txt | grep -v '/api-reference/' | grep -v '\.\./langchain/agents'); \
		if echo "$$filtered" | grep -qE '^[[:space:]]+.*/'; then \
			echo "$$filtered"; echo ""; echo "❌ Broken links found"; exit 1; \
		else \
			echo "✅ No broken links"; \
		fi

check-openapi: build
	@echo "Checking openapi spec validity"
	@command -v mint >/dev/null 2>&1 || { echo "Error: mint is not installed. Run 'npm install -g mint@4.2.126'"; exit 1; }
	@cd build && output=$$(mint openapi-check langsmith/agent-server-openapi.json) && echo "$$output"

check-pnpm:
	@command -v pnpm >/dev/null 2>&1 || { echo >&2 "pnpm is not installed. Please install pnpm to proceed (https://pnpm.io/installation)"; exit 1; }

# Extract code snippets from src/code-samples using Bluehawk
code-snippets:
	@echo "Extracting code snippets with Bluehawk..."
	@mkdir -p src/code-samples-generated
	@npx --yes bluehawk snip -o src/code-samples-generated/ --ignore node_modules --ignore .DS_Store src/code-samples/
	@PYTHONPATH=$(CURDIR) python scripts/generate_code_snippet_mdx.py

# Run code samples. By default runs all; pass FILES to test specific paths.
#   make test-code-samples
#   make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
test-code-samples:
	@if [ -f src/code-samples/package.json ]; then (cd src/code-samples && npm install --silent) || true; fi
	@FILES="$(FILES)" PYTHONPATH=$(CURDIR) python scripts/test_code_samples.py

# Reference docs commands (in reference/ subdirectory)
build-references: check-pnpm
	@echo "Building references..."
	cd reference && pnpm i && pnpm build

preview-references: check-pnpm
	@echo "Previewing references..."
	cd reference && pnpm i && pnpm run preview

help:
	@echo "Available commands:"
	@echo "  make dev                - Start development mode with file watching and mint dev"
	@echo "  make build              - Build documentation to ./build directory"
	@echo "  make broken-links       - Check for broken links in built documentation"
	@echo "  make build-references   - Build reference docs"
	@echo "  make preview-references - Preview reference docs"
	@echo "  make format             - Format code"
	@echo "  make lint               - Lint code"
	@echo "  make lint_md            - Lint markdown files"
	@echo "  make lint_md_fix        - Lint and fix markdown files"
	@echo "  make test               - Run tests"
	@echo "  make install            - Install dependencies"
	@echo "  make code-snippets      - Extract code snippets with Bluehawk"
	@echo "  make test-code-samples  - Run code samples (FILES=\"path ...\" for specific)"
	@echo "  make clean              - Clean build artifacts"
	@echo "  make help               - Show this help message"
