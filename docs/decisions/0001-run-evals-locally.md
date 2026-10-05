# 0001. Run skill evals locally on a subscription, not in CI

- **Status:** Accepted
- **Decided by:** @huwd
- **Decided:** 2026-10-05
- **Recorded:** 2026-10-05
- **Discussion:** #10

## Summary

In the context of a public side-project repository whose skills are tested
with `claude plugin eval`, facing eval runs that each start a full agent
session and so cost model usage, the decision was to run the evals
locally on the maintainer's Claude subscription before merging skill
changes, and against running them in CI with an API key, a subscription
token or a self-hosted runner, to avoid API charges and keep credentials
out of CI, accepting that the evals are a habit rather than an enforced
check.

## Context

The first eval suite, for `technical-writing`, landed in October 2026.
Its graders are mechanical: regular expressions over the files the agent
changed and checks on which tools it called. Grading costs nothing.

Each run of a case, though, is a full Claude Code session doing the task
under test, and that does use a model. A full pass of the first suite is
4 cases × 3 runs × 2 arms (with and without the skill), or 24 sessions,
which `claude plugin eval` estimated at $2.68 at list price. Run locally,
those sessions use the maintainer's subscription and its usage limits.
Run in CI, they need credentials of their own.

This is a public side project. Paying per token for every pull request
isn't wanted. The repository is also public, so any workflow holding
credentials needs care about what can trigger it.

Two practical unknowns also weigh on CI. On NixOS the eval sandbox resets
`PATH`, which the suite works around. GitHub's Ubuntu runners may block
the `bubblewrap` sandbox that shell-using evals need, which hasn't been
tested.

## Options considered

### Run locally on the subscription (chosen)

Run `evals/technical-writing/run.sh` before merging a change to a skill,
and paste the score table into the pull request. CI keeps running the
checks that need no model: skill validation, Markdown lint, shellcheck,
secret scanning and workflow audits.

No API charges and no credentials in CI. The cost is that nothing
enforces it: a skill change could merge without its evals being run.

### CI with an Anthropic API key

A repository secret and an eval job on pull requests. Fully automatic,
but billed per token on every run, which is what this decision avoids.

### CI with a subscription token, run on demand

`claude setup-token` creates a long-lived token tied to the subscription,
which a workflow could use, triggered only by hand or on pushes to
`main`, never by pull requests from forks. No API charges, but it puts a
credential for a personal subscription into CI, the plan's terms on
automated use need checking, and the runner sandbox is untested. It
remains the most likely next step if running locally proves too easy to
forget.

### A self-hosted runner on the maintainer's machine

Uses the existing login with no new credentials in GitHub. For a public
repository, it means code from pull requests could run on a personal
laptop, which is a security risk not worth taking for a side project.

## Decision

Skill evals run locally, on the maintainer's subscription, with each
suite's `run.sh`. Changes to a skill, its references or its evals are
evaluated before merging, and the pull request includes the resulting
score table. CI doesn't run evals and holds no model credentials.

Quick iterations can use `--runs 1 --ablation none`. A full run, with
three runs per case and the no-skill baseline, is for the last change
before merging.

## Consequences

- No API charges, and no model credentials stored in GitHub.
- Running the evals is a habit, not a gate. A pull request that changes a
  skill without a score table is the signal to ask for one.
- Results depend on the local machine's tools and Claude Code version.
  The score table should name the Claude Code version it ran on.
- Revisit if evals get skipped in practice, if more people contribute, or
  if the sandbox is shown to work on GitHub's runners. The on-demand
  subscription-token option is the likely successor, and adopting it
  means a new record that supersedes this one.
