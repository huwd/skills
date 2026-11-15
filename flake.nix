{
  description = "Development tools for the huwd/skills catalogue";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (pkgs: {
        # nix run .#vale -- <files>: Vale with this repository's styles
        vale = import ./nix/vale.nix { inherit pkgs; };
      });

      # nix develop: every tool the pre-commit hooks and CI checks use
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [
            (import ./nix/vale.nix { inherit pkgs; })
            pkgs.pre-commit
            pkgs.markdownlint-cli2
            pkgs.shellcheck
            pkgs.gitleaks
            pkgs.zizmor
            pkgs.bats
            pkgs.jq
            pkgs.uv
            pkgs.go
            pkgs.nodejs
            (pkgs.python3.withPackages (ps: [ ps.pyyaml ]))
          ];
        };
      });
    };
}
