# Skill authoring and review — research brief

Implement [issue #24](https://github.com/huwd/skills/issues/24): make the
catalogue's own authoring and improvement practices reusable. Research
reviewed on 13 November 2026. The user's decision is to ship separate
creation and review skills in one draft pull request.

## Decisions

| Question | Decision and consequence |
| -------- | ------------------------ |
| One skill or separate creation and review? | Separate `authoring-skills` and `reviewing-skills`, as requested. Authoring owns file changes and verification; review owns assessment and diagnosis. A request including both may use both. |
| What does introspection add? | Trace a concrete correction or failed run to its cause before proposing a durable change. Allow no-change outcomes and distinguish missing prerequisites, execution failures and faulty graders from missing guidance. |
| How do they compose? | Pass evidence, the expected outcome, a proposed remedy and a regression scenario. Neither skill requires the other to be installed; no mandatory invocation chain or shared file outside the installed directory. |
| Where is the common guidance? | The repository format remains in `docs/skill-format.md`. Installed skills repeat only essential boundaries; authoring has comparison guidance, while review has a diagnostic rubric. Each owns a different procedure. |
| Include instruction-file authoring? | No. Recognise when knowledge belongs in AGENTS.md or CLAUDE.md, but recommend that destination without expanding into general instruction-file maintenance. |
| Automatic self-improvement? | No automatic end-of-session edits, persistent learning log or completion hook. Apply changes within the user's requested scope and publish only with authorisation. |
| New tools or eval infrastructure? | Reuse the existing local Claude plugin eval format. No model credentials or behavioural evaluations in CI, following decision 0001. |
| Who handles installation targets? | Agent-manager downloads and installs the whole skill folder. This catalogue owns its content, references and versions; no per-target installation code or compatibility matrix is added. |

## Distribution boundary

This repository publishes bundles for
[agent-manager](https://github.com/ai-agent-manager/agent-manager#supported-coding-tools).
Its installation targets determine where each whole skill folder goes.
Keep that responsibility there. The plain files and commands in our skills
make sense because the installer does not translate tool APIs or execute
workflows. The Claude plugin manifest here supports the existing local
eval runner; it is not a second installation route introduced by this work.

## Findings from primary sources

### GitLab authoring-skills

[GitLab's source and supporting references](https://gitlab.com/gitlab-org/ai/skills/-/tree/605c17ffb7054415959e75347c3e33f761e54ec9/skills/authoring-skills),
version 0.7.1, provide the starting point: check whether a skill is useful,
write its discovery description, choose a compact structure, and compare
execution with a baseline. Retain these principles and the MIT notice.
Do not import custom frontmatter, OpenCode-specific tooling, the taxonomy
as a mandatory split rule, or the broad instruction-file authoring scope.
Review all linked references before choosing the smaller local set.

### GitLab ADR creation and review

[adr-create](https://gitlab.com/gitlab-org/ai/skills/-/blob/main/skills/adr-create/SKILL.md)
produces a record; [adr-review](https://gitlab.com/gitlab-org/ai/skills/-/blob/main/skills/adr-review/SKILL.md)
inventories a decision log and finds missing, stale or contradictory
decisions. That is a meaningful difference in inputs and outputs.
However, both repeat discovery, quality and backfill guidance. Creation
allows `rejected` while review's status check omits it, illustrating drift
when the same rule has two owners. The reviewer also backfills and uses
an OpenCode completion hook, so the split alone does not establish a
read-only boundary.

A split is useful for distinct permissions, an independent assessment or
an inventory of many artefacts. It costs more discovery metadata and can
duplicate rules. For our requested split, make assessment read-only and
keep the hand-off small. Do not duplicate the authoring procedure in the
reviewer or require the reviewer for every small authoring change.

### AGENTS.md and the Agent Skills project

[AGENTS.md](https://agents.md/) is repository context: commands, conventions
and local guidance, with more specific files taking precedence. It is
not a reason to package every project rule as a portable skill.

[Agent Skills creator guidance](https://agentskills.io/skill-creation/best-practices)
favours knowledge extracted from actual work, traces and corrections.
It warns that both narrow fragments and broad catch-all skills have costs,
and that a baseline may show no added value. Apply that to this pair:
retain a coherent job per skill, route conditional references explicitly,
and judge whether the pair changes outcomes rather than assuming it does.

### Claude

[Claude's official authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
supports concise instructions, control proportional to fragility,
progressive disclosure and evaluation before extensive documentation.
Use representative tasks and avoid documenting imagined failures.

[Anthropic's skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
combines creation and iteration, uses baseline comparisons and examines
traces for unnecessary work. Its evaluator and reviewer machinery is
useful when warranted, but importing its full harness would duplicate
our existing runner and make the skill less portable. Broad, deliberately
pushy trigger descriptions also need balancing against near-miss cases.

### OpenAI

[OpenAI's skill eval guidance](https://developers.openai.com/blog/eval-skills)
treats a run as prompt, trace, artefacts and checks. Selection, outcome,
process and efficiency are separate questions; a polished final response
does not prove the required actions happened. Record those distinctions
in the authoring reference and in the review report.

[OpenAI's guidance on revisiting skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
warns about broad descriptions, over-prescriptive itineraries and repeated
approval language that causes unnecessary stops. Use precise triggers
and preserve existing user authorisation. Treat model-specific advice as
context rather than proof that every supported harness behaves the same.

### An existing introspective skill

[szelemeh/skills self-improve](https://github.com/szelemeh/skills/blob/main/skills/self-improve/SKILL.md)
is a small retrospective: find session friction, trace its cause, and
propose a durable fix in the appropriate part of the setup. The useful
addition is choosing the correct home for a correction, instead of always
adding a skill rule. Its broad session-wide scope and demand to account
for every friction point are unsuitable as an implicit workflow here.
Use its idea as a comparison, without copying its implementation.

## Implementation and verification

Both skills start at 0.1.0 and enter bundle 0.1.1. Their MIT licences retain
GitLab's notice. They have no harness-specific metadata, hooks, mandatory
subagents or automatic writes to installed copies.

Local fixtures exercise creation from a concrete runbook, a minimal repair,
declining an unnecessary skill, read-only review, environment diagnosis and
a negative trigger. Selection indicators are reported separately from
task checks. The fixtures are small probes, not proof across domains or
environments. Checks on words in a generated file or response need trace
inspection to ensure they reflect the intended behaviour.

The [evaluation report](authoring-skills-evaluation.md) records actual run
results and limitations: the final fixtures pass in both arms and show no
measured uplift. The pair is
also used to assess its own draft against this brief: the authoring work
produces the files, and a subsequent static review checks scope, discovery,
licensing, packaging and the honesty of behavioural claims. That pass has
the author's context and is not an independent benchmark.
