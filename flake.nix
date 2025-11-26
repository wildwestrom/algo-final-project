{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
  };

  outputs =
    {
      nixpkgs,
      devenv,
      systems,
      ...
    }@inputs:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      devShells = forEachSystem (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = devenv.lib.mkShell {
            inherit inputs pkgs;
            modules = [
              (
                { pkgs, ... }:
                let
                  # Use Python 3.13 if available, fallback to python3Packages
                  pythonPackages = pkgs.python313Packages or pkgs.python3Packages;
                in
                {
                  packages = [
                    pkgs.tk
                    pkgs.tcl
                  ];

                  languages.python.enable = true;
                  languages.python.package = pythonPackages.python;
                  languages.python.uv.enable = true;
                  languages.python.uv.sync.enable = true;
                }
              )
            ];

            # fixes libstdc++ issues and libgl.so issues
            # LD_LIBRARY_PATH = ''${pkgs.stdenv.cc.cc.lib}/lib/:/run/opengl-driver/lib/'';
          };
        }
      );
    };
}
