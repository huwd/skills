# Technical writing skill — brief

A hand-off brief for building a `technical-writing` skill in this repository.
It records what the skill should do, why, and what we learnt setting up
documentation linting in [huwd/declarative_laptop](https://github.com/huwd/declarative_laptop),
which will be its first consumer.

Read [`skill-format.md`](skill-format.md) and [`plan.md`](plan.md) first, and
use `skills/dependabot-pr-review/` as the reference for shape and tone.

## Goal

When an agent writes or edits Markdown in any repository, it should write to
that repository's standard the first time, check its work with the
repository's own tools, and fix what they find, rather than failing CI and
patching afterwards.

## Origin

- [declarative_laptop#52](https://github.com/huwd/declarative_laptop/issues/52)
  asked for enforced technical-writing standards: British English, plain
  language, consistent Markdown structure, and a skill so agents write to
  that standard.
- [declarative_laptop#65](https://github.com/huwd/declarative_laptop/pull/65)
  implemented the tooling. During that work we decided:
  - **markdownlint-cli2 runs in CI.** Structural problems are objective and
    cheap to fix.
  - **Vale runs locally only, as advice.** With stock rules it raised about
    575 findings across 12 files, which is too noisy to gate on. The skill
    is how Vale gets used: the agent runs it on the files it touched and
    applies judgement to the results.
- The skill lives here, not in declarative_laptop, because it should work in
  any repository. Repository-specific rules (vocabulary, style guide, lint
  config) stay in each repository; the skill discovers and uses them.

## Design principles

1. **Repository first, defaults second.** Discover and obey the
   repository's own style guide and tooling. Fall back to built-in defaults
   only when the repository has none.
2. **Harness-agnostic.** Follow `skill-format.md`: ordinary files, commands
   and repository state; no tool names, subagents or hooks.
3. **Errors are fixed; warnings are judged.** Lint errors must be fixed.
   Style warnings (passive voice, wordiness, weasel words) are prompts to
   reconsider, not orders. Do not contort clear prose to silence a
   heuristic.
4. **Never silence a real problem by changing config.** Adding genuine
   project jargon to a vocabulary is fine, and the skill should say that it
   did. Adding a misspelling, disabling a rule, or adding an ignore comment
   to get a pass is not, unless the user agrees.
5. **Don't install things unasked.** Use tools the repository already
   provides (`just` recipes, `nix run`, `npx` scripts in `package.json`). If
   none exist, say which checks were skipped rather than installing
   software.
6. **Small `SKILL.md`.** Aim for under about 250 lines, with detail in
   `references/`.

## Generic and repository rules

Two layers of Vale rules, and Vale merges them itself:

- **Generic, shipped here.** `assets/vale/` holds two configs, installed
  in the user's Vale config directory (`~/.config/vale/` on Linux) by their
  machine configuration (for example, declarative_laptop), not by the
  skill:
  - `.vale.ini`, the global config: a `Generic` vocabulary of common
    technical terms, and nothing else.
  - `british.ini`: en_GB (`-ise`) spelling plus the vocabulary, run with
    `vale --config` in repositories that have no Vale config.
- **Repository, local.** A repository's own `.vale.ini`, styles and
  vocabulary. Run from the repository root (for example,
  `~/.config/nixos-config`), Vale reads these and merges the global config
  in. Vocabularies add together: a word on either list passes.

Verified with Vale 3.17: global and repository `Vocab` lists are
concatenated and both style paths are searched; `--no-global` drops the
generic layer.

Why the spelling rule isn't global: `BasedOnStyles` merges too, so a
global en_GB rule would also run in American-English repositories. It also
fails outright in repositories that set their own `StylesPath`, because
Vale then looks for the dictionary only under the repository's path.

Rules for the skill:

- **Prefer the repository.** Run Vale from the repository root, without
  `--config` or `--no-global`, so both layers apply.
- **Add words to the repository's allowlist**, the vocabulary named in its
  `.vale.ini`. Never edit the generic set from another repository; changes
  to it are pull requests to this repository. If the same term keeps being
  added across repositories, suggest promoting it to the generic set.
- **Keep the global config to vocabulary only.** It merges into every
  repository, so any rule there runs everywhere.
- **No repository config:** run `british.ini` with `--config`. Say that only
  the generic rules ran, and don't create a repository config unless the
  user asks.

## Scope of the first version

v1 uses what a repository already has: discover, write, check, fix, report.
These are out of scope until v1 works and has evals:

- **Setup mode:** bootstrapping linting into a repository that has none
  (open question 1). `references/setting-up-linting.md` waits for this.
- **Style guide template:** shipping an `assets/style-guide.md` (open
  question 4).

The lessons below are recorded now so they aren't lost.

## Proposed layout

```text
skills/technical-writing/
  SKILL.md
  README.md                      # human-facing: purpose, provenance, changelog
  assets/
    vale/                        # generic layer: .vale.ini, Generic vocabulary, en_GB spelling
  references/
    discovery.md                 # how to find a repo's standard and tools
    style-defaults.md            # fallback house style (GOV.UK-derived, British)
    linters.md                   # running and interpreting Vale and markdownlint
    setting-up-linting.md        # not in v1: bootstrapping a repo (see below)
```

## Draft frontmatter

```yaml
---
name: technical-writing
description: >-
  Write and edit Markdown documentation to the repository's own style guide
  and check it with the repository's documentation linters before finishing.
  Defaults to plain, British English in the GOV.UK style when the repository
  has no guide. Use when creating or editing README files, docs/ pages, ADRs,
  guides, how-tos, changelogs, issue or PR templates, or any other .md file,
  or when the user asks to proofread, tidy, lint or check documentation, fix
  spelling or Markdown structure, or make docs follow the house style.
license: MIT
---
```

Trigger evals should cover both explicit requests ("tidy the README") and
implicit ones (an agent mid-task about to write `docs/install.md`).

## Procedure for `SKILL.md`

### 1. Discover the repository's standard

Look for these, in order, and read whatever exists:

| What | Where to look |
| ---- | ------------- |
| Style guide | `docs/style-guide.md`, `STYLE.md`, `CONTRIBUTING.md`, a "Writing" or "Docs" section in `README.md` |
| Agent instructions | `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` |
| Vale | `.vale.ini`, `.vale/`, `styles/`; vocabulary at `<StylesPath>/config/vocabularies/<Name>/accept.txt` |
| markdownlint | `.markdownlint-cli2.*`, `.markdownlint.*` |
| Other prose tools | `cspell.json`, `.cspell.*`, `.textlintrc*`, `.alexrc` |
| How to run them | `justfile`, `Makefile`, `package.json` scripts, `flake.nix` apps and packages, CI workflows under `.github/workflows/` |

Note which checks run in CI. Those are hard gates. Local-only checks are
advisory.

#### Finding the style guide

The recommended home for a repository's style guide is
`docs/style-guide.md`. The skill should look for a guide wherever it lives,
in this order, and stop at the first it finds:

1. **An explicit pointer.** A link or path to a style guide in `CLAUDE.md`,
   `AGENTS.md`, `.github/copilot-instructions.md` or `CONTRIBUTING.md`.
   This wins over any conventional path, because it is what the maintainers
   chose.
2. **A conventional path:** `docs/style-guide.md`, then `STYLE.md`,
   `STYLEGUIDE.md`, `docs/STYLE.md` and `.github/STYLE.md`.
3. **A search** for other likely files, skipping dependency and build
   directories:

   ```bash
   find . \( -path ./node_modules -o -path ./vendor -o -path ./.git \) -prune \
     -o -type f \( -iname '*style*guide*.md' -o -iname 'style.md' \) -print
   ```

4. **A section** headed "Writing", "Style" or "Documentation" in
   `CONTRIBUTING.md` or `README.md`.

Read the whole guide before writing; it may override the fallback defaults
in ways a skim misses (for example, Oxford `-ize` spellings).

When there is no guide, use `references/style-defaults.md` and say so in
the report. Suggest adding `docs/style-guide.md`, and linking it from
`CLAUDE.md` or `AGENTS.md` so every agent finds it. Don't create either file
unless the user asks.

### 2. Write

- Follow the repository's style guide. Where it is silent, use
  `references/style-defaults.md`.
- Match the surrounding documents' structure: heading depth, list style,
  link style, code fence languages.
- Respect the repository's terminology. A vocabulary file with
  case-sensitive entries (for example `Flatpak`, `NVMe`) is a terminology
  list as well as a spelling allowlist.

### 3. Check

Run the checks on the files you changed, not the whole repository, unless
the user asks for a full sweep. Prefer the repository's own commands (a
`just` recipe, `make` target or `package.json` script) over calling the
tools directly. Keep repository-specific commands out of `SKILL.md`;
declarative_laptop's `just docs-lint` and `just docs-prose` recipes belong in
`references/linters.md` as a worked example.

When there is config but no recipe, run from the repository root so Vale
picks up the repository's rules and the generic layer (see "Generic and
repository rules"):

```bash
markdownlint-cli2 path/to/file.md
vale --output=line path/to/file.md
```

### 4. Fix and judge

- **markdownlint errors:** fix all of them. `markdownlint-cli2 --fix`
  handles many rules automatically. Review its diff.
- **Spelling errors:** fix real misspellings. Add clear project terms
  (tool, product and command names) to the repository's own vocabulary,
  keeping its existing order and case conventions, and list the additions
  in your report. Ask first when unsure whether a word is jargon or a typo,
  or when a change would edit or remove an existing entry. Never add to the
  generic set from another repository.
- **Terminology errors** (`Vale.Terms`, "Use 'X' instead of 'x'"): fix
  them, unless the hit is a false positive such as a domain name, file
  extension or code. Vale skips inline code, so wrapping a real identifier
  in backticks is the right fix, not a workaround.
- **Style warnings** (write-good, proselint): rewrite when the suggestion
  genuinely improves clarity; otherwise leave the text as it is. Don't
  report each one.

### 5. Report

State which style guide was followed (by path, or "none found, used the
defaults"), which checks ran and their result, which were unavailable or
skipped, any vocabulary additions and the file they went in, and any
warnings deliberately left. Keep
it short.

## Fallback style defaults (`references/style-defaults.md`)

Derived from the [GOV.UK style guide](https://www.gov.uk/guidance/style-guide)
and [content design guidance](https://www.gov.uk/guidance/content-design/writing-for-gov-uk).
GOV.UK content is under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/),
which permits reuse with attribution. Summarise and attribute rather than
copying large passages, and put the attribution in `README.md` and the
reference file.

Starting points:

- British English with -ise spellings (organise, licence as a noun, licence
  or license as a verb, colour, behaviour). Check that -ise rather than
  Oxford -ize is wanted; declarative_laptop uses -ise.
- Plain English: short sentences, common words, active voice where natural,
  front-load the point.
- Sentence-case headings.
- Address the reader as "you".
- Numerals for numbers, except "one" in running prose.
- Spell out an abbreviation on first use unless it is better known than
  its expansion (USB, URL).
- "Wi-Fi", "email", "website", "online".
- Descriptive link text, never "click here".
- Every fenced code block declares a language (`bash`, `nix`, `text`…).

## Lessons from setting up declarative_laptop

These belong in `references/setting-up-linting.md`, for when a user asks
the skill to add linting to a repository, and in `references/linters.md`
for interpreting output.

**Vale:**

- Vale's built-in `Vale.Spelling` uses an en_US dictionary, so American
  spellings pass silently. `Vocab` does not fix this. Vocabularies are
  accept/reject word lists, not dictionaries. For British English, add a
  custom rule and disable the built-in:

  ```yaml
  # <StylesPath>/House/Spelling.yml
  extends: spelling
  message: "'%s' isn't in the British English dictionary or the House vocabulary."
  level: error
  dictionaries:
    - en_GB
  ```

  with `en_GB.aff` and `en_GB.dic` in `<StylesPath>/config/dictionaries/`
  and `Vale.Spelling = NO` in `.vale.ini`.
- `proselint.Spelling` flags British forms as "inconsistent". Disable it
  in British-English repositories.
- `write-good.E-Prime` flags every "is" and "are". In declarative_laptop
  that was 176 of the ~575 findings. Disable it.
- Vocabulary entries are case-sensitive regexes. Prefix with `(?i)` for
  common words (`(?i)config`) and leave proper nouns case-sensitive so they
  enforce capitalisation. Make an entry case-insensitive when it collides
  with an ordinary word, a domain or an abbreviation (`Framework` the brand
  vs "framework", `cd` vs "CI/CD", `Nix` vs `nix.dev`).
- The ~300 spelling hits reduced to about 100 unique words. Seeding a
  vocabulary is a one-off job, not ongoing toil. Present the unique count,
  not the raw count, when proposing it.
- On Nix, the styles and dictionary can be bundled into a wrapped Vale so
  no network `vale sync` is needed. See `packages/vale.nix` in
  declarative_laptop: a `symlinkJoin` of `vale`, `valeStyles.*`, the
  repository's own `.vale/styles` and `hunspellDicts.en_GB-ise`, with
  `VALE_STYLES_PATH` set by `makeBinaryWrapper`. Copy local styles with
  `cp -r --no-preserve=mode`, or later writes fail on read-only store files.

**markdownlint:**

- The noisiest rules were MD060 (table column style, 108 hits) and MD013
  (line length, 35 hits). Both were disabled as low-value churn.
- MD024 (duplicate headings) with `siblings_only: true` permits repeated
  section names under different parents.
- What remained was all worth fixing: fence languages (MD040), bare URLs
  (MD034) and blank lines around lists and fences (MD031, MD032).

**CI:**

- When adding a docs lint job that could become a required check, don't
  filter it with workflow-level `on: paths:`. A PR that doesn't match never
  reports the check and is blocked. Instead, diff in the job and skip its
  steps, which still reports success.
- Keep CI output specific. A check that is correct but unreadable isn't
  useful.

## Evals

The first eval suite in this repository is built against this skill (see
`plan.md`, "Evals: first target"). Most behaviour can be graded
mechanically, so start with these, each a small fixture repository:

| Behaviour | Fixture | Check |
| --------- | ------- | ----- |
| Fix every markdownlint error | Doc with missing fence languages, bare URLs, no blank lines around lists | `markdownlint-cli2` exits 0 on the touched files |
| Never silence a problem through config | Same, with an error that is awkward to fix | Lint config unchanged; no `markdownlint-disable` or Vale ignore comments added |
| Add genuine jargon, report it | Doc using a real tool name and a seeded misspelling | Tool name in `accept.txt` in the existing order; misspelling fixed, not added; report lists the addition |
| British spelling by default | No style guide; doc containing `color`, `organize` | Output has `colour`, `organise` |
| Local allowlist | Repository vocabulary plus generic layer; doc using a new project term | Term added to the repository's `accept.txt`; generic set unchanged |
| Generic term | Doc using `GitHub`, which is only in the generic set | No vocabulary change in the repository |
| Repository first | Style guide that asks for `-ize` | Output follows the guide, not the default |
| Follow the pointer | Guide at `handbook/writing.md`, linked from `AGENTS.md`; a decoy `STYLE.md` with conflicting rules | Output follows the linked guide; report names its path |
| No guide | No guide anywhere | Report says defaults were used and suggests `docs/style-guide.md`; no new files |
| Don't install things unasked | Lint config but no linters available | No new files or lockfile changes; report names the skipped checks |
| Judge warnings, don't obey them | A clear sentence that trips a write-good rule | Sentence unchanged |

Trigger evals: explicit requests ("tidy the README", "lint the docs"),
implicit ones (mid-task, about to write `docs/install.md`), and negatives
that mention Markdown without asking to write it ("what does this README
say?").

The eval sandbox needs `markdownlint-cli2`, Vale, its styles and an en_GB
dictionary available offline. declarative_laptop's wrapped Vale already
bundles these.

## Open questions

Settle these with the user before or while implementing:

1. **Scope of the setup mode** (out of scope for v1). Should the skill
   bootstrap linting into a repository that has none (proposing config,
   vocabulary and a recipe), or only use what exists? Suggested approach:
   use what exists by default, and offer setup only when the user asks.
2. ~~**Default spelling.**~~ Decided: British English with -ise when the
   repository has no guide. A guide that says otherwise wins.
3. ~~**Vocabulary edits.**~~ Decided: add clear project terms to the
   repository's own vocabulary and report them; ask when unsure. The
   generic set changes only through this repository (see "Generic and
   repository rules").
4. **Style guide template** (out of scope for v1). The recommended path
   is settled as `docs/style-guide.md`, and declarative_laptop#52 still
   needs one there. Should this skill ship an `assets/style-guide.md`
   template, derived from GOV.UK plus a terminology section, that repositories
   copy and adapt?

## Tasks

- [x] Branch from an up-to-date `main`
- [x] Resolve open questions 2 and 3 with the user
- [x] Write `skills/technical-writing/SKILL.md` and the v1 `references/` files
- [x] Build the generic layer in `assets/vale/`, and document wiring it into
      `~/.config/vale/` (declarative_laptop is the first user)
- [x] Write the first evals under `evals/technical-writing/` and get them
      running: `fix-markdownlint`, `british-default`, `vocab-local`,
      `no-trigger`
- [ ] Write the remaining cases: repository first, follow the pointer, no
      guide, generic term, and no linters available
- [x] Write `README.md` with purpose, GOV.UK/OGL attribution and changelog
- [x] Add the skill to the table in the root `README.md`
- [ ] Symlink it into the harness skill directories (see `skill-format.md`)
      and confirm it triggers when editing Markdown in declarative_laptop
- [ ] Try it end to end in declarative_laptop: edit a doc, confirm
      `just docs-lint` and `just docs-prose` run, errors get fixed and
      warnings are judged, not blindly applied
- [ ] Delete or archive this brief once the skill and its README replace it
