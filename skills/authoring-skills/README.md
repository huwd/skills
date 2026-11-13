# authoring-skills

Creates or changes a reusable skill from concrete expertise, a demonstrated
failure or a review finding. It follows the target repository's conventions
and tests behavioural changes against a baseline. It can also recommend
that no skill is needed.

Use `reviewing-skills` for assessment without edits. The two skills install
independently: an author can work from a supplied finding, and a reviewer
can give a useful report without an authoring skill present.

## Files

- [SKILL.md](SKILL.md): the authoring and change workflow.
- [references/evaluation.md](references/evaluation.md): behavioural comparisons.
- [LICENSE](LICENSE): MIT terms, including the upstream copyright notice.

Published in this catalogue's versioned bundle for agent-manager, which
installs the whole skill folder into the selected tools' locations. The
skill adds no installation adapters. Verification uses the target
repository's tools; behavioural evaluation uses its existing local runner.

## Provenance

Adapted from GitLab B.V.'s MIT-licensed
[authoring-skills](https://gitlab.com/gitlab-org/ai/skills/-/tree/605c17ffb7054415959e75347c3e33f761e54ec9/skills/authoring-skills).
Descriptions, progressive disclosure and evaluation guidance were
synthesised with the official sources linked in
[the research brief](../../docs/authoring-skills-brief.md).
The upstream custom fields, OpenCode requirements, instruction-file
authoring and automatic contribution procedure are not imported.

## Changelog

- **0.1.0:** first version, with local creation, repair and no-skill eval cases.
