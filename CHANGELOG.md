# Changelog

## [Unreleased]

- technical-writing 0.3.0: plan a document's message and outline before
  drafting, keep evidence with the point it supports, inventory facts
  before restructuring, and keep corrections and small additions
  proportional.

- commit-messages 0.2.0: disclose the agent's part in commits with an
  `Assisted-by` or `Generated-by` trailer when project rules are silent,
  keep tool-added `Co-Authored-By` and leave `Signed-off-by` to the human.

- Replace do-release with managing-releases 0.2.0: record each shipped
  change under `[Unreleased]`, prepare minimal release pull requests, choose
  the bump from the recorded changes and never tag before merge. **Breaking:**
  the skill ID changes; replace `do-release` with `managing-releases` in
  agent-manager configurations.

## [0.2.0]

- Add commit-messages 0.1.0: plan reviewable commit series, use Conventional
  Commits by default and make requested commits while preserving existing
  staging, hooks and signing.

- technical-writing 0.2.0: plan new documents around their reader, purpose
  and type; keep session wording and stray instructions out of records;
  read new documents cold before finishing.

- Add authoring-skills and reviewing-skills at 0.1.0: separate authoring
  and read-only diagnosis, with local behavioural eval fixtures.

## [0.1.0]

- Publish reproducible, checksummed skill bundles through GitHub Releases
  and GitHub Pages.
- Include dependabot-pr-review, do-release and technical-writing at 0.1.0.
- Validate skill and bundle versions; publish bundle version increases after CI.
