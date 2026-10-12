# 0004. Install skills from versioned bundles on GitHub Pages

- **Status:** Accepted
- **Decided by:** @huwd
- **Decided:** 2026-10-12
- **Recorded:** 2026-10-12
- **Discussion:** #17

## Summary

In the context of installing this repository's skills into several agent
harnesses with agent-manager, facing install names that every other route
prefixes (`github.com~huwd~skills~technical-writing`), the decision was for
a reproducible bundle per release, attached to a GitHub Release and served
from GitHub Pages with no discovery document, installed headless with a
pinned agent-manager, and against installing from the git repository,
publishing a discovery document, or hand-made symlinks, to achieve
versioned, checksummed installs under the skills' own names, accepting a
dependency on agent-manager's fallback for sources with no discovery
document.

## Context

Phase 3 of `docs/plan.md` installs the skills with agent-manager. Trying
each route with agent-manager 1.23.1, in scratch home directories:

| Route | Installed as | Notes |
| ----- | ------------ | ----- |
| GitHub repository (`huwd/skills`) | `github.com~huwd~skills~technical-writing` | Tracks `main` or a pinned commit |
| Repository with `.agents/discovery.json` | `github.com~huwd~skills~technical-writing` | The discovery name doesn't change git install names |
| HTTP bundles with a discovery document | `huwd-skills~technical-writing` | Discovery sources are always namespaced |
| HTTP bundles, no discovery document | `technical-writing` | agent-manager's headless fallback for bare bundles |

Claude Code names a skill after its directory, so the namespaced routes
make `/technical-writing` unusable. A headless session listed the skill as
`github.com~huwd~skills~technical-writing`. Automatic triggering from the
description still works on every route.

Two agent-manager bugs shaped the choice; both are to be reported upstream:

- `/tree/<ref>` pins keep only the first path segment, so branches such as
  `feat/x` can't be pinned.
- HTTP discovery documents are looked up at the root of the origin, ignoring
  the base URL's path. On GitHub Pages this repository is served under
  `/skills/`, so agent-manager looks for a discovery document at
  `https://huwd.github.io/` instead of under the project path. The origin
  must remain free of a discovery document for the fallback to apply.

## Options considered

### Bundles on GitHub Pages, no discovery document (chosen)

`build-bundle.py` zips the tracked skill files and a manifest, reproducibly,
with a sha256 sidecar. Increasing the root `VERSION` with a matching
changelog entry creates a `vX.Y.Z` tag and attaches both to a GitHub Release
after CI passes on `main`. The Release workflow then rebuilds the Pages
site from every release's assets: one directory per version and an
`index.json`. `config/ai-skills.yml` installs from it headless.

Versioned, checksummed, and installed under the skills' own names. The cost
is relying on behaviour agent-manager documents as a legacy fallback, and on
its origin-root discovery lookup finding nothing. Pinning the agent-manager
version in the install command keeps that stable until it's deliberately
upgraded. The interactive menu needs a discovery document, so it isn't
supported.

### Install from the git repository

No release machinery: every merge to `main` ships. The install names are
the longest, and branch pins don't work.

### Bundles with a discovery document

The documented, supported route, including the interactive menu. Names are
prefixed with the source name, so `/technical-writing` still doesn't work.

### Hand-made symlinks

Short names and live edits, but nothing manages them and there are no
versions. This remains the way to work on a skill locally.

## Decision

Releases are driven by increases to the root `VERSION` on commits that
have passed CI on `main`. The workflow creates tags of the form `vX.Y.Z`
and uses the matching `CHANGELOG.md` entry as release notes. Each release's
bundle and checksum are attached to its GitHub Release, which is the
permanent record. GitHub Pages serves every released
version at `https://huwd.github.io/skills/`, rebuilt from the Releases,
with no discovery document. Machines install with
`npx @ai-agent-manager/cli@1.23.1 https://huwd.github.io/skills/ --config config/ai-skills.yml`.

## Consequences

- One release versions the combined bundle. Each skill also carries its
  own `metadata.version`; changed skill files require an increase. By
  convention, skill bumps prompt a bundle version bump and changelog entry.
  Independent publication would need one bundle source per skill; revisit
  if skills start changing at different speeds.
- Before upgrading the pinned agent-manager, check that bare bundles still
  install under the skills' own names.
- If agent-manager fixes its discovery lookup to honour the base path, this
  layout is unaffected: there's still no discovery document to find.
- A discovery document published at the root of `huwd.github.io` would
  change these install names. Keep that site free of one, or move the
  bundles to their own origin.
- Releases need Pages enabled with GitHub Actions as its source, and the
  `github-pages` environment.
