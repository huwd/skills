# 0000. Record decisions in lightweight decision records

- **Status:** Accepted
- **Decided by:** @huwd
- **Decided:** 2026-10-05
- **Recorded:** 2026-10-05
- **Discussion:** #10, huwd/declarative_laptop#67 (the format this adopts)

## Summary

In the context of a skills repository whose reasoning lived in
`docs/plan.md`, PR descriptions and agent session notes, facing decisions
that a future reader couldn't explain from the repository alone, the
decision was to reuse the decision record format already in use in
[huwd/declarative_laptop](https://github.com/huwd/declarative_laptop/blob/main/docs/decisions/0000-record-decisions.md),
and against a new or different format, to achieve one familiar way of
recording decisions across these repositories, accepting the effort of
writing records.

## Context

By October 2026 this repository had made several deliberate choices: one
monorepo rather than a repository per skill, public from the start, CI
checks that never call a model, and how skills are evaluated. The
reasoning lived in `docs/plan.md`, which mixes decisions with a task list
that changes every session, in PR descriptions, and in local notes that
aren't published at all.

huwd/declarative_laptop had already weighed the options for recording
decisions (plain Nygard records, MADR, RFCs, tooling, or nothing) in its
own record 0000, and settled on a light format suited to one person
working with AI coding agents. The same constraints apply here.

## Options considered

### Reuse declarative_laptop's format (chosen)

Nygard's sections, plus a one-sentence Y-statement summary, the options
considered, and separate decided and recorded dates. The README and
template are copied from that repository, with the parts specific to it
removed. One format across both repositories means one habit, and the
reasoning for the format is already written down.

### A different format for this repository

Plain Nygard records or MADR, chosen afresh. There's nothing about a
skills repository that the shared format doesn't cover, so a second
format would only add something to remember.

### Keep decisions in `docs/plan.md`

No new files. The plan is a working document that changes every session,
and its decisions get rewritten along with its tasks, so the reasoning
doesn't last.

## Decision

Significant decisions are recorded as numbered Markdown files in
`docs/decisions/`, using [`template.md`](template.md), following
declarative_laptop's
[record 0000](https://github.com/huwd/declarative_laptop/blob/main/docs/decisions/0000-record-decisions.md).
[`README.md`](README.md) in the same folder covers when and how to write
one, and indexes them.

## Consequences

- Decisions already recorded in `docs/plan.md`, such as one monorepo and
  public from day one, can get retrospective records with honest dates.
- `docs/plan.md` can then link to records rather than restating the
  reasoning.
- If declarative_laptop changes its format, this repository should
  follow with a record of its own, rather than drifting apart silently.
