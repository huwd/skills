# Evaluation of the pull-requests skill

This report is for contributors deciding whether `pull-requests` 0.1.0
improves pull request descriptions enough to merge. It compares the skill
with no skill on the same offline fixtures. The
[research note](code-review-size-research.md) records the review budget
the skill applies, and the [eval suite](../evals/pull-requests/README.md)
defines the cases.

## Result

With the skill, every run of every case passed every check. Without it,
descriptions summarised the change well but gave a reviewer no time
estimate, no route through the diff and, for a 1,787-line branch, no
advice to split it.

| Case | With skill | Without skill |
| ---- | ---------- | ------------- |
| `large-mixed` | 1.00, 1.00, 1.00 | 0.38, 0.38, 0.38 |
| `oversized` | 1.00, 1.00, 1.00 | 0.60, 0.60, 0.60 |
| `small-fix` | 1.00, 1.00, 1.00 | 1.00, 1.00, 1.00 |
| `explain-branch` | 1.00, 1.00, 1.00 | 1.00, 1.00, 1.00 |

Scores are the fraction of a case's checks passed, excluding the skill
selection diagnostic. The skill loaded in every `large-mixed`, `oversized`
and `small-fix` run, and in no `explain-branch` run.

## Method

- Skill: `pull-requests` 0.1.0, as committed with this report. The runs
  used a temporary snapshot commit with identical skill files.
- Harness: Codex CLI 0.167.1, through `evals/run-codex.py`.
- Model: `gpt-6.1-sol`, medium reasoning effort.
- Runs: three per arm per case, on 17 and 20 November 2026.
- Environment: no network and a read-only `.git`.

## What the baseline did

In `large-mixed`, every baseline run wrote an accurate summary in commit
order: rename, lockfile, reformat, then the rounding change. None gave a
review time, separated the 58 core lines from the 2,204 changed in all,
named the core files before the lockfile, said how to verify the rename,
or said the lockfile need not be read.

In `oversized`, every run described the three features and their tests
and none estimated review time or suggested splitting. Against an earlier
version of the fixture, the baseline noticed that the generated functions
were identical apart from their names. The fixture was changed so that
each function has different logic before the results reported here.

The baseline kept `small-fix` descriptions short, between 61 and 85 words,
and wrote nothing for `explain-branch`. Neither case shows a need for the
skill; both check that it does no harm.

## What the skill changed

In `large-mixed`, descriptions had a size table separating core,
mechanical and generated parts, an estimate of 12 to 15 minutes for
the core, and a numbered reading guide starting with `rounding.py` and
`invoice.py`. They gave `git show --word-diff` or the recorded `sed`
command for the rename, and said `uv.lock` was regenerated and need not
be read line by line.

In `oversized`, every run estimated about six hours and recommended three
pull requests, one per feature, with sizes and a merge order. Descriptions
gave stopping points within and between modules.

`small-fix` descriptions stayed between 91 and 113 words, with a one-line
size and time.

## Changes during evaluation

The first draft recommended splitting `large-mixed` into four pull
requests, because it counted the rename and the lockfile as separate
concerns, and put that advice in the description. Its descriptions ran to
about 1,000 words and included a 20-line verification script. The skill
now counts only core concerns towards a split, gives split advice to the
author rather than the reviewer, and asks for short verification commands.
Descriptions fell to about 500 words.

Two graders were corrected after the second run, and every saved run in
both arms was re-scored:

- `split-proposed` matched "split" but not "splitting".
- `core-first` compared first mentions anywhere in the description, so a
  summary naming `uv.lock` failed a description whose reading guide put
  the core first. It now reads only list items.

Neither correction changed a baseline score.

## Limits

- The description checks are patterns. `review-estimate` does not judge
  whether an estimate is sensible, and `split-proposed` does not judge the
  proposed groups. The descriptions were read by hand for this report.
- Three runs per arm on one model is a small sample.
- The fixtures are synthetic Python, without a pull request template, a
  remote or an existing pull request. Opening a pull request, and asking
  for approval first, are not tested.
- The review budget itself rests on the evidence and limits in the
  research note.
