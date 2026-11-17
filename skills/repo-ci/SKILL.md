---
name: repo-ci
description: >-
  Set up or update GitHub Actions CI for a repository the same way each
  time: read-only workflows with one job per check, every action locked to
  a commit verified against its upstream release tag, a verify job, and
  Dependabot with a cooldown. Also checks an existing workflow's action pins
  and reports mismatches and release dates. Use when asked to add, set up,
  copy or harden CI or Dependabot, or to check whether action pins are
  right. Explaining an existing workflow does not start this workflow.
compatibility: >-
  GitHub Actions on github.com or GHE.com. Needs an authenticated gh with
  the github/gh-actions-lock extension, and `actionlint` with `shellcheck`.
  Falls back to SHA pins where the extension is unavailable.
metadata:
  version: "0.1.0"
---

# Repository CI

Pins decide which code runs with the repository's token. A commit SHA
copied from another repository's workflow, or recalled from memory, can be
wrong while its version comment looks right. Every commit this skill
writes or accepts is resolved from the upstream release tag at the time of
the change, never taken from another workflow, a template or memory.

Writing files is local. Pushing, opening a pull request and changing
repository settings or rulesets are outward actions: ask before each one.

## Choose the task

| Request | Do | Change files |
| ------- | -- | ------------ |
| Set up or update CI or Dependabot | [Set up CI](#set-up-ci) | Yes |
| Check whether pins are right | [Check pins](#check-pins) | No, unless asked |

## Set up CI

### 1. Learn the repository

Read the existing workflows, `.github/dependabot.yml`, any rulesets, and
how contributors run checks: `Makefile` targets, package scripts, pre-commit,
`CONTRIBUTING.md`. CI runs the same commands, so a check passes locally and
in CI for the same reasons. Note each package ecosystem the repository
uses, from its manifests and lockfiles.

Treat any workflow you are given to start from as a list of checks to run,
not as a source of pins. Record each pin it carries; you will report the
ones that do not match their tag.

Check the lockfile tool is available:

```sh
gh extension list | grep -q gh-actions-lock || gh extension install github/gh-actions-lock
gh actions-lock --help
```

GitHub Enterprise Server does not support the lockfile. There, or if the
extension cannot be installed, pin every action as in step 4 instead and
say so in the report.

### 2. Write the workflows

Start from [assets/ci.yml](assets/ci.yml). Keep:

- `permissions: contents: read` at the top. Grant more to one job only, and
  only what it needs.
- `persist-credentials: false` on every `actions/checkout`, so the token
  is not left in `.git/config` for later steps.
- One job per check, each with a stable `name:`. Rulesets require checks
  by job name.
- No `on: paths:` filters on a job that may become required.

Quote shell expansions in `run:` steps. Prefer
`git ls-files -z '*.sh' | xargs -0 -r shellcheck` to an unquoted
`$(find ...)`, which breaks on spaces and runs on untracked files.

### 3. Resolve versions and lock them

For each action, look up its latest release and its date:

```sh
gh api repos/OWNER/REPO/releases/latest --jq '.tag_name + " " + .published_at'
```

Write `uses: OWNER/REPO@TAG` with that full tag, then lock every workflow:

```sh
gh actions-lock
```

This writes `.github/workflows/actions.lock` with each direct and
transitive action's commit and repository IDs. It also narrows partial
tags such as `@v7` to the full tag. Never edit the lockfile by hand. Do
not pass `--accept-moved` to clear a `ref-moved` error; report it, since a
moved tag needs explaining. For a `local-action` error, read
`gh actions-lock --help` and choose between `--migrate-local-actions` and
`--ignore-local-actions` with the user.

### 4. Pin what the lockfile does not cover

The lockfile does not lock reusable workflows called at `jobs.<id>.uses`
or container images. Pin a reusable workflow to the commit its tag
resolves to now:

```sh
gh api repos/OWNER/REPO/commits/TAG --jq .sha
```

Write `uses: OWNER/REPO/.github/workflows/FILE.yml@SHA # TAG`, with the
full tag in the comment. Pin container images by `@sha256:` digest.

### 5. Add the verify job

Copy [assets/verify-pins.yml](assets/verify-pins.yml) to
`.github/workflows/` and [scripts/verify-pins.sh](scripts/verify-pins.sh)
to `.github/scripts/verify-pins.sh`, keeping it executable. Pin the
extension in the workflow to its latest release:

```sh
gh api repos/github/gh-actions-lock/releases/latest --jq .tag_name
```

Run `gh actions-lock` again so the verify workflow is locked too.

The verify job fails on a locked ref that is not a full version tag, such
as `@main` or `@v7`, since a lockfile cannot detect a floating ref moved
back to an older commit.

If the repository runs zizmor, copy [assets/zizmor.yml](assets/zizmor.yml)
to the repository root, or merge its `unpinned-uses` rule into an existing
zizmor configuration. zizmor does not read the lockfile and would report
every locked tag as unpinned. The verify job covers what the relaxed rule
no longer checks; keep the file's comment so the reason travels with it.

### 6. Configure Dependabot

Start from [assets/dependabot.yml](assets/dependabot.yml). Keep
`github-actions`, and add one entry for each ecosystem from step 1, using
Dependabot's name for it: `uv` for `uv.lock`, `pip` for requirements files
or Poetry, `npm`, `bundler`, `cargo`, `gomod`, `docker`, `pre-commit`.
Keep any existing schedule and cooldown that is weekly or slower; otherwise
use weekly with a seven-day cooldown.

Dependabot updates `actions.lock` in the same pull request as the workflow.
Tools installed by version inside `run:` steps are invisible to it; list
them in a comment in `dependabot.yml` so they are bumped by hand.

### 7. Run the checks locally

Run what the tools allow, and report anything you could not run and why:

```sh
actionlint
gh actions-lock --verify
.github/scripts/verify-pins.sh
```

`actionlint` checks `run:` scripts only when `shellcheck` is installed.
Run `zizmor --offline .` too if it is available. Then run each job's
commands as the job runs them.

### 8. Report, and leave required checks for later

Report the files changed, the checks run and their results, and a pin
table: each action, its tag, the tag's release date, and the latest release
and its date. List every pin from the source material that did not match
its tag, with the tag's actual commit.

Do not add required status checks. A required check that has never
reported blocks every merge. Name the jobs to add to the ruleset as a
follow-up, once they have reported on the default branch.

## Check pins

Do not change files unless asked. From the repository root, run this
skill's [scripts/verify-pins.sh](scripts/verify-pins.sh), or the copy in
`.github/scripts/` if the repository has one. It reads the workflows and
calls the GitHub API; it writes nothing. If the repository has a lockfile,
also run `gh actions-lock --no-fix`. Without the script,
resolve each pin's tag with `gh api repos/OWNER/REPO/commits/TAG --jq .sha`
and compare.

The script prints a status per pin: `OK`, `LOCKED`, `MISMATCH` with the
tag's actual commit, `NO-TAG` for a SHA without a version comment,
`FLOATING` for a locked branch or partial tag, `UNPINNED`, or
`UNRESOLVED`. It exits 1 if any pin is not `OK` or `LOCKED`.

A newer release is not a fault. Compare its date with the Dependabot
cooldown for that ecosystem: a release inside the cooldown is a deliberate
wait. Report it as pending, not as stale. Report a pin as behind only when
its newer release is older than the cooldown and no Dependabot pull request
is open for it.

Offer fixes with the commands from [Set up CI](#set-up-ci), and apply them
only once the user agrees.
