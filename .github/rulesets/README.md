# Rulesets

The GitHub rulesets for this repository, as JSON. These files are the
record of what the rulesets should be; GitHub's settings pages are not.
The approach follows
[govuk-one-login/account-interventions-service](https://github.com/govuk-one-login/account-interventions-service/tree/main/.github/rulesets),
with a script in place of hand-written API calls, and a drift check.

| File | Ruleset |
| ---- | ------- |
| [`protect_main.json`](protect_main.json) | Protect main: pull requests, linear history and required status checks |
| [`prevent_tag_deletion.json`](prevent_tag_deletion.json) | Prevent tag deletion |

Each file holds only the fields GitHub accepts when creating or updating a
ruleset: `name`, `target`, `enforcement`, `conditions`, `rules` and
`bypass_actors`. GitHub finds the live ruleset by `name`, so renaming one
creates a new ruleset rather than renaming the old.

## Changing a ruleset

1. Edit or add the JSON, in a pull request like any other change.
2. Merge it.
3. Apply it, with a `gh` login that has admin rights on the repository:

   ```bash
   .github/scripts/rulesets.sh apply
   ```

   This shows the differences first and asks before changing anything.

Apply after merging, not before, so that `main` stays the record. Until a
merged change is applied, the Rulesets workflow fails on `main`, which is
the reminder.

A change that makes a new status check required should be applied only
once the job that reports it is on `main`; otherwise every open pull
request waits for a check that never runs.

## Checking for drift

```bash
.github/scripts/rulesets.sh check
```

This is read-only. The Rulesets workflow runs it on every push to `main`
and weekly, to catch changes made in GitHub's settings pages. Those should
be copied back into the JSON, or undone with `apply`.

GitHub shows `bypass_actors` only to admins, so the workflow's check, which
has read access only, can't see that field. Run the check locally with an
admin login to compare it too.

## Rules that GitHub sets

Rules applied from outside the repository, such as an organisation's
rulesets, aren't listed here and aren't affected by `apply`.
