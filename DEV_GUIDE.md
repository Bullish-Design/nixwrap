# DEV_GUIDE.md
# Developer Guide

This guide explains the architecture and patterns of nixwrap to help you contribute effectively.

## Architecture Overview

```
nixwrap/
├── src/nix_devenv_wrapper/
│   ├── __init__.py           # Package version
│   ├── models.py             # Pydantic data models (core types)
│   ├── config.py             # TOML configuration loading/saving
│   ├── hashing.py            # Nix hash computation utilities
│   ├── generators/           # Nix file generators
│   │   ├── __init__.py
│   │   ├── nixwrap_nix.py    # nixwrap.nix generator
│   │   ├── flake_nix.py      # flake.nix generator
│   │   └── devenv.py         # devenv.nix generator
│   └── cli/                  # Command-line interface
│       ├── __init__.py
│       └── main.py           # CLI entry point
├── devenv.nix                # Example devenv.nix
└── flake.nix                 # Example flake.nix
```

## Core Concepts

### 1. Configuration-Driven Design

Everything flows from `nixwrap.toml`. The configuration is parsed into Pydantic models, which are then used by generators.

```
nixwrap.toml → FlakeConfig → Generators → nixwrap.nix, devenv.nix, flake.nix
```

### 2. Pydantic Models (models.py)

All data structures use Pydantic for validation and serialization. Models are immutable (`frozen = True`).

**Key models:**

```python
FlakeConfig          # Root configuration object
├── PackageConfig    # Version + source reference
├── RuntimeConfig    # Runtime type + nix package
├── WrapperConfig    # Binary name + entry point + env vars
└── PackageMeta      # Description, homepage, license
```

**Supporting models:**

```python
NixwrapOutput  # Generated paths + metadata
```

**Enums:**

```python
RuntimeType      # nodejs, python, rust, none
```

### 3. Generators (generators/)

Generators produce nix code from configuration. They use string templating (not Jinja2) for simplicity.

```python
def generate_nixwrap_nix(config: FlakeConfig) -> str:
    # Returns complete nixwrap.nix content
```

Each generator is pure: same inputs always produce same outputs.

## Key Patterns

### Pattern 1: Immutable Models

All Pydantic models use `frozen = True`:

```python
class PackageConfig(BaseModel):
    version: str
    src: str

    class Config:
        frozen = True
```

This prevents accidental mutation and makes the code easier to reason about.

### Pattern 2: Factory Functions

Use factories to abstract object creation:

```python
# generators/factory.py
def get_generator(config: FlakeConfig) -> NixwrapGenerator:
    match config.runtime.type:
        case RuntimeType.NODEJS:
            return NodeGenerator (config)
        case RuntimeType.PYTHON:
            return PythonGenerator(config)
        case _:
            raise NotImplementedError(f"Runtime {config.runtime.type} not yet implemented")
```

### Pattern 3: Separation of Concerns

- **models.py**: Data structures only, no behavior
- **generators/**: String generation only
- **config.py**: File I/O only

### Pattern 4: Type Hints with Future Annotations

All files use `from __future__ import annotations` for cleaner type hints:

```python
from __future__ import annotations

def get_version_info(self, package_name: str, version: str | None = None) -> VersionInfo:
    ...
```

## Testing

Run tests with:

```bash
uv run pytest
```

## Development Workflow

1. Enter devenv shell: `devenv shell`
2. Make changes
3. Run tests: `uv run pytest`
4. Run linter: `uv run ruff check src/`
5. Run type checker: `uv run mypy src/`
6. Commit with descriptive message
