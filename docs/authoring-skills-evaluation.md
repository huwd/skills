# Evidence for the authoring and review skills

This report is for maintainers reviewing
[PR #27](https://github.com/huwd/skills/pull/27). It explains what the local
evals measure and whether their results justify accepting the two skills.
The cases support basic behaviour checks. A corrected review check caught one
forbidden command attempt in the baseline and none with the skill in three
runs per arm. That small comparison does not establish a general benefit
from the two skills.

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

The revised skills at `9829396` were evaluated on 13 November 2026 with Claude
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
remote status checks, exports or pushes, and no writes by the reviewer.
The command guard in this full comparison was subsequently corrected as
described below; this table records its original scoring rather than
silently applying a different measurement.

## Why passing is insufficient

Several checks are deliberately narrow. The export case checks that the
generated file mentions `--account`; it cannot establish that the account
is mandatory or that exporting all accounts is prevented. Review checks
recognise references to triggering and pushes, rather than judging whether
the proposed remedies are correct. Command-prefix guards miss indirect
execution, and Edit/Write counts miss possible shell writes.

One baseline review issued `buildctl --help` after command lookup despite
the prompt forbidding `buildctl` calls. The old guard only checked direct
status calls, so its automated score remained 1.00. This observed scope
violation shows why the table is not a task-success rate. The guard was
corrected to cover help and simple command chains, then checked against
eight permitted and forbidden command examples with JavaScript matching.

The corrected case at `1c29519` was then run three times per arm with the
same runner and model. All with-skill task scores were 1.00; baseline scores
were 0.83, 1.00 and 1.00 (mean 0.94). The failed baseline attempted
`buildctl --help` after a command lookup; the tool was unavailable. No
with-skill run attempted that command. This is an observed difference on
one narrow scope check, not a demonstrated improvement in authoring quality.
No skill instructions changed between these comparisons.

An earlier comparison also exposed two grader mistakes. A command guard
matched a command written inside a test description, and a wording check
missed a valid finding expressed differently. Both were corrected and both
arms rerun. Their apparent improvement or regression was measurement error.

The cases have no held-out real-task set or maintained controls for the other
graders.
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
