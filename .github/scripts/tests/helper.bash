# Shared setup for the .github/scripts tests.
#
# Each test gets a throwaway git repository holding a copy of the script
# under test, and a bin/ directory at the front of PATH for fake versions of
# the external tools (gh, uvx, skill-validator). Fakes record each call, one
# line per call, in $CALLS, so tests can check what would have been run
# without touching GitHub or downloading anything.

scripts_dir="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"

setup_repo() {
  REPO="$BATS_TEST_TMPDIR/repo"
  BIN="$BATS_TEST_TMPDIR/bin"
  CALLS="$BATS_TEST_TMPDIR/calls"
  mkdir -p "$REPO/.github/scripts" "$BIN"
  : > "$CALLS"
  git -C "$REPO" init -q
  export PATH="$BIN:$PATH" CALLS REPO BIN
  unset GITHUB_ACTIONS
  cd "$REPO" || return 1
}

# copy_script NAME: put the real script into the test repository.
copy_script() {
  cp "$scripts_dir/$1" "$REPO/.github/scripts/$1"
}

# add_skill NAME: a minimal skill directory.
add_skill() {
  mkdir -p "$REPO/skills/$1"
  printf -- '---\nname: %s\ndescription: Test skill.\n---\n' "$1" > "$REPO/skills/$1/SKILL.md"
}

# fake NAME BODY: a fake command that logs its arguments, then runs BODY.
fake() {
  cat > "$BIN/$1" <<FAKE
#!/usr/bin/env bash
printf '%s %s\n' "$1" "\$*" >> "\$CALLS"
$2
FAKE
  chmod +x "$BIN/$1"
}

# called PATTERN / not_called PATTERN: assert a fake was (or wasn't) called
# with arguments matching an extended regex. Use these rather than `! grep`:
# bash ignores set -e for a negated command, so `! grep` mid-test can never
# fail the test.
called() {
  grep -Eq -- "$1" "$CALLS" || {
    echo "expected a call matching: $1" >&2
    cat "$CALLS" >&2
    return 1
  }
}

not_called() {
  if grep -Eq -- "$1" "$CALLS"; then
    echo "unexpected call matching: $1" >&2
    grep -E -- "$1" "$CALLS" >&2
    return 1
  fi
}
