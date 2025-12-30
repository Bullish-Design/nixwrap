"""TOML configuration loading and saving."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import tomllib

from nix_devenv_wrapper.models import (
    CachixConfig,
    FlakeConfig,
    GitHubActionsConfig,
    PackageMeta,
    PackageSource,
    RuntimeConfig,
    WrapperConfig,
)


def _load_toml(path: Path) -> dict[str, Any]:
    data = tomllib.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Invalid wrapper.toml structure")
    return data


def load_config(path: str | Path) -> FlakeConfig:
    """Load wrapper.toml and return a FlakeConfig."""
    config_path = Path(path)
    data = _load_toml(config_path)

    source = PackageSource(**data["source"])
    runtime = RuntimeConfig(**data["runtime"])
    wrapper = WrapperConfig(**data["wrapper"])
    meta = PackageMeta(**data["meta"])

    cachix = None
    if "cachix" in data:
        cachix = CachixConfig(**data["cachix"])

    github_actions = None
    if "github_actions" in data:
        github_actions = GitHubActionsConfig(**data["github_actions"])

    return FlakeConfig(
        source=source,
        runtime=runtime,
        wrapper=wrapper,
        meta=meta,
        cachix=cachix,
        github_actions=github_actions,
        flake_name=data["flake_name"],
        devenv_enabled=data.get("devenv_enabled", True),
    )


def save_config(config: FlakeConfig, path: str | Path) -> None:
    """Save a FlakeConfig back to a TOML file."""
    config_path = Path(path)

    data: dict[str, Any] = {
        "flake_name": config.flake_name,
        "devenv_enabled": config.devenv_enabled,
        "source": config.source.model_dump(),
        "runtime": config.runtime.model_dump(by_alias=True),
        "wrapper": config.wrapper.model_dump(),
        "meta": config.meta.model_dump(),
    }

    if config.cachix:
        data["cachix"] = config.cachix.model_dump()
    if config.github_actions:
        data["github_actions"] = config.github_actions.model_dump()

    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"[{key}]")
            for subkey, subvalue in value.items():
                lines.append(_format_toml_entry(subkey, subvalue))
            lines.append("")
        else:
            lines.append(_format_toml_entry(key, value))
    config_path.write_text("\n".join(lines).rstrip() + "\n")


def _format_toml_entry(key: str, value: Any) -> str:
    if isinstance(value, str):
        return f"{key} = \"{value}\""
    if isinstance(value, bool):
        return f"{key} = {str(value).lower()}"
    if isinstance(value, list):
        entries = ", ".join(_format_toml_value(item) for item in value)
        return f"{key} = [{entries}]"
    if isinstance(value, dict):
        entries = ", ".join(f"{k} = {_format_toml_value(v)}" for k, v in value.items())
        return f"{key} = {{{entries}}}"
    return f"{key} = {value}"


def _format_toml_value(value: Any) -> str:
    if isinstance(value, str):
        return f"\"{value}\""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
