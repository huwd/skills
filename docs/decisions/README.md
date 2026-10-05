# Decision records

Significant decisions about this repository, one per file, with the context
and the options that lost. [0000](0000-record-decisions.md) explains why
they exist and why they take this form.

## When to write one

Write a record when a decision:

- is costly or awkward to reverse, such as the repository layout or how
  skills are tested
- chooses between real alternatives, and the losing options are worth
  remembering
- would leave a future reader asking "why is it like this?"

Routine changes don't need one. When unsure, ask whether the reasoning
would otherwise only live in a closed issue or a PR description.

## How to write one

1. Copy [`template.md`](template.md) to `NNNN-short-slug.md`, using the next
   free number.
2. Fill in every section. The summary is one sentence in the
   [Y-statement](https://medium.com/olzzio/y-statements-10eb07b5a177) form.
3. List the options that lost and why. This is often the most useful part.
4. Link the discussion: the issue or pull request where the decision was
   made.
5. Add the record to the index below. CI lints it with markdownlint, like
   every other Markdown file.

### Voice

Name the people who made the decision in the "Decided by" line, by GitHub
handle, such as @huwd. Elsewhere, avoid personal pronouns: write "the
decision was", "this repository" or "the suite", not "I" or "we". Anyone
can propose a record, and it should read the same whoever wrote it.

### Dates

**Decided** is when the decision was made; **Recorded** is when the record
was written. Give both, so a record written after the fact never appears
older than it is.

### Status

| Status | Meaning |
| ------ | ------- |
| Proposed | Written, not yet agreed |
| Accepted | In effect |
| Deprecated | No longer applies, and nothing replaced it |
| Superseded by NNNN | Replaced by a later record |

Don't rewrite an accepted record when a decision changes. Write a new
record, set the old one's status to "Superseded by" with a link, and leave
the rest of it as it was. Fixing typos and broken links is fine.

## Index

| Number | Decision | Status |
| ------ | -------- | ------ |
| [0000](0000-record-decisions.md) | Record decisions in lightweight decision records | Accepted |
| [0001](0001-run-evals-locally.md) | Run skill evals locally on a subscription, not in CI | Accepted |
| [0002](0002-static-checks-in-ci.md) | Gate pull requests on static checks only, and run them locally too | Accepted |
