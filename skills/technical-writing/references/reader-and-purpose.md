# Reader, purpose and document type

Use this when writing a new document or a substantial new section. A
document can pass every linter and still fail its reader. The repository's
own templates and style guide win over anything here.

## Name the reader and the purpose

Answer these before drafting:

- Who opens this document, and where do they arrive from: a link in a
  pull request, a search, the docs index?
- What do they already know, and what don't they?
- What will they do or decide after reading it?

The reader has this page and the pages it links to. They did not see the
conversation, the issue or the pull request that produced it.

If the request and the repository don't answer these, choose the likeliest
reader and say which in the report. Ask the user only when the answer
would change what you write.

## Give the document one job

Choose the type first, then write only what that type needs.

| Type | The reader wants to | Write it as | Leave out |
| ---- | ------------------- | ----------- | --------- |
| Tutorial | learn by working through a complete example | steps to follow, with the result of each | design reasoning, alternatives |
| How-to guide | get one task done | prerequisites, then commands in order | background beyond a sentence |
| Reference | look something up | tables and lists, complete and consistent | narrative, steps |
| Explanation | understand how or why something works | statements in prose | step-by-step instructions |
| Decision record or design note | know what was decided, why, and what was rejected | dated statements, in the repository's template | instructions to the reader, to-do items |
| Report (evaluation, incident, research) | know what was found and how far to trust it | the result first, then the method, then the limits | instructions, claims the evidence doesn't support |
| README | decide whether this is for them, then get started | what it is, who it's for, the shortest route to a first use | history, internals |
| Changelog | know what changed for them | one line for each change, as its visible effect | how the work was done |

The first four types come from [Diátaxis](https://diataxis.fr/). When
content doesn't fit the type, put it in another document and link to it.

## Open with orientation

The first paragraph tells the reader what the document is, what it is for
and whether they need to read it. Name the reader when the document's
location doesn't make it obvious. Start with specifics, not scene-setting.

Before:

```markdown
# Queue research brief

Implement issue 12. Research reviewed on 4 March. The user's decision is
to use Redis streams.
```

After:

```markdown
# Design of the job queue

The worker takes jobs from a Redis stream, which ended the duplicate
deliveries seen when it polled the database. This note is for
contributors changing the worker. It records why Redis streams were
chosen over database polling and a hosted queue.
```

## Keep the session out of the document

A document outlives the conversation that produced it. Wording that only
makes sense inside that conversation is the most common fault in
documents drafted by an agent.

| Session wording | Write instead |
| --------------- | ------------- |
| "the user", "as requested", "the maintainer asked for" | The decision itself, with a named role only if it matters: "The worker uses Redis streams" |
| "we discussed", "as agreed earlier" | The fact, with a link to its source |
| "this change", "this PR", "the new approach" | The name of the thing, with a link to the pull request or issue |
| "now", "currently", "recently", "yesterday" | An absolute date or a version |
| A work order as the opening: "Implement issue 12" | What the document is: "This note records the design of…" |
| Process narration: "I checked", "after reviewing the sources" | The finding alone. Method belongs in a report's method section |
| A label coined during the work: "the pair", "the corrected guard" | A plain description, or a definition at first use |

## Keep records and instructions apart

A record states what was decided or found. A guide tells the reader what
to do. Mixing them leaves instructions with nobody to follow them.

Test each imperative sentence: who is being told, and when do they act?
In a guide the answer is the reader, now. In a record there is usually no
answer, so rewrite the sentence as a statement with its reason.

Before:

```markdown
Keep one stream per tenant. Do not put payloads over 1 MB on the stream.
```

After:

```markdown
Each tenant has its own stream, so one tenant's backlog can't delay
another. Payloads over 1 MB go to object storage and the job carries
their key, which keeps the stream small.
```

Put work that remains under one heading, such as "Open questions", with a
link to the issue that tracks each item. Don't scatter it through the
record.

The same holds the other way round: a guide doesn't stop to justify the
design. Link to the explanation.

## Read it cold

Linters can't check any of this. Before finishing, reread the document as
its reader, with only the page and its links:

1. From the title and first paragraph alone, what is this and who is it
   for?
2. Is every term, name and abbreviation defined or linked where it first
   appears?
3. Does every "it", "this" and "the change" refer to something on the
   page?
4. Does every imperative have someone to follow it? A record should have
   none.
5. Will it still make sense in 6 months, once the pull request has merged
   and the conversation is gone?
6. Is each fact stated once?

Fix what fails, then run the checks again.

## Sources

The document types follow [Diátaxis](https://diataxis.fr/). "One job per
page", the reader who has only the page, and the writer's check before
hand-off draw on the documentation skills in
[gitlab-org/ai/skills](https://gitlab.com/gitlab-org/ai/skills) (MIT).
