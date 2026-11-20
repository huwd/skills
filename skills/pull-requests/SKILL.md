---
name: pull-requests
description: >-
  Prepare a branch for human review: measure the change against a
  reviewer's time budget, recommend splitting it when one review cannot
  cover it, and write a pull request description that estimates review
  time and tells the reviewer where to look closely and what they can
  check quickly. Opens or edits the pull request only with approval. Use
  when asked to write, draft or improve a PR description, open a PR, or
  judge whether a branch is too big to review. Explaining what a branch
  does is not this workflow.
metadata:
  version: "0.1.0"
---

# Pull requests for human review

A reviewer finds problems at roughly 200 to 400 changed lines an hour, for
up to about an hour at a time. Beyond that they find markedly fewer. Plan
the pull request around that budget: count the lines that need judgement,
estimate the time, and give the reviewer a route through the rest.
[references/review-budget.md](references/review-budget.md) holds the
evidence and its limits; read it when someone questions the figures.

## Measure the change

Find the base branch from repository instructions or the remote's default
branch, then read the whole change: `git log --format='%h %s%n%b' BASE..`,
`git diff --stat BASE...` and `git diff --numstat BASE...`. Read the
commit messages; they often say how a mechanical change was made.

Sort every changed file into one of three parts:

- **Core:** changes that need a reviewer's judgement, such as behaviour,
  interfaces, security, data handling and their tests.
- **Mechanical:** renames, moves, reformatting and other changes produced
  by a command or tool, where checking one example and re-running or
  diffing the rest is enough. Confirm a claimed mechanical change
  yourself, for example with `git diff -w`, `--word-diff` or
  `--color-moved`, before calling it mechanical.
- **Generated:** lockfiles, generated code, vendored code and snapshots
  that nobody reads line by line. Name what checks them instead, such as
  the command that regenerates them or the CI job that uses them.

A file can hold more than one part: count each commit or hunk where it
belongs. Line count is a proxy. A one-line change to a shared interface,
build file or configuration can affect the whole system; put it in the
core and say why.

## Estimate review time

Estimate core review time at 300 changed lines an hour, giving a range of
200 to 400. Add a few minutes for sampling each mechanical part. Generated
parts take no review time. Present the result as an estimate with its
basis, never as a measurement.

| Core changed lines | Review | Action |
| ------------------ | ------ | ------ |
| up to about 400 | one session | describe it |
| about 400 to 800 | two sessions | describe it with a reading order and a natural place to stop |
| over about 800, or several independent core concerns | three or more hours | recommend splitting before the PR is opened |
| over 2,000 | not credible as one review | say so plainly, and recommend splitting |

Only core lines and core concerns count. Mechanical and generated parts
riding along with a small core change are cheap to review with a good
guide; you can mention moving them to their own pull request as an
option, but do not recommend a split for them.

Give a split recommendation to the author in your reply, not in the
description: the reviewer reviews the pull request as it is. Propose the
pull requests by concern, using existing commit boundaries where they fit,
with each one's size and estimate, and an order in which they can merge.
Write the description for the branch as it stands unless the user chooses
to split. Do not rewrite, move or push commits to make the split without
separate authorisation.

## Write the description

Follow the repository's pull request template if it has one, in
`.github/` or `docs/`, adding the size and review sections where the
template allows. Otherwise start from
[assets/pr-body.md](assets/pr-body.md).

- Open with what changes and why, for someone who has not seen the work.
- Give the size and review time per part, with the estimate's basis.
- Order the reading guide by risk: core files first, then the sample to
  check from each mechanical part with the command that verifies the rest,
  then the generated parts and what covers them. Reviewers comment less on
  files they reach last.
- Point at where the risk is and what to check, not at why the code is
  right. A description that argues correctness can make a reviewer look
  less hard.
- Report tests and checks only as observed, saying what ran.

Scale the description to the change, and keep it short enough to read in a
few minutes: it is a route through the diff, not a second copy of it. A
small change with no mechanical or generated parts needs a few sentences
and one line of size and time, not the full template. Give each
verification as a command of a line or two, such as the recorded command
or a diff option, rather than a script. Detail about how the work was done
belongs in the commit messages.

## Act within authorisation

Writing a description to a file or the reply is local. Pushing a branch,
running `gh pr create`, editing an existing pull request and requesting
reviewers are outward-facing: show the description and ask before doing
them, unless the user has already asked for that action. Pass the body
with `--body-file` rather than on the command line.
