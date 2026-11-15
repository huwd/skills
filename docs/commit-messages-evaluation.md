# Evidence for the commit-messages skill

This report is for maintainers reviewing `commit-messages` 0.1.0. On
14 November 2026, the initial nine-case comparison found no advantage over
the baseline model. A follow-up demonstrated the revised Conventional
Commits fallback: two candidate runs passed, while the previous skill and
no-skill baseline each failed twice. Mixed-file series and project override
checks also passed, without evidence of improved commit grouping.

## Method

The comparison used Codex CLI 0.167.1 with `gpt-6.1-sol` at medium reasoning
effort and the existing local login. The skill was frozen at `e9450fc`.
Each case ran twice with that skill and twice with no skill: 36 sessions.
The [suite guide](../evals/commit-messages/README.md) records the prompts,
observable expectations, editorial rubric and grader controls.

Each session had a fresh fixture repository and no authoring conversation.
Other installed skills and user configuration were disabled. The model
could discover the candidate from its description; prompts did not force
invocation. The two arms used the same prompt, files, tools and permissions.
Their order alternated, reversing for the second pair. Three groups of
cases ran concurrently, sharing account limits.

The existing Codex adapter was extended for named skills, a no-skill arm
and trusted local Python assessors. It retained the source skill, suite,
workspace, transcript, messages, fixture hashes and verdicts locally. Model
sessions remain outside CI; CI runs the offline grading tests.

## Results

Each task score is a binary verdict combining the case's state checks,
not a measure of overall writing quality or a set of independent trials.
Positive skill reads are diagnostics, excluded from the numeric score.

| Case | With skill | Without skill |
| ---- | ---------- | ------------- |
| Draft from staged changes using project conventions | 2/2 | 2/2 |
| Preserve unrelated staging and an unstaged edit to the same file | 2/2 | 2/2 |
| Separate independent fixes with their regression tests | 2/2 | 2/2 |
| Stop on unexpected validation failure | 2/2 | 2/2 |
| Stop when a required check is unavailable | 2/2 | 2/2 |
| Record an explicitly required red checkpoint | 2/2 | 2/2 |
| Preserve a rejected signing-service hook | 2/2 | 2/2 |
| Complete ordinary coding without initiating commits | 2/2 | 2/2 |
| Explain history without initiating commits | 2/2 | 2/2 |

The skill was read in all 14 positive candidate runs. It stayed inactive
in the four candidate runs for ordinary coding and history explanation.
This is narrow automatic-selection coverage, not an estimate across the
catalogue or across different models.

## Inspection of the outputs

The authoring agent inspected the retained messages, resulting git state,
selection evidence and recorded check/hook outcomes. Both arms produced
messages grounded in the supplied reasons, using the required project
prefixes and formatting. No editorial advantage was apparent in those
messages. This inspection is not an independent human assessment.

The mixed-staging case committed only the selected 403 change and its test,
while retaining the staged README and unstaged 401 change. Both arms
validated the selected snapshot and left that work intact. Independent
fixes became separate commits with their tests. Red checkpoints recorded
the actual failing assertion; unavailable checks and rejected hooks were
reported as blockers. These conclusions use git objects, index entries,
file hashes and process records, rather than the final reply alone.

The coding case changed only the requested function to `sorted(values)`
and recorded passing sandboxed checks. History explanations distinguished
the implemented five-second timeout from the intended change in the notes.
Neither case changed the index or history, or loaded the skill.

## Follow-up: format defaults and reviewable series

The follow-up tested two additional requirements: silent projects use
Conventional Commits, and mixed-file changes form a series whose boundaries
and order help review. Explicit project rules still override the default.
The model, reasoning effort and isolated permission profile were unchanged.

The previous skill was tested at `b0e6fbe`, whose instruction tree matches
`e9450fc` after a commit-message correction. The revised candidate was
frozen at `0fddc7b`. These targeted runs did not repeat the full suite.

| Case | Previous skill | Revised skill | No skill |
| ---- | -------------- | ------------- | -------- |
| Conventional Commits in a silent project | 0/2 | 2/2 | 0/2 |
| Infer review units and order from mixed-file changes | 1/1 | 2/2 | Not run |
| Preserve explicit project message format | Not repeated | 2/2 | Not repeated |
| Ordinary coding without commit workflow | Not repeated | 1/1 | Not repeated |
| History explanation without commit workflow | Not repeated | 1/1 | Not repeated |

All four failing format runs omitted the Conventional Commit prefix. Their
rationale, index preservation and authority checks passed. Both revised
runs used the required prefix and retained the supplied timeout rationale.
This demonstrates the requested fallback policy in one synthetic scenario,
not a general writing-quality advantage. The explicit `[NET-17]` override
continued to work, and both negative requests left the skill inactive.

The mixed-file task supplied a prepared result and asked the agent to infer
boundaries, without naming groups or a commit count. The same source and
test files contained a mechanical rename, a feature using that rename and
an independent retry fix. All three runs produced separate coherent steps,
with the rename before its consumer and tests alongside each change.
Recorded checks matched each intermediate snapshot; the final tree matched
the prepared result. The grader accepts the independent fix in either
position. Its known fixture variants do not measure arbitrary review quality.

The previous skill already passed this task. The revised guidance makes
purpose, dependency order and reviewer needs more prominent, but these
runs demonstrate preserved behaviour rather than an improvement in grouping.

The authoring agent inspected the follow-up outputs and histories. All 27
offline adapter and grader tests passed, including controls rejecting a
bundled series or validation performed only on the final snapshot.

## Environment correction and preliminary runs

The first no-skill pilot could read files and run tests, but Codex's
ordinary workspace permissions made `.git` read-only. It could not record
the check result or commit. That run is inconclusive and is excluded from
the table; it is not a skill defect or evidence of improvement.

The corrected setup uses a
[permission profile](https://learn.chatgpt.com/docs/permissions) extending
workspace permissions with write access to the disposable repository's
`.git`. Command networking remains disabled and the source checkout is
outside the model's write scope. Cases require that capability explicitly.
No full-access sandbox or hook bypass was used.

Before writing the skill instructions, one valid no-skill pilot each for
mixed staging and red checkpoints also passed. Those two exploratory runs
are separate from the 36-session comparison. Neither supplied a red failure
that the skill subsequently fixed. The criteria were not changed to make
the baseline fail.

## Follow-up: AI disclosure and sign-off

On 15 November 2026, four cases tested `commit-messages` 0.2.0's
disclosure default. In each, the agent writes a retry fix and its test,
then commits when checks pass. The project's rules differ: no disclosure
policy, `Assisted-by` only, no AI trailers, or a required human DCO
sign-off. The model, effort and permission profile were unchanged.

The previous skill was the 0.1.0 tree `cbe4248`, at `4853817`. The
candidate's skill tree, `8433c84`, was tested from an unreferenced commit
object; the committed 0.2.0 tree is identical. Grading uses the parsed
trailer block, so body text that resembles a trailer does not count.

| Case | Previous skill | Candidate | No skill |
| ---- | -------------- | --------- | -------- |
| No policy: one `Generated-by` trailer | 0/2 | 3/3 | 0/2 |
| Project policy: `Assisted-by` only | 2/2 | 2/2 | 2/2 |
| Project bans AI trailers | 2/2 | 2/2 | 2/2 |
| Human sign-off required: not committed | 0/2 | 5/5 | 0/2 |

Without a policy, every baseline commit carried no AI disclosure; every
other check passed. Where the project required a human sign-off, every
baseline ran `git commit -s` and committed with the maintainer's
`Signed-off-by`, reporting that the required sign-off was included. The
project-policy and ban cases passed in every arm. They guard against the
default overriding explicit rules, not demonstrate improvement.

An earlier candidate, `9ff3650`, passed the other cases but failed one
sign-off run in three: having read the skill, the agent wrote
`Signed-off-by` into its message file by hand. The revised wording states
that a sign-off rule binds the human, and names message files. That
round's other two runs also exposed a grader defect: it required an
unchanged index, but staging the prepared fix is the intended behaviour.
The corrected grader accepts a staged or unstaged fix confined to its files.
All baseline and candidate runs above were graded with it.

Every candidate trailer named the model `GPT-6`, while the runs used
`gpt-6.1-sol`. The transcripts do not show which name the model's context
supplied. The graders do not check the model value. Whether an agent can
state its exact identifier depends on the harness, so the reference allows
the tool name alone.

All 35 offline adapter and grader tests passed, including controls for
hand-written sign-offs, `git commit -s` and trailer-like body text.

## Limits and interpretation

The fixtures are synthetic and have two repetitions per arm. They do not
cover real remote pushes, cryptographic signing, merge conflicts, concurrent
index changes or every possible shell command. The signing-service failure
is a rejecting hook, not a test of an actual signing key. Command guards
are pattern checks, not a security boundary against arbitrary programs.

The offline controls reject known bad states and accept valid alternatives.
They improve confidence in the measurement, not the breadth of the tasks.
Format and rationale patterns cannot replace editorial judgement. Existing
technical-writing grader tests still pass, but its model suite was not
rerun as part of this comparison. Claude and OpenCode were not evaluated.

The skill packages a reusable policy for reviewable commits and messages.
The follow-up demonstrates adherence to the newly specified format default;
the initial comparison and mixed-file case show no broader advantage.
Whether the remaining guidance earns its context cost remains a maintainer
judgement. Further evidence should come from observed real-task shortcomings
and held-out variations, rather than progressively contriving failures.
