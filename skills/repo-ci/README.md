# repo-ci

Sets up GitHub Actions CI for a repository the same way each time, and
checks the action pins of an existing setup. Workflows are read-only, with
one job per check. Every action is locked to a commit resolved from its
upstream release tag, through GitHub's workflow dependency lockfile, and
Dependabot keeps those commits current after a cooldown.

The skill never takes a commit SHA from another repository's workflow, a
template or memory. It reports any pin in its source material that does
not match its tag. It leaves required status checks for a follow-up, once
the new jobs have reported on the default branch.

## Files

- [SKILL.md](SKILL.md): setting up CI, and checking existing pins.
- [assets/ci.yml](assets/ci.yml): workflow skeleton with one job per check.
- [assets/verify-pins.yml](assets/verify-pins.yml): verify workflow copied
  into the target repository.
- [assets/dependabot.yml](assets/dependabot.yml): weekly updates with a
  cooldown and grouped minor and patch updates.
- [assets/zizmor.yml](assets/zizmor.yml): relaxes zizmor's
  `unpinned-uses` audit, which does not read the lockfile, for repositories
  that run zizmor.
- [scripts/verify-pins.sh](scripts/verify-pins.sh): checks SHA pins
  against their tags and reports release dates; copied into the target
  repository for the verify workflow.

The [design note](../../docs/repo-ci-design.md) records why the lockfile
is the default and what it does not cover. The
[eval suite](../../evals/repo-ci/README.md) defines the synthetic cases.

## Provenance

Written for [issue #26](https://github.com/huwd/skills/issues/26).
`assets/verify-pins.yml` adapts the `verify-lockfile.yml` example from
[github/gh-actions-lock](https://github.com/github/gh-actions-lock)
(MIT), adding the SHA pin job.
