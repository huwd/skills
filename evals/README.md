# Local skill evals

These evals test skill behaviour in temporary fixture repositories. This
guide is for contributors checking a skill change before merging it.
Model runs use the caller's account and run locally, outside CI.

## Claude Code

The existing runner uses `claude plugin eval` and the case definitions
under `technical-writing/`:

```bash
evals/technical-writing/run.sh --case vocab-local --runs 10 --keep-temp
```

It runs with and without the plugin by default. Use `--ablation none` to
test only the plugin. Preserve temporary files when investigating a
failure; the HTML report alone does not contain the agent's transcript.

## Codex

`run-codex.py` compares committed skill versions using the same fixture
and prompt. It needs Python 3.12 or later, PyYAML,
Git, the Codex CLI with a saved login, and the fixture's tools on `PATH`.
For `vocab-local`, those tools are Vale and an en_GB Hunspell dictionary.
The scaffold resolves the dictionary through Nix when available.

Run from the repository root, using a Python environment with PyYAML:

```bash
python3 evals/run-codex.py --case vocab-local \
  --ref HEAD --ref origin/main --runs 10 \
  --model gpt-6.1-sol --effort medium
```

On NixOS, enter a shell providing Vale first:

```bash
nix shell nixpkgs#vale
```

Start with `--runs 1` to check authentication, scaffolding and transcript
grading before launching a larger batch. Use `--output-dir PATH` to choose
an unused results directory. Otherwise, output goes under the ignored
`evals/results/` directory. Ref names resolve to commit IDs before any
model runs start. Uncommitted skill edits are not tested.

The default suite and skill are `technical-writing`. Use `--suite NAME` for
another suite and `--skill NAME` when its skill has a different name.
`--ref none` adds a no-skill arm for evaluating a new skill. Positive
skill-read diagnostics are omitted in that arm; negative selection checks
still apply. The runner keeps a copy of itself and the suite with the results.

Codex-only cases use `codex-case.yaml` and `task.md`, keeping their script
graders outside Claude's `case.yaml`/`prompt.md` discovery. The
[commit-messages suite](commit-messages/README.md) uses this format.

For cases that must create fixture commits, `--allow-fixture-git` selects
a profile extending Codex's workspace permissions with write access to the
disposable workspace's `.git`. Command networking remains disabled; the
source checkout is not a writable workspace. Other protected paths retain
their normal permissions. Cases declaring `requires_fixture_git: true`
reject a run without this flag before calling a model.

The runner:

- alternates the two refs, reversing their order for each pair
- creates a fresh fixture repository for every run
- installs the selected skill at `.agents/skills/<skill-name>/`
- disables installed user and admin skills and bundled system skills
- uses a temporary Codex configuration with no user instructions, plugins
  or execution rules copied from the caller
- copies saved authentication into a private temporary directory outside
  the retained output, then removes that copy when the runner exits
- runs Codex with the workspace-write sandbox and no approval prompts
- stops the batch on a scaffold, authentication, quota or runtime error

Scaffolds run as the caller, so use this runner only with trusted fixtures.
Skill snapshots are committed repository files, and the prompt and graders
come from the working tree. All refs use the same fixture.

## Read the Codex results

`aggregate-result.json` records the refs, commit IDs, model, effort,
fixture hashes and each run's verdicts. Each run directory contains:

- `workspace/`: the final files, repository history and tested skill
- `events.jsonl`: commands, command output, edits and agent messages
- `response.txt`: the final agent response
- `stderr.log`: Codex diagnostics
- `scaffold.stdout` and `scaffold.stderr`: fixture setup logs
- `prompt.txt`, `command.json` and `result.json`: invocation and verdicts

Exit code 0 means every check passed. Exit code 1 means the completed batch
contains a failed check. Exit code 2 means the batch stopped on a runtime
or setup error. Check `complete` in the aggregate report before treating
the output as a completed comparison. Failed model calls are not scored
as skill failures.

The adapter supports regex graders and the following tool graders:

| Claude grader | Codex evidence | Treatment |
| ------------- | -------------- | --------- |
| `Bash` | A completed command whose command text matches `input_match` | Included in the score |
| `Skill` | A successful command reading the tested `SKILL.md`, with its content in the output | Diagnostic; excluded from the score |

A Codex-only `script` grader runs a trusted Python assessor after the model
session. Its frontmatter names a `script` relative to the grader file and a
`check`. The assessor receives the workspace path and check as arguments,
and the event list as JSON on standard input. It returns a JSON object with
a boolean `passed` field and an optional `detail`. A failed assertion returns
`passed: false`; a crash or invalid verdict stops the batch as a runtime
error. Like scaffolds, these assessors execute as the caller, so inspect
them before running an unfamiliar suite. They can check actual git state
without trusting the model's description of what it did.

The skill-read diagnostic can miss a read split across several commands.
Inspect the transcript when it fails. Unsupported grader types are
rejected before model calls start.

Codex uses the fixture's wall-clock timeout. Claude-specific `max_turns`
and `allowed_tools` settings are not translated; Codex uses its own tools
and sandbox. Its score therefore describes behaviour under Codex, and
does not establish why a Claude run failed. Compare branch and main
within the same harness, model, reasoning effort and fixture environment.

Run the adapter's offline grading tests with:

```bash
python3 -m unittest discover -s evals/tests -v
```

## Read a case as a test specification

The existing Claude plugin eval runner discovers cases under `evals/`:

| File | Purpose |
| ---- | ------- |
| `case.yaml` | Names the case, assigns tags and selects its scaffold |
| `scaffold.sh` | Creates a disposable repository containing the task inputs |
| `prompt.md` | Gives the agent its task and sets run limits |
| `graders/*.md` | Defines one check per file using YAML frontmatter |

A `regex` grader checks a generated file or the final response. Its score
depends on the pattern, not a model judging the prose. A `tool_used` grader
checks recorded calls, optionally matching their inputs and limiting counts.
Under the runner's with/without comparison, positive Skill-call checks are
selection indicators and are excluded from task scores. Negative selection
checks marked `arm: both` remain scored in both arms.

Separate files are the runner's discovery format. The two new suites contain
seven cases and 38 grader definitions, not 38 independent scenarios.

## How the new cases were authored

Codex authored the authoring/review prompts, synthetic repositories and
assertions for PR #27, following the existing `technical-writing` suite's
format. A temporary Python script wrote the repeated case, scaffold and
grader files from that authored specification. Later corrections were made
directly to the grader files. They were not generated by `claude plugin eval`,
copied from upstream suites or extracted from real agent failures.

The checked-in files are the maintained test specification; there is no
maintained generator to rerun. The generation step saved repetitive file
writing and did not validate the assertions. Review the fixtures and checks
as authored tests, including whether they reject plausible incorrect results.

## What each new case checks

| Case | Intended behaviour | Current checks and limits |
| ---- | ------------------ | ------------------------- |
| [Authoring: create](authoring-skills/create) | Preserve a runbook's constraints in a new skill | Checks the name, local version format, an account-flag mention and preserved source text. It does not execute the produced skill or prove the flag is mandatory. |
| [Authoring: repair](authoring-skills/repair) | Correct a retry rule while preserving polling | Checks references to access failures, pending builds, an increased version and a regression scenario. Text mentions do not prove runtime retry behaviour. |
| [Authoring: decline](authoring-skills/decline) | Avoid files for an unnecessary skill | Checks the explanation and absence of Edit/Write calls. It can pass without the skill loading. |
| [Authoring: documentation edit](authoring-skills/doc-edit) | Fix an install path in a skills catalogue's README without initiating authoring or review | Checks the corrected and removed paths, no selection of either skill and no Edit of the skill. A guard: with no plugin, neither skill can load. |
| [Review: findings](reviewing-skills/review-only) | Identify overly broad triggering and an unwanted push without edits | Checks the finding topics, a test proposal and tool calls. It does not assess every finding's quality. |
| [Review: diagnose](reviewing-skills/diagnose) | Recognise a missing prerequisite rather than invent a skill defect | Checks the diagnosis, a no-change conclusion and no Edit/Write calls. |
| [Review: reading only](reviewing-skills/no-trigger) | Explain a skill without initiating authoring or review | Checks the described command, no selection of either skill and no Edit/Write calls. |

The review command guard covers direct and simple chained `buildctl` calls,
including help, and pushes. It allows `command -v buildctl`, which only looks
up the command. The authoring guards cover direct export/status commands.
These are pattern checks, not shell parsers; wrappers and indirect execution
can escape them. Edit/Write counts cannot catch every shell write. Inspect
traces and artefacts alongside scores; a passing word pattern alone is
insufficient evidence of correct behaviour.

## Technical-writing editorial cases

Four Codex-only cases check whether the skill helps a document serve its
reader without rewriting documents that already work. Each case's
`task.md` names the reader and the task. `editorial_assess.py` checks
facts, session wording, work orders and the size of a change against
originals saved outside the model's working directory.

| Case | Input | Expected result |
| ---- | ----- | --------------- |
| `editorial-brief` | The authoring brief as first written for PR #27, at `267fa8b` | An oriented brief with no session wording or work orders, keeping every listed fact and source |
| `editorial-report` | The evaluation report from the same commit | An oriented report keeping the method, results, grader corrections and limits |
| `coherent-addition` | The rewritten, coherent brief | One short addition; headings and other paragraphs unchanged |
| `small-correction` | The current report with one wrong run count | Only the corrected sentence changes |

The regex checks cannot judge whether a restructured document helps its
reader. Score those outputs with the
[editorial rubric](technical-writing/editorial-rubric.md), reading them
without knowing which arm produced each one.

## Run and interpret the suites

From the repository root:

```bash
evals/authoring-skills/run.sh --runs 3
evals/reviewing-skills/run.sh --runs 3
```

Each case has a with-plugin and no-plugin arm by default. Use `--keep-temp`
when you need the trace and workspace for diagnosis, and `--output-dir PATH`
to choose where local results go. The runner's `--help` describes its flags.
Scaffolds run as the local user, so inspect an unfamiliar suite before running
it. The eval files are outside the skill folders and are not installed by
agent-manager.

Define expected outcomes before changing the skill. Check that a known bad
output fails and a valid alternative passes; do not add wording requirements
just to make a baseline fail. Compare the previous version with the candidate,
or no skill with a new skill, then rerun the relevant cases after simplifying.
Record the model, runner version, revision, run counts, selection results and
per-case task scores. A case that passes equally well in both arms is not
evidence of added value. See the [current evidence report](../docs/authoring-skills-evaluation.md).
