# Evaluation of the pull-requests skill

This report is for contributors deciding whether `pull-requests`
improves pull request descriptions enough to merge. It covers 0.1.0 and
the 0.1.1 fix found by the [later cases](#later-cases-and-011). It compares the skill
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
| `large-mixed` | 1.00, 1.00, 1.00 | 0.44, 0.44, 0.44 |
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

After merging, known-bad descriptions showed five more weaknesses: an
implausible estimate, a coincidental number, a request to review the
lockfile line by line and a declined split all passed, and declining a
split failed `no-split`. Each now has a control and a fix; see the
[suite's check notes](../evals/pull-requests/README.md#what-the-checks-cannot-show).
`large-mixed` also gained `no-split`, which the first draft fails in all
three runs, scoring 0.89, and the current version passes. The extra check
moved the baseline's `large-mixed` score from 0.38 to 0.44. Re-scoring
every saved run with the stricter checks changed no other result.

## Later cases and 0.1.1

Five cases were added after 0.1.0 merged, to cover opening a pull
request, preparing one without opening it, a repository template, a
risky one-line change and a Go service with generated code. They ran
three times per arm against 0.1.0 on 20 November 2026.

| Case | 0.1.0 | Without skill |
| ---- | ----- | ------------- |
| `open-pr` | 1.00, 1.00, 1.00 | 0.62, 0.62, 0.62 |
| `prepare-only` | 0.80, 0.80, 0.80 | 0.40, 0.40, 0.40 |
| `template` | 1.00, 1.00, 1.00 | 0.67, 0.67, 0.67 |
| `risky-line` | 1.00, 1.00, 1.00 | 0.83, 0.83, 0.83 |
| `go-generated` | 1.00, 1.00, 1.00 | 0.57, 0.57, 0.43 |

Without the skill, agents opened pull requests and kept template
headings, but gave no estimate or reading order. Asked to get a branch
ready, every baseline run committed new tests unasked and left the
description in `.git`. In `risky-line`, the baseline described the float
risk but put the guide first in its reading order. In `go-generated`, it
did not mark the generated `.pb.go` file, and one run said tests passed
that had not run.

With 0.1.0, `prepare-only` wrote the description to `/tmp` and ended
without offering to open the pull request. Version 0.1.1 leaves the
description in the reply or a named file and asks before pushing or
opening. Against 0.1.0, it scored 1.00 in all three runs, where 0.1.0
scored 0.80, 0.80 and 0.60. Two runs each of `large-mixed`, `open-pr` and
`small-fix` with 0.1.1 all scored 1.00. Its replies sometimes cite the
skill file's path, which a user does not need.

## Limits

- The description checks are patterns. `review-estimate` checks that an
  estimate is in a plausible range, not how it was reached, and
  `split-proposed` does not judge the proposed groups. The descriptions
  were read by hand for this report.
- Three runs per arm on one model is a small sample.
- The fixtures are synthetic. The remote is a local bare repository and
  `gh` is a stub, so a real pull request page, reviewers and an existing
  pull request are not tested.
- The review budget itself rests on the evidence and limits in the
  research note.
