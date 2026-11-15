#!/usr/bin/env bash
# Run Vale over the repository's tracked Markdown, with the configuration in
# .vale.ini. Pre-commit runs this before push and CI runs it on every pull
# request. Vale exits non-zero only for errors; warnings are advice.
#
#   .github/scripts/check-prose.sh                          # errors only
#   .github/scripts/check-prose.sh --minAlertLevel=suggestion # all advice
#
# Eval inputs are skipped: task and prompt files, graders and the editorial
# fixtures are deliberately faulty or must stay as the cases were measured.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# The flake's Vale bundles the styles and the en_GB dictionary, and sets
# VALE_STYLES_PATH. A plain Vale has neither, so use the flake's instead.
if [[ -n "${VALE_STYLES_PATH:-}" ]] && command -v vale >/dev/null 2>&1; then
  vale=(vale)
elif command -v nix >/dev/null 2>&1; then
  vale=(nix --extra-experimental-features 'nix-command flakes' run .#vale --)
else
  echo "check-prose: needs the flake's Vale. Run it inside 'nix develop', or install Nix." >&2
  exit 2
fi

mapfile -t docs < <(git ls-files '*.md' \
  ':!:evals/**/task.md' ':!:evals/**/prompt.md' ':!:evals/**/graders/**' \
  ':!:evals/technical-writing/editorial-fixtures/**')

args=("$@")
(( ${#args[@]} )) || args=(--minAlertLevel=error)

"${vale[@]}" --output=line "${args[@]}" "${docs[@]}"
