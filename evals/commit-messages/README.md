# Commit-message evals

This suite is for contributors checking the `commit-messages` skill. It
compares the requested git state and message quality with and without the
skill. The fixtures and their failure inputs are synthetic, not production
incident records. No case has a remote repository or a real signing service.

The [evaluation report](../../docs/commit-messages-evaluation.md) records
the completed comparison and its limits.

## Run the comparison

From the repository root, using Python with PyYAML and a saved Codex login:

```bash
python3 evals/run-codex.py --suite commit-messages \
  --case preserve-index --ref HEAD --ref none --runs 2 \
  --allow-fixture-git --model gpt-6.1-sol --effort medium
```

Repeat for the case names below. `HEAD` must contain the committed skill;
`none` installs no skill. The adapter disables unrelated installed skills
and retains the workspace, transcript, actual checked inputs and verdicts.
Model calls remain local; CI runs the offline grader controls only.

These are Codex-only cases: `codex-case.yaml` records the runner and fixture
requirements, `task.md` supplies the prompt, and `graders/` supplies the
selection indicator and trusted local state assessor. Their filenames keep
the script graders out of the Claude plugin runner's discovery.

The explicit fixture-git permission is necessary because ordinary Codex
workspace permissions protect `.git`. It permits metadata writes only in
the disposable repository. The source checkout remains outside that write
scope, and command networking is disabled. A run blocked by the environment
is inconclusive, rather than evidence that the skill improves behaviour.

## Cases and observable expectations

| Case | Expected result |
| ---- | --------------- |
| `fallback-format` | With no explicit format and plain subjects in history, drafting uses the Conventional Commits fallback while preserving git state. |
| `draft-staged` | A message follows the project's custom prefix and 80-character limit, explains the staged timeout change, and leaves the index, history and existing files untouched. |
| `preserve-index` | One commit contains exactly the staged retry fix and test. An unrelated staged README and an unstaged edit to the same source file survive unchanged. |
| `split-work` | Two independent fixes become two commits, each with its regression test, in either order. |
| `reviewable-series` | Infer review units in a mixed-file change: validate mechanical preparation before its dependent feature, and keep an unrelated correction separate. Preserve the prepared final files. |
| `validation-failure` | A failing required test is reported and no commit or file change occurs. |
| `missing-check` | An unavailable required tool is reported without installation, replacement of the check or a commit. |
| `red-checkpoint` | Explicit repository policy permits the expected failing test checkpoint, recorded truthfully without changing implementation or bypassing hooks. |
| `hook-rejection` | A synthetic signing-service hook rejects the commit; the agent reports it and preserves the hook and history. No real signing key is exercised. |
| `coding-only` | An ordinary coding request changes the requested function and runs checks without loading this skill, staging files or committing. |
| `history-only` | Reading and explaining the latest commit does not load this skill or change files, staging or history. |

`fixture.py` creates each repository and saves its initial state outside the
model's working directory. `assess.py` reads that state and the final git
objects, index entries, files, hook records and command transcript. It does
not execute model-produced code outside the model's sandbox. The coding
case checks the recorded sandboxed check result and file boundaries; its
diff also needs inspection.

`reviewable-series` uses `series_fixture.py`. Its prompt does not supply the
groups or a commit count. The fixture has three intended concerns sharing
source and test files. The checker recognises their known intermediate ASTs
(so comments and whitespace do not define the groups), requires preparation
before the dependent feature, and permits the independent fix anywhere.
Each commit must match a passing recorded check of its source/test contents.
Checking only the final tree is insufficient. This is a narrow fixture for
review structure, not a universal rule that changes need three commits.

One script grader reports the individual state checks and a combined task
verdict. The numeric score is therefore a binary task verdict per run, not
a count of independent tests. Positive skill-read indicators are separate
diagnostics; negative selection remains an acceptance check.

## Editorial rubric

Before changing the instructions, assess messages and split proposals on
these criteria as well as the mechanical checks:

- Does the message identify the concrete change and explain its reason
  from supplied evidence, without needing the task conversation?
- Does it distinguish the staged change from unrelated or unfinished work?
- Do the subject, body, references and trailers follow project policy?
- Do validation claims match the recorded checks, including expected red
  failures, unavailable tools and rejected hooks?
- Does each commit have one coherent purpose, with its relevant tests?
- Does the sequence reduce review complexity, with dependencies in order,
  rather than just splitting files or recording editing chronology?

The format and rationale patterns are narrow checks, not a complete
editorial judgement. Command guards recognise ordinary direct and chained
commands, not arbitrary shell programs. Hook records are observations, not
proof against deliberate tampering. Inspect the actual diffs and traces.

## Check the graders

Run the offline controls before relying on a comparison:

```bash
python3 -m unittest discover -s evals/tests -v
```

The controls reject a changed index, committing an unstaged blob, bundling
independent fixes, an unsupported message format and hook bypass commands.
They also accept a valid subset commit preserving the user's index, either
order for the independent fixes, and an alternative rationale. Failed and
unavailable checks and a rejected hook have real non-zero process results.
The mixed-file controls reject a bundled final tree and intermediate commits
that were not checked, while accepting a dependency-ordered series with the
independent fix first. The format controls accept a deliberate project
override above the fallback subject limit while rejecting plain subjects in
a silent project.
