#!/usr/bin/env bash
# Helper script to switch between dev and prod pyproject.toml configurations

set -e

MODE="${1:-}"

if [[ -z "$MODE" ]]; then
    echo "Usage: $0 <dev|prod|status>"
    echo ""
    echo "  dev    - Switch to development config (local editable installs)"
    echo "  prod   - Switch to production config (git sources)"
    echo "  status - Show current configuration"
    exit 1
fi

case "$MODE" in
    dev)
        echo "Switching to development configuration..."
        if [[ -f pyproject.toml ]] && ! grep -q "# Local installs for development" pyproject.toml; then
            echo "  Backing up production config to pyproject.prod.toml"
            cp pyproject.toml pyproject.prod.toml
        fi
        echo "  Activating pyproject.dev.toml"
        cp pyproject.dev.toml pyproject.toml
        echo "✓ Development configuration active (local editable installs)"
        ;;

    prod)
        echo "Switching to production configuration..."
        if [[ -f pyproject.prod.toml ]]; then
            echo "  Restoring pyproject.prod.toml"
            cp pyproject.prod.toml pyproject.toml
        else
            echo "  ERROR: pyproject.prod.toml not found"
            echo "  The production config should exist as pyproject.toml by default"
            exit 1
        fi
        echo "✓ Production configuration active (git sources)"
        ;;

    status)
        if grep -q "# Local installs for development" pyproject.toml 2>/dev/null; then
            echo "Current configuration: DEVELOPMENT (local editable installs)"
        elif grep -q "# Remote installs for prod" pyproject.toml 2>/dev/null; then
            echo "Current configuration: PRODUCTION (git sources)"
        else
            echo "Current configuration: UNKNOWN"
        fi
        ;;

    *)
        echo "Error: Unknown mode '$MODE'"
        echo "Use: $0 <dev|prod|status>"
        exit 1
        ;;
esac
