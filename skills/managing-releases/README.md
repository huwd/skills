# managing-releases

Keeps shipping a change separate from releasing it. Each change records
itself under `## [Unreleased]` in the changelog as it merges, so `main` can
run ahead of the latest release. A release is a minimal pull request that
bumps the version and moves those entries under it. Publishing then follows
the repository's own mechanism: a pushed tag, CI that tags on merge, or a
documented manual step.

The skill chooses the version bump from the recorded changes, including
component versions and pre-1.0 policy. It never tags before the release
pull request merges, and asks before every outward release action.

## Files

- [SKILL.md](SKILL.md): learning the repository's process, shipping a
  change, preparing a release, publishing and verification.
- [references/ecosystems.md](references/ecosystems.md): version sources,
  checks, tagging, GitHub Releases and registry verification for RubyGems,
  npm, Cargo, PyPI, Go modules and skill bundles.

The [eval suite](../../evals/managing-releases/README.md) defines the
synthetic cases and their limits.

## Provenance

Replaces `do-release` 0.1.0, which was imported from `huwd/standards`. The
ecosystem commands and the recovery rules are retained from it, moved into
the reference. The changelog-first workflow, pull-request releases, bump
reasoning and the rule against tagging before merge are new.
