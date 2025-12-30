"""npm registry client."""
from __future__ import annotations

import httpx

from nix_devenv_wrapper.models import VersionInfo
from nix_devenv_wrapper.registries.base import RegistryClient


class NpmRegistry(RegistryClient):
    """Client for the npm registry."""

    BASE_URL = "https://registry.npmjs.org"

    def __init__(self, timeout: float = 30.0):
        self._client = httpx.Client(timeout=timeout)

    def get_latest_version(self, package_name: str) -> str:
        response = self._client.get(f"{self.BASE_URL}/{package_name}")
        response.raise_for_status()
        data = response.json()
        return data["dist-tags"]["latest"]

    def get_version_info(self, package_name: str, version: str | None = None) -> VersionInfo:
        if version is None:
            version = self.get_latest_version(package_name)
        response = self._client.get(f"{self.BASE_URL}/{package_name}/{version}")
        response.raise_for_status()
        data = response.json()
        return VersionInfo(
            version=version,
            tarball_url=data["dist"]["tarball"],
            published_at=data.get("time", {}).get(version),
        )

    def get_tarball_url(self, package_name: str, version: str) -> str:
        if package_name.startswith("@"):
            scope, name = package_name.split("/", 1)
            return f"{self.BASE_URL}/{scope}/{name}/-/{name}-{version}.tgz"
        return f"{self.BASE_URL}/{package_name}/-/{package_name}-{version}.tgz"

    def close(self) -> None:
        self._client.close()
