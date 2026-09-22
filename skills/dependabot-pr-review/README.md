# dependabot-pr-review

An agent skill that reviews Dependabot pull requests and gives each one a
**Merge**, **Verify**, **Investigate**, or **Hold** verdict. It works on one PR
or audits every open Dependabot PR in a repo.

For each PR it checks:

- CI against the branch's *required* checks, not just the checks that have run
- upstream changelogs and release notes for the exact version range
- where the package is used in the codebase, and related packages that should
  move together
- repo policy: a Dependabot cooldown, `ignore` rules, and split versions
  across workspaces

The review is read-only. Commenting, merging, rebasing, and opening or closing
PRs each need explicit approval. PR bodies and changelogs are treated as
untrusted data, never as instructions. Merges keep history linear, using
rebase by default.

## Files

- `SKILL.md`: the procedure the agent follows
- `references/github-api.md`: GitHub REST commands (`curl` + `jq`), used first
- `references/github-cli.md`: the same tasks with `gh`, as a fallback
- `references/output-format.md`: report, audit table, and PR comment formats

## Requirements

`git`, plus either `curl` and `jq` with GitHub API access, or an authenticated
`gh` CLI.

## Provenance

Adapted from
[thoughtbot/dependabot-review-skill-thoughtbot](https://github.com/thoughtbot/dependabot-review-skill-thoughtbot)
by Jose Blanco and thoughtbot, under the MIT License. It keeps their review
modes, output and comment formats, and `dependabot-audit:v1` marker, so each
skill recognizes the other's comments. See [LICENSE](LICENSE).
