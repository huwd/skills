# CLAUDE.md — skills repo

Reusable, cross-harness agent skills. See `docs/plan.md` for the plan and
current status, and `docs/skill-format.md` for authoring conventions.

## Working in this repo

- Each skill lives in `skills/<skill-name>/` with a `SKILL.md` whose `name`
  matches the directory. Keep this layout: agent-manager only discovers skills
  at `skills/<id>/SKILL.md`.
- Keep `SKILL.md` portable: ordinary files, commands and repo state, no
  harness-specific tool names unless declared in `compatibility`.
- Skills that take outward-facing actions (comments, merges, pushes) must ask
  for explicit approval first.
- This repo is public. Never commit secrets, personal tokens, or private repo
  names.
- Vale checks the Markdown before push and in CI. Run
  `.github/scripts/check-prose.sh` before pushing documentation; fix
  misspellings rather than adding them to the vocabulary.

## Commit standards and branching

Follow the global standard in `huwd/standards` (`standards/CLAUDE.md`). Never
commit directly to `main`; branch as `<type>/<short-description>`.

Commit messages are technical writing. Apply `technical-writing` to their
prose and `commit-messages` to diff selection, commit boundaries and requested
git operations. The shared standards remain the authority for this repo's
Conventional Commits, 50-character subjects and 72-character body wrapping.

The shared TDD workflow explicitly permits red test checkpoints on feature
branches. Record the expected failure honestly, keep unrelated checks passing
and preserve hooks and signing. An unavailable tool or rejected hook is not
an expected red test failure. Behavioural skill evals use a measured baseline
shortcoming as their red step; they do not require breaking static CI.
