# Evidence for the authoring and review skills

This report is for maintainers reviewing
[PR #27](https://github.com/huwd/skills/pull/27). It explains what the local
evals measure and whether their results justify accepting the two skills.
The current evidence supports basic behaviour checks, but does not demonstrate
that the skills improve results over an agent working without them.

## What was tested

The six cases exercise writing a skill, making a specified correction,
declining an unnecessary skill, reporting review findings without edits,
diagnosing a missing tool and reading a skill without initiating review.
They are synthetic fixtures authored for this PR, not recorded production
incidents. In particular, the failure transcript in the retry case was written
as test input; it is not evidence of a failure observed in a real deployment.

The [eval guide](../evals/README.md) maps each case to its checks and explains
the source and format of the graders. They primarily examine generated text
and recorded tool calls. They do not execute the skill produced by the
authoring case to establish whether that new skill behaves correctly.

## Recorded comparison

The original draft at `508689f` was evaluated on 13 November 2026 with Claude
Code 2.1.318 and model `claude-opus-5-5`, using the local subscription. Each
case ran three times with the plugin and three times without: 36 sessions.
Positive selection indicators were reported separately from task scores.

| Case | With plugin | Without plugin |
| ---- | ----------- | -------------- |
| Create from a ledger export runbook | 1.00 | 1.00 |
| Decline an unnecessary skill | 1.00 | 1.00 |
| Repair a retry instruction | 1.00 | 1.00 |
| Diagnose a missing prerequisite | 1.00 | 1.00 |
| Read without initiating review | 1.00 | 1.00 |
| Review trigger and authority problems | 1.00 | 1.00 |

A score is the mean fraction of scored checks passed, not a measure of overall
writing quality. Both arms passed every scored check in that comparison.
Authoring loaded in all creation and repair runs; reviewing loaded in all
diagnosis and review runs. Neither loaded for reading only. The agent declined
the trivial skill without loading authoring, so that case does not test the
authoring instructions themselves.

The comparison removed the whole plugin in the baseline arm. Trace inspection
found only the intended skill invoked in positive cases. It also found no
remote build checks, exports or pushes, and no writes by the reviewer.
After the distribution wording changed, one repair and one review comparison
were repeated in both arms: four further sessions, with all scores 1.00.
These smaller runs are smoke checks, not a new success-rate estimate.

## Why passing is insufficient

Several checks are deliberately narrow. The export case checks that the
generated file mentions `--account`; it cannot establish that the account
is mandatory or that exporting all accounts is prevented. Review checks
recognise references to triggering and pushes, rather than judging whether
the proposed remedies are correct. Command-prefix guards miss indirect
execution, and Edit/Write counts miss possible shell writes.

The first comparison also exposed two grader mistakes. A command guard
matched a command written inside a test description, and a wording check
missed a valid finding expressed differently. Both were corrected and both
arms rerun. Their apparent improvement or regression was measurement error.

The cases have no held-out real-task set or automated bad-output controls.
Local shell startup errors add noise to command-reliability measurements.
The scores therefore support a limited smoke-test claim. They establish
neither added value nor a security guarantee.

## What would strengthen the evidence

Use an actual catalogue authoring or maintenance task with a concrete failure
in the baseline. Define expected behaviour before editing instructions, and
include a nearby case that must keep working. Check that graders reject
known bad results and accept valid alternatives. For the creation case,
also exercise the produced skill against its own workflow requirements.

Run the cases locally as described in the eval guide. Keep the result and
selection evidence separate, and state the revision being measured. Claude
is the existing test runner; these results do not test agent-manager's
installation behaviour. The new skills remain unreleased while this draft
is reviewed.
