# Evidence for technical-writing 0.3.0

This report is for maintainers reviewing technical-writing 0.3.0, which
adds message, outline and evidence guidance for
[issue #28](https://github.com/huwd/skills/issues/28). The automated
checks show that both skill versions fix the faults in the original
PR #27 documents, and that no skill fails to in every run. They do not
separate 0.2.0 from 0.3.0. The difference between those versions is in
structure, which only the blind rubric assessment can judge, and that
assessment has not yet been done.

## Method

The editorial comparison used Codex CLI 0.167.1 with `gpt-6.1-sol` at
medium reasoning effort on 15 November 2026. Technical-writing 0.2.0 was
tested from `9c70232`. The candidate skill tree, `36b3462`, was tested from
an unreferenced commit object. The committed 0.3.0 tree differs from it by
one later addition: results such as measurements stay even when the source
narrates them, together with the matching words in the planning step.

Each case ran three times for each arm. The
[suite guide](../evals/README.md#technical-writing-editorial-cases)
describes the cases. `editorial_assess.py` checked the result against
originals saved outside the model's working directory. Its controls in
`evals/tests/test_editorial_evals.py` show that the original documents fail
the editorial checks and that valid alternatives pass. After the runs, the
session-wording pattern was corrected to match a phrase broken across a
line; every output was regraded with it, and no result changed.

The [editorial rubric](../evals/technical-writing/editorial-rubric.md) was
written before the skill changed.

## Automated results

| Case | No skill | 0.2.0 | 0.3.0 |
| ---- | -------- | ----- | ----- |
| `editorial-brief` | 0/3 | 3/3 | 3/3 |
| `editorial-report` | 0/3 | 3/3 | 3/3 |
| `coherent-addition` | 3/3 | 3/3 | 3/3 |
| `small-correction` | 3/3 | 3/3 | 3/3 |

Without a skill, every brief opened by describing the pull request, such
as "This pull request addresses issue #24", and kept wording from the
session: "the user requested", "the user's decision" or "the user chose".
Two of those openings never named the reader. Every report without a skill
lacked an opening naming its reader, and one dropped a listed fact.

Both skill versions passed every check in every run. Neither restructured
a coherent document to make an addition or a correction, and nor did no
skill, so the proportionality cases show preserved behaviour, not
improvement.

## Structure, not yet scored

The outputs differ in ways the regex checks do not measure. These
observations come from reading the headings and are unscored:

- 0.2.0 briefs had 11 or 12 headings and kept the original's separate
  "Findings from primary sources" section, with a subsection for each
  source.
- 0.3.0 briefs had 6 or 7 headings, each stating a point, such as
  "Separate skills distinguish editing from assessment". The evidence from
  each source sat in the section whose decision it supported.
- 0.3.0 reports led with the result, "All six cases passed with and
  without the plugin", and used point headings for the method and limits.
  0.2.0 and no-skill reports used category headings such as "Method" and
  "Limits of the evidence".

Whether this helps a maintainer decide is the question the rubric answers.
A blind pack of all 18 restructured outputs, with a separate key, is
retained locally for that assessment. Its scores will be added here.

## Regression on existing cases

The existing Claude cases ran twice each with 0.3.0 using Claude Code
2.1.321, against the 0.2.0 scores recorded in PR #29:

| Case | 0.3.0 | 0.2.0 |
| ---- | ----- | ----- |
| `brief-from-conversation` | 1.00 | not recorded |
| `british-default` | 1.00 | 0.89 |
| `design-note-from-session` | 0.88 | 1.00 |
| `fix-markdownlint` | 1.00 | 1.00 |
| `no-trigger` | 1.00 | 1.00 |
| `vocab-local` | 1.00 | 0.94 |

In both `design-note-from-session` misses, the note kept the 41 and 6
second measurements but stated 6 seconds first, which the grader did not
accept. The grader now accepts either order. Four further runs, with the
committed tree and the original grader, scored 0.94: one kept the
measurement in the 6-then-41 order, and one did not name SQLite in its
opening.

## Limits

- Three runs for each arm show presence or absence of a fault, not a
  reliable rate.
- One reviewer brief and one report, from one repository, are the only
  restructuring inputs. A held-out document would test whether the
  guidance generalises.
- The fact checks list the facts a maintainer needs. They do not detect a
  changed meaning, which the rubric's accuracy criterion covers.
- Codex reached its usage limit during the regression runs, so those ran
  only through the Claude runner.
