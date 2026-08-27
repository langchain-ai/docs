#!/usr/bin/env bash
# Install a pinned Vale binary to "$1" (default .bin/vale).
#
# The version comes from a single source of truth, .mise.toml, so local runs,
# the prek hooks, and the lint-prose workflow all lint with the same engine.
# Pass an explicit version as "$2" to override (with or without a leading "v").
#
# Note on release naming: the git tag carries a "v" prefix while the asset
# filename does not, e.g. tag v3.17.1 holds vale_3.17.1_Linux_64-bit.tar.gz.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dest_path="${1:-.bin/vale}"
requested_version="${2:-}"

# Read the canonical pin from .mise.toml unless one was passed in.
if [ -z "$requested_version" ]; then
  mise_toml="$repo_root/.mise.toml"
  if [ ! -f "$mise_toml" ]; then
    echo "Cannot resolve the Vale version: $mise_toml is missing." >&2
    exit 1
  fi
  requested_version="$(sed -n 's/^[[:space:]]*vale[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' "$mise_toml" | head -n 1)"
  if [ -z "$requested_version" ]; then
    echo "Cannot resolve the Vale version: no 'vale = \"...\"' entry in $mise_toml." >&2
    exit 1
  fi
fi

# Normalize away any leading "v" so the tag and the filename can be built
# separately below.
vale_version="${requested_version#v}"

# This value is interpolated into a download URL and a filesystem path, so
# constrain it to a bare semantic version before going any further.
if ! printf '%s' "$vale_version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "Refusing to use Vale version '$requested_version': expected a bare semantic version such as 3.17.1." >&2
  exit 1
fi

# Report the version of a vale binary, or nothing if it cannot be determined.
installed_version() {
  local candidate="$1"
  [ -x "$candidate" ] || return 0
  "$candidate" --version 2>/dev/null | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -n 1 || true
}

# Already correct at the destination.
if [ "$(installed_version "$dest_path")" = "$vale_version" ]; then
  exit 0
fi

# A matching vale is already on PATH (for example one that mise installed), so
# reuse it rather than downloading a second copy.
if path_vale="$(command -v vale 2>/dev/null)" &&
   [ "$(installed_version "$path_vale")" = "$vale_version" ]; then
  mkdir -p "$(dirname "$dest_path")"
  ln -sf "$path_vale" "$dest_path"
  exit 0
fi

os_name="$(uname -s)"
arch_name="$(uname -m)"

case "$os_name" in
  Linux)
    case "$arch_name" in
      x86_64|amd64) asset_suffix="Linux_64-bit" ;;
      arm64|aarch64) asset_suffix="Linux_arm64" ;;
      *)
        echo "Unsupported Linux architecture for Vale: $arch_name" >&2
        exit 1
        ;;
    esac
    ;;
  Darwin)
    case "$arch_name" in
      x86_64|amd64) asset_suffix="macOS_64-bit" ;;
      arm64|aarch64) asset_suffix="macOS_arm64" ;;
      *)
        echo "Unsupported macOS architecture for Vale: $arch_name" >&2
        exit 1
        ;;
    esac
    ;;
  *)
    echo "Unsupported operating system for Vale installation: $os_name" >&2
    exit 1
    ;;
esac

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
archive="$workdir/vale.tar.gz"
url="https://github.com/errata-ai/vale/releases/download/v${vale_version}/vale_${vale_version}_${asset_suffix}.tar.gz"

echo "Installing Vale $vale_version ($asset_suffix) to $dest_path"
curl -fsSL --max-time 120 --retry 3 "$url" -o "$archive"
tar -xzf "$archive" -C "$workdir"
install_bin="$(find "$workdir" -type f -name vale | head -n 1)"
if [ -z "$install_bin" ]; then
  echo "Downloaded Vale archive did not contain a vale binary." >&2
  exit 1
fi
mkdir -p "$(dirname "$dest_path")"
cp "$install_bin" "$dest_path"
chmod +x "$dest_path"
