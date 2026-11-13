# Skills

This repository's `skills/` directory is the canonical home for reusable agent skills that should work across Codex, Claude Code, and OpenCode where possible.

## Structure

Each skill lives in its own directory and uses the Agent Skills shape:

```text
skills/
  <skill-name>/
    SKILL.md
    scripts/       # optional executable helpers
    references/    # optional supporting docs
    assets/        # optional templates or static resources
```

The directory name and the `name` frontmatter value in `SKILL.md` must match. Use lowercase letters, numbers, and single hyphens only:

```yaml
---
name: example-skill
description: Does a specific repeatable workflow. Use when the user asks for that workflow or mentions its inputs.
metadata:
  version: "0.1.0"
---
```

Keep shared skill frontmatter conservative for cross-harness compatibility:

- `name`
- `description`
- `license`, if useful
- `compatibility`, only when the skill has real environment requirements
- `metadata`, including the required stable SemVer `version`

Avoid tool-specific features in shared skills unless the skill is explicitly marked as tool-specific. Put detailed references in `references/` instead of making `SKILL.md` huge.

## Versioning

Increase `metadata.version` when changing any tracked file in the skill
folder, including references, scripts and assets. Versions use stable
`MAJOR.MINOR.PATCH` numbers without leading zeroes; prerelease and build
suffixes are not supported yet. Existing versions cannot decrease.

Record changes and affected skill versions under `[Unreleased]` in
`CHANGELOG.md`. Prepare the root `VERSION` bump and matching numbered
changelog section in a separate release step. The root version controls
publication of the combined bundle; several skill updates can share one
release.

## Compatibility

Release bundles install into Claude Code and the shared `~/.agents/skills/`
through agent-manager. See the root [README](../README.md) and
[decision 0004](decisions/0004-install-from-versioned-bundles.md) for the
versioned installation command and its constraints. Agent-manager handles
download, version selection, installation state and target directories.
It installs the skill folder; it does not translate the instructions or
provide their operational tools. Author one skill directory rather than
installation wrappers for each target.

Write instructions in terms of ordinary files, commands, and repository state. Do not rely on a particular model, subagent, tool name, permission mode, or dynamic context feature unless the skill documents that requirement in `compatibility`.

## Authoring and reviewing

Use `authoring-skills` to create or change a skill and `reviewing-skills`
for a read-only assessment. Neither requires the other. Reviews give
evidence, the expected outcome, a focused remedy and a regression scenario;
authoring applies requested changes and verifies them. See
[the brief](authoring-skills-brief.md) for the split and its trade-offs.

Start from a demonstrated workflow or missing expertise. An ordinary
one-off command may need no skill; repository conventions may belong in
agent instructions. Do not add universal rules for every session correction.
Diagnose whether a failure comes from discovery, guidance, execution,
tooling or the grader before changing instructions.

Write a concise description that explains the capability and when to use
it. Keep essential guidance in SKILL.md and link conditional references
where they are needed. Optional helpers and templates should solve a
concrete problem. Keep instructions in terms of files, commands and
repository state; agent-manager does not translate runtime-specific tools.

Use [dependabot-pr-review](../skills/dependabot-pr-review/SKILL.md) as a
worked structural example: a bounded description, conservative metadata,
a compact procedure, command references and output templates. Its
GitHub access strategy is specific to that job, not a requirement for
other skills. Human READMEs record usage and provenance; adapted content
keeps its licence notice within the installed skill directory.

## Validation

Run the static checks in the root README. For behavioural changes, use
local evals under `evals/<skill>/`, kept outside installed content. Compare
a new skill with no skill, or a change with the previous version, on the
same inputs and environment. Check outcomes, important actions and nearby
cases that must remain unaffected, including negative triggers.

Run representative cases more than once, read traces and report actual
results and limitations. Static validity does not establish usefulness,
and forced loading does not test automatic selection. Evals remain local
under [decision 0001](decisions/0001-run-evals-locally.md).

## Development symlinks

For live development, link the whole skill directory so its references,
scripts and assets travel together. Do not replace an existing managed
installation without deciding how it will be restored.

For example, with no existing directory at the destination:

```bash
mkdir -p ~/.agents/skills
ln -s ~/Projects/skills/skills/authoring-skills ~/.agents/skills/authoring-skills
```

Restart the agent session after adding a development link if the harness
does not discover the skill live. Use versioned bundles for normal installs.

## Agents Are Separate

Do not put tool-specific subagent definitions in this directory. Claude Code and OpenCode use similar Markdown files for agents, but their frontmatter and runtime semantics differ enough that they should have separate wrappers.

Keep portable prompts or procedures here as skills. Keep harness-specific agent definitions in a separate `agents/` tree if and when one is needed.
