# Authoring and review skill evaluation

On 13 November 2026, both suites passed their task checks with and without
the plugin. These fixtures verify basic behaviour but demonstrate no
measured improvement over the baseline. Keep that limitation visible when
assessing whether the skills earn their context cost.

## Method

- Claude Code 2.1.318, using the local subscription.
- Model reported in every final trace: `claude-opus-5-5`.
- Skills: authoring-skills 0.1.0 and reviewing-skills 0.1.0 at the original
  draft revision `508689f`. Instructions were unchanged during those runs.
- Three runs per case and arm; six cases, 36 sessions in the final comparison.
- Ablation: the whole `huwd-skills` plugin is present or absent. Trace
  inspection found only the intended authoring or review skill loaded in
  the positive cases; no other plugin skill was invoked.
- Each suite allowed two concurrent sessions. Both suite processes ran
  at the same time, sharing the subscription's limits.
- Deterministic regex and tool-use graders; no paid model graders.
  Read traces alongside scores to interpret findings and command matches.

Run from the repository root:

```bash
evals/authoring-skills/run.sh --runs 3 --concurrency 2
evals/reviewing-skills/run.sh --runs 3 --concurrency 2
```

The runner uses the existing plugin eval format, runs authored scaffolds
in disposable repositories and keeps reports local. These commands use the
maintainer's existing login; they do not configure CI credentials.

## Final task scores

The scores below exclude positive selection indicators, which the eval
runner reports separately under with/without ablation.

| Case | With plugin | Without plugin | Runs per arm |
| ---- | ----------- | -------------- | ------------ |
| Create from a ledger export runbook | 1.00 | 1.00 | 3 |
| Decline an unnecessary skill | 1.00 | 1.00 | 3 |
| Repair the retry instruction | 1.00 | 1.00 | 3 |
| Diagnose a missing prerequisite | 1.00 | 1.00 | 3 |
| Read a skill without initiating review | 1.00 | 1.00 | 3 |
| Review trigger and authority problems | 1.00 | 1.00 | 3 |

Authoring was selected in 3/3 creation runs and 3/3 repair runs. It was
not selected in any decline run; the agent correctly declined using its
own judgement. That case verifies the no-change outcome, not execution
of the authoring skill's refusal path.

Reviewing was selected in 3/3 diagnosis runs and 3/3 review runs. Neither
new skill loaded in the three reading-only runs. None of these prompts
forced invocation. This is narrow routing coverage, not a catalogue-wide
trigger accuracy estimate.

Trace inspection found the review runs stayed read-only, and the repair
runs preserved pending-build polling while distinguishing access failures.
No remote build check, ledger export or push was executed. The reviewer
distinguished the missing CLI from an instruction defect in both arms.

The final authoring suite took 174 seconds and reported $2.39 at list
price; review took 176 seconds and reported $2.24. These are runner
estimates for subscription usage, not new API billing. The totals exclude
earlier smoke runs and the initial comparison.

After clarifying agent-manager's installation responsibility, focused
repair and review comparisons were repeated on the revised instructions.
Each used one run per arm: four sessions, all task scores 1.00 in both
arms, with the intended skill selected in each positive run. This follow-up
is a smoke check; it does not replace the recorded 36-session comparison
or change the conclusion about measured uplift.

## Grader corrections

The initial comparison exposed two measurement errors:

1. A command guard matched `buildctl status` inside a shell heredoc writing
   a regression scenario. The trace showed no remote execution. Anchor
   that guard to the command prefix; its apparent baseline failure was
   not evidence that the authoring skill improved safety.
2. The trigger-finding grader recognised phrases such as "too broad" but
   missed "loads for almost any task". Trace inspection showed the
   expected finding in all three review outputs. Accept that wording
   without changing the expected finding.

Both suites were rerun in full after those corrections. No skill
instructions were changed to chase these scores. The earlier apparent
authoring improvement and review regression are not valid conclusions.

## Limits and next evidence

The fixtures are small and authored for this change, with no held-out
real-task set. Regex checks can reward mentions without proving quality.
Tool guards cover direct command prefixes, not arbitrary shell programs;
Edit/Write counts cannot detect every possible write through Bash. Trace
inspection supplements those checks but is not a security proof.

The eval sandbox sometimes emitted shell startup/state-file errors after
otherwise successful commands. Runs completed and produced the expected
artefacts, but that local environment noise limits conclusions about
tool-call reliability or efficiency.

Claude is the existing local behavioural eval runner. Agent-manager owns
installation into target tools; this PR adds no target-specific adapters.
The bundle was inspected for both skills' files and licence notices, but
these behavioural scores are not an agent-manager installation test.

The next useful evidence is a further real catalogue task, such as
[issue #25](https://github.com/huwd/skills/issues/25), with a held-out
variation and an old/new or no-skill comparison. The
draft provides a reviewable workflow and a baseline for that work; it
does not establish that these instructions outperform a capable model.
