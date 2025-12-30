"""Registry factory utilities."""
from __future__ import annotations

from nix_devenv_wrapper.models import PackageRegistry
from nix_devenv_wrapper.registries.base import RegistryClient
from nix_devenv_wrapper.registries.npm import NpmRegistry
from nix_devenv_wrapper.registries.pypi import PyPIRegistry


def get_registry(registry_type: PackageRegistry) -> RegistryClient:
    """Return a registry client for the given registry type."""
    match registry_type:
        case PackageRegistry.NPM:
            return NpmRegistry()
        case PackageRegistry.PYPI:
            return PyPIRegistry()
        case _:
            raise NotImplementedError(f"Registry {registry_type} not yet implemented")
