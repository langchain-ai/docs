#!/usr/bin/env bash
# Local guard for the check-removed-pages-redirects CI job.
# See .github/workflows/check-removed-pages-redirects.yml.
#
# Runs scripts/check_removed_pages_redirects.py using the base branch's
# src/docs.json, fetched with `git show`, as the reference point. This lets prek
# catch missing redirects before they hit CI.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

HEAD_DOCS="src/docs.json"
if [[ ! -f "$HEAD_DOCS" ]]; then
  echo "Warning: $HEAD_DOCS not found; skipping redirect check" >&2
  exit 0
fi

# Prefer an explicit override for CI or local experiments, then fall back to
# common base refs. Try each candidate until one works.
CANDIDATES=()
if [[ -n "${DOCS_JSON_BASE_REF:-}" ]]; then
  CANDIDATES+=("$DOCS_JSON_BASE_REF")
fi
CANDIDATES+=(
  "origin/main"
  "upstream/main"
  "main"
  "HEAD"
)

TMP_BASE="$(mktemp -t docs-json-base.XXXXXX)"
trap 'rm -f "$TMP_BASE"' EXIT

for ref in "${CANDIDATES[@]}"; do
  if git show "${ref}:${HEAD_DOCS}" >"$TMP_BASE" 2>/dev/null; then
    BASE_REF="$ref"
    break
  fi
done

if [[ -z "${BASE_REF:-}" ]]; then
  echo "Warning: could not resolve a base ref for $HEAD_DOCS; skipping redirect check" >&2
  exit 0
fi

exec python3 scripts/check_removed_pages_redirects.py "$TMP_BASE" "$HEAD_DOCS"
