# Design of the commit-messages skill

This note is for contributors maintaining `commit-messages`. It records
the scope and policy choices for [issue #25](https://github.com/huwd/skills/issues/25),
including how commit guidance relates to the shared standards. Evaluation
results will be recorded separately from these design choices.

## One entry point

`commit-messages` covers organising a reviewable series and drafting its
messages. Both depend on understanding the diff and its purposes. Incremental
execution is conditional on the request; ordinary coding and reading history
do not start a committing workflow. This replaces the planned `atomic-commits`
skill. There is no separate orchestration skill or automatic commit hook.

Drafting, staging, committing, pushing and rewriting history have separate
effects. The request and existing authorisation determine which are allowed.
A request to draft a message authorises no index or history changes. Existing
authorisation remains valid across checkpoints; repeated confirmation is
not part of the workflow.

## Repository policy before defaults

Explicit project instructions and commit tooling take precedence over
the fallback: [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
with an imperative subject of at most 50 characters, including the prefix,
and explanatory prose wrapped at 72 characters. The length limits are this
skill's defaults, not requirements of the Conventional Commits specification.
History informs scope names and wording but cannot silently relax that
fallback. A project sets its standard in agent instructions, a linked
maintained guide or commit tooling. Conflicting explicit rules need resolution.
The skill does not add an enforcement hook or CI rule.

The [shared commit standards](https://github.com/huwd/standards/blob/main/standards/CLAUDE.md#commit-standards)
already require Conventional Commits, a 50-character subject and a body
for non-trivial changes in this catalogue. The skill does not replace that
source of truth. Commit messages are technical writing: their reader needs
the concrete change, its reason and relevant effects without the authoring
conversation. Validation claims and issue links require evidence.

## Reviewable steps before message formatting

The series is part of the explanation. The agent identifies purposes and
dependencies across the whole relevant diff, proposes complete units and
orders them for a reviewer. Tests and documentation belong with the change
they explain. Mechanical preparation is separated from behaviour when that
reduces the complexity of reviewing each step; related changes are not split
merely to meet a size target. File boundaries and development chronology
do not define the review units.

The original split fixture supplies two independent groups. A further
mixed-file case tests discovering boundaries without those hints, separating
preparation from a dependent feature, and validating every intermediate state.
History cleanup can improve that explanation but still needs authorisation;
planning a sequence does not implicitly authorise rebasing or force-pushing.

## Test checkpoints and failed validation

The shared standards require red, green and refactor commits. That differs
from the One Login workflow's requirement that every commit passes checks.
The skill's normal default is a passing logical unit, including its tests.
An explicit repository requirement for a red checkpoint takes precedence:
the expected assertion failure is recorded honestly, unrelated checks still
run, and hooks and signing remain in force. Unexpected failures, missing
required tools and rejected hooks are not red checkpoints. No tests are
disabled or marked pending to disguise failure. Merge gates remain green.

Where project instructions themselves conflict, the agent reports that
specific conflict rather than inventing an exception or bypassing a hook.
Absent checks are reported as absent; unavailable checks are not passes.

## Preserve the index as well as the files

An existing index may contain user work unrelated to the requested commit.
The working copy may also differ from its staged snapshot. Selective staging
and a final state check protect both. In particular, committing a working-copy
path is not equivalent to committing that path's staged blob. A subset commit
must not sweep unstaged edits or other staged paths into history.

## Sources and reuse

- [GitLab commit-messages 1.0.3](https://gitlab.com/gitlab-org/ai/skills/-/tree/7124241490817d2bd690dff89887b129befe7884/skills/commit-messages),
  including `COMMIT_FORMAT.md`, `ATOMIC_COMMITS.md` and `COMMON_MISTAKES.md`,
  informs convention discovery, rationale, references and coherent commits.
  Its MIT notice is retained. The local fallback uses 50 rather than 72
  subject characters and requires Conventional Commits in silent projects.
  File count and the word "and" are clues, not split rules.
- [GOV.UK One Login incremental-commits](https://github.com/govuk-one-login/agent-skills/tree/52bafe92e12dedf4a9b06c97fdcb166b80b576f7/skills/incremental-commits)
  and its `references/sources.md` inform opt-in checkpoints, validation and
  staged-diff review. No licence declaration was found in the reviewed tree
  on 14 November 2026. Its text is not copied. Mandatory repeated approval
  and unconditional rejection of red checkpoints are not adopted.
- [GDS's Git guidance](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/working-with-git.html#commits)
  and [Joel Chippindale's talk](https://blog.mocoso.co.uk/posts/talks/telling-stories-through-your-commits/)
  inform the emphasis on coherent steps, dependency order and reviewing a
  prepared history. Their ideas are discussed in original wording; no article
  text or worked example is copied.

## Evaluation approach

The existing Codex adapter will compare fresh sessions with and without the
skill. Trusted local graders will inspect git history, staged blobs, working
files and hook/check records, alongside the transcript. Cases cover drafting,
project overrides, unrelated changes, existing staging, validation failures,
red checkpoints, hook rejection and negative triggers. Known bad states and
valid alternatives will exercise the graders before instruction changes.

The fixtures are synthetic. Rationale and the usefulness of a proposed split
also need a recorded human assessment. Passing checks alone will not be
reported as evidence that the skill adds value.
