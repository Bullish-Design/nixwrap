# DEV_GUIDE.md
# Developer Guide

This guide explains the architecture and patterns of nix-devenv-wrapper to help you contribute effectively.

## Architecture Overview

```
nix-devenv-wrapper/
├── src/nix_devenv_wrapper/
│   ├── __init__.py           # Package version
│   ├── models.py             # Pydantic data models (core types)
│   ├── config.py             # TOML configuration loading/saving
│   ├── hashing.py            # Nix hash computation utilities
│   ├── updater.py            # Version checking and update orchestration
│   ├── registries/           # Package registry clients
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract base class
│   │   ├── npm.py            # npm registry implementation
│   │   ├── pypi.py           # PyPI registry implementation
│   │   └── factory.py        # Registry factory function
│   ├── generators/           # Nix file generators
│   │   ├── __init__.py
│   │   ├── package_nix.py    # package.nix generator
│   │   ├── flake_nix.py      # flake.nix generator
│   │   └── devenv.py         # devenv.nix generator
│   └── cli/                  # Command-line interface
│       ├── __init__.py
│       └── main.py           # CLI entry point
├── template/                 # User-facing template files
└── scripts/                  # Update scripts
```

## Core Concepts

### 1. Configuration-Driven Design

Everything flows from `wrapper.toml`. The configuration is parsed into Pydantic models, which are then used by generators and the updater.

```
wrapper.toml → FlakeConfig → Generators → .nix files
                          → Updater → package.nix updates
```

### 2. Pydantic Models (models.py)

All data structures use Pydantic for validation and serialization. Models are immutable (`frozen = True`).

**Key models:**

```python
FlakeConfig          # Root configuration object
├── PackageSource    # Registry + package name + version
├── RuntimeConfig    # Runtime type + nix package
├── WrapperConfig    # Binary name + entry point + env vars
├── PackageMeta      # Description, homepage, license
├── CachixConfig     # Binary cache settings (optional)
└── GitHubActionsConfig  # CI/CD settings (optional)
```

**Supporting models:**

```python
VersionInfo    # Version + tarball URL + hash
UpdateResult   # Current vs latest version + update status
```

**Enums:**

```python
PackageRegistry  # npm, pypi, cargo, github_release
RuntimeType      # nodejs, python, rust, none
```

### 3. Registry Abstraction (registries/)

Registries follow the Strategy pattern via an abstract base class:

```python
class RegistryClient(ABC):
    @abstractmethod
    def get_latest_version(self, package_name: str) -> str: ...

    @abstractmethod
    def get_version_info(self, package_name: str, version: str | None) -> VersionInfo: ...

    @abstractmethod
    def get_tarball_url(self, package_name: str, version: str) -> str: ...
```

Each registry (npm, PyPI) implements this interface. The factory creates the appropriate client:

```python
from nix_devenv_wrapper.registries import get_registry
from nix_devenv_wrapper.models import PackageRegistry

registry = get_registry(PackageRegistry.NPM)
version = registry.get_latest_version("@anthropic-ai/claude-code")
```

### 4. Updater (updater.py)

The `Updater` class orchestrates version checking and updates:

```python
class Updater:
    def __init__(self, config: FlakeConfig, package_nix_path: Path | None = None): ...

    def get_current_version(self) -> str: ...      # Parse from package.nix
    def check_for_updates(self) -> UpdateResult: ... # Compare versions
    def fetch_hash(self, version: str) -> str: ...   # Get tarball hash
    def update_to_version(self, version: str | None) -> UpdateResult: ...  # Apply update
```

### 5. Generators (generators/)

Generators produce nix code from configuration. They use string templating (not Jinja2) for simplicity.

```python
def generate_package_nix(config: FlakeConfig, version: str, sha256: str) -> str:
    # Returns complete package.nix content
```

Each generator is pure: same inputs always produce same outputs.

## Key Patterns

### Pattern 1: Immutable Models

All Pydantic models use `frozen = True`:

```python
class PackageSource(BaseModel):
    registry: PackageRegistry
    name: str
    version: str | None = None

    class Config:
        frozen = True
```

This prevents accidental mutation and makes the code easier to reason about.

### Pattern 2: Context Managers for HTTP Clients

Registry clients implement context manager protocol for proper resource cleanup:

```python
class NpmRegistry(RegistryClient):
    def __init__(self, timeout: float = 30.0):
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> NpmRegistry:
        return self

    def __exit__(self, *args) -> None:
        self.close()

# Usage
with get_registry(PackageRegistry.NPM) as registry:
    version = registry.get_latest_version(package_name)
```

### Pattern 3: Factory Functions

Use factories to abstract object creation:

```python
# registries/factory.py
def get_registry(registry_type: PackageRegistry) -> RegistryClient:
    match registry_type:
        case PackageRegistry.NPM:
            return NpmRegistry()
        case PackageRegistry.PYPI:
            return PyPIRegistry()
        case _:
            raise NotImplementedError(f"Registry {registry_type} not yet implemented")
```

### Pattern 4: Separation of Concerns

- **models.py**: Data structures only, no behavior
- **registries/**: HTTP client logic only
- **generators/**: String generation only
- **updater.py**: Orchestration only
- **config.py**: File I/O only

### Pattern 5: Type Hints with Future Annotations

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
