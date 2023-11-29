{
  description = "Description for the project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
    devenv.url = "github:cachix/devenv";
    nix2container.url = "github:nlewo/nix2container";
    nix2container.inputs.nixpkgs.follows = "nixpkgs";
    mk-shell-bin.url = "github:rrbutani/nix-mk-shell-bin";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.devenv.flakeModule
      ];
      systems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];

      perSystem = { config, self', inputs', pkgs, system, lib, ... }:
        let
          pythonVersions = [
            "3.8"
            "3.9"
            "3.10"
            "3.11"
          ];
          mkShell = v:
            let
              isDefaultPython = v == (lib.versions.majorMinor pkgs.python3.version);
              python =
                if isDefaultPython then
                  pkgs.python3
                else
                  inputs'.nixpkgs-python.packages.${v};
              pythonPackages = ps: with ps; [
                build
                pip-tools
                tox
                twine
              ];
              shell = {
                name = v;
                packages = [
                  pkgs.pre-commit
                ];
                languages.python.enable = true;
                languages.python.version = v;
                languages.python.package = lib.mkForce (python.withPackages pythonPackages);
                languages.python.venv.enable = true;
                languages.python.venv.requirements = ./requirements.txt;
              };

            in
              [ { name = lib.replaceStrings ["."] [""] v; value = shell; } ]
              ++ (lib.optionals isDefaultPython [ { name = "default"; value = shell; }]);
        in {
        devenv.shells = lib.trivial.pipe pythonVersions [
          (map mkShell)
          lib.flatten
          lib.listToAttrs
        ];
      };
    };
}
