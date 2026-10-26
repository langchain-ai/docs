#!/usr/bin/env bash
# Fail if any authored docs file links to a retired documentation site.
#
# Scans every .md and .mdx file under src/ (or the paths passed as arguments),
# not only lines a PR adds, so stale links already on a page are reported too.
# Replace matches with relative docs paths or reference.langchain.com URLs.
set -euo pipefail

# Retired sites. Each one now redirects to a generic landing page or serves stale content.
LEGACY='(python\.langchain\.com|js\.langchain\.com|api\.python\.langchain\.com|api\.js\.langchain\.com|docs\.smith\.langchain\.com|langchain-ai\.github\.io)'
# Still live and not documentation: the Helm chart repository.
ALLOWED='langchain-ai\.github\.io/helm'

paths=("$@")
[ ${#paths[@]} -eq 0 ] && paths=(src)

matches=$(grep -rnE "$LEGACY" --include='*.md' --include='*.mdx' "${paths[@]}" \
  | grep -vE "$ALLOWED" || true)

if [ -n "$matches" ]; then
  echo "❌ Found links to retired documentation sites:"
  echo ""
  echo "$matches"
  echo ""
  echo "Use relative links (/oss/..., /langsmith/...) for docs pages and"
  echo "https://reference.langchain.com/ for API reference pages."
  exit 1
fi

echo "✅ No links to retired documentation sites."
