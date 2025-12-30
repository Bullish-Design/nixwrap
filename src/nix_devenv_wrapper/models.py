"""Core Pydantic models for package configuration."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class PackageRegistry(str, Enum):
    """Supported package registries."""

    NPM = "npm"
    PYPI = "pypi"
    CARGO = "cargo"
    GITHUB_RELEASE = "github_release"


class RuntimeType(str, Enum):
    """Supported runtime types for wrapped packages."""

    NODEJS = "nodejs"
    PYTHON = "python"
    RUST = "rust"
    NONE = "none"


class PackageSource(BaseModel):
    """Configuration for where to fetch the package."""

    registry: PackageRegistry
    name: str = Field(..., description="Package name in the registry (e.g., @anthropic-ai/claude-code)")
    version: str | None = Field(None, description="Specific version, or None for latest")

    class Config:
        frozen = True


class RuntimeConfig(BaseModel):
    """Configuration for the runtime environment."""

    runtime_type: RuntimeType = Field(..., alias="type")
    nix_package: str = Field(..., description="Nix package name (e.g., nodejs_22, python312)")
    extra_packages: list[str] = Field(default_factory=list, description="Additional nix packages to include")

    class Config:
        frozen = True
        populate_by_name = True


class WrapperConfig(BaseModel):
    """Configuration for the generated wrapper script."""

    binary_name: str = Field(..., description="Name of the binary to create")
    entry_point: str = Field(..., description="Entry point (e.g., cli.js, __main__.py)")
    env_vars: dict[str, str] = Field(default_factory=dict, description="Environment variables to set")
    node_flags: list[str] = Field(
        default_factory=lambda: ["--no-warnings", "--enable-source-maps"],
        description="Node.js flags (only for nodejs runtime)",
    )
    disable_auto_update: bool = Field(True, description="Disable package auto-updater")

    class Config:
        frozen = True


class PackageMeta(BaseModel):
    """Package metadata for nix derivation."""

    description: str
    homepage: HttpUrl | str
    license: str = Field(default="unfree", description="Nix license identifier")
    main_program: str | None = Field(None, description="Main program name, defaults to binary_name")
    platforms: str = Field(default="platforms.all", description="Nix platforms expression")

    class Config:
        frozen = True


class CachixConfig(BaseModel):
    """Cachix binary cache configuration."""

    name: str = Field(..., description="Cachix cache name")
    public_key: str | None = Field(None, description="Public key for the cache")

    class Config:
        frozen = True


class GitHubActionsConfig(BaseModel):
    """GitHub Actions automation configuration."""

    update_cron: str = Field(default="0 * * * *", description="Cron schedule for update checks")
    auto_merge: bool = Field(True, description="Auto-merge update PRs when CI passes")
    test_platforms: list[str] = Field(
        default_factory=lambda: ["ubuntu-latest", "macos-latest"],
        description="Platforms to test on",
    )

    class Config:
        frozen = True


class FlakeConfig(BaseModel):
    """Complete configuration for a wrapped package flake."""

    source: PackageSource
    runtime: RuntimeConfig
    wrapper: WrapperConfig
    meta: PackageMeta
    cachix: CachixConfig | None = None
    github_actions: GitHubActionsConfig | None = None
    flake_name: str = Field(..., description="Name for the flake (used in overlay)")
    devenv_enabled: bool = Field(True, description="Enable devenv.sh integration")

    class Config:
        frozen = True

    @property
    def pname(self) -> str:
        """Get the package name for nix derivation."""
        return self.flake_name

    def to_nix_attrs(self) -> dict[str, Any]:
        """Convert to attributes suitable for nix generation."""
        return {
            "pname": self.pname,
            "version": self.source.version or "latest",
            "registry": self.source.registry.value,
            "package_name": self.source.name,
            "runtime_package": self.runtime.nix_package,
            "binary_name": self.wrapper.binary_name,
            "entry_point": self.wrapper.entry_point,
            "description": self.meta.description,
            "homepage": str(self.meta.homepage),
            "license": self.meta.license,
            "main_program": self.meta.main_program or self.wrapper.binary_name,
        }


class VersionInfo(BaseModel):
    """Information about a package version."""

    version: str
    tarball_url: str
    sha256: str | None = None
    published_at: str | None = None

    class Config:
        frozen = True


class UpdateResult(BaseModel):
    """Result of a version update check."""

    current_version: str
    latest_version: str
    update_available: bool
    new_hash: str | None = None

    class Config:
        frozen = True
