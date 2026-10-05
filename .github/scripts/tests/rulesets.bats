#!/usr/bin/env bats
# rulesets.sh: `check` compares .github/rulesets/*.json with the live
# rulesets; `apply` updates GitHub from the files after asking. A fake gh
# serves live rulesets from $LIVE and records writes, so nothing reaches
# GitHub.

load helper

setup() {
  setup_repo
  copy_script rulesets.sh
  export GITHUB_REPOSITORY=owner/repo
  LIVE="$BATS_TEST_TMPDIR/live"
  mkdir -p "$LIVE" .github/rulesets
  : > "$LIVE/list"
  export LIVE

  # GET .../rulesets lists "id<TAB>name"; GET .../rulesets/ID returns
  # $LIVE/ID.json; writes are only recorded. GH_FAIL=1 fails every call.
  # The body is single-quoted on purpose: it expands when the fake runs.
  # shellcheck disable=SC2016
  fake gh '
[ "${GH_FAIL:-0}" = 1 ] && { echo "gh: HTTP 401" >&2; exit 1; }
case "$*" in
  *--method*) exit 0 ;;
  "api repos/owner/repo/rulesets?includes_parents=false"*) cat "$LIVE/list" ;;
  "api repos/owner/repo/rulesets/"*) id="${2##*/}"; cat "$LIVE/$id.json" ;;
  *) echo "unexpected gh call: $*" >&2; exit 1 ;;
esac'
}

# A ruleset with two required checks, in the given order.
ruleset() {
  jq -n --arg name "$1" --arg a "$2" --arg b "$3" '{
    name: $name, target: "branch", enforcement: "active",
    conditions: {ref_name: {include: ["~DEFAULT_BRANCH"], exclude: []}},
    rules: [
      {type: "deletion"},
      {type: "required_status_checks", parameters: {
        strict_required_status_checks_policy: false,
        required_status_checks: [{context: $a}, {context: $b}]}}
    ],
    bypass_actors: []
  }'
}

# live ID NAME [JSON]: a live ruleset, with server-only fields added.
live() {
  printf '%s\t%s\n' "$1" "$2" >> "$LIVE/list"
  jq --argjson id "$1" '. + {id: $id, source: "owner/repo", _links: {}}' > "$LIVE/$1.json"
}

@test "check passes when files and GitHub match, ignoring order and server fields" {
  ruleset "Protect main" "Lint" "Test" > .github/rulesets/protect_main.json
  ruleset "Protect main" "Test" "Lint" | jq '.rules |= reverse' | live 1 "Protect main"
  run .github/scripts/rulesets.sh check
  [ "$status" -eq 0 ]
  [[ "$output" == *"In step: Protect main"* ]]
}

@test "check reports drift with a diff" {
  ruleset "Protect main" "Lint" "Test" > .github/rulesets/protect_main.json
  ruleset "Protect main" "Lint" "Build" | live 1 "Protect main"
  run .github/scripts/rulesets.sh check
  [ "$status" -eq 1 ]
  [[ "$output" == *'differs from GitHub'* ]]
  [[ "$output" == *'"context": "Build"'* ]]
}

@test "check reports a file with no live ruleset" {
  ruleset "Protect main" "Lint" "Test" > .github/rulesets/protect_main.json
  run .github/scripts/rulesets.sh check
  [ "$status" -eq 1 ]
  [[ "$output" == *'"Protect main" is defined here but not on GitHub'* ]]
}

@test "check reports a live ruleset with no file" {
  ruleset "Protect tags" "Lint" "Test" | live 2 "Protect tags"
  run .github/scripts/rulesets.sh check
  [ "$status" -eq 1 ]
  [[ "$output" == *'"Protect tags" is on GitHub but has no file'* ]]
}

@test "check compares bypass_actors only when GitHub shows them" {
  ruleset "Protect main" "Lint" "Test" \
    | jq '.bypass_actors = [{actor_id: 5, actor_type: "RepositoryRole", bypass_mode: "always"}]' \
    > .github/rulesets/protect_main.json

  # Without admin rights GitHub omits the field: nothing to compare.
  ruleset "Protect main" "Lint" "Test" | jq 'del(.bypass_actors)' | live 1 "Protect main"
  run .github/scripts/rulesets.sh check
  [ "$status" -eq 0 ]

  # With admin rights it's shown, and a difference is drift.
  ruleset "Protect main" "Lint" "Test" > "$BATS_TEST_TMPDIR/admin.json"
  jq '. + {id: 1}' "$BATS_TEST_TMPDIR/admin.json" > "$LIVE/1.json"
  run .github/scripts/rulesets.sh check
  [ "$status" -eq 1 ]
}

@test "check stops with an error when GitHub can't be read" {
  ruleset "Protect main" "Lint" "Test" > .github/rulesets/protect_main.json
  GH_FAIL=1 run .github/scripts/rulesets.sh check
  [ "$status" -eq 2 ]
  [[ "$output" == *"Couldn't read rulesets for owner/repo"* ]]
  [[ "$output" != *"not on GitHub"* ]]
}

@test "apply changes nothing unless confirmed" {
  ruleset "Protect main" "Lint" "Test" > .github/rulesets/protect_main.json
  ruleset "Protect main" "Lint" "Build" | live 1 "Protect main"
  run .github/scripts/rulesets.sh apply <<<"n"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Nothing changed."* ]]
  not_called '--method'
}

@test "apply updates existing rulesets and creates new ones" {
  ruleset "Protect main" "Lint" "Test" > .github/rulesets/protect_main.json
  ruleset "Protect tags" "Lint" "Test" > .github/rulesets/protect_tags.json
  ruleset "Protect main" "Lint" "Build" | live 7 "Protect main"
  run .github/scripts/rulesets.sh apply <<<"y"
  called '^gh api --method PUT repos/owner/repo/rulesets/7 --input \.github/rulesets/protect_main\.json'
  called '^gh api --method POST repos/owner/repo/rulesets --input \.github/rulesets/protect_tags\.json'
  not_called 'PUT .*protect_tags|POST .*protect_main'
}

@test "rejects an unknown command" {
  run .github/scripts/rulesets.sh deploy
  [ "$status" -eq 2 ]
  [[ "$output" == *"Usage:"* ]]
}
