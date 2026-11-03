"""Resolve agent-owned connection secrets for authored tools."""

from __future__ import annotations

import os

from managed_deepagents import connections

GITHUB_CONNECTION = "docs-github"
LINEAR_CONNECTION = "docs-linear"


async def resolve_secret(slug: str, *, env_fallbacks: tuple[str, ...] = ()) -> str:
    """Resolve an agent-owned connection, then optional env fallbacks.

    In ``mda dev``, agent-owned opaque connections read ``MDA_DEV_<SLUG>``
    (hyphens become underscores). After deploy, create the connection with
    ``mda connections create``.
    """
    try:
        value = await connections.get(slug, {"type": "agent"})
    except Exception:
        value = None

    if isinstance(value, str) and value.strip():
        return value.strip()

    for name in env_fallbacks:
        fallback = os.environ.get(name, "").strip()
        if fallback:
            return fallback

    env_hint = f"MDA_DEV_{slug.upper().replace('-', '_')}"
    fallback_hint = ", ".join(env_fallbacks) if env_fallbacks else "(none)"
    raise RuntimeError(
        f"Missing credential for connection {slug!r}. "
        f"For local dev set {env_hint} (or {fallback_hint}). "
        f"After deploy, run: mda connections create {slug} --secret-from-env <ENV_VAR>"
    )


async def github_token() -> str:
    return await resolve_secret(
        GITHUB_CONNECTION,
        env_fallbacks=("GITHUB_TOKEN", "GH_TOKEN"),
    )


async def linear_api_key() -> str:
    return await resolve_secret(
        LINEAR_CONNECTION,
        env_fallbacks=("LINEAR_API_KEY",),
    )
