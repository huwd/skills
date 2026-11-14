# Mixed staging and validation boundaries

Use this reference when a requested commit shares the index or working
copy with work that must remain uncommitted, or when validation is blocked.
Preserving files alone is insufficient: staging is part of the user's state.

## Commit the selected snapshot

Before changing state, identify the original HEAD, selected staged blobs,
other index entries and unstaged changes. Read both the staged diff and
the relevant working-copy diff. Select by the requested purpose, including
tests; do not infer ownership from which file was edited most recently.

`git commit --only PATH` includes the path's working-copy contents and can
therefore commit unstaged work. Broad staging can include unrelated work
that was already in the index. Neither is a safe substitute for selecting
the intended staged blobs.

For an unambiguous subset, a temporary index can represent the intended
commit without disturbing the user's index. It starts from HEAD and adds
the selected index entries, preserving their blob IDs and modes. A
disposable checkout of that index can validate the intended snapshot.
The normal commit still runs hooks and signing; another index is not a
reason to suppress them.

After the commit, verify the selected blobs in its tree and compare the
real index and working files with the recorded state. Changes made by a
hook need inspection too. Avoid a destructive reset, checkout or stash
that could lose user work. Do not overwrite concurrent changes; report
an ambiguous selection or changed baseline when it prevents a safe commit.

## Distinguish validation outcomes

| Outcome | Treatment |
| ------- | --------- |
| Required checks pass on the intended snapshot | The authorised checkpoint can proceed. |
| A required check fails unexpectedly | Fix within the authorised task, or report the blocker and leave it uncommitted. |
| A required tool is unavailable | Report what could not run; do not call it a pass or replace the check unasked. |
| No check is defined | Report that no check was found and what inspection was possible. Follow project policy on whether an authorised commit can proceed. |
| An optional check is unavailable | Disclose the missing evidence; do not turn an advisory check into an invented mandatory gate. |
| A hook or signing operation rejects the commit | Preserve it and report the failure. Do not skip, disable or silently reconfigure it. |

## Explicit red checkpoints

A project can deliberately require a failing-test checkpoint before the
implementation. Follow that policy only within the authorised scope and
identify the specific expected assertion failure. Other checks still run;
syntax errors, missing tools and unrelated failures are not the intended
red result. The message and report state the actual evidence.

The ordinary default remains a passing logical unit with its regression
test. Do not introduce red commits where project policy does not request
them, or hide failures with pending tests or weakened assertions. When
explicit project rules conflict, report that conflict rather than invent
an exception. A red checkpoint does not relax the project's merge gates,
hook requirements, signing policy or permission to push.
