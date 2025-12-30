{
  description = "nixwrap";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        nixwrap = pkgs.python311Packages.buildPythonApplication {
          pname = "nixwrap";
          version = "0.1.0";
          pyproject = true;
          src = ./.;
          propagatedBuildInputs = with pkgs.python311Packages; [
            httpx
            pydantic
          ];
        };
      in
      {
        packages.default = nixwrap;

        apps.default = {
          type = "app";
          program = "${nixwrap}/bin/ndw";
        };
      });
}
