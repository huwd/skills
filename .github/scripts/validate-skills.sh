#!/usr/bin/env bash
# Validate every skill under skills/. Run by CI and by pre-commit.
#
# - skills-ref: the Agent Skills spec (name, description, allowed keys)
# - skill-validator: links, token budgets, unreferenced files, code fences
#
# Errors fail; skill-validator warnings are reported only (its exit 2).
# Needs uv and skill-validator on PATH.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

shopt -s nullglob
skills=(skills/*/)
if (( ${#skills[@]} == 0 )); then
  echo "::error::No skills found under skills/; discovery is broken" >&2
  exit 1
fi

status=0
for skill in "${skills[@]}"; do
  uvx --quiet --from skills-ref==0.1.1 agentskills validate "$skill" || status=1
done

annotations=()
if [[ "${GITHUB_ACTIONS:-}" == true ]]; then annotations=(--emit-annotations); fi

# assets/vale mirrors Vale's own directory layout, so its nesting is expected.
skill-validator check "${annotations[@]}" --allow-nested-paths=assets/vale skills/ \
  || { rc=$?; (( rc == 2 )) || status=1; }

exit "$status"
