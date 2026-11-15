# Evidence for the managing-releases skill

This report is for maintainers reviewing `managing-releases` 0.2.0, which
replaces `do-release` 0.1.0 for
[issue #35](https://github.com/huwd/skills/issues/35). The new skill
recorded a shipped fix under `[Unreleased]` in every run; neither
`do-release` nor no skill did so in any run. Both baselines already
prepared minimal release pull requests, so those cases show preserved
behaviour, not improvement.

## Method

The comparison used Codex CLI 0.167.1 with `gpt-6.1-sol` at medium
reasoning effort on 15 November 2026. `do-release` was tested from
`4853817`. The candidate's skill tree, `f2431b6`, was tested from an
unreferenced commit object; the committed tree is identical. The
[suite guide](../evals/managing-releases/README.md) records the fixtures,
expected results and grader controls.

Each session had a fresh synthetic repository with no remote. A trusted
local assessor read the new branch, its diff, the changelog sections, the
tags and the command transcript. Model-produced code was not run outside
the model's sandbox.

## Results

| Case | `do-release` | Candidate | No skill |
| ---- | ------------ | --------- | -------- |
| Ship a fix with an `[Unreleased]` entry | 0/2 | 3/3 | 0/2 |
| Minimal release PR, tag-driven package | 2/2 | 3/3 | 2/2 |
| Minimal release PR, CI tags on merge | 2/2 | 3/3 | 2/2 |
| Explain the release workflow without changes | 2/2 | 3/3 | 2/2 |

Every baseline fix was correct, tested and committed on a branch, but left
the changelog untouched, although the file already had entries under
`[Unreleased]`. Every candidate run added a `Fixed` entry describing the
effect for users, without changing the release version.

In the release cases, every run in every arm changed only the version
source and the changelog, chose the expected minor bump and created no tag.
Candidate runs matched each changelog's date style: dated for the package,
undated for the catalogue. The skill loaded in all nine workflow runs and
in none of the explanation runs.

## Corrections to the measurement

The first baseline had two grader and fixture defects, both corrected
before the candidate runs:

- The command guard treated `git tag -n`, a listing command, as creating a
  tag. Re-grading cleared two apparent failures; no run created or pushed
  a tag.
- The catalogue fixture's required check found no tests, so it failed.
  Both `do-release` runs added tests to make it pass, which the grader
  counted as unrelated release edits. The fixture now includes a test
  module, and the catalogue baseline was rerun: 4/4 passed.

Controls for listing and creating tags, and the fixed fixture's check, are
part of the offline grader tests.

## Limits

The fixtures have no remote, so pushing, opening pull requests, merging,
tag-driven publishing, GitHub Releases and registry verification were not
exercised. Those steps rely on the skill's instructions and its approval
rules, which these cases do not test. The graders check state, not the
wording of changelog entries or pull request descriptions.

The release-preparation cases show no advantage over the baseline. Their
value is regression coverage for the rewrite and rename. Two or three
repetitions per arm are a small sample. The Ruby libraries named in the
issue were not tested directly; their tag-driven model is represented by
the synthetic Python package. Claude and OpenCode were not evaluated.
