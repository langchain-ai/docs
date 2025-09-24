"""Main entry point for the Python reference docs build."""

import logging
import sys

from .build import build

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(levelname)s: %(message)s",
    )
    build()
