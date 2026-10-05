# 0002. Gate pull requests on static checks only, and run them locally too

- **Status:** Accepted
- **Decided by:** @huwd
- **Decided:** 2026-10-05
- **Recorded:** 2026-10-05
- **Discussion:** #11

## Summary

In the context of a public repository of agent skills with no model
credentials in CI ([0001](0001-run-evals-locally.md)), facing the question
of what an automated check can usefully say about a skill, the decision
was for a pipeline of static checks (spec and content validation, a
static security scan, linting, secret scanning and workflow audits), run
by both CI and pre-commit from shared scripts, and against copying a
large community pipeline or adding model-based review, to achieve fast,
free, repeatable gates, accepting that static checks can't judge whether
a skill behaves well.

## Context

In October 2026 the best-known skill repositories, from Anthropic,
OpenAI and obra/superpowers, ran no CI at all. Three published
pipelines were worth comparing:

- **trailofbits/skills:** static checks on pull requests (frontmatter,
  plugin metadata, pre-commit linting, `bats` tests for skill scripts),
  plus a model review on non-fork pull requests that needs an API key.
- **microsoft/skills:** a smoke test on pull requests, with model-based
  evals on a nightly schedule or a manual trigger, behind a repository
  variable.
- **github/awesome-copilot:** about 60 workflows for triaging a large
  community catalogue: intake gates, risk scans, labelling and review
  routing.

This repository already ran skill spec validation, markdownlint,
shellcheck, gitleaks and zizmor. Two static tools covered gaps:

- **[skill-validator](https://github.com/agent-ecosystem/skill-validator)**
  checks what the spec doesn't: links, token budgets, files nothing
  references, code fences, and descriptions that read as keyword lists.
- **[SkillSpector](https://github.com/nvidia/skillspector)** scans skills
  for prompt injection, data exfiltration, privilege escalation and
  similar risks. Its static mode needs no model.

Trying SkillSpector on this repository's skills showed two things. Every
finding on the existing skills was a false positive, such as "Do not
judge CI from the check list alone" read as an instruction to stop
refusing. And its risk score is a weak gate: a skill told to read
`~/.ssh/id_ed25519` produced one HIGH finding but scored 22, under the
default failure threshold of 50.

## Options considered

### Static checks, shared by CI and pre-commit (chosen)

Add skill-validator and SkillSpector to the existing checks, and take
Trail of Bits' smaller habits: cancel superseded runs, fail loudly when no
skills are found, and run the same checks locally through pre-commit.

- skill-validator fails on errors; its warnings show as annotations.
- SkillSpector fails on any finding not accepted in a reviewed baseline
  under `.github/skillspector/`, rather than on its score. Each accepted
  finding records why. Exact fingerprints cover one-off phrases, so an
  edit brings them back for review; glob rules cover patterns that are
  safe wherever they appear, such as calls to `api.github.com`.
- The skill checks live in `.github/scripts/`, called by both CI and
  `.pre-commit-config.yaml`, with tool versions pinned in one place.

Free, fast, and the same result locally as in CI. The cost is baseline
upkeep when a skill's flagged text changes, and no judgement of quality.

### Copy github/awesome-copilot's pipeline

Built for strangers' submissions at scale, with one maintainer it is
mostly machinery to maintain. Its workflows also filter on paths, which
blocks pull requests when those workflows are required checks.

### Add a model-based review, as Trail of Bits does

Useful, but it needs an API key in CI, which
[0001](0001-run-evals-locally.md) rules out. Local evals cover behaviour.

### Gate SkillSpector on its risk score

The tool's default. Shown above to pass a skill that reads private SSH
keys, so it isn't used.

### Keep the existing checks

Leaves broken links, token bloat and security patterns unchecked, in a
repository whose skills other people may install.

## Decision

Pull request CI runs only static checks, and none call a model:

- **Validate skills:** the Agent Skills spec (skills-ref) and
  skill-validator's structure, link and content checks
- **Scan skills:** SkillSpector in static mode, failing on any finding
  not in that skill's reviewed baseline
- **Lint Markdown, Check shell, Scan for secrets, Audit workflows:** as
  before

Each is a required status check. `.pre-commit-config.yaml` runs the same
checks before each commit, using the same scripts and pinned versions.

## Consequences

- Skills are checked for broken links, bloat and common attack patterns
  before merging, at no cost.
- A change that rewords flagged text, or a SkillSpector upgrade, needs the
  baseline reviewed and regenerated. That's deliberate: accepting a
  finding should be a decision, not a default.
- Dependabot updates the GitHub Actions and the pre-commit hooks. Tools
  pinned by version in `ci.yml` and `.github/scripts/` (skills-ref,
  SkillSpector, skill-validator, gitleaks, zizmor) aren't visible to it
  and need bumping by hand.
- Static checks can't tell whether a skill works; evals under
  [0001](0001-run-evals-locally.md) do that.
- Revisit if contributions from other people grow, when awesome-copilot's
  intake checks would start to earn their keep.
