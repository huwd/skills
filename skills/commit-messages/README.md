# commit-messages

Organises requested changes into self-contained, ordered commits that make
review easier, and writes messages from the relevant diff. It follows project
rules, preserves existing staging and keeps planning or drafting separate
from permission to change history. Ordinary coding and reading history do
not initiate commits.

Conventional Commits with 50/72 formatting are the fallback unless explicit
project rules choose otherwise. A project can set its standard in agent
instructions or a linked guide and commit tooling. Old history alone does
not override the fallback. This skill does not install an enforcement hook.

Commits an agent prepares disclose its part with an `Assisted-by` or
`Generated-by` trailer unless project rules say otherwise. The agent
never adds a human `Signed-off-by`.

This skill is unreleased. For local development, follow the
[development symlink instructions](../../docs/skill-format.md#development-symlinks),
using `commit-messages` as the skill directory name. A later bundle release
will make it available through agent-manager.

## Files

- [SKILL.md](SKILL.md): scope, message drafting and requested commit workflow.
- [references/index-and-checks.md](references/index-and-checks.md): mixed
  staging, validation failures and explicit red checkpoints.
- [references/reviewable-series.md](references/reviewable-series.md): logical
  units, dependency order and authorised history cleanup.
- [references/ai-disclosure.md](references/ai-disclosure.md): the default
  AI disclosure trailers, sign-off boundary and their trade-offs.
- [LICENSE](LICENSE): MIT terms and retained upstream notice.

The [design note](../../docs/commit-messages-design.md) explains the policy
choices. The [eval suite](../../evals/commit-messages/README.md) defines the
synthetic cases and their limits. Passing those cases is not proof that
the skill improves a capable model's results.

## Provenance

Adapted from [GitLab commit-messages 1.0.3](https://gitlab.com/gitlab-org/ai/skills/-/tree/7124241490817d2bd690dff89887b129befe7884/skills/commit-messages)
and its commit-format, atomic-commit and common-mistake references. GitLab's
MIT notice is retained. The subject fallback is 50 rather than 72 characters;
project overrides and meaningful commit boundaries take precedence over
mechanical rules about keywords or file counts. Conventional Commits are
the local fallback even when legacy history uses plain subjects.

[GOV.UK One Login incremental-commits](https://github.com/govuk-one-login/agent-skills/tree/52bafe92e12dedf4a9b06c97fdcb166b80b576f7/skills/incremental-commits)
informed the opt-in checkpoint design. No licence declaration was found at
that revision; its text is not copied. The skill preserves existing user
authorisation and explicit project TDD policies instead of requiring new
approval at every checkpoint or forbidding every red commit.

The review-series guidance also draws on
[GDS's Git guidance](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/working-with-git.html#commits)
and [Joel Chippindale's talk](https://blog.mocoso.co.uk/posts/talks/telling-stories-through-your-commits/).
It uses original wording rather than copying either source's text.

## Changelog

- **0.1.0:** first version, covering message drafts and requested commits.
