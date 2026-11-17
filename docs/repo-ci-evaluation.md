# Evaluation of the repo-ci skill

This report is for contributors deciding whether `repo-ci` 0.1.0 improves
CI setup enough to merge. It compares the skill with no skill on the same
offline fixtures. The [design note](repo-ci-design.md) records why the
skill works as it does, and the [eval suite](../evals/repo-ci/README.md)
defines the cases.

## Result

With the skill, every run of every case passed every check. Without it,
no run of `new-ci` resolved a pin from upstream or reported the bad pin in
its source material. That is the failure that motivated
[issue #26](https://github.com/huwd/skills/issues/26).

| Case | With skill | Without skill |
| ---- | ---------- | ------------- |
| `new-ci` | 1.00, 1.00, 1.00 | 0.42, 0.50, 0.42 |
| `check-pins` | 1.00, 1.00, 1.00 | 0.83, 0.67, 0.83 |
| `explain-only` | 1.00, 1.00, 1.00 | 1.00, 1.00, 1.00 |

Scores are the fraction of a case's checks passed, excluding the skill
selection diagnostic. The skill loaded in every `new-ci` and `check-pins`
run, and in no `explain-only` run.

A later `new-ci` rerun added a repository that runs zizmor, and a check
that the new workflows pass it; see [zizmor](#zizmor). With the skill,
all three runs scored 1.00. Without it, the runs scored 0.46, 0.54 and
0.54, and every run kept the copied `actions/checkout` pin.

## Method

- Skill: `repo-ci` 0.1.0, from snapshot commit `037a3d2`, and
  `1adcee9` for the zizmor rerun.
- Harness: Codex CLI 0.167.1, through `evals/run-codex.py`.
- Model: `gpt-6.1-sol`, medium reasoning effort.
- Runs: three per arm per case, alternating the arms' order, on
  16 November 2026; the zizmor rerun of `new-ci` on 17 November.
- Environment: no network. `gh` and `git ls-remote` answered from
  synthetic upstream data through the suite's stubs; `actionlint` and
  `shellcheck` were available.

## What the baseline did

In `new-ci`, no baseline run asked upstream for any commit. One run kept
the copied `actions/checkout` pin, v6.0.0's commit labelled v7.0.1. Two
runs replaced it with commits recalled or read from elsewhere, which match
no upstream tag. A third, in the paired batch, resolved tags with
`git ls-remote` and pinned correctly, but still did not report the copied
pin. Every baseline run used one job for all checks, set no Dependabot
cooldown, added no lockfile or verify job, and did not mention deferring
required checks.

In `check-pins`, the baseline found the `setup-python` mismatch in most
runs, but never described `actions/checkout` v7.0.2 against the seven-day
cooldown. In an earlier run, before the `git` stub existed, it reported
commits it had not resolved as "upstream" and called a correct pin wrong.

## What the skill changed

With the skill, the agent resolved every tag through `gh`, wrote a
lockfile, copied the verify workflow and script, and ran `actionlint`,
`gh actions-lock --verify` and `verify-pins.sh` locally. It reported the
copied pin with the commit its tag actually resolves to, and named the jobs
to require once they report on `main`. In `check-pins` it ran
`verify-pins.sh` and changed nothing.

## zizmor

In one run of the first comparison, the agent ran zizmor and reported the
tag references that `actions.lock` locks. zizmor's `unpinned-uses` audit
does not read the lockfile, so a repository that adopts the lockfile and
runs zizmor would fail CI.

The skill now adds `zizmor.yml` with a `ref-pin` policy to such
repositories. That policy also accepts `@main` and `@v7`, so
`verify-pins.sh` now fails a locked ref that is not a full version tag.
The [design note](repo-ci-design.md) records the trade-off.

The `new-ci` fixture now includes a pre-commit configuration that runs
zizmor. A new `zizmor-clean` check runs zizmor on the result, and
`pins-verified` now rejects branch and partial tags. Both arms were rerun
on the changed fixture. Every skill run added `zizmor.yml` and passed.
Baseline runs passed `zizmor-clean` because they used commit SHAs, which
zizmor accepts.

## Grader corrections

Three checks were corrected after reading traces, and every saved run of
both arms was regraded with the corrected assessor:

- `tree-clean` counted the runner's `.agents/` skill install as a change,
  failing only the skill arm. It now excludes that directory.
- `resolved-upstream` accepted only direct `gh` queries. It now also
  accepts `git ls-remote` and `verify-pins.sh`, which queries every pin.
- `reusable-checked` required the string `shared-workflows`. It now also
  accepts the workflow file's name or "reusable workflow".

An earlier correction widened `explained`, which rejected a correct
explanation of `persist-credentials`. The `git` stub was added after the
first baseline batch, when traces showed the baseline trying
`git ls-remote`. The comparison above uses the batch run after that.

## Limits

- Three runs per arm is a smoke comparison, not a success rate.
- The stubs cover the routes agents took; one using `curl` against the API
  would get a network error.
- Response checks match patterns, not the correctness of an explanation.
- Codex's sandbox allows reads outside the workspace. Some baseline runs
  may have read pins from this checkout rather than recalled them.
  [Issue #42](https://github.com/huwd/skills/issues/42) tracks isolating
  eval runs.
- Claude Code was not tested.
- `check-pins` and `explain-only` were not rerun after the zizmor change,
  which touched neither fixture.
