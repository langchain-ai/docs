#!/usr/bin/env bash
set -euo pipefail

# Bake a snapshot with git and gh for cloning product + docs repos and
# searching source at a release tag. Prefer read-only public clones; write
# tools talk to GitHub/Linear through agent connections, not sandbox auth.

install_apt_packages() {
  apt-get update
  apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    curl \
    tar
}

if ! command -v git >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    install_apt_packages
  else
    echo "git is required in the sandbox image" >&2
    exit 1
  fi
fi

if ! command -v gh >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    if ! command -v curl >/dev/null 2>&1; then
      install_apt_packages
    fi
    # Pin a recent gh release for reproducible snapshots.
    GH_VERSION="2.76.2"
    ARCH="$(uname -m)"
    case "${ARCH}" in
      x86_64|amd64) GH_ARCH="amd64" ;;
      aarch64|arm64) GH_ARCH="arm64" ;;
      *)
        echo "unsupported architecture for gh: ${ARCH}" >&2
        exit 1
        ;;
    esac
    curl -fsSL \
      "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${GH_ARCH}.tar.gz" \
      -o /tmp/gh.tgz
    tar -xzf /tmp/gh.tgz -C /tmp
    install -m 0755 "/tmp/gh_${GH_VERSION}_linux_${GH_ARCH}/bin/gh" /usr/local/bin/gh
    rm -rf /tmp/gh.tgz "/tmp/gh_${GH_VERSION}_linux_${GH_ARCH}"
  else
    echo "gh is required in the sandbox image" >&2
    exit 1
  fi
fi

git --version
gh --version
