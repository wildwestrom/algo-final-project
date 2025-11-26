{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
  };

  outputs =
    {
      self,
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
                  pythonBase = if pkgs ? python313 then pkgs.python313 else pkgs.python3;
                  python = pythonBase.withPackages (ps: [ ps.tkinter ]);
                in
                {
                  packages = [
                    pkgs.tk
                    pkgs.tcl
                  ];

                  languages.python.enable = true;
                  languages.python.package = python;
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
