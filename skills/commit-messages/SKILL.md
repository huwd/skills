---
name: commit-messages
description: >-
  Organise requested changes into a reviewable commit series and write
  messages grounded in the relevant diff. Use for commit planning or series
  review, message-writing requests, selective commits and requested checkpoints.
  Ordinary coding or reading history alone does not start a commit workflow.
license: MIT (see LICENSE)
compatibility: Uses git and the target repository's existing validation tools.
metadata:
  version: "0.2.0"
  source: Adapted from gitlab-org/ai/skills commit-messages 1.0.3 (MIT, GitLab B.V.).
---

# Reviewable commits

Help the reviewer understand a change through coherent steps and useful
messages. Each commit has a clear purpose; the series explains how those
steps fit together. Messages describe what will actually be committed.
Planning or drafting can leave git state untouched. Executing the plan
depends on the requested workflow and existing authorisation.

## Establish scope and project policy

Read repository instructions, commit tooling and recent messages before
choosing a format. Explicit project rules and configured commit tooling
override the defaults below. History informs scope names and wording, but
does not silently replace Conventional Commits when no format is stated.
Include hooks, signing, attribution and sign-off policies. A project's AI
disclosure rules override this skill's default; adding a trailer to a commit
does not write a policy into the repository. Repository instructions can state
the standard directly or point to its maintained guide. Report conflicting
explicit requirements rather than guessing which to ignore.

Distinguish the permission to draft, stage, commit, push and rewrite history.
Drafting alone does not authorise an index change or commit. Existing user
authorisation remains valid across checkpoints; do not repeatedly ask for
the same action. Project workflow instructions do not expand the user's
authorisation. A request to commit is not permission to push or rewrite.

Inspect status, the staged diff and relevant unstaged changes. Identify
which work belongs to the request and what was already present. When
preparing a commit, its selected staged snapshot is the message's source,
not the union of staged and unstaged changes. Read supplied context for the
reason; ask only when missing information would materially change the record.

## Draft the message

Commit messages are technical writing. The reader has the commit and its
links, not the authoring conversation. Name the concrete change, explain
why it is needed and describe relevant effects or limitations. Do not
invent a motivating incident, measurement, test result or issue reference.

Without explicit project-format rules, use Conventional Commits:

- Start with `<type>[optional scope][!]: <description>`, for example
  `fix(parser): preserve empty fields`. Choose the type from the actual
  change. Mark a breaking change only when the evidence supports it.
- Keep the subject specific and imperative, at most 50 characters including
  the prefix, with no final full stop. Explicit project rules may choose
  another format or limit; old unprefixed messages alone are not that rule.
- Separate an explanatory body from the subject with a blank line. A
  non-trivial change needs its reason, not a restatement of the diff.
  Wrap prose at 72 characters; keep indivisible URLs and identifiers intact.
- Follow the project's reference and trailer format. Use a supplied full
  issue URL when no shorthand convention is established. A reference does
  not replace an explanation. Never invent a human sign-off or attribution.
- When you wrote or materially shaped the change, disclose it as the
  project says. Without project rules, add one `Generated-by` or
  `Assisted-by: <tool>:<model>` trailer, with the model identifier exactly
  as your context states it or the tool alone. Keep a tool-added
  `Co-Authored-By`; see [references/ai-disclosure.md](references/ai-disclosure.md).
  Disclosing your own part is not inventing attribution.
- Never add `Signed-off-by`, whether in a message file or with
  `git commit -s`. A project rule requiring sign-off binds the human; it
  does not ask you to add their name. Leave that change uncommitted, with
  its drafted message, and say why.

Report validation only when observed, and distinguish the working copy
from the selected commit snapshot. If the reason is unknown, state that
gap rather than turning a plausible story into recorded history.

## Arrange requested commits

Before staging a mixed change, identify its distinct purposes and their
dependencies. Propose the commits in the order a reviewer should read them,
with the change and reason for each, included paths or hunks, and relevant
checks. A series should reduce the amount the reviewer has to understand
at once, rather than reproduce the order of editing sessions.

Prefer the smallest complete step that makes sense independently. Keep a
fix with its regression test and relevant documentation. Separate mechanical
preparation from behaviour changes when that makes review clearer; put
required preparation before its consumers. Independent concerns can appear
in the same file, and one coherent change can span many files. File count,
line count and the word "and" are clues, not mechanical split rules.

For mixed concerns, dependencies or an existing noisy feature history,
read [references/reviewable-series.md](references/reviewable-series.md).
Respect explicit project red/green checkpoints; the normal default is a
usable, passing step. Do not create a broken intermediate commit merely to
make the series look smaller.

For requested incremental work, discover validation commands once and
validate at useful logical boundaries. Stage selectively and inspect the
complete selected diff, including unexpected staged paths. Preserve user
work in both the index and working copy.

When only part of the index belongs to the commit, or the same file has
unstaged edits, read [references/index-and-checks.md](references/index-and-checks.md).
In particular, `git commit --only PATH` takes that path from the working
copy, not necessarily its staged blob. Do not use it to sweep unfinished
edits into a supposedly staged-only commit.

Run checks on the intended snapshot. A passing working-copy check does not
verify different staged contents. Required checks normally need to pass;
an unavailable tool, unexpected failure or rejected hook is a blocker.
Read the reference for explicit red-checkpoint policies and absent checks.
Do not disable tests, hooks or required signing to manufacture a pass.

## Commit and verify within authorisation

If committing is authorised and the relevant policy is satisfied, commit
the selected change using the project's hooks and signing. For a multiline
message, a temporary message file avoids shell quoting changing its text.
Do not amend earlier commits as a side effect.

Inspect the resulting commit and status. Check its actual contents against
the selected snapshot and confirm unrelated staged and unstaged work
survived. Read the series as a reviewer: do its messages and diffs explain
one step at a time, in dependency order, without fixup noise? Recommend
folding corrections into the commits they repair, but execute history
changes only when authorised. Report the commit ID, checks and remaining
work accurately. If
the task was drafting or proposing boundaries, deliver those results and
leave git state unchanged. Pushing and history rewriting require their
own authorisation, including any authorisation already given.
