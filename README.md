# nixwrap (nix-devenv-wrapper)

`nixwrap` is a Python library that wraps packages from registries (npm, PyPI) as Nix flakes with optional `devenv.sh`
automation. It provides a TOML-driven configuration model, generators for Nix files, and a small CLI to keep wrapper
flakes updated.

## Features

- **Registry support**: npm and PyPI (cargo/GitHub releases planned)
- **Config-driven**: single `wrapper.toml` becomes `package.nix`, `flake.nix`, and `devenv.nix`
- **Updater tooling**: fetch latest versions + update hashes
- **CLI**: `ndw` to initialize, generate, and update wrappers

## Installation

```bash
uv add nix-devenv-wrapper
# or
pip install nix-devenv-wrapper
```

## Quick Start

```bash
mkdir my-wrapper && cd my-wrapper
cp -r /path/to/nixwrap/template/* .

# Edit wrapper.toml
ndw init
```

## Flake import example

Use nixwrap as a flake input (mirroring the devman example) and pass the inputs to your module:

```nix
{
  description = "Terminal-only Home Manager profile - Pulls in Neovim config from another repo";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    nixvim = {
      url = "github:Bullish-Design/nixvim/main";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    devman = {
      url = "github:Bullish-Design/devman/nixos";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    nixwrap = {
      url = "github:your-org/nixwrap";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixvim, devman, nixwrap, ... }: {
    homeManagerModules.terminal = import ./modules/terminal.nix {
      inherit nixvim devman nixwrap;
    };
  };
}
```

## Library Usage

```python
from nix_devenv_wrapper.config import load_config
from nix_devenv_wrapper.updater import Updater

config = load_config("wrapper.toml")
updater = Updater(config)

result = updater.check_for_updates()
print(f"Update available: {result.update_available}")

result = updater.update_to_version()
print(f"Updated to {result.latest_version}")
```

## CLI Usage

```bash
ndw check                    # Check for updates
ndw update                   # Update to latest
ndw update -v 1.2.3          # Update to specific version
ndw init                     # Initialize nix files from config
ndw generate                 # Regenerate all nix files
ndw generate package         # Regenerate package.nix only
```

## Supported Registries

| Registry | Status |
|----------|--------|
| npm | ✅ Supported |
| PyPI | ✅ Supported |
| Cargo | 🚧 Planned |
| GitHub Releases | 🚧 Planned |

## License

MIT
