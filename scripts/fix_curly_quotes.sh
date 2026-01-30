#!/bin/bash
# Fix curly/smart quotes by replacing them with straight quotes
#
# Replaces:
#   " (U+201C) → " - Left double quotation mark
#   " (U+201D) → " - Right double quotation mark
#   ' (U+2018) → ' - Left single quotation mark
#   ' (U+2019) → ' - Right single quotation mark

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Default to src/ if no arguments provided
if [ $# -eq 0 ]; then
    SEARCH_PATHS="src/"
else
    SEARCH_PATHS="$@"
fi

# Find all relevant files
FILES=$(find $SEARCH_PATHS \
    -type f \
    \( -name "*.md" -o -name "*.mdx" -o -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) \
    -not -path "*/reference/*" \
    -not -path "*/build/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/.venv/*" \
    -not -path "*/__pycache__/*" \
    2>/dev/null || true)

FIXED_COUNT=0

for file in $FILES; do
    if grep -q -E '[""'']' "$file" 2>/dev/null; then
        echo -e "${YELLOW}Fixing: $file${NC}"
        # Use sed to replace curly quotes with straight quotes
        # macOS and Linux compatible
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' -e 's/[""]/"/g' -e "s/['']/'/g" "$file"
        else
            sed -i -e 's/[""]/"/g' -e "s/['']/'/g" "$file"
        fi
        FIXED_COUNT=$((FIXED_COUNT + 1))
    fi
done

if [ $FIXED_COUNT -gt 0 ]; then
    echo ""
    echo -e "${GREEN}Fixed curly quotes in $FIXED_COUNT file(s).${NC}"
else
    echo -e "${GREEN}No curly quotes found. Nothing to fix.${NC}"
fi
