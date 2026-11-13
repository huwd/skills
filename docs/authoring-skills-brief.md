# Design of the skill authoring and review workflows

This design note is for contributors maintaining `authoring-skills` and
`reviewing-skills`. The two skills were proposed in
[issue #24](https://github.com/huwd/skills/issues/24) to make the catalogue's
own maintenance practices reusable. This note explains their responsibilities
and the reasons for the split. Each skill's SKILL.md contains its instructions.

## Separate assessment from writing

Authoring produces a new skill or implements a specified change. Reviewing
assesses an existing skill and produces findings without editing it. The
distinction is the requested result, rather than whether a file already exists.

Creating and modifying share the work of writing descriptions, instructions,
references and checks. Modification also needs a defined behaviour change,
a comparison with the previous version and protection for existing behaviour.
A review adds a different question: is a skill change the right remedy at all?
A missing tool or an incorrect grader may explain the failure instead.

Separate skills let a caller request an assessment without authorising edits.
The cost is another discovery description and some shared context. Keep the
writing procedure in authoring and the diagnostic procedure in reviewing;
neither requires the other to be installed.

## Choose the workflow from the request

| Request | Workflow | Expected result |
| ------- | -------- | --------------- |
| Turn a repeatable runbook into a skill | Authoring | Skill files and eval cases |
| Fix a specified error in a skill | Authoring | A focused change with relevant checks |
| Investigate why a skill failed | Reviewing | Findings grounded in the requirements and run evidence |
| Review and improve a skill | Reviewing, then authoring | Findings followed by authorised changes and verification |

An existing file does not automatically require review first. A clear edit
can go straight to authoring. When the problem is unclear, diagnosis precedes
the fix. Both stages can belong to one task; no separate conversation or
pull request is required. Review alone stops at the findings.

## Make the review criteria explicit

The reviewer compares the skill with its intended workflow, the target
repository's conventions and the bundled authoring criteria. A user request,
brief or runbook supplies the expected inputs, outputs and constraints.
The reviewer names those sources and distinguishes missing requirements
from actual defects. A general checklist cannot establish domain correctness.

Findings identify evidence, impact, a focused remedy and a testable expected
outcome. This gives the author enough information to act without repeating
an entire assessment. The author still checks the resulting change.

## Evaluate behaviour before adding instructions

Every new skill needs workflow and discovery evals. Changes in behaviour need
regression coverage; spelling and link fixes can use focused static checks.
Existing catalogue gaps remain work to complete, not examples to copy.

Use a red, green, refactor loop: expose a shortcoming in the baseline,
make a minimal change, then simplify while preserving the expected outcomes.
Repeated runs matter because agent behaviour varies. Check the graders too:
bad outputs should fail, and valid alternatives should pass. A baseline that
already succeeds does not establish a benefit from new instructions.

The [evaluation report](authoring-skills-evaluation.md) describes the evidence
for this pair. Its small synthetic cases provide limited evidence: the report
distinguishes one observed review difference from unproven authoring benefits.

## Reuse the existing catalogue and tools

Agent-manager installs the whole skill folder from this repository's bundles.
The skills supply content and relative references; they do not add installation
adapters. Behavioural evals use the existing local Claude plugin runner, kept
outside installed skill folders, following
[decision 0001](decisions/0001-run-evals-locally.md). Release preparation is
separate from skill changes; entries stay under `[Unreleased]` until then.

## Sources that shaped the design

- [GitLab's authoring skill](https://gitlab.com/gitlab-org/ai/skills/-/tree/605c17ffb7054415959e75347c3e33f761e54ec9/skills/authoring-skills)
  supplies the starting approach to descriptions, structure and comparisons.
  Adapted material retains its MIT notice; its catalogue-specific fields
  and general instruction-file authoring scope are omitted.
- GitLab's [ADR creation](https://gitlab.com/gitlab-org/ai/skills/-/blob/main/skills/adr-create/SKILL.md)
  and [review](https://gitlab.com/gitlab-org/ai/skills/-/blob/main/skills/adr-review/SKILL.md)
  show the value of distinct outputs, but also repeat quality rules. They
  motivate explicit responsibilities here rather than two copies of a process.
- [AGENTS.md](https://agents.md/) and the
  [Agent Skills creator guidance](https://agentskills.io/skill-creation/best-practices)
  help distinguish repository conventions from reusable workflows and favour
  knowledge grounded in actual work.
- [Claude's authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
  [Anthropic's skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
  and [OpenAI's skill eval guidance](https://developers.openai.com/blog/eval-skills)
  support concise instructions and comparisons based on traces and outputs.
  Reuse their method rather than importing another evaluation framework.
- The small [self-improve skill](https://github.com/szelemeh/skills/blob/main/skills/self-improve/SKILL.md)
  contributes a useful diagnostic question: where does a correction belong?
  It does not justify automatic edits to memory or instructions after every task.
