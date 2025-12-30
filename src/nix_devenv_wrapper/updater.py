"""Update service for checking and applying version updates."""
from __future__ import annotations

import re
from pathlib import Path

from nix_devenv_wrapper.hashing import prefetch_url_hash
from nix_devenv_wrapper.models import FlakeConfig, UpdateResult, VersionInfo
from nix_devenv_wrapper.registries import get_registry


class Updater:
    """Service for checking and applying version updates."""

    def __init__(self, config: FlakeConfig, package_nix_path: Path | None = None):
        self.config = config
        self.package_nix_path = package_nix_path or Path("package.nix")

    def get_current_version(self) -> str:
        """Read the current version from package.nix."""
        content = self.package_nix_path.read_text()
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if not match:
            raise ValueError("Could not find version in package.nix")
        return match.group(1)

    def get_current_hash(self) -> str:
        """Read the current sha256 hash from package.nix."""
        content = self.package_nix_path.read_text()
        match = re.search(r'sha256\s*=\s*"([^"]+)"', content)
        if not match:
            raise ValueError("Could not find sha256 in package.nix")
        return match.group(1)

    def check_for_updates(self) -> UpdateResult:
        """Check if a newer version is available."""
        current_version = self.get_current_version()

        with get_registry(self.config.source.registry) as registry:
            latest_version = registry.get_latest_version(self.config.source.name)

        update_available = current_version != latest_version

        return UpdateResult(
            current_version=current_version,
            latest_version=latest_version,
            update_available=update_available,
        )

    def get_version_info(self, version: str | None = None) -> VersionInfo:
        """Get detailed info for a specific version."""
        with get_registry(self.config.source.registry) as registry:
            return registry.get_version_info(self.config.source.name, version)

    def fetch_hash(self, version: str) -> str:
        """Fetch the hash for a specific version's tarball."""
        with get_registry(self.config.source.registry) as registry:
            info = registry.get_version_info(self.config.source.name, version)
        return prefetch_url_hash(info.tarball_url)

    def update_package_nix(self, version: str, sha256: str) -> None:
        """Update package.nix with new version and hash."""
        content = self.package_nix_path.read_text()

        content = re.sub(
            r'version\s*=\s*"[^"]+"',
            f'version = "{version}"',
            content,
        )

        content = re.sub(
            r'sha256\s*=\s*"[^"]+"',
            f'sha256 = "{sha256}"',
            content,
        )

        self.package_nix_path.write_text(content)

    def update_to_version(self, version: str | None = None) -> UpdateResult:
        """Update to a specific version or latest."""
        current_version = self.get_current_version()

        if version is None:
            with get_registry(self.config.source.registry) as registry:
                version = registry.get_latest_version(self.config.source.name)

        if version == current_version:
            return UpdateResult(
                current_version=current_version,
                latest_version=version,
                update_available=False,
            )

        new_hash = self.fetch_hash(version)
        self.update_package_nix(version, new_hash)

        return UpdateResult(
            current_version=current_version,
            latest_version=version,
            update_available=True,
            new_hash=new_hash,
        )
