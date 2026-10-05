#!/usr/bin/env bats
# scan-skills.sh: runs SkillSpector on each skill in static mode, failing on
# any finding not in that skill's baseline.

load helper

setup() {
  setup_repo
  copy_script scan-skills.sh
  add_skill alpha
  add_skill beta
  fake uvx 'exit 0'
}

@test "scans every skill in static mode, failing on any new finding" {
  run .github/scripts/scan-skills.sh
  [ "$status" -eq 0 ]
  [ "$(grep -c 'skillspector scan' "$CALLS")" -eq 2 ]
  [ "$(grep -c 'skillspector scan .* --no-llm --fail-on-findings' "$CALLS")" -eq 2 ]
}

@test "pins SkillSpector to a commit" {
  run .github/scripts/scan-skills.sh
  called 'skillspector\.git@[0-9a-f]{40} '
}

@test "passes a baseline only for skills that have one" {
  mkdir -p .github/skillspector
  touch .github/skillspector/alpha.yaml
  run .github/scripts/scan-skills.sh
  [ "$status" -eq 0 ]
  called 'scan skills/alpha/ .*--baseline \.github/skillspector/alpha\.yaml'
  not_called 'scan skills/beta/ .*--baseline'
}

@test "fails when one skill has findings, and still scans the rest" {
  fake uvx 'case "$*" in *skills/alpha/*) exit 1 ;; esac'
  run .github/scripts/scan-skills.sh
  [ "$status" -eq 1 ]
  called 'scan skills/beta/'
}

@test "fails when SkillSpector errors (exit 2)" {
  fake uvx 'exit 2'
  run .github/scripts/scan-skills.sh
  [ "$status" -eq 1 ]
}

@test "fails loudly when no skills are found" {
  rm -r skills
  run .github/scripts/scan-skills.sh
  [ "$status" -eq 1 ]
  [[ "$output" == *"No skills found"* ]]
  [ ! -s "$CALLS" ]
}
