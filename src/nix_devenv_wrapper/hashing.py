"""Nix hash computation utilities."""
from __future__ import annotations

import subprocess


def prefetch_url_hash(url: str) -> str:
    """Compute a sha256 hash for a URL using nix-prefetch-url."""
    result = subprocess.run(
        ["nix-prefetch-url", "--type", "sha256", url],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()
