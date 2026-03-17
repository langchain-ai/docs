"""PostgreSQL setup for code samples.

This module provides PostgreSQL connection setup for code samples.
It attempts to use testcontainers if available, otherwise provides
utilities to work with environment-configured postgres.
"""

import os
import subprocess
import sys
import time

_DEFAULT_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"


def get_postgres_uri() -> str:
    """Get PostgreSQL connection URI.

    Tries multiple approaches in order:
    1. Check POSTGRES_URI environment variable
    2. Attempt to use testcontainers to spin up postgres
    3. Try docker directly
    4. Fall back to default local postgres connection
    """
    # Check environment variable first
    if env_uri := os.environ.get("POSTGRES_URI"):
        return env_uri

    # Try testcontainers
    try:
        from testcontainers.postgres import (  # type: ignore[import-not-found]
            PostgresContainer,
        )

        # Store container in a global so it persists
        if not hasattr(get_postgres_uri, "_container"):
            # Use pgvector image which includes the vector extension
            container = PostgresContainer("pgvector/pgvector:pg17")
            container.start()
            get_postgres_uri._container = container  # type: ignore[attr-defined]
            # Give it a moment to fully start
            time.sleep(2)

        return get_postgres_uri._container.get_connection_url()  # type: ignore[attr-defined]
    except ImportError:
        print("conftest: testcontainers not installed, trying docker", file=sys.stderr)

    # Try to use docker directly if testcontainers not available
    try:
        # Check if postgres container is already running
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                "name=langchain-docs-postgres",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

        if "langchain-docs-postgres" not in result.stdout:
            # Start a postgres container with pgvector extension
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "langchain-docs-postgres",
                    "-e",
                    "POSTGRES_PASSWORD=postgres",
                    "-e",
                    "POSTGRES_DB=postgres",
                    "-p",
                    "5442:5432",
                    "pgvector/pgvector:pg17",
                ],
                check=True,
                capture_output=True,
                timeout=30,
            )
            # Give it time to start
            time.sleep(3)

        return _DEFAULT_URI
    except FileNotFoundError:
        print("conftest: docker not found, using default URI", file=sys.stderr)
    except subprocess.TimeoutExpired as e:
        print(
            f"conftest: docker timed out after {e.timeout}s, using default URI",
            file=sys.stderr,
        )
    except subprocess.CalledProcessError as e:
        print(
            f"conftest: docker failed (exit {e.returncode}), using default URI",
            file=sys.stderr,
        )

    # Fall back to default (assumes postgres is running locally)
    print(f"conftest: falling back to default URI: {_DEFAULT_URI}", file=sys.stderr)
    return _DEFAULT_URI


def prepare_postgres_store(uri: str) -> None:
    """Drop existing store tables so setup() creates a fresh schema.

    Use before PostgresStore.from_conn_string when tests share a database
    (e.g. CI) and may see leftover tables from a different schema version.
    """
    import psycopg

    try:
        with psycopg.connect(uri, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DROP TABLE IF EXISTS public.store_vectors CASCADE; "
                    "DROP TABLE IF EXISTS public.store CASCADE; "
                    "DROP TABLE IF EXISTS public.store_migrations CASCADE;"
                )
    except psycopg.OperationalError as e:
        print(f"conftest: could not connect to clean tables: {e}", file=sys.stderr)
    except psycopg.Error as e:
        print(f"conftest: failed to drop store tables: {e}", file=sys.stderr)
