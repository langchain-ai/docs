#!/usr/bin/env bash
# Link check using Playwright (headless browser).
# Crawls docs.langchain.com and verifies all links, including client-rendered content.
#
# Prerequisites:
#   - Node.js 18+
#   - Run from repo root: npm install (in this dir) and npx playwright install chromium
#
# Usage: make check-links-playwright  OR  ./scripts/check-links-playwright.sh

set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
SCRIPT_DIR="$REPO_ROOT/scripts/check-links-playwright"

cd "$SCRIPT_DIR"

if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Ensure Chromium is installed (idempotent)
npx playwright install chromium 2>/dev/null || true

echo ""
node check.js "$@"
