---
name: managing-releases
description: >-
  Ship changes separately from releases: record each shipped change under a
  changelog's Unreleased section, then prepare a minimal release pull request
  that only bumps the version and moves those entries, and publish through
  the repository's own mechanism. Use when committing or preparing a pull
  request for a user-facing change in a repository with a changelog, or when
  asked to prepare, cut, tag, publish or verify a release. Explaining release
  configuration does not start this workflow.
compatibility: Uses git and the repository's own release tooling; gh for GitHub releases.
metadata:
  version: "0.2.0"
  source: Rewritten from do-release 0.1.0, imported from huwd/standards.
---

# Managing releases

Changes ship separately from releases. Each change records itself in the
changelog as it merges, so `main` can run ahead of the latest release. A
release is then a small pull request that bumps the version and moves the
recorded entries under it. Publishing follows the repository's mechanism
after that pull request merges.

Release actions are outward-facing. Pushing, opening or merging a pull
request, tagging, creating a GitHub Release, dispatching a workflow and
publishing each need explicit approval. Existing approval for one of these
does not cover the others. Never print, read or store registry tokens.

## Learn the repository's process

Read the agent instructions, contribution and README release sections,
`CHANGELOG.md`, release workflows and the version sources. Find the latest
release tag with `git tag --sort=-v:refname` or `git describe --tags --abbrev=0`.
Identify:

- the release version source, and any component versions, such as
  per-package or per-skill versions, that change with their own work
- the changelog's headings, categories and date style
- what publishes: a pushed tag, CI on merging a version change, a manual
  workflow or a local command
- preflight checks that the release workflow runs

Explicit project rules override this skill. If documented steps contradict
each other or the workflow, for example a checklist that pushes to `main`
when `main` is protected, report the conflict rather than choosing one. For
ecosystem details, read [references/ecosystems.md](references/ecosystems.md).

## Ship a change

When committing or preparing a pull request for a change users would notice,
add an entry under `## [Unreleased]` in the same change:

- Follow the existing categories, such as `Added`, `Changed`, `Fixed` and
  `Removed`, or the flat list the changelog uses. Describe the effect for
  someone upgrading, not the implementation.
- Mark breaking changes clearly and say what users need to do.
- Bump component versions where the repository requires it. Never change
  the release version or move entries in an ordinary change.
- Follow the repository's practice for internal changes, such as tests and
  CI. When it is unclear, leave them out.

If the changelog has no `## [Unreleased]` section, or there is no changelog,
say so and propose adding one. Ask before adding it: it changes the
repository's convention. Do not rewrite released sections.

## Prepare a release

1. Start from an up-to-date, clean `main`. List what changed since the last
   release tag with `git log --oneline <tag>..main` and read the
   `[Unreleased]` entries. Report merged user-facing changes that have no
   entry. Add missing entries in their own change, not in the release
   pull request, unless the user decides otherwise.
2. Choose the version from the entries, not from habit:
   - major for breaking changes, including removed or renamed components
   - minor for new functionality, including new components
   - patch for fixes only

   Below 1.0.0, follow the repository's stated policy. Without one, use a
   minor bump for breaking changes and new functionality, and say so. With
   component versions, the release bump reflects the largest component
   change. State the reason for the bump, and confirm it with the user when
   it is not obvious or is a major bump.
3. On a release branch, change only:
   - the release version source
   - the changelog: insert `## [X.Y.Z]` below an empty `## [Unreleased]`
     heading, with a date when the existing sections have one, and move the
     entries across unchanged; update comparison links if the file uses them
   - files the ecosystem derives from the version and would otherwise
     leave stale, such as a lockfile's entry for the package itself

   Component versions were set when their changes shipped. Fix any other
   problem in a separate pull request.
4. Run the checks that CI and the release preflight run.
5. Commit following the project's rules, for example
   `chore: prepare vX.Y.Z release`. With approval, push and open the pull
   request. Its description gives the version, the reason for the bump,
   the release notes and what happens after merge.

## Publish after merge

Never tag before the release pull request merges, and never tag a branch
commit. Once it merges and `main` passes CI:

- **CI publishes on merge**: do not create the tag or release. Watch the
  run, then verify.
- **A pushed tag publishes**: show the tag, the merged commit, the release
  notes and the exact commands, and ask. Then create the tag on the merged
  commit, using the repository's tag format and type, push it and watch the
  workflow. Use a dry run first where the workflow supports one.
- **Manual or local publishing**: follow the documented commands. Prefer
  trusted publishing or existing CI secrets over local credentials.

Where the repository uses GitHub Releases, check that one exists for the
tag with the changelog section as its notes. Create or update it only with
approval, and only after a tag-driven publish has succeeded.

## Verify and recover

Confirm the tag on the remote, the GitHub Release and the registry version.
If indexing delays the registry, say so and give the workflow run.

If a check fails, stop before tagging. If publishing fails after a tag is
pushed, do not move or delete the tag unless the user asks. Read the logs,
fix forward, and use a new version if the failed one reached a registry.
Never reuse a published version.

## Report

Give the version and the reason for its bump, the release pull request,
the checks run, the tag and commit, the workflow result, the registry
check and the GitHub Release URL. Say which steps remain and who needs to
approve them.
