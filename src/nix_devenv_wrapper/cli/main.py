"""Command-line interface for nix-devenv-wrapper."""
from __future__ import annotations

import argparse
from pathlib import Path

from nix_devenv_wrapper.config import load_config
from nix_devenv_wrapper.generators import generate_devenv_nix, generate_flake_nix, generate_package_nix
from nix_devenv_wrapper.updater import Updater


def _latest_or_pinned_version(updater: Updater) -> str:
    config_version = updater.config.source.version
    if config_version:
        return config_version
    return updater.get_version_info().version


def _write_file(path: Path, content: str) -> None:
    path.write_text(content)


def cmd_check(args: argparse.Namespace) -> int:
    """Check if updates are available."""
    config = load_config(args.config)
    updater = Updater(config)
    result = updater.check_for_updates()

    if result.update_available:
        print(f"Update available: {result.current_version} -> {result.latest_version}")
        return 0

    print(f"Already at latest version ({result.current_version})")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Update package.nix to the latest or specified version."""
    config = load_config(args.config)
    updater = Updater(config)
    result = updater.update_to_version(args.version)

    if not result.update_available:
        print(f"Already at version {result.current_version}")
        return 0

    print(f"Updated: {result.current_version} -> {result.latest_version}")
    print(f"Hash: {result.new_hash}")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    """Regenerate nix files from config."""
    config = load_config(args.config)
    updater = Updater(config)

    version = _latest_or_pinned_version(updater)
    sha256 = updater.fetch_hash(version)

    targets = args.targets or ["package", "flake", "devenv"]

    if "package" in targets:
        _write_file(Path(args.package_nix), generate_package_nix(config, version, sha256))
    if "flake" in targets:
        _write_file(Path(args.flake_nix), generate_flake_nix(config))
    if "devenv" in targets and config.devenv_enabled:
        _write_file(Path(args.devenv_nix), generate_devenv_nix(config))

    print("Generated: " + ", ".join(targets))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize nix files from config."""
    return cmd_generate(args)


def main() -> int:
    parser = argparse.ArgumentParser(description="nix-devenv-wrapper CLI")
    parser.add_argument("-c", "--config", default="wrapper.toml", help="Path to wrapper.toml")
    parser.add_argument("--package-nix", default="package.nix", help="Path to package.nix")
    parser.add_argument("--flake-nix", default="flake.nix", help="Path to flake.nix")
    parser.add_argument("--devenv-nix", default="devenv.nix", help="Path to devenv.nix")

    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check for updates")
    check_parser.set_defaults(func=cmd_check)

    update_parser = subparsers.add_parser("update", help="Update to latest or specific version")
    update_parser.add_argument("-v", "--version", help="Version to update to")
    update_parser.set_defaults(func=cmd_update)

    init_parser = subparsers.add_parser("init", help="Initialize nix files from config")
    init_parser.add_argument("targets", nargs="*", choices=["package", "flake", "devenv"])
    init_parser.set_defaults(func=cmd_init)

    generate_parser = subparsers.add_parser("generate", help="Generate nix files from config")
    generate_parser.add_argument("targets", nargs="*", choices=["package", "flake", "devenv"])
    generate_parser.set_defaults(func=cmd_generate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
