#!/usr/bin/env bash
set -euo pipefail

dest_path="${1:-.bin/vale}"
vale_version="${2:-v3.9.6}"

if [ -x "$dest_path" ]; then
  exit 0
fi

os_name="$(uname -s)"

mkdir -p "$(dirname "$dest_path")"

if [ "$os_name" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
  brew install vale
  exit 0
fi

if [ "$os_name" = "Linux" ] && command -v docker >/dev/null 2>&1; then
  cat > "$dest_path" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
exec docker run --rm -i \
  -v "$PWD:/work" \
  -w /work \
  jdkato/vale:latest "$@"
EOF
  chmod +x "$dest_path"
  exit 0
fi

arch_name="$(uname -m)"
case "$os_name" in
  Linux)
    case "$arch_name" in
      x86_64|amd64)
        asset_suffix="Linux_64-bit"
        ;;
      arm64|aarch64)
        asset_suffix="Linux_arm64"
        ;;
      *)
        echo "Unsupported Linux architecture for Vale: $arch_name" >&2
        exit 1
        ;;
    esac
    ;;
  Darwin)
    echo "Homebrew is required to install Vale on macOS when it is not already present." >&2
    exit 1
    ;;
  *)
    echo "Unsupported operating system for Vale installation: $os_name" >&2
    exit 1
    ;;
esac

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
archive="$workdir/vale.tar.gz"
url="https://github.com/errata-ai/vale/releases/download/${vale_version}/vale_${vale_version}_${asset_suffix}.tar.gz"

curl -fsSL "$url" -o "$archive"
tar -xzf "$archive" -C "$workdir"
install_bin="$(find "$workdir" -type f -name vale | head -n 1)"
if [ -z "$install_bin" ]; then
  echo "Downloaded Vale archive did not contain a vale binary." >&2
  exit 1
fi
cp "$install_bin" "$dest_path"
chmod +x "$dest_path"
