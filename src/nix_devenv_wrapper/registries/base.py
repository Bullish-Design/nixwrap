"""Registry client base classes."""
from __future__ import annotations

from abc import ABC, abstractmethod

from nix_devenv_wrapper.models import VersionInfo


class RegistryClient(ABC):
    """Abstract registry client interface."""

    @abstractmethod
    def get_latest_version(self, package_name: str) -> str:
        """Return the latest version string for the package."""

    @abstractmethod
    def get_version_info(self, package_name: str, version: str | None = None) -> VersionInfo:
        """Return version info for a package."""

    @abstractmethod
    def get_tarball_url(self, package_name: str, version: str) -> str:
        """Return tarball URL for a package version."""

    @abstractmethod
    def close(self) -> None:
        """Close any underlying resources."""

    def __enter__(self) -> "RegistryClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
