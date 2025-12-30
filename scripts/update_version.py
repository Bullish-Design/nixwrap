#!/usr/bin/env -S uv run
# scripts/update_version.py
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "nix-devenv-wrapper",
#     "httpx>=0.25",
#     "pydantic>=2.0",
# ]
# ///
"""Update package to latest or specified version."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from nix_devenv_wrapper.config import load_config
from nix_devenv_wrapper.updater import Updater


def verify_build() -> bool:
    """Run nix build to verify the update works."""
    print("\nVerifying build...")
    result = subprocess.run(
        ["nix", "build", "--no-link"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Update package version")
    parser.add_argument("version", nargs="?", help="Specific version to update to")
    parser.add_argument("--no-verify", action="store_true", help="Skip build verification")
    args = parser.parse_args()

    config_path = Path("wrapper.toml")
    if not config_path.exists():
        print("Error: wrapper.toml not found", file=sys.stderr)
        return 1

    config = load_config(config_path)
    updater = Updater(config)

    target_version = args.version
    if target_version:
        print(f"Updating {config.source.name} to version {target_version}...")
    else:
        print(f"Updating {config.source.name} to latest version...")

    result = updater.update_to_version(target_version)

    if not result.update_available:
        print(f"Already at version {result.current_version}")
        return 0

    print(f"Updated: {result.current_version} -> {result.latest_version}")
    print(f"Hash: {result.new_hash}")

    if not args.no_verify:
        if verify_build():
            print("\n✅ Build successful!")
        else:
            print("\n❌ Build failed. Check the error messages above.", file=sys.stderr)
            print("You may need to revert changes to package.nix", file=sys.stderr)
            return 1

    print("\nDon't forget to:")
    print("  1. Test the build: nix run . -- --version")
    print(
        "  2. Commit changes: git add package.nix && git commit -m 'chore: update to v{}'".format(
            result.latest_version
        )
    )
    print("  3. Push to GitHub")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
