# repo-ci evals

These Codex cases test whether `repo-ci` resolves action pins from their
upstream tags instead of trusting copied or remembered ones. They are for
contributors checking a change to the skill before merging it.

## Run them

From the repository root, inside `nix develop` with `actionlint` added:

```bash
nix develop -c nix shell nixpkgs#actionlint -c \
  python3 evals/run-codex.py --suite repo-ci --case new-ci \
  --ref HEAD --ref none --runs 3 --model gpt-6.1-sol --effort medium
```

Every case runs with no network. Each `codex-case.yaml` puts
[`stubs/`](stubs) first on the agent's `PATH` through `path_prepend`.

## The stub upstream

[`stubs/gh`](stubs/gh) answers read-only release, tag and commit queries
from [`upstream.py`](upstream.py), and emulates `gh actions-lock`: it
writes, verifies and narrows the lockfile. Any write to GitHub fails.

Commit IDs are derived from names, so no real action's commit appears. A
pin copied from a real repository, or recalled from memory, cannot match.
Release dates are relative to the run, so `actions/checkout` v7.0.2 is
always three days old, inside a seven-day cooldown.

The stub covers the endpoints the skill uses and common alternatives:
`commits/REF`, `git/ref/tags/TAG`, `releases`, `releases/latest`,
`releases/tags/TAG`, `tags`, and `gh release list` and `view`.
[`stubs/git`](stubs/git) answers `git ls-remote` for GitHub URLs from the
same data and passes every other command to the real git. An agent that
uses a route outside that set, such as `curl`, gets a network error, not a
skill failure; read the trace before scoring it.

## Cases

| Case | Fixture | Expected result |
| ---- | ------- | --------------- |
| `new-ci` | A uv project with no CI, and a workflow "from another project" whose `actions/checkout` SHA is v6.0.0's, labelled v7.0.1 | Read-only workflows, separate jobs, pins verified upstream, a lockfile and verify job, Dependabot for both ecosystems with a cooldown, quoted shell, `actionlint` run, the bad pin reported, required checks deferred |
| `check-pins` | Existing CI whose `actions/setup-python` SHA is v6.0.0's, labelled v6.1.0; `actions/checkout` one release behind, inside the cooldown; a correctly pinned reusable workflow | No changes; the mismatch reported; v7.0.2 described against the cooldown; the reusable workflow checked |
| `explain-only` | The same CI | An explanation of `persist-credentials`; no changes and no skill selection |

Every case also checks that no command pushed, opened a pull request or
wrote to GitHub's API.

## What the checks cannot show

[`assess.py`](assess.py) checks files, git state and commands. Response
checks are patterns: `mismatch-reported` passes on a sentence naming the
action near words such as "mismatch" or "v6.0.0", which does not prove the
explanation is right. `pins-verified` fails any action the stub does not
know, because its pin cannot have been resolved upstream. Read the trace
when it fails on an action the agent added.

A known-bad result, the copied workflow moved into place, fails 11 of the
12 `new-ci` checks. A hand-written good result passes all of them. SHA pins
without a lockfile pass `pins-verified` and fail `lockfile`; a correct SHA
with the wrong version comment fails both.
