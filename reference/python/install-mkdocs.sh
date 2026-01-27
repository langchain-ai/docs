#!/usr/bin/env bash
# Install MkDocs Material and system dependencies

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
else
    echo "✓ Local/CI environment detected"
fi
