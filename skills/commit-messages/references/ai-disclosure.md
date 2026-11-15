# AI disclosure in commits

Read this when an agent wrote or materially shaped a change it is about
to commit or describe in a message.

## Precedence

1. The user's instruction in the current task.
2. The project's explicit rules: agent instructions such as `AGENTS.md` or
   `CLAUDE.md`, contribution guides, commit templates, hooks and CI checks.
   A project may name other trailers, require a pull request note instead,
   ban AI attribution in commits or ban AI contributions altogether.
3. The default below.

History alone is not a project rule. Old commits without trailers do not
mean the project has chosen not to disclose. When explicit rules conflict,
report the conflict rather than choosing one.

## Default

Disclose the agent's part in every commit it prepares, using one trailer:

- `Generated-by: <tool>:<model>` when the agent wrote most of the
  committed diff from prompting.
- `Assisted-by: <tool>:<model>` when a human wrote most of it, or
  substantially reworked what the agent produced. An agent that only
  drafted the message for a human's change uses this trailer.

When unsure which applies, use `Generated-by`. Over-disclosure misleads
less than under-disclosure.

Take the tool and model names from your own context, such as
`Claude Code:claude-opus-5-5`. Use the model identifier exactly as your
context states it. A model family or shortened name is a guess at the
identifier. If your context does not state it, give the tool alone.

Keep a `Co-Authored-By` trailer that the tool adds by default. GitHub shows
it on the commit, so it makes AI involvement visible. Do not add a second
one, and do not invent one with a made-up address when the tool adds none.

Put trailers in the final paragraph of the message, with nothing after
them, so `git interpret-trailers` recognises them.

## Sign-off is the human's

`Signed-off-by` certifies the Developer Certificate of Origin, or a similar
statement, for a person. Never add one: not in a message file, and not
with `git commit -s` or `--signoff`, even with the human's git identity. A
project rule requiring sign-off states the human's obligation; it is not
an instruction to add their name. Leave the change ready, staged if that
helps, with a drafted message. Explain that the sign-off is theirs to add,
and do not commit it.

## Why this default

A research report, [Wording AI Attribution in Commits](https://heios.github.io/research/2026-07-08/ai-commit-attribution/),
recommends naming the tool and model and separating assistance from
generation. It advises against `Co-Authored-By` for AI, because the trailer
implies shared authorship and responsibility.

This default keeps a tool-added `Co-Authored-By` despite that advice,
because it is the trailer that hosting services display. `Assisted-by` or
`Generated-by` records the actual role and takes priority. A project that
prefers the report's position can ban `Co-Authored-By` in its own rules.

The default applies a trailer to a commit. It does not change the
project's configuration or write a policy into the repository.
