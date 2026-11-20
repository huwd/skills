# Pull-request evals

These Codex cases test whether `pull-requests` writes a description that
helps a reviewer spend their time well. They are for contributors checking
a change to the skill before merging it. The review budget they test comes
from the [code review capacity research](../../docs/code-review-size-research.md).

## Run them

From the repository root, inside `nix develop`:

```bash
nix develop -c python3 evals/run-codex.py --suite pull-requests \
  --case large-mixed --ref HEAD --ref none --runs 3 \
  --model gpt-6.1-sol --effort medium
```

No case needs network access or writes to `.git`. The fixtures are
synthetic: a small Python package, `ledger`, with one feature branch for
each case.

## Cases

| Case | Branch | Expected result |
| ---- | ------ | --------------- |
| `large-mixed` | 58 core lines adding banker's rounding, behind a mechanical rename, a reformat and a regenerated `uv.lock`: 2,204 changed lines in all | A description that estimates review time, gives the core change's size separately, points the reviewer at the core files before the lockfile, says how to verify the rename and marks the lockfile as not needing line-by-line review, with no split advice in the description |
| `oversized` | Three independent features, 1,787 new lines, each function with different logic | A description with a review-time estimate, and a recommendation to split the branch into separate pull requests that names at least two of the features |
| `small-fix` | A 6-line fix with its test | A short description of 250 words or fewer, with no split recommendation |
| `explain-branch` | The `large-mixed` branch | An explanation only: no skill selection and no files written |

Every case also checks that no command pushed or opened a pull request,
and that no branch or commit changed.

## What the checks cannot show

[`assess.py`](assess.py) reads `PR_BODY.md`, git refs, the final response
and the command transcript. Its description checks are patterns, not
judgements of quality:

- `review-estimate` passes when a duration near the word "review", or in
  a table whose header mentions review, falls between half the time at 400
  lines an hour and twice the time at 200 lines an hour plus 30 minutes,
  and no such duration is above that range. It does not check how the
  estimate was reached.
- `core-size` passes when a number within 35% of the core change's added
  lines, or its added and deleted lines, appears near "core", "rounding"
  or "behaviour" and is not a count of files, packages, tests or minutes.
- `core-first` compares where `rounding.py`, `invoice.py` or
  `test_rounding.py` is first named in the description's list items with
  where `uv.lock` is first named there. A summary or size table may name
  the parts in any order.
- `generated-deferred` passes when the text near `uv.lock` says it was
  regenerated or need not be read, and fails if it asks for the lockfile
  to be reviewed carefully or line by line.
- `split-proposed` and `no-split` look for split wording in a sentence
  without a negation before it, so "no need to split" is not a split
  recommendation. `split-proposed` also needs two feature names. Neither
  check judges the proposed groups.

Read the description itself before treating a pass as a good result.
[`test_pull_requests_evals.py`](../tests/test_pull_requests_evals.py) holds
the offline controls: a guided description passes every `large-mixed`
check, a summary in commit order fails the five description checks, and
each weakness found in an earlier version of a check has a control.
