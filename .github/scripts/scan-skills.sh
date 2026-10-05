#!/usr/bin/env bash
# Scan every skill under skills/ with NVIDIA SkillSpector in static mode
# (no model, no API key). Run by CI and by pre-commit.
#
# Any finding not accepted in .github/skillspector/<skill>.yaml fails. The
# risk score alone isn't used: a single HIGH finding, such as reading
# ~/.ssh keys, can score under its default threshold of 50.
# Needs uv on PATH.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# SkillSpector v2.12.0. Bump deliberately, then re-review the baselines.
version=c7958a3268d9498644b22edb75d0f051bbc8cbfc

shopt -s nullglob
skills=(skills/*/)
if (( ${#skills[@]} == 0 )); then
  echo "::error::No skills found under skills/; discovery is broken" >&2
  exit 1
fi

status=0
for skill in "${skills[@]}"; do
  name="$(basename "$skill")"
  args=(scan "$skill" --no-llm --fail-on-findings)
  baseline=".github/skillspector/$name.yaml"
  if [[ -f "$baseline" ]]; then args+=(--baseline "$baseline"); fi

  echo "== $name"
  uvx --quiet --from "git+https://github.com/NVIDIA/skillspector.git@$version" \
    skillspector "${args[@]}" || status=1
done

exit "$status"
