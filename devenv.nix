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
    echo "  build          - Build the nix package"
    echo "  test-build     - Build and verify version output"
    echo ""
  '';
}
