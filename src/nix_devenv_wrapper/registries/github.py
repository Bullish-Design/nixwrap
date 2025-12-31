"""GitHub releases registry client."""
from __future__ import annotations

import httpx

from nix_devenv_wrapper.models import VersionInfo
from nix_devenv_wrapper.registries.base import RegistryClient


class GitHubRegistry(RegistryClient):
    """Client for GitHub releases."""

    BASE_URL = "https://api.github.com"

    def __init__(self, timeout: float = 30.0, token: str | None = None):
        """
        Initialize GitHub registry client.

        Args:
            timeout: Request timeout in seconds
            token: Optional GitHub personal access token for higher rate limits
        """
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(timeout=timeout, headers=headers)

    def _parse_repo(self, package_name: str) -> tuple[str, str]:
        """Parse owner/repo from package name."""
        parts = package_name.split("/")
        if len(parts) != 2:
            raise ValueError(f"GitHub package name must be in format 'owner/repo', got: {package_name}")
        return parts[0], parts[1]

    def get_latest_version(self, package_name: str) -> str:
        """Get the latest release version from GitHub."""
        owner, repo = self._parse_repo(package_name)
        response = self._client.get(f"{self.BASE_URL}/repos/{owner}/{repo}/releases/latest")
        response.raise_for_status()
        data = response.json()
        # GitHub tags often have a 'v' prefix, strip it for consistency
        tag = data["tag_name"]
        return tag.lstrip("v")

    def get_version_info(self, package_name: str, version: str | None = None) -> VersionInfo:
        """Get version info for a specific release."""
        owner, repo = self._parse_repo(package_name)

        if version is None:
            version = self.get_latest_version(package_name)

        # Try with and without 'v' prefix
        tag = f"v{version}" if not version.startswith("v") else version

        response = self._client.get(f"{self.BASE_URL}/repos/{owner}/{repo}/releases/tags/{tag}")
        if response.status_code == 404:
            # Try without 'v' prefix
            tag = version.lstrip("v")
            response = self._client.get(f"{self.BASE_URL}/repos/{owner}/{repo}/releases/tags/{tag}")

        response.raise_for_status()
        data = response.json()

        # Get tarball URL from the release
        tarball_url = data.get("tarball_url") or f"https://github.com/{owner}/{repo}/archive/refs/tags/{tag}.tar.gz"

        return VersionInfo(
            version=version.lstrip("v"),
            tarball_url=tarball_url,
            published_at=data.get("published_at"),
        )

    def get_tarball_url(self, package_name: str, version: str) -> str:
        """Get tarball URL for a specific version."""
        owner, repo = self._parse_repo(package_name)
        tag = f"v{version}" if not version.startswith("v") else version
        return f"https://github.com/{owner}/{repo}/archive/refs/tags/{tag}.tar.gz"

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
