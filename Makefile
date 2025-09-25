.PHONY: dev build format lint test install clean lint_md lint_md_fix mint-broken-links mint-broken-links-all build-references preview-references format-check

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

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf __pycache__/
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "*.pyd" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} +

# Mintlify commands (run from build directory where final docs are generated)
# Note: mint must be installed globally via npm
mint-broken-links: build
	@echo "Checking for broken links (excluding integrations directories)..."
	@command -v mint >/dev/null 2>&1 || { echo "Error: mint is not installed. Run 'npm install -g mint@4.1.0'"; exit 1; }
	@cd build && mint broken-links 2>&1 | python3 ../scripts/filter_broken_links.py --exclude-integrations

mint-broken-links-all: build
	@echo "Checking for broken links (including all directories)..."
	@command -v mint >/dev/null 2>&1 || { echo "Error: mint is not installed. Run 'npm install -g mint@4.1.0'"; exit 1; }
	@cd build && mint broken-links 2>&1 | python3 ../scripts/filter_broken_links.py

check-pnpm:
	@command -v pnpm >/dev/null 2>&1 || { echo >&2 "pnpm is not installed. Please install pnpm to proceed (https://pnpm.io/installation)"; exit 1; }

build-references: check-pnpm
	@echo "Building references..."
	cd reference && pnpm i && pnpm build

preview-references: check-pnpm
	@echo "Previewing references..."
	cd reference && pnpm i && pnpm run preview

help:
	@echo "Available commands:"
	@echo "  make dev             - Start development mode with file watching and mint dev"
	@echo "  make build           - Build documentation to ./build directory"
	@echo "  make mint-broken-links - Check for broken links in built documentation (excludes integrations)"
	@echo "  make mint-broken-links-all - Check for broken links in built documentation (includes all directories)"
	@echo "  make build-references  - Build reference docs"
	@echo "  make preview-references - Preview reference docs"
	@echo "  make format          - Format code"
	@echo "  make lint            - Lint code"
	@echo "  make lint_md         - Lint markdown files"
	@echo "  make lint_md_fix     - Lint and fix markdown files"
	@echo "  make test            - Run tests"
	@echo "  make install         - Install dependencies"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make help            - Show this help message"
