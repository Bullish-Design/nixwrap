"""Registry clients."""
from __future__ import annotations

from nix_devenv_wrapper.registries.base import RegistryClient
from nix_devenv_wrapper.registries.factory import get_registry
from nix_devenv_wrapper.registries.npm import NpmRegistry
from nix_devenv_wrapper.registries.pypi import PyPIRegistry

__all__ = ["RegistryClient", "NpmRegistry", "PyPIRegistry", "get_registry"]
