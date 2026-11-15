# 0005. Check prose with Vale from a Nix flake, before push and in CI

- **Status:** Proposed
- **Decided by:**
- **Decided:**
- **Recorded:** 2026-11-15
- **Discussion:** #38

## Summary

In the context of a catalogue whose Markdown is checked by markdownlint but
not for spelling, facing British spelling errors and Americanisms that
reach `main` unnoticed, the decision was for Vale, bundled with its styles
and an en_GB dictionary by a Nix flake, run by one script before push and
as a required CI check, and against installing Vale and its dictionary
separately for each environment or running it only by hand, to achieve the
same versions and configuration locally and in CI, accepting that the
check needs Nix.

## Context

Vale was not part of the repository's tooling. The technical-writing skill
ships a generic Vale layer for other repositories, but this repository had
no configuration of its own, and no development environment: the README
asked contributors to install uv, jq, shellcheck and Go themselves.

British spelling needs an `-ise` en_GB Hunspell dictionary in Vale's styles
directory. Ubuntu's packages and Vale's own install do not provide one in
that place, and a second copy for CI could drift from the one used locally.

The first run, before any changes, reported 621 errors. Almost all were
project vocabulary and possessives the dictionary rejects; the rest were
American spellings in dependabot-pr-review. It also showed that the
generic vocabulary's acronym-plural pattern made `Vale.Terms` flag nearly
every word ending in "s", a fault in the skill itself.

## Options considered

### Nix flake, shared script, pre-push and CI (chosen)

`flake.nix` provides `nix run .#vale`, which bundles Vale, write-good,
proselint, the repository's `.vale/styles`, technical-writing's Generic
vocabulary and the dictionary, following the wrapper in
[huwd/declarative_laptop](https://github.com/huwd/declarative_laptop). Its
dev shell also provides every tool the other hooks need.
`.github/scripts/check-prose.sh` runs it for pre-commit and CI alike.
`flake.lock` pins the versions for both.

### Install Vale and a dictionary separately in each environment

A release binary in CI, as for gitleaks, plus a dictionary download, and a
local install documented in the README. It avoids Nix, but needs two setups
to stay in step, and contributors still install everything by hand.

### Run Vale by hand only

The status quo. It costs nothing to set up, and is the reason errors reach
`main`.

## Decision

`.vale.ini` configures Vale for the repository's Markdown, except eval
inputs: task and prompt files, graders and the editorial fixtures. The
`Check prose` CI job runs `.github/scripts/check-prose.sh` on every pull
request and push to `main`, and is a required status check. Pre-commit
runs the same script before push. Errors fail; warnings and suggestions
are reported as advice.

## Consequences

- One command, `nix develop`, gives a working setup for every hook.
- The check needs Nix. Without it, the script stops and says so; CI
  installs Nix with `cachix/install-nix-action`.
- Dependabot updates the action, but not `flake.lock`. Update Vale and the
  other dev shell tools by hand with `nix flake update`, checking the
  resulting versions are settled.
- New project terms need a vocabulary entry in
  `.vale/styles/config/vocabularies/Skills/accept.txt`. A misspelling is
  fixed, never added.
- The repository now checks itself with technical-writing's own generic
  vocabulary, so faults in it surface here first.
