# nixwrap

`nixwrap` is a TOML-driven tool for generating Nix packaging and devenv setup from a single `nixwrap.toml`. It produces
`nixwrap.nix`, an optional `flake.nix`, and a structured `devenv.nix` output so you can keep wrapper repos tidy and
repeatable.

## Features

- **Config-driven**: `nixwrap.toml` is the single source of truth
- **Generated outputs**: `nixwrap.nix`, `flake.nix`, and `devenv.nix`
- **Simple CLI**: `nixwrap init/generate/flake/validate`

## Installation

```bash
uv add nixwrap
# or
pip install nixwrap
```

## Quick Start

```bash
mkdir my-wrapper && cd my-wrapper
nixwrap init

# Edit nixwrap.toml, then regenerate outputs
nixwrap generate
```

## Output layout (devenv pattern)

`nixwrap generate` writes a structured `devenv.nix` under `nix/` and a thin root-level shim:

```
.
├── nixwrap.toml
├── nixwrap.nix
├── flake.nix
├── nix/
│   └── devenv.nix         # generated content
└── devenv.nix             # imports ./nix/devenv.nix
```

## Flake + nixwrap.nix integration snippet

Use `nixwrap.nix` directly from your `flake.nix` outputs:

```nix
{
  description = "My wrapped CLI";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      nixwrapOutputs = import ./nixwrap.nix { inherit nixpkgs systems; };
    in
    {
      packages = forAllSystems nixwrapOutputs.packages;
      devShells = forAllSystems nixwrapOutputs.devShells;
    };
}
```

## CLI Usage

```bash
nixwrap init                 # Create nixwrap.toml and scaffolding
nixwrap generate             # Regenerate nixwrap.nix + devenv.nix
nixwrap flake                # Generate/update flake.nix wrapper
nixwrap validate             # Validate nixwrap.toml
```

## License

MIT
