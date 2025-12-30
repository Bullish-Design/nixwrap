#!/usr/bin/env -S uv run
# scripts/check_update.py
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "nix-devenv-wrapper",
#     "httpx>=0.25",
#     "pydantic>=2.0",
# ]
# ///
"""Check for updates for the wrapped package."""
from __future__ import annotations

import sys
from pathlib import Path

from nix_devenv_wrapper.config import load_config
from nix_devenv_wrapper.updater import Updater


def main() -> int:
    config_path = Path("wrapper.toml")
    if not config_path.exists():
        print("Error: wrapper.toml not found", file=sys.stderr)
        return 1

    config = load_config(config_path)
    updater = Updater(config)
    result = updater.check_for_updates()

    if result.update_available:
        print(f"Update available: {result.current_version} -> {result.latest_version}")
        return 0

    print(f"Already at latest version ({result.current_version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
