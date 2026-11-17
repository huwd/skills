# Design of the repo-ci skill

This note is for contributors maintaining `repo-ci`. It records the scope
and policy choices for [issue #26](https://github.com/huwd/skills/issues/26)
and the evidence behind them. Evaluation results are recorded separately.

## The job

`repo-ci` sets up continuous integration for a new or existing repository
the same way each time: read-only workflows, one job per check, every
third-party action locked to a verified commit, and Dependabot keeping those
commits current. It also checks an existing setup's pins on request.

The skill came from setting up CI for a repository by reusing another
repository's workflow. The copied pins had to be checked against their
release tags by hand. A pin copied from another workflow, or recalled from
memory, can be wrong while its version comment looks right. The skill
resolves every commit from the upstream tag through the GitHub API instead.

## Lock with the workflow dependency lockfile

GitHub's [`gh actions-lock`](https://github.com/github/gh-actions-lock)
extension writes `.github/workflows/actions.lock`. It records the commit,
owner ID and repository ID for each direct and transitive action. The
runner checks the lockfile again at job start, and Dependabot updates the
lockfile in the same pull request as the workflow.

The skill uses the lockfile by default. It is the only approach that pins
transitive dependencies, and repository IDs detect a deleted and recreated
repository that a commit SHA alone would not.

Trade-offs accepted in November 2026:

- No GitHub documentation page states a release stage for the lockfile.
  The extension was first published in April 2026 and is at v0.4.1, and
  its lockfile format is `v0.0.3`.
- Whether organisations on every plan can enforce the "Require lockfile"
  policy is not documented. Its Evaluate mode is GitHub Enterprise Cloud
  only. Repositories without the policy still get the runner's check.
- GitHub Enterprise Server is not supported. On that platform the skill
  falls back to commit SHA pins.

## Pin what the lockfile does not cover

The lockfile does not lock reusable workflows called at
`jobs.<job_id>.uses`, container images, or local `./` actions. The skill
pins reusable workflow calls to a full commit SHA with the version in a
trailing comment, and container images to an `@sha256:` digest. It
resolves both from the upstream source, never from another repository.

When it checks pins, the skill reports the latest release and the release
dates alongside any mismatch. A repository with a Dependabot cooldown
deliberately waits for new releases, and a recent release under that wait
is not stale.

## Verify in the target repository's CI

The skill ships a verify job to the repositories it sets up. One job runs
`gh actions-lock --verify`, which fails on a stale lockfile or a locked
commit that no longer verifies upstream. The skill's
`scripts/verify-pins.sh` is copied into the target repository and checks
the SHA pins that the lockfile does not cover against their tags.

A target repository then catches a hand-edited or copied pin in review,
not only at the time of setup. The cost is a copied script for each
repository to maintain, updated when the skill's version changes.

## Relax zizmor's pin audit, and check refs in the verify job

[zizmor](https://docs.zizmor.sh/audits/#unpinned-uses)'s `unpinned-uses`
audit requires a commit SHA in every `uses:` line. It does not read
`actions.lock`, so it reports every action the lockfile locks by tag. A
repository that adopts the lockfile and runs zizmor would fail CI from the
first pull request.

The skill adds `zizmor.yml` with a `ref-pin` policy for every action to
such repositories. That policy also accepts branches and partial tags,
such as `@main` or `@v7`. A lockfile locks those to a commit, but cannot
detect a lockfile change that moves a floating ref back to an older commit
in its history. `verify-pins.sh` therefore fails on any locked ref that is
not a full version tag. The verify job takes over the check zizmor gave
up, and `zizmor.yml` carries a comment saying so.

Keeping SHAs in the workflow files alongside the lockfile would satisfy
zizmor without the relaxation. It was not chosen: with the verify job
covering floating refs, the lockfile alone is enough, and workflow files
stay readable.

## Templates live in the skill

Workflow and Dependabot templates are in `assets/`. The skill is then
self-contained and installs anywhere agent-manager does, without fetching
another repository. Templates carry no commit SHAs: the lockfile or the
API supplies those when the skill runs, so a template cannot spread a
stale pin. `huwd/standards` can point to this skill rather than keep its
own copies.

## Required checks come later

The skill does not add required status checks. A required check that has
never reported blocks every merge. Once the new jobs have reported on the
default branch, a follow-up change adds them to the repository's ruleset.
This matches [decision 0003](decisions/0003-rulesets-as-code.md). The skill
names the job names to add and leaves the ruleset change to that follow-up.

## A standalone skill

`repo-ci` covers CI, pins and Dependabot only. Rulesets, decision records,
licences and AI disclosure belong to other small skills. A later repository
setup skill can compose them; that is outside this issue.

## Approval for outward actions

Writing workflow files is local. Pushing, opening a pull request and
changing repository settings or rulesets are outward actions that need the
user's explicit approval, under this repository's rule for skills.
