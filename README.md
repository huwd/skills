# skills

Reusable agent skills for Claude Code, Codex, OpenCode and other harnesses
that read the [Agent Skills](https://agentskills.io/specification) format.

## Skills

| Skill | What it does |
| ----- | ------------ |
| [`dependabot-pr-review`](skills/dependabot-pr-review) | Reviews one or all open Dependabot PRs and gives a merge / verify / investigate / hold verdict |
| [`do-release`](skills/do-release) | Runs a package release workflow |

## Installing

Installation through [agent-manager](https://github.com/ai-agent-manager/agent-manager)
is planned; see [`docs/plan.md`](docs/plan.md). Until then, symlink a skill
directory into your harness's skills directory as described in
[`docs/skill-format.md`](docs/skill-format.md).

## Layout

```text
skills/<skill-name>/SKILL.md   # one directory per skill
docs/skill-format.md           # authoring conventions
docs/plan.md                   # plan and progress
```

## Licence

[MIT](LICENSE). `dependabot-pr-review` is adapted from
[thoughtbot/dependabot-review-skill-thoughtbot](https://github.com/thoughtbot/dependabot-review-skill-thoughtbot)
and carries its copyright notice in [its own `LICENSE`](skills/dependabot-pr-review/LICENSE),
so the notice travels with the skill when it is installed on its own.
