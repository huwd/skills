#!/usr/bin/env bash
# Keep this repository's GitHub rulesets in step with .github/rulesets/*.json.
#
#   .github/scripts/rulesets.sh check   # read-only: report drift, exit 1 if any
#   .github/scripts/rulesets.sh apply   # update GitHub from the JSON (admin)
#
# Needs gh and jq. `check` works with any token, or none, on a public
# repository; GitHub only shows bypass_actors to admins, so `check` compares
# that field only when the live ruleset includes it. `apply` needs a gh login
# with admin rights on the repository, and asks before changing anything.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

repo="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"
dir=.github/rulesets

# Canonical form for comparison: only the fields we manage, keys sorted,
# rules sorted by type and required checks by name.
normalise() {
  jq -S '
    {name, target, enforcement, conditions, rules, bypass_actors}
    | with_entries(select(.value != null))
    | .rules |= (map(
        if .type == "required_status_checks"
        then .parameters.required_status_checks |= sort_by(.context)
        else . end) | sort_by(.type))
  '
}

# Live rulesets as "id<TAB>name" lines. Callers assign the output to a
# variable on its own line, so a failure here stops the script (set -e)
# rather than reporting every ruleset as missing.
live_ids() {
  gh api "repos/$repo/rulesets?includes_parents=false" --jq '.[] | "\(.id)\t\(.name)"' || {
    echo "::error::Couldn't read rulesets for $repo; is gh logged in, or GH_TOKEN set?" >&2
    return 2
  }
}

check() {
  local status=0 file name id live want listing
  declare -A seen=()
  listing="$(live_ids)"
  while IFS=$'\t' read -r id name; do
    [[ -n "$name" ]] && seen["$name"]="$id"
  done <<<"$listing"

  shopt -s nullglob
  for file in "$dir"/*.json; do
    name="$(jq -r .name "$file")"
    id="${seen[$name]:-}"
    if [[ -z "$id" ]]; then
      echo "::error file=$file::Ruleset \"$name\" is defined here but not on GitHub"
      status=1
      continue
    fi
    unset "seen[$name]"

    live="$(gh api "repos/$repo/rulesets/$id" | normalise)"
    want="$(normalise < "$file")"
    if ! jq -e 'has("bypass_actors")' <<<"$live" >/dev/null; then
      want="$(jq 'del(.bypass_actors)' <<<"$want")"
    fi

    if diff -u --label "GitHub: $name" <(echo "$live") \
         --label "$file" <(echo "$want"); then
      echo "In step: $name"
    else
      echo "::error file=$file::Ruleset \"$name\" differs from GitHub (diff above)"
      status=1
    fi
  done

  for name in "${!seen[@]}"; do
    echo "::error::Ruleset \"$name\" is on GitHub but has no file in $dir"
    status=1
  done
  return "$status"
}

apply() {
  local file name id answer listing
  declare -A ids=()
  listing="$(live_ids)"
  while IFS=$'\t' read -r id name; do
    [[ -n "$name" ]] && ids["$name"]="$id"
  done <<<"$listing"

  echo "Current differences:"
  check || true
  read -r -p "Apply every file in $dir to $repo? [y/N] " answer
  [[ "$answer" == [yY] ]] || { echo "Nothing changed."; return 0; }

  shopt -s nullglob
  for file in "$dir"/*.json; do
    name="$(jq -r .name "$file")"
    id="${ids[$name]:-}"
    if [[ -n "$id" ]]; then
      gh api --method PUT "repos/$repo/rulesets/$id" --input "$file" --silent
      echo "Updated: $name"
    else
      gh api --method POST "repos/$repo/rulesets" --input "$file" --silent
      echo "Created: $name"
    fi
  done
  check
}

case "${1:-}" in
  check) check ;;
  apply) apply ;;
  *) echo "Usage: $0 check|apply" >&2; exit 2 ;;
esac
