# pull-requests

Prepares a branch for human review. It counts the changed lines that need
a reviewer's judgement, estimates review time from published research on
review rates, and recommends splitting a branch that one review cannot
cover. It writes a description with a size and review-time table and a
reading guide: the core files to check closely, the mechanical changes to
sample and verify, and the generated files to skip.

The skill writes descriptions locally. Pushing, opening or editing a pull
request needs the user's approval.

## Files

- [SKILL.md](SKILL.md): measuring, estimating, splitting and describing.
- [assets/pr-body.md](assets/pr-body.md): description template.
- [references/review-budget.md](references/review-budget.md): the figures,
  the evidence behind them and its limits.

The [research note](../../docs/code-review-size-research.md) records the
full evidence review. The [eval suite](../../evals/pull-requests/README.md)
defines the synthetic cases.
