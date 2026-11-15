# Release-workflow evals

This suite is for contributors checking the `managing-releases` skill. It
compares the resulting git state with and without the skill, and with the
`do-release` skill it replaced. The fixtures are synthetic repositories with
no remote, so no push, registry or GitHub Release is exercised.

The [evaluation report](../../docs/managing-releases-evaluation.md)
records the completed comparison and its limits.

## Run the comparison

From the repository root, using Python with PyYAML and a saved Codex login:

```bash
python3 evals/run-codex.py --suite managing-releases \
  --case release-tag --ref HEAD --ref none --runs 2 \
  --allow-fixture-git --model gpt-6.1-sol --effort medium
```

Repeat for the case names below. To measure the replaced skill, add
`--skill do-release` and a ref that still contains it, such as `4853817`.

## Cases and observable expectations

| Case | Fixture | Expected result |
| ---- | ------- | --------------- |
| `ship-change` | Python package released by pushing a tag, with entries already under `[Unreleased]` | The bug fix, its test and a new `[Unreleased]` entry are committed on a branch. The release version, earlier sections, `main` and the tags are unchanged. |
| `release-tag` | The same package with an `Added` and a `Fixed` entry since `v1.2.0` | A release branch changes only `pyproject.toml` and `CHANGELOG.md`: version 1.3.0, a dated `## [1.3.0]` section below an empty `[Unreleased]`, earlier sections unchanged. No tag is created, because tagging follows merge. |
| `release-ci` | Skill catalogue whose CI tags when `VERSION` changes on `main`, with a new skill and a skill fix since `v0.2.0` | A release branch changes only `VERSION` and `CHANGELOG.md`: version 0.3.0 for the new skill, entries moved under `## [0.3.0]`. No skill version changes and no tag is created. |
| `explain-only` | The tag-driven package | Explaining the release workflow changes no files, branches or tags and does not load the skill. |

`fixture.py` builds each repository and saves its initial head, tags and
changelog outside the model's working directory. `assess.py` reads the one
new branch, its diff from the initial head, the changelog sections, the tags
and the command transcript. It does not run model-produced code; the
`ship-change` case relies on the sandboxed check log for the tests.

The command guard rejects `git push`, creating a tag, `gh release create`,
`twine upload` and `--no-verify`. It recognises ordinary direct and chained
commands, not arbitrary shell programs. The checks do not judge the wording
of changelog entries or pull request descriptions; read the diffs as well.

## Check the graders

```bash
python3 -m unittest discover -s evals/tests -v
```

The controls accept a minimal release in each fixture, with or without a
date in the catalogue's undated style. They reject a missing changelog
entry, a version bump in an ordinary change, committing to `main`, a tag
before merge, a patch bump for new functionality, entries left under
`[Unreleased]`, unrelated edits in a release, a rewritten earlier release,
a skill bump in a release and a missing `[Unreleased]` heading.
