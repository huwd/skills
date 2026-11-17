#!/usr/bin/env bash
# Check workflow pins against their upstream release tags.
#
# For every `uses: OWNER/REPO[/PATH]@REF` in the given workflow files
# (default: .github/workflows/*.yml and *.yaml):
#
# - a 40-character SHA must carry a `# TAG` comment, and the tag must
#   resolve to that commit through the GitHub API;
# - any other ref must be a full version tag (vX.Y.Z) covered by
#   .github/workflows/actions.lock; reusable workflow calls, which the
#   lockfile does not lock, must use a SHA;
# - local (./) and docker:// references are skipped.
#
# Prints one tab-separated line per pin: status, target, pinned tag and its
# release date, latest release and its date. A release newer than the pin
# is information, not a failure: a Dependabot cooldown waits for it on
# purpose. Exits 1 if any pin is wrong or unverified.
#
# Needs gh, authenticated or with GH_TOKEN set. Read-only.
set -euo pipefail

if (( $# == 0 )); then
  shopt -s nullglob
  set -- .github/workflows/*.yml .github/workflows/*.yaml
fi
if (( $# == 0 )); then
  echo "verify-pins: no workflow files found" >&2
  exit 1
fi

lockfile=.github/workflows/actions.lock
status=0
seen=$'\n'

release_date() { # repo tag -> publication date, or "-" when the tag has no release
  gh api "repos/$1/releases/tags/$2" --jq .published_at 2>/dev/null || echo "-"
}

latest_release() { # repo -> "tag<TAB>date", or "-<TAB>-"
  gh api "repos/$1/releases/latest" --jq '.tag_name + "\t" + .published_at' 2>/dev/null \
    || printf -- '-\t-\n'
}

# `uses: TARGET # TAG`, optionally quoted: group 1 is TARGET, group 3 is TAG.
q="['\"]?"
uses_re="^[[:space:]]*-?[[:space:]]*uses:[[:space:]]*${q}"
uses_re+="([^[:space:]'\"#]+)${q}"
uses_re+="[[:space:]]*(#[[:space:]]*([^[:space:]]+))?"

printf 'STATUS\tTARGET\tPINNED\tPINNED_DATE\tLATEST\tLATEST_DATE\n'
while IFS= read -r line; do
  [[ $line =~ $uses_re ]] || continue
  target=${BASH_REMATCH[1]}
  comment=${BASH_REMATCH[3]:-}
  [[ $target == ./* || $target == docker://* || $target == '$/'* || $target != *@* ]] && continue
  [[ $seen == *$'\n'"$target $comment"$'\n'* ]] && continue
  seen+="$target $comment"$'\n'
  name=${target%@*}
  ref=${target##*@}
  repo=$(cut -d/ -f1-2 <<<"$name")
  latest=$(latest_release "$repo")

  if [[ $ref =~ ^[0-9a-f]{40}$ ]]; then
    if [[ -z $comment ]]; then
      printf 'NO-TAG\t%s\t-\t-\t%s\n' "$target" "$latest"
      status=1
      continue
    fi
    if ! resolved=$(gh api "repos/$repo/commits/$comment" --jq .sha 2>/dev/null); then
      printf 'UNRESOLVED\t%s\t%s\t-\t%s\n' "$target" "$comment" "$latest"
      status=1
      continue
    fi
    if [[ $resolved != "$ref" ]]; then
      printf 'MISMATCH\t%s\t%s (is %s)\t%s\t%s\n' "$target" "$comment" "$resolved" \
        "$(release_date "$repo" "$comment")" "$latest"
      status=1
      continue
    fi
    printf 'OK\t%s\t%s\t%s\t%s\n' "$target" "$comment" "$(release_date "$repo" "$comment")" "$latest"
  elif [[ $name == */.github/workflows/* ]]; then
    printf 'UNPINNED\t%s\t%s\t-\t%s\n' "$target" "$ref" "$latest"
    status=1
  elif [[ -f $lockfile ]] && grep -qF "'$target':" "$lockfile" \
    && ! [[ $ref =~ ^v?[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    # Locked, but to a branch or partial tag that can move. zizmor's ref-pin
    # policy accepts these, so this job is what catches them.
    printf 'FLOATING\t%s\t%s\t-\t%s\n' "$target" "$ref" "$latest"
    status=1
  elif [[ -f $lockfile ]] && grep -qF "'$target':" "$lockfile"; then
    printf 'LOCKED\t%s\t%s\t%s\t%s\n' "$target" "$ref" "$(release_date "$repo" "$ref")" "$latest"
  else
    printf 'UNPINNED\t%s\t%s\t-\t%s\n' "$target" "$ref" "$latest"
    status=1
  fi
done < <(cat -- "$@")

exit "$status"
