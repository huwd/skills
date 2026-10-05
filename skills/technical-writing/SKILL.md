---
name: technical-writing
description: >-
  Write and edit Markdown documentation to the repository's own style guide,
  and check it with the repository's documentation linters before finishing.
  Defaults to plain British English in the GOV.UK style when the repository
  has no guide. Use when creating or editing README files, docs/ pages, ADRs,
  guides, how-tos, changelogs, issue or PR templates, or any other .md file,
  or when the user asks to proofread, tidy, lint or check documentation, fix
  spelling or Markdown structure, or make docs follow the house style.
license: MIT
compatibility: >-
  Uses markdownlint-cli2 and Vale when the repository or machine provides
  them. Works without either and reports which checks it skipped.
---

# Technical Writing

Write documentation to the repository's standard the first time, check it
with the repository's own tools, and fix what they find, rather than
failing CI and patching afterwards.

## Principles

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

## 2. Write

- Follow the style guide. Where it is silent, use
  [references/style-defaults.md](references/style-defaults.md): plain
  British English with `-ise` spellings, in the GOV.UK style.
- Match the surrounding documents: heading depth, list style, link style,
  and code fence languages.
- Respect the repository's terminology. A vocabulary file with
  case-sensitive entries (`Flatpak`, `NVMe`) is a terminology list as well
  as a spelling allowlist.

## 3. Check

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
run plain `vale` and say in the report which rules were used.

[references/linters.md](references/linters.md) explains the generic
layer, reading each tool's output, and common false positives.

## 4. Fix and judge

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

## 5. Report

Keep it short:

```text
Style guide: docs/style-guide.md
Checks:
- markdownlint-cli2 (just docs-lint): pass
- Vale (just docs-prose): pass, 3 warnings left as written
Vocabulary: added Tailscale, tailnet to .vale/styles/config/vocabularies/House/accept.txt
Skipped: none
```

- **Style guide:** its path, or `none found, used the defaults`. With no
  guide, suggest adding `docs/style-guide.md` and linking it from
  `CLAUDE.md` or `AGENTS.md` so every agent finds it. Don't create either
  file unless asked.
- **Checks:** each check, how it ran and its result.
- **Vocabulary:** additions and the file they went in.
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
- Rewriting documents the task didn't touch. Mention problems seen in
  passing; don't fix them unasked.
- Enforcing style warnings as if they were errors.
