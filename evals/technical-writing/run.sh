#!/usr/bin/env bash
# Run the technical-writing eval suite from the repository root.
#
#   evals/technical-writing/run.sh [extra claude plugin eval flags]
#
# Scaffolds resolve markdownlint-cli2 and vale from PATH and bake their
# paths into each fixture's own lint scripts, because the agent's sandbox
# may not inherit PATH (on NixOS it is reset to the system profile). On
# Nix, this script provides both tools; elsewhere, install them first.
set -euo pipefail
cd "$(dirname "$0")/../.."

args=(
  . --tag technical-writing
  --scaffold --trust-plugin --no-publish
  --allow-tools Bash Edit Write
)

if command -v nix >/dev/null 2>&1; then
  exec nix shell nixpkgs#vale nixpkgs#markdownlint-cli2 \
    -c claude plugin eval "${args[@]}" "$@"
fi
exec claude plugin eval "${args[@]}" "$@"
