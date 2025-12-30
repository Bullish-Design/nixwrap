# USER.md
# nixwrap User Guide

## Quick Start

### 1. Initialize a New Wrapper Project

```bash
# Create project directory
mkdir my-package-nix && cd my-package-nix

# Initialize nixwrap scaffolding
nixwrap init
```

### 2. Configure Your Package

Edit `nixwrap.toml`:

```toml
name = "my-cli"

[package]
version = "1.2.3"
src = "github:your-org/my-cli?ref=v1.2.3"

[runtime]
type = "nodejs"
nix_package = "nodejs_22"

[wrapper]
binary_name = "mycli"
entry_point = "cli.js"

[meta]
description = "My CLI tool"
homepage = "https://example.com"
license = "mit"
```

### 3. Generate and Build

```bash
# Enter development environment
devenv shell

# Generate nix files from config
nixwrap generate

# Build the package
nix build

# Test it works
./result/bin/mycli --version
```

### 4. Use Your Package

```bash
# Run directly
nix run github:your-org/my-package-nix

# Install to profile
nix profile install github:your-org/my-package-nix

# Add to NixOS configuration
environment.systemPackages = [ inputs.my-package-nix.packages.${system}.default ];

# Add to Home Manager
home.packages = [ inputs.my-package-nix.packages.${system}.default ];
```

---

## Configuration Reference

### nixwrap.toml Structure

```toml
# Required: Name used in flake outputs
name = "package-name"

[package]
# Required: Version for your wrapper
version = "1.2.3"

# Required: Source reference (git, flake, or local path)
src = "github:your-org/package?ref=v1.2.3"

[runtime]
# Required: Runtime type
type = "nodejs"  # "nodejs" | "python"

# Required: Nix package for runtime
nix_package = "nodejs_22"  # nodejs_22, python312, etc.

# Optional: Additional nix packages
extra_packages = ["git", "ripgrep"]

[wrapper]
# Required: Binary name
binary_name = "mycli"

# Required: Entry point file
entry_point = "cli.js"

# Optional: Node.js flags (nodejs only)
node_flags = ["--no-warnings", "--enable-source-maps"]

# Optional: Environment variables
env_vars = { MY_VAR = "value" }

[meta]
# Required: Package description
description = "My package description"

# Required: Homepage URL
homepage = "https://example.com"

# Optional: Nix license identifier (default: "unfree")
license = "mit"

# Optional: Platform support (default: "platforms.all")
platforms = "platforms.linux"
```

---

## CLI Tool

```bash
nixwrap init                 # Create nixwrap.toml and scaffolding
nixwrap generate             # Regenerate nixwrap.nix + devenv.nix
nixwrap flake                # Generate/update flake.nix wrapper
nixwrap validate             # Validate nixwrap.toml
```
