---
name: technical-writing
description: >-
  Write and edit Markdown documentation to the repository's own style guide,
  and check it with the repository's documentation linters before finishing.
  Plans new documents around their reader and purpose, so they make sense
  to someone who was not part of the work. Defaults to plain British English in the GOV.UK style when the repository
  has no guide. Use when creating or editing README files, docs/ pages, ADRs,
  design notes, reports, guides, how-tos, changelogs, issue or PR templates, or any other .md file,
  or when the user asks to proofread, tidy, lint or check documentation, fix
  spelling or Markdown structure, or make docs follow the house style.
license: MIT
compatibility: >-
  Uses markdownlint-cli2 and Vale when the repository or machine provides
  them. Works without either and reports which checks it skipped.
metadata:
  version: "0.2.0"
---

# Technical Writing

Write documentation for its reader and to the repository's standard the
first time, check it with the repository's own tools, and fix what they
find, rather than failing CI and patching afterwards.

## Principles

- **Write for a reader who wasn't there.** They have the page and what it
  links to, not the conversation, issue or pull request that produced it.
  No linter checks this.
- **Repository first, defaults second.** The repository's style guide,
  vocabulary and lint config win. Use this skill's defaults only where the
  repository is silent.
- **Errors are fixed; warnings are judged.** Fix every lint error. Treat
  style warnings (passive voice, wordiness, weasel words) as prompts to
  reconsider, not orders. Don't contort clear prose to silence a heuristic.
- **Never silence a real problem through config.** Don't disable a rule,
  add an ignore comment, or add a misspelling to a vocabulary to get a
  pass. Ask the user first.
- **Don't install anything.** Use the tools the repository or machine
  already provides. If a check can't run, say so in the report.

## 1. Discover the repository's standard

Before writing, find and read:

- **The style guide.** Follow an explicit pointer from `CLAUDE.md`,
  `AGENTS.md`, `.github/copilot-instructions.md` or `CONTRIBUTING.md`
  first. Otherwise try `docs/style-guide.md`, then `STYLE.md`,
  `STYLEGUIDE.md`, `docs/STYLE.md` and `.github/STYLE.md`, then search.
  Read the whole guide; it may override the defaults in ways a skim misses.
- **Lint config:** `.vale.ini`, `.markdownlint-cli2.*`, `.markdownlint.*`,
  and any other prose tools.
- **How the checks run:** `justfile`, `Makefile`, `package.json` scripts,
  `flake.nix` apps, and CI workflows under `.github/workflows/`.

Checks that run in CI are hard gates. Local-only checks are advisory.

[references/discovery.md](references/discovery.md) has the full search
order, the search command and where each tool keeps its config.

## 2. Plan the document

Do this when creating a document or writing a substantial new section.
Skip it for proofreading, lint fixes and small edits, and don't
restructure a document the user only asked to tidy.

Decide before drafting:

- **Reader:** who opens this, and what they already know.
- **Purpose:** what they will do or decide after reading it.
- **Type:** one job for each document. A record (decision record, design
  note, report, changelog) states what was decided or found, and why. A
  guide (tutorial, how-to) tells the reader what to do. Reference is for
  looking things up.

Three faults follow from skipping this, and all three pass the linters:

- **No orientation.** The first paragraph must say what the document is
  and what it is for, so the reader can tell whether to read on.
- **Written from inside the session.** "The user", "as requested", "we
  discussed", "this change" and "currently" mean nothing once the
  conversation is gone. State the fact, name the thing, link the source
  and give the date.
- **Records mixed with instructions.** An imperative in a record
  ("Implement…", "Keep X in Y") has nobody to follow it. Rewrite it as a
  statement with its reason, and put remaining work under one heading.

[references/reader-and-purpose.md](references/reader-and-purpose.md) has
the document types, wording to replace, and examples. Read it before
writing a new document.

## 3. Write

- Follow the style guide. Where it is silent, use
  [references/style-defaults.md](references/style-defaults.md): plain
  British English with `-ise` spellings, in the GOV.UK style.
- Match the surrounding documents: heading depth, list style, link style,
  and code fence languages.
- Respect the repository's terminology. A vocabulary file with
  case-sensitive entries (`Flatpak`, `NVMe`) is a terminology list as well
  as a spelling allowlist.

## 4. Check

Check the files you changed, not the whole repository, unless the user
asks for a full sweep. Run from the repository root.

Prefer the repository's own commands (a `just` recipe, `make` target,
`package.json` script or `nix run` app) over calling tools directly; they
carry the repository's wrappers, styles and dictionaries.

When the repository has config but no command:

```bash
markdownlint-cli2 path/to/file.md
vale --output=line path/to/file.md
```

Vale has two layers, and merges them itself:

- **The repository's own rules**: its `.vale.ini`, styles and vocabulary.
- **The generic layer**, if the machine has it installed: a global Vale
  config holding a shared vocabulary of common technical terms.

So run `vale` without `--config` or `--no-global` in a repository that has
its own `.vale.ini`; either flag drops a layer. When the repository has no
Vale config, use the generic British fallback if it is installed:

```bash
vale --config "<vale config dir>/british.ini" path/to/file.md
```

`vale ls-dirs` shows the config directory. If the fallback isn't there,
Vale has nothing British to check against, and with no config at all it
refuses to run. Skip it, say so in the report, and check British spelling
by eye.

[references/linters.md](references/linters.md) explains the generic
layer, reading each tool's output, and common false positives.

**Then read a new document cold.** Reread it as its reader, with only the
page and its links. Check that the first paragraph orients them, every
term and "this" is explained on the page, and no session wording or
stray instruction remains. The questions are in
[references/reader-and-purpose.md](references/reader-and-purpose.md#read-it-cold).

## 5. Fix and judge

**Scope: every file you edited, all of it.** CI checks whole files, so an
error that was already in a file you touched still fails the pull request.
Fix lint errors anywhere in those files, including ones that were there
before you started, and list those in the report. Leave files you didn't
edit alone.

- **markdownlint errors:** fix all of them. `markdownlint-cli2 --fix`
  handles many rules automatically; review its diff.
- **Spelling errors:** fix real misspellings, including American spellings
  in a British repository. Add clear project terms (tool, product and
  command names) to the **repository's** vocabulary, the one named in its
  `.vale.ini`, keeping that file's order and case conventions. Ask first
  when unsure whether a word is jargon or a typo, or when a change would
  edit or remove an existing entry.
- **Never edit the generic vocabulary from another repository.** It
  changes only through the repository that ships this skill. If the same
  term keeps being added across repositories, suggest promoting it.
- **No repository vocabulary:** don't create one. Fix what you can and
  list the remaining project terms in the report.
- **Terminology errors** (`Use 'X' instead of 'x'`): fix them, unless the
  hit is a domain name, file extension or code. Vale skips inline code, so
  wrapping a real identifier in backticks is the right fix, not a
  workaround.
- **Style warnings:** rewrite when the suggestion genuinely improves
  clarity; otherwise leave the text as it is. Don't report each one.

Re-run the checks after fixing, until errors are gone.

## 6. Report

Keep it short:

```text
Reader and purpose: contributors changing the cache; why SQLite was chosen
Style guide: docs/style-guide.md
Checks:
- markdownlint-cli2 (just docs-lint): pass
- Vale (just docs-prose): pass, 3 warnings left as written
Vocabulary: added Tailscale, tailnet to .vale/styles/config/vocabularies/House/accept.txt
Existing errors fixed: bare URL on line 3 (MD034)
Skipped: none
```

- **Reader and purpose:** one line, for a document you planned in step 2.
  Leave it out otherwise.
- **Style guide:** its path, or `none found, used the defaults`. With no
  guide, suggest adding `docs/style-guide.md` and linking it from
  `CLAUDE.md` or `AGENTS.md` so every agent finds it. Don't create either
  file unless asked.
- **Checks:** each check, how it ran and its result.
- **Vocabulary:** additions and the file they went in.
- **Existing errors fixed:** errors that were in an edited file before you
  started, so the user can see the change went beyond what they asked.
- **Skipped:** checks that couldn't run and why, such as a tool that isn't
  installed.

## Changes That Need Approval

Ask before:

- disabling or reconfiguring a lint rule, or adding an ignore comment
- editing or removing an existing vocabulary entry
- creating a style guide, lint config, vocabulary or recipe
- installing a tool

## Explicit Non-Goals

- Setting up linting in a repository that has none. Offer it, but only do
  it when the user asks.
- Rewriting or restructuring a document the user asked only to proofread
  or lint. Mention an unclear reader or purpose; don't fix it unasked.
- Changing files the task didn't touch. Mention problems seen in passing;
  don't fix them unasked.
- Enforcing style warnings as if they were errors.
