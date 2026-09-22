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

## Commit standards and branching

Follow the global standard in `huwd/standards` (`standards/CLAUDE.md`). Never
commit directly to `main`; branch as `<type>/<short-description>`.
