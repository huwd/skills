# Evaluating a skill change

Use the target project's existing runner or fresh local agent sessions.
Do not add a new evaluation platform as a side effect of editing a skill.

Every new skill needs behavioural and discovery evals. When
changing behaviour, add a regression case for the change. This does not
require repeating expensive runs for a spelling or link correction.

## Use red, green, refactor for behavioural changes

1. **Red:** run the previous version, or no skill for a new workflow, and
   capture a shortcoming against a defined expected outcome. Write a case
   that exposes it. If the baseline already succeeds, the case does not
   establish a need for new instructions; choose a justified harder case
   or reconsider the skill rather than manufacturing a failure.
2. **Green:** make the smallest instruction or helper change that addresses
   that shortcoming. Compare repeated runs and check preserved behaviour.
3. **Refactor:** simplify the instructions or helpers while keeping the
   expected outcomes stable, then rerun the affected cases.

An eval is a measurement, not an ordinary deterministic unit test. Record
variation across runs rather than treating a single pass as proof.
Validate the measurement too: a known bad output should fail and a valid
alternative should pass. A grader that only requires the skill to load
cannot demonstrate that the skill improves the task.

## Choose a fair comparison

| Change | Baseline | Candidate |
| ------ | -------- | --------- |
| New skill | Same task without the skill | Same task with the skill |
| Existing skill | Previous skill version | Proposed version |

Keep input files, task prompt, model, available tools and permissions the
same between arms. Use fresh disposable workspaces; the authoring
conversation and previous outputs must not leak into test sessions.
Record what other skills or instructions were loaded, since they can
hide the contribution of the skill being tested.

Define observable checks before inspecting candidate outputs:

- **Selection:** loaded for a relevant paraphrase; stayed inactive for a
  nearby request outside its scope. Forced invocation tests execution,
  not automatic discovery.
- **Result:** the output meets the task's requirements and local conventions.
- **Process:** required steps happened; unwanted writes or network actions
  did not. Inspect commands and filesystem changes, not just the final reply.
- **Regression:** behaviour that should remain unchanged still works.

Prefer checking artefacts, command results and state to matching a phrase
from the instructions. Use a documented human judgement where a mechanical
check would reward surface wording instead of quality. Distinguish a
deliberate no-change result from a run that failed before doing any work.

## Iterate without overfitting

Start with one useful scenario and its baseline. Add coverage for the
observed failure, a nearby counterexample and preserved behaviour. Keep
some variants out of the editing loop, then try them before claiming the
fix generalises. Repeated runs expose variance; a single successful run
is a smoke check, not a reliable success rate.

Read unsuccessful and successful traces. Change the instructions only
where they explain the gap; changing a path, prerequisite or tool may be
the actual fix. If several scenarios repeatedly rebuild the same helper,
consider shipping it. Do not reward a skill for tests that pass equally
well without it or excuse a regression with an aggregate score.

Keep the acceptance criteria stable across versions. If a grader is wrong,
correct it transparently and rerun affected arms. Separate the resulting
measurement change from any improvement in the skill itself.

## Report what was tested

Record the skill revision, harness and version, model, scenarios, runs per
arm, checks, per-case results and any important limitations. Compare old
and new results without inventing missing data. Report selection and task
success separately. Keep private traces and credentials out of published
fixtures and reports; sanitise examples before sharing them.
