#!/usr/bin/env bash
# Conditionally install MkDocs Material or MkDocs Material Insiders
# based on the build environment (Vercel vs local/other CI)

set -e

echo "Checking MkDocs Material installation requirements..."

# Check if we're running on Vercel and install system dependencies
if [[ "${VERCEL:-0}" == "1" ]]; then
    echo "✓ Vercel environment detected"

    # Set locale to avoid package manager warnings
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
    export LANGUAGE=C.UTF-8

    echo "  Installing system dependencies..."

    # Install pngquant for image optimization
    # pngquant is required by mkdocs-material[imaging] for optimizing PNG images
    # used in social cards and other image processing features
    if command -v apt-get &> /dev/null; then
        echo "  Installing pngquant via apt-get..."
        apt-get update -qq && apt-get install -y -qq pngquant || echo "⚠ Failed to install pngquant via apt-get"
    elif command -v yum &> /dev/null; then
        echo "  Installing pngquant via yum..."
        yum install -y -q pngquant || echo "⚠ Failed to install pngquant via yum"
    else
        echo "⚠ No package manager found, skipping pngquant installation"
    fi

    # Verify pngquant installation
    if command -v pngquant &> /dev/null; then
        echo "✓ pngquant installed: $(pngquant --version)"
    else
        echo "⚠ pngquant not available"
    fi
fi

# Check if we're running on Vercel and have the MKDOCS_INSIDERS token
if [[ "${VERCEL:-0}" == "1" ]] && [[ -n "${MKDOCS_INSIDERS}" ]]; then
    echo "✓ Vercel environment detected with MKDOCS_INSIDERS token"
    echo "  Installing MkDocs Material Insiders..."

    # Install MkDocs Material Insiders from private repo into project venv
    INSIDERS_VERSION="9.6.21-insiders-4.53.17"
    INSIDERS_URL="git+https://${MKDOCS_INSIDERS}@github.com/squidfunk/mkdocs-material-insiders.git@${INSIDERS_VERSION}"

    echo "  Installing: mkdocs-material-insiders@${INSIDERS_VERSION}"

    # Uninstall regular mkdocs-material if it exists and install Insiders
    uv pip uninstall mkdocs-material || true
    uv pip install "mkdocs-material[imaging] @ ${INSIDERS_URL}"

    echo "✓ MkDocs Material Insiders installed successfully"
else
    if [[ "${VERCEL:-0}" == "1" ]]; then
        echo "⚠ Vercel environment detected but MKDOCS_INSIDERS token not set"
        echo "  Falling back to regular mkdocs-material"
    else
        echo "✓ Local/CI environment detected"
        echo "  Using regular mkdocs-material from pyproject.toml"
    fi

    # Regular mkdocs-material will be installed via uv sync from pyproject.toml
    echo "✓ MkDocs Material installation configured"
fi
