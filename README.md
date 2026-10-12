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
npx @ai-agent-manager/cli@1.23.1 https://huwd.github.io/skills/ \
  --config config/ai-skills.yml
```

Run it again to update. [`config/ai-skills.yml`](config/ai-skills.yml) picks
the skills and tools, and can pin a version. Skills install under their own
names, such as `/technical-writing`. See
[decision 0004](docs/decisions/0004-install-from-versioned-bundles.md).

To work on a skill, symlink its directory instead, as described in
[`docs/skill-format.md`](docs/skill-format.md).

## Releasing

Each skill records its own stable SemVer in `metadata.version`. Changes to
any files in a skill directory require an increased skill version.

To release the combined bundle, increase the root [`VERSION`](VERSION) and
add a matching `## [X.Y.Z]` entry to [`CHANGELOG.md`](CHANGELOG.md). Our
convention is to prepare a bundle release whenever a skill version changes;
several skill updates can share a release. Normally increment the bundle
patch number; choose minor or major deliberately for larger changes.

After the merged commit passes CI on `main`, the Release workflow creates
`vX.Y.Z`, builds the bundle and checksum, attaches them to a GitHub Release,
and republishes Pages. The matching changelog entry supplies the release
notes. Unchanged bundle versions do not create releases. CI checks version
format, decreases, changed skills and changelog entries; the convention
linking skill bumps to bundle releases is not a blocking check.

Retry an interrupted publication by rerunning that commit's CI workflow.
Existing tags must identify the same commit and existing assets must match;
published assets are never overwritten. Run Release manually to rebuild
Pages from existing releases without creating a release.

Before the first release, enable GitHub Pages with GitHub Actions as its
source. No manual tag push is needed.

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
