# reviewing-skills

Reviews a skill or a requested set of skills without editing them. It
traces failures to their likely cause before recommending a change, and
distinguishes a skill defect from an unavailable prerequisite, a missed
instruction or a faulty grader.

Use `authoring-skills` when you want changes applied. The reviewer produces
evidence and a regression scenario that a maintainer can act on without
having that skill installed.

## Files

- [SKILL.md](SKILL.md): review boundaries, diagnosis and findings.
- [references/review-criteria.md](references/review-criteria.md): assessment
  criteria and examples of instruction versus environment failures.
- [LICENSE](LICENSE): MIT terms, including the upstream copyright notice.

Agent-manager installs this skill from the catalogue's versioned bundle.
Static review needs access to the skill and relevant local conventions.
It does not require running the operational workflow. Behavioural testing
is limited to authorised evaluations in disposable fixtures.

## Provenance

The review approach is informed by GitLab B.V.'s MIT-licensed
[authoring-skills](https://gitlab.com/gitlab-org/ai/skills/-/tree/605c17ffb7054415959e75347c3e33f761e54ec9/skills/authoring-skills),
its separate ADR creation and review workflows, and the primary sources
compared in [the research brief](../../docs/authoring-skills-brief.md).
It adds explicit cause diagnosis and a read-only report boundary.

## Changelog

- **0.1.0:** first version, with review, environment-diagnosis and negative
  trigger eval cases.
