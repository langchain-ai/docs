"""Build helpers for fetching and extracting Python API reference HTML.

Downloads tarballs from GitHub and extracts only the `api_reference_build`
directory into the `dist/python` directory (dropping any top-level prefix like
`langchain-api-docs-html-*`).
"""

import logging
import shutil
import tarfile
import tempfile
import urllib.parse
import urllib.request
from contextlib import suppress
from pathlib import Path

from .errors import InvalidTarballURLSchemeError, TarPathTraversalError

logger = logging.getLogger(__name__)

DIST_DIR = Path(__file__).parent / ".." / "dist" / "python"

VERSION_TAGS: list[str] = []


def _extract_api_reference_build(tar: tarfile.TarFile, path: Path) -> None:
    """Extract only `api_reference_build` members from the tar into `path`.

    Drops the top-level prefix (e.g., `langchain-api-docs-html-main/`) so that
    files are written under `path/api_reference_build/...`.

    Guards against path traversal by verifying each member remains under `path`.
    """
    for member in tar.getmembers():
        try:
            start_idx = member.name.index("api_reference_build")
        except ValueError:
            continue

        # Keep `api_reference_build/...` (or the directory itself)
        relative_with_prefix = member.name[start_idx:]
        dest_path = path / relative_with_prefix
        if not dest_path.is_relative_to(path):
            raise TarPathTraversalError

        logger.debug("%s -> %s", member.name, dest_path)

        if member.isdir():
            dest_path.mkdir(parents=True, exist_ok=True)
            continue

        if member.isfile():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            fileobj = tar.extractfile(member)
            if fileobj is not None:
                with dest_path.open("wb") as out_f:
                    shutil.copyfileobj(fileobj, out_f)


def _fetch_extract_tarball(url: str, tmpdir: Path) -> None:
    """Download tarball from `url` and extract relevant HTML into `tmpdir`."""
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme != "https":
        raise InvalidTarballURLSchemeError(parsed_url.scheme)

    # Write to a named temporary file, then extract and clean it up.
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmp_tarball:
            tmp_tarball_path = Path(tmp_tarball.name)
            logger.info("Downloading %s to %s", url, tmp_tarball_path)
            with urllib.request.urlopen(url) as response:  # noqa: S310 (validated scheme)
                shutil.copyfileobj(response, tmp_tarball)
            with tarfile.open(tmp_tarball_path, "r:gz") as tar:
                _extract_api_reference_build(tar, tmpdir)
    finally:
        with suppress(Exception):
            logger.debug("Cleaning up %s", tmp_tarball_path)
            tmp_tarball.close()


def _extract_reference_tag(tag: str, output_dir: Path) -> None:
    """Extract a specific tagged release of the reference HTML into `output_dir`."""
    tarball_url = f"https://github.com/langchain-ai/langchain-api-docs-html/archive/refs/tags/{tag}.tar.gz"
    logger.info("Extracting %s", tarball_url)
    _fetch_extract_tarball(tarball_url, output_dir)


def _extract_reference_latest(output_dir: Path) -> None:
    """Extract the latest main branch reference HTML into `output_dir`."""
    tarball_url = "https://github.com/langchain-ai/langchain-api-docs-html/archive/refs/heads/main.tar.gz"
    logger.info("Extracting %s", tarball_url)
    _fetch_extract_tarball(tarball_url, output_dir)


def clean() -> None:
    """Remove previous build artifacts under `DIST_DIR`."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Cleaning %s", DIST_DIR)
    for entry in DIST_DIR.iterdir():
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def build() -> None:
    """Build the Python reference docs into `DIST_DIR`."""
    clean()
    logger.info("Building reference docs")
    _extract_reference_latest(DIST_DIR)
    for tag in VERSION_TAGS:
        _extract_reference_tag(tag, DIST_DIR / "versions" / tag)
