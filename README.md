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

Each release is published as a versioned bundle, installed with
[agent-manager](https://github.com/ai-agent-manager/agent-manager) into Claude
Code and the shared `~/.agents/skills`, which Codex and OpenCode read. From a
checkout of this repository:

```bash
npx @ai-agent-manager/cli@1.23.1 https://huwdiprose.co.uk/skills \
  --config config/ai-skills.yml
```

Run it again to update. [`config/ai-skills.yml`](config/ai-skills.yml) picks
the skills and tools, and can pin a version. Skills install under their own
names, such as `/technical-writing`. See
[decision 0004](docs/decisions/0004-install-from-versioned-bundles.md).

To work on a skill, symlink its directory instead, as described in
[`docs/skill-format.md`](docs/skill-format.md).

## Releasing

Tag a commit on `main` as `vX.Y.Z` and push the tag. The Release workflow
builds the bundle, attaches it to a GitHub Release, and republishes the
site with every released version.

## Checks

Every pull request runs static checks, none of which call a model: skill
validation, a static security scan, Markdown and shell linting, secret
scanning, workflow audits, and [bats](https://github.com/bats-core/bats-core)
tests for the scripts in `.github/scripts/`. Run the same checks before each commit with
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
