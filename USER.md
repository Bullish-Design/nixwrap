# USER.md
# nix-devenv-wrapper User Guide

## Quick Start

### 1. Initialize a New Wrapper Project

```bash
# Create project directory
mkdir my-package-nix && cd my-package-nix
```

### 2. Configure Your Package

Edit `wrapper.toml`:

```toml
flake_name = "my-cli"

[source]
registry = "npm"                    # npm or pypi
name = "@scope/package-name"        # Package name in registry

[runtime]
type = "nodejs"                     # nodejs or python
nix_package = "nodejs_22"           # Nix package for runtime

[wrapper]
binary_name = "mycli"               # Command users will run
entry_point = "cli.js"              # Main entry point

[meta]
description = "My CLI tool"
homepage = "https://example.com"
license = "mit"                     # Nix license identifier
```

### 3. Generate and Build

```bash
# Enter development environment
devenv shell

# Generate nix files from config
ndw init

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

### wrapper.toml Structure

```toml
# Required: Name used in flake outputs
flake_name = "package-name"

# Optional: Enable devenv.sh integration (default: true)
devenv_enabled = true

[source]
# Required: Registry type
registry = "npm"  # "npm" | "pypi"

# Required: Package name in registry
name = "@scope/package"

# Optional: Pin to specific version (omit for latest)
version = "1.2.3"

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

# Optional: Disable upstream auto-updater (default: true)
disable_auto_update = true

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

# Optional: Override main program name
main_program = "mycli"

# Optional: Platform support (default: "platforms.all")
platforms = "platforms.linux"

[cachix]
# Optional: Cachix cache name
name = "my-cache"

# Optional: Public key for cache
public_key = "my-cache.cachix.org-1:..."

[github_actions]
# Optional: Cron schedule for update checks (default: hourly)
update_cron = "0 * * * *"

# Optional: Auto-merge update PRs (default: true)
auto_merge = true

# Optional: CI platforms
test_platforms = ["ubuntu-latest", "macos-latest"]
```

---

## Development Commands

Inside `devenv shell`:

| Command | Description |
|---------|-------------|
| `build` | Build the nix package |
| `test-build` | Build and run version check |

### CLI Tool (ndw)

```bash
ndw check                    # Check for updates
ndw update                   # Update to latest
ndw update -v 1.2.3          # Update to specific version
ndw init                     # Initialize nix files from config
ndw generate                 # Regenerate all nix files
ndw generate package         # Regenerate package.nix only
```
