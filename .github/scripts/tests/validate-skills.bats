#!/usr/bin/env bats
# validate-skills.sh: runs skills-ref on each skill, then skill-validator on
# skills/, failing on errors but not on skill-validator's warnings.

load helper

setup() {
  setup_repo
  copy_script validate-skills.sh
  add_skill alpha
  add_skill beta
  fake uvx 'exit 0'
  fake skill-validator 'exit 0'
}

@test "passes when every check passes" {
  run .github/scripts/validate-skills.sh
  [ "$status" -eq 0 ]
  called 'uvx .*agentskills validate skills/alpha/'
  called 'uvx .*agentskills validate skills/beta/'
  called '^skill-validator check .*skills/$'
}

@test "passes when skill-validator only warns (exit 2)" {
  fake skill-validator 'exit 2'
  run .github/scripts/validate-skills.sh
  [ "$status" -eq 0 ]
}

@test "fails when skill-validator finds errors (exit 1)" {
  fake skill-validator 'exit 1'
  run .github/scripts/validate-skills.sh
  [ "$status" -eq 1 ]
}

@test "fails when one skill breaks the spec, and still checks the rest" {
  fake uvx 'case "$*" in *skills/alpha/*) exit 1 ;; esac'
  run .github/scripts/validate-skills.sh
  [ "$status" -eq 1 ]
  called 'agentskills validate skills/beta/'
  called '^skill-validator '
}

@test "fails loudly when no skills are found" {
  rm -r skills
  run .github/scripts/validate-skills.sh
  [ "$status" -eq 1 ]
  [[ "$output" == *"No skills found"* ]]
  [ ! -s "$CALLS" ]
}

@test "adds GitHub annotations only when running in Actions" {
  run .github/scripts/validate-skills.sh
  not_called '--emit-annotations'

  GITHUB_ACTIONS=true run .github/scripts/validate-skills.sh
  called '^skill-validator check --emit-annotations '
}
