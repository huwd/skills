# 0003. Keep the repository's rulesets as code, applied by hand

- **Status:** Accepted
- **Decided by:** @huwd
- **Decided:** 2026-10-05
- **Recorded:** 2026-10-12
- **Discussion:** #12

## Summary

In the context of a repository whose branch protection and required
checks were changed through GitHub's settings pages and the API, facing
settings that had no history and no review, the decision was for JSON
rulesets in `.github/rulesets/`, applied by a maintainer with a script
after merging and checked for drift by a read-only workflow, and against
leaving them in the settings pages or applying them automatically from
CI, to achieve reviewed, versioned repository settings, accepting a
manual step after each change.

## Context

By October 2026 this repository had two rulesets, "Protect main" and
"Prevent tag deletion", first imported from the huwd/standards templates.
Their required status checks had already changed once, through the API,
and were about to change again as new CI jobs arrived. Nothing recorded
what the settings were meant to be, or when and why they changed.

[govuk-one-login/account-interventions-service](https://github.com/govuk-one-login/account-interventions-service/tree/main/.github/rulesets)
keeps its rulesets as JSON, applied by hand with `curl` and a personal
access token, with no check that the live settings still match.

Applying a ruleset needs admin rights on the repository. Since
[0002](0002-static-checks-in-ci.md), CI holds no credentials beyond its
own read-only token.

## Options considered

### JSON files, applied by hand, with a drift check (chosen)

The rulesets live as JSON. `.github/scripts/rulesets.sh check` compares
them with GitHub, read-only; `.github/scripts/rulesets.sh apply` updates
GitHub from them, using the maintainer's own `gh` login, after showing
the diff and asking. A Rulesets workflow runs `check` on every push to
`main` and weekly.

Changes are reviewed like code, and admin rights never leave the
maintainer's machine. The cost is a manual `apply` after each merge, and
a window in which `main` and GitHub differ; the workflow fails during that
window, as a reminder.

### Leave them in GitHub's settings pages

No files and no scripts, but no history, no review, and no way to tell
whether a setting was deliberate.

### Apply automatically from CI on merge

No manual step, but CI would need a token with admin rights on the
repository, which anything able to change a workflow could use. That
contradicts [0002](0002-static-checks-in-ci.md).

### Terraform, or a settings app such as safe-settings

Built for managing many repositories. For two rulesets in one
repository, they add a tool, state and credentials to look after.

## Decision

The repository's rulesets are defined in `.github/rulesets/*.json`, one
file per ruleset, and changed only through pull requests. After a change
merges, a maintainer with admin rights runs
`.github/scripts/rulesets.sh apply`. The Rulesets workflow reports drift
on pushes to `main` and weekly, and isn't a required check.

## Consequences

- Every change to branch protection and required checks has a pull
  request and a commit explaining it.
- Changes made in GitHub's settings pages show up as drift within a week,
  to be copied into the JSON or undone.
- A new required check is applied only once the job that reports it is on
  `main`, or every open pull request waits for a check that never runs.
- GitHub shows `bypass_actors` only to admins, so the workflow can't
  check that field; a local `check` with an admin login can.
