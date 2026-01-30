#!/bin/bash
# Check for curly/smart quotes in source files
#
# Detects:
#   " (U+201C) - Left double quotation mark
#   " (U+201D) - Right double quotation mark
#   ' (U+2018) - Left single quotation mark
#   ' (U+2019) - Right single quotation mark

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Default to src/ if no arguments provided
if [ $# -eq 0 ]; then
    SEARCH_PATHS="src/"
else
    SEARCH_PATHS="$@"
fi

# Pattern for curly quotes
CURLY_QUOTE_PATTERN='[""'']'

# Find files with curly quotes
# Exclude reference directories (auto-generated) and build artifacts
FOUND_FILES=$(grep -r -l -E "$CURLY_QUOTE_PATTERN" $SEARCH_PATHS \
    --include="*.md" \
    --include="*.mdx" \
    --include="*.py" \
    --include="*.js" \
    --include="*.ts" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.json" \
    --include="*.yaml" \
    --include="*.yml" \
    --exclude-dir=reference \
    --exclude-dir=build \
    --exclude-dir=node_modules \
    --exclude-dir=.git \
    --exclude-dir=.venv \
    --exclude-dir=__pycache__ \
    2>/dev/null || true)

if [ -n "$FOUND_FILES" ]; then
    echo -e "${RED}Error: Curly quotes found in the following files:${NC}"
    echo ""

    for file in $FOUND_FILES; do
        echo -e "${RED}$file:${NC}"
        # Show line numbers and content with curly quotes
        grep -n -E "$CURLY_QUOTE_PATTERN" "$file" | head -10
        echo ""
    done

    echo "Please replace curly quotes with straight quotes:"
    echo '  " -> "  (left double quote)'
    echo '  " -> "  (right double quote)'
    echo "  ' -> '  (left single quote)"
    echo "  ' -> '  (right single quote)"
    echo ""
    echo "Tip: You can use 'make fix-curly-quotes' to automatically fix these."
    exit 1
else
    echo -e "${GREEN}No curly quotes found.${NC}"
    exit 0
fi
