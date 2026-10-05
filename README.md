# skills

Reusable agent skills for Claude Code, Codex, OpenCode and other harnesses
that read the [Agent Skills](https://agentskills.io/specification) format.

## Skills

| Skill | What it does |
| ----- | ------------ |
| [`dependabot-pr-review`](skills/dependabot-pr-review) | Reviews one or all open Dependabot PRs and gives a merge / verify / investigate / hold verdict |
| [`do-release`](skills/do-release) | Runs a package release workflow |
| [`technical-writing`](skills/technical-writing) | Writes and edits Markdown to the repository's style guide, and checks it with the repository's linters |

## Installing

Installation through [agent-manager](https://github.com/ai-agent-manager/agent-manager)
is planned; see [`docs/plan.md`](docs/plan.md). Until then, symlink a skill
directory into your harness's skills directory as described in
[`docs/skill-format.md`](docs/skill-format.md).

## Checks

Every pull request runs static checks, none of which call a model: skill
validation, a static security scan, Markdown and shell linting, secret
scanning and workflow audits. Run the same checks before each commit with
[pre-commit](https://pre-commit.com/), which needs uv and Go:

```bash
pre-commit install          # once
pre-commit run --all-files  # every check, by hand
```

Skill behaviour is tested with evals, run locally before merging a change
to a skill, for example `evals/technical-writing/run.sh`. See
[decision 0001](docs/decisions/0001-run-evals-locally.md) and
[decision 0002](docs/decisions/0002-static-checks-in-ci.md).

## Layout

```text
skills/<skill-name>/SKILL.md   # one directory per skill
docs/skill-format.md           # authoring conventions
docs/plan.md                   # plan and progress
docs/decisions/                # decision records
evals/<skill-name>/            # eval suites, not installed with skills
```

## Licence

[MIT](LICENSE). `dependabot-pr-review` is adapted from
[thoughtbot/dependabot-review-skill-thoughtbot](https://github.com/thoughtbot/dependabot-review-skill-thoughtbot)
and carries its copyright notice in [its own `LICENSE`](skills/dependabot-pr-review/LICENSE),
so the notice travels with the skill when it is installed on its own.
