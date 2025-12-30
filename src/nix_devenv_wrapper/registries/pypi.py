"""PyPI registry client."""
from __future__ import annotations

import httpx

from nix_devenv_wrapper.models import VersionInfo
from nix_devenv_wrapper.registries.base import RegistryClient


class PyPIRegistry(RegistryClient):
    """Client for the PyPI registry."""

    BASE_URL = "https://pypi.org/pypi"

    def __init__(self, timeout: float = 30.0):
        self._client = httpx.Client(timeout=timeout)

    def get_latest_version(self, package_name: str) -> str:
        response = self._client.get(f"{self.BASE_URL}/{package_name}/json")
        response.raise_for_status()
        return response.json()["info"]["version"]

    def get_version_info(self, package_name: str, version: str | None = None) -> VersionInfo:
        if version is None:
            version = self.get_latest_version(package_name)
        response = self._client.get(f"{self.BASE_URL}/{package_name}/{version}/json")
        response.raise_for_status()
        data = response.json()
        urls = data.get("urls", [])
        if not urls:
            raise ValueError(f"No distribution files found for {package_name} {version}")
        sdist = next((item for item in urls if item.get("packagetype") == "sdist"), urls[0])
        return VersionInfo(
            version=version,
            tarball_url=sdist["url"],
            published_at=sdist.get("upload_time_iso_8601"),
        )

    def get_tarball_url(self, package_name: str, version: str) -> str:
        info = self.get_version_info(package_name, version)
        return info.tarball_url

    def close(self) -> None:
        self._client.close()
