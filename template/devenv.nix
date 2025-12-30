# template/devenv.nix
{ pkgs, lib, config, inputs, ... }:

{
  packages = with pkgs; [
    nixpkgs-fmt
    nix-prefetch-git
    cachix
  ];

  languages.python = {
    enable = true;
    uv = {
      enable = true;
      sync.enable = true;
    };
  };

  pre-commit.hooks = {
    nixpkgs-fmt.enable = true;
  };

  scripts = {
    check-update.exec = "uv run scripts/check_update.py";
    update-version.exec = "uv run scripts/update_version.py $@";
    build.exec = "nix build --print-build-logs";
    test-build.exec = ''
      nix build --print-build-logs
      ./result/bin/binary-name --version
    '';
  };

  enterShell = ''
    echo ""
    echo "🔧 Development environment ready"
    echo ""
    echo "Commands:"
    echo "  check-update   - Check for new upstream versions"
    echo "  update-version - Update to latest (or specify version)"
    echo "  build          - Build the nix package"
    echo "  test-build     - Build and verify version output"
    echo ""
  '';
}
