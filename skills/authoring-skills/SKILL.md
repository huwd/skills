---
name: authoring-skills
description: >-
  Create or change reusable agent skills. Use when turning a demonstrated
  workflow into a SKILL.md, fixing a skill's triggering or instructions,
  or applying findings from a skill review. For assessment without edits,
  use reviewing-skills when available.
license: MIT (see LICENSE)
metadata:
  version: "0.1.0"
  source: Adapted from gitlab-org/ai/skills authoring-skills (MIT, GitLab B.V.).
---

# Authoring skills

Encode useful knowledge the agent would otherwise lack. A skill earns its
place through better task outcomes, not the amount of guidance it contains.

## Establish the change

Read the target repository's instructions, skill conventions and relevant
existing skills. Work in the source checkout; an installed or generated
copy may be overwritten on the next update. If its source is unavailable,
prepare a proposed change in the authorised workspace and state that it
has not been applied upstream.

- **New skill:** identify the repeatable job, the inputs and desired result,
  and the concrete expertise, correction or failure that motivates it.
  Reuse an existing skill if it already covers the job. A one-off command
  or ordinary model capability may need no skill at all.
- **Existing skill:** identify the smallest change supported by the user's
  request, a review finding or a recorded failure. Preserve unrelated
  behaviour. If asked to diagnose rather than edit, give findings without
  modifying files; `reviewing-skills`, if available, supports that work.

Repository-wide conventions belong in repository instructions; ordinary
explanation belongs in docs. Recommend the appropriate home when the
problem is outside the skill. Do not expand into general AGENTS.md or
CLAUDE.md authoring, catalogue audits or environment setup unasked.

## Define evidence before expanding instructions

State what the change should make an agent do differently and how to
observe it. Use the supplied runbook, correction, trace or output as
evidence; distinguish observations from your hypotheses. A missing tool
does not establish that the skill's instructions are wrong.

For a new workflow or a behavioural change, prepare a representative
scenario, a nearby case that should keep working, and a request that
should not trigger it. Keep expected outcomes independent of the proposed
wording. Use the project's existing eval framework where available.
For a spelling or link fix, a focused static check may be sufficient.

Read [references/evaluation.md](references/evaluation.md) when designing
or running behavioural comparisons. Do not turn an unavailable eval
runner into an unrequested platform project.

## Write the smallest useful skill

Write the discovery description first: capability, situations where it
applies, and a boundary only where confusion is likely. Describe the
user's job rather than listing every associated keyword. A summary of the
body alone may not explain when the skill should load.

Keep essential instructions in SKILL.md. Include the non-obvious facts,
decision points and constraints that change how the job is done; avoid
repeating general advice the model already follows. Explain why an unusual
constraint exists. Specify exact commands where correctness depends on
them, leaving judgement where several approaches work.

Add supporting files only for a demonstrated purpose:

- `references/`: substantial detail needed for a particular case. Link it
  where that case arises and explain when to read it.
- `scripts/`: repeated or fragile deterministic work. Say whether to run
  or read a helper, its inputs, dependencies and effect on state.
- `assets/`: files copied into the output, such as templates.

Keep paths relative to the skill root so the whole directory can be
distributed together. Follow the target repository's frontmatter and
version policy; do not import another catalogue's custom fields.
Declare actual runtime requirements in `compatibility` when needed.
Attribute adapted material and retain its licence notices.

## Verify the change

Run applicable spec, link, content, lint and security checks using the
repository's commands. Exercise any new or changed helper on disposable
inputs, including relevant failure paths.

For behavioural changes, compare the new version with the previous skill
on the same scenarios; for a new skill, compare with no skill. Read the
trace as well as the result. A good output reached through an unwanted
action still fails. Recheck preserved behaviour and negative triggers.
Do not weaken the expected result to make the new instructions pass.

If a change adds no observed benefit, consider removing or narrowing it.
Once the acceptance criteria pass, stop rather than adding speculative
rules. If execution is unavailable, report the limit and leave the
behavioural claim unverified.

## Deliver within scope

Summarise the evidence, change, affected files, check results and remaining
uncertainty. Include version and release metadata required by the target
repository. Distinguish a successful file check from an executed workflow.

Do not edit installed skills, persistent memory or unrelated repository
instructions as a side effect. Committing, pushing, publishing or opening
an upstream contribution needs explicit user authorisation; existing
authorisation for that action remains valid.

## Contributing improvements

This skill is maintained in [huwd/skills](https://github.com/huwd/skills).
Bring a reproducible failure or correction to that source repository;
keep the proposed fix focused and respect the user's publication scope.
