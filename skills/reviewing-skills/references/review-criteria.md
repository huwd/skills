# Review criteria

Use the rows that matter to the requested assessment. Findings need a
consequence, not just a difference from your preferred writing style.

| Area | Questions that reveal useful findings |
| ---- | ------------------------------------- |
| Value | What expertise or operational fact does this add beyond model defaults? Does the baseline already perform the job equally well? |
| Scope | Is there one coherent job? Do creation and assessment have clear permissions and outputs? Would a split reduce irrelevant context or simply repeat the same procedure? |
| Discovery | Does the description explain when to use the skill? Try a paraphrase and a nearby request it should reject. Are sibling descriptions competing for the same job? |
| Instructions | Are decisions and exceptional constraints concrete? Does the agent have room to adapt ordinary steps? Does a reported failure already have a clear instruction? |
| Files | Can the agent find the relevant reference at the point of need? Do relative paths resolve after installation? Are templates mistaken for instructions or optional references required unconditionally? |
| Dependencies | Are tools and environment requirements declared or discovered? Do those prerequisites match the commands the skill actually uses? |
| Authority | Does the workflow stay within the user's request? Does reviewing or reading accidentally authorise edits, uploads, commits or live operations? |
| Validation | Do checks measure the result and important actions? Are fixtures isolated, expected results stable, and old/new comparisons fair? What regression or missing evidence limits the claim? |
| Maintenance | Is this the source version? Are provenance, licence notices and versions maintained? Is the proposed fix local to this failure, or an unnecessary universal rule? |

## Example: an instruction defect

A status-check skill says to retry every failure. Its trace shows repeated
HTTP 403 responses; the user's requirement distinguishes access failures
from transient transport failures. Recommend making that distinction in
the retry rule. Verify that 403 stops without a retry, while an allowed
transient failure still follows the existing bounded retry policy.

## Counterexample: the environment failed

A skill requires a preinstalled CLI and says to report its absence. The
trace shows command-not-found, an accurate explanation and no attempted
installation. Report the missing prerequisite, with no skill change
unless other evidence shows the fallback is inadequate. Adding another
paragraph about installing the CLI would change the policy, not repair
the observed behaviour.
