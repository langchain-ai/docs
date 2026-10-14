#!/usr/bin/env bash
set -euo pipefail

# Bake a snapshot with git available for cloning langchain-ai/docs read-only.
if ! command -v git >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update
    apt-get install -y --no-install-recommends git ca-certificates
  else
    echo "git is required in the sandbox image" >&2
    exit 1
  fi
fi

git --version
