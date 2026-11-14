# Plan a series for its reviewer

Use this reference when several concerns share a working diff or a feature
branch contains development checkpoints and later corrections. A useful
series lets a reviewer assess a sequence of complete decisions, without
having to separate unrelated changes mentally.

## Identify the units before selecting files

Read the whole relevant change and its motivation. Name the purposes first:
a behaviour correction, mechanical preparation, a new capability or an
independent cleanup. Group the necessary implementation, tests and docs
for each purpose. Splitting by file, editing session or test/implementation
phase can hide the actual units.

A boundary is useful when the step has a clear result and can be understood
or reverted without taking an unrelated change with it. Prefer a complete
step over an arbitrary size target. Avoid separating a dependency from its
only use if that leaves an incoherent intermediate state.

Mechanical changes can obscure the smaller behaviour change among them.
Where the preparation is meaningful on its own, isolating it lets a reviewer
check that behaviour stayed the same before examining the new behaviour.
Do not add a refactor solely to manufacture another commit.

## Order the explanation

Give each proposed commit a purpose, the relevant paths or hunks, its
dependencies and the checks that establish that step. Required preparation
comes before changes that use it. Independent concerns can move without
being bundled together. Keep the proposed result consistent with the scope
already authorised; a plan alone does not authorise staging or committing.

Review the sequence before executing it:

- Can a reviewer explain each step from its message and diff?
- Can they verify one concern without mentally subtracting another?
- Are implementation, tests and documentation aligned at that boundary?
- Does every intermediate state meet the project's validation policy?
- Does the final series produce exactly the intended result?

Subject lines are a useful outline of the series. If they cannot explain
the progression, reconsider the boundaries or descriptions. A good message
cannot repair an unrelated bundle of changes.

## Distinguish development from the submitted history

Development checkpoints may include experiments or corrections. Before
review, identify follow-up commits that only repair earlier commits and
recommend folding them into those commits. Preserve changes with genuinely
different purposes. The aim is an intelligible explanation of the result,
not a transcript of every attempt.

Reordering, splitting, squashing, amending and force-pushing change history.
Check authorisation and shared-branch constraints before doing them; do not
rewrite merged history as routine cleanup. When rewriting is authorised,
preserve a recovery point and verify that the final tree is unchanged unless
a content change was also requested. Existing authorisation remains valid;
there is no mandatory approval question for each individual fixup.

## Sources

[GDS's Git guidance](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/working-with-git.html#commits)
informs complete steps and dependency order.
[Joel Chippindale's talk](https://blog.mocoso.co.uk/posts/talks/telling-stories-through-your-commits/)
informs the distinction between development chronology and a reviewable
explanation. These ideas are expressed here in original wording; the
examples and text from the sources are not copied.
