# template/flake.nix
{
  description = "Nix wrapper package with devenv.sh integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    devenv.url = "github:cachix/devenv";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = { self, nixpkgs, flake-utils, devenv }@inputs:
    let
      overlay = final: prev: {
        # Package name will be replaced during init
        wrapped-package = final.callPackage ./package.nix { };
      };
    in
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [ overlay ];
        };
      in
      {
        packages = {
          default = pkgs.wrapped-package;
          wrapped-package = pkgs.wrapped-package;
        };

        apps = {
          default = {
            type = "app";
            program = "${pkgs.wrapped-package}/bin/binary-name";
          };
        };

        devShells.default = devenv.lib.mkShell {
          inherit inputs pkgs;
          modules = [ ./devenv.nix ];
        };
      }) // {
        overlays.default = overlay;
      };
}
