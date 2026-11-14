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

`run-codex.py` compares committed versions of the technical-writing skill
using the same fixture and prompt. It needs Python 3.12 or later, PyYAML,
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

The runner:

- alternates the two refs, reversing their order for each pair
- creates a fresh fixture repository for every run
- installs the selected skill at `.agents/skills/technical-writing/`
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
