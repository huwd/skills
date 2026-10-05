# Running and reading the linters

## markdownlint-cli2

Checks Markdown structure. It reads `.markdownlint-cli2.*` or
`.markdownlint.*` from the repository root.

```bash
markdownlint-cli2 path/to/file.md
markdownlint-cli2 --fix path/to/file.md   # fixes what it can; review the diff
```

Output is `file:line[:column] RULE/alias description`. Common rules:

| Rule | Fix |
| ---- | --- |
| MD040 fenced code language | Add a language: `bash`, `text`, `json`… |
| MD034 bare URL | Wrap in `<...>` or give it link text |
| MD031, MD032 blanks around fences and lists | Add a blank line before and after |
| MD029 ordered list prefix | Usually a paragraph that should be indented into the list item above |
| MD024 duplicate heading | Rename, or nest it under a different parent if the config allows siblings only |

Fix every error. Never add `<!-- markdownlint-disable -->` comments or
change the config without the user's agreement.

## Vale

Checks prose: spelling, terminology and style. Output with
`--output=line` is `file:line:column:Style.Rule:message`.

### Severity

- **error:** fix it. Spelling (`*.Spelling`) and terminology (`*.Terms`,
  "Use 'X' instead of 'x'") rules are usually errors.
- **warning and suggestion:** judge it. write-good and proselint rules
  (passive voice, weasel words, wordiness) flag patterns, not mistakes.
  Rewrite only when it makes the text clearer.

### The two layers

Vale loads a global config from its config directory (`vale ls-dirs`
shows it; `~/.config/vale/` on Linux) and merges it with the repository's
`.vale.ini`:

- **Vocabularies add together.** A word on either the global or the
  repository list passes.
- **Styles add together too.** A style enabled globally runs in every
  repository, alongside the repository's own.

This skill ships a generic layer in `assets/vale/` that relies on this:

| File | Installed as | Holds |
| ---- | ------------ | ----- |
| `.vale.ini` | `<config dir>/.vale.ini` | The `Generic` vocabulary only, so it is safe to merge into any repository |
| `british.ini` | `<config dir>/british.ini` | en_GB (`-ise`) spelling plus the vocabulary, for repositories with no Vale config |
| `styles/` | `<config dir>/styles/` | The `Generic` spelling rule and vocabulary |

The en_GB spelling rule needs an `-ise` en_GB Hunspell dictionary
(`en_GB.aff`, `en_GB.dic`) in `<config dir>/styles/config/dictionaries/`.
The skill's README covers installing it.

How to run it:

- **The repository has a `.vale.ini`:** run `vale` (or the repository's
  recipe) with no `--config` and no `--no-global`. Both layers apply.
- **No `.vale.ini`:** run
  `vale --config "<config dir>/british.ini" FILE.md`. If `british.ini`
  isn't installed, plain `vale` uses Vale's built-in en_US spelling, so say
  so in the report and check British spellings by eye.

Don't pass `--no-global` in a repository with a Nix-wrapped Vale either:
some wrappers rely on the global config path to find their styles.

### Vocabulary entries

Vale vocabularies live at
`<StylesPath>/config/vocabularies/<Name>/accept.txt`, one entry per line.
Entries are case-sensitive regular expressions:

- **Ordinary words:** prefix with `(?i)` so any case passes:
  `(?i)lockfiles?`.
- **Product and proper names:** leave case-sensitive so the capitalisation
  is enforced: `GitHub`, `NVMe`, `Flatpak`.
- **Collisions:** make an entry case-insensitive when the name is also an
  ordinary word, a domain or an abbreviation (`Framework` the brand and
  "framework"; `Nix` and `nix.dev`).
- Keep the file's existing order (usually alphabetical) and style.

Vale doesn't flag all-capital acronyms (`JSON`, `CLI`), but it does flag
their plurals (`APIs`, `UUIDs`). The generic vocabulary accepts those with
one pattern, `[A-Z]{2,}s`.

### Common false positives

- **Code, paths, commands and identifiers** in prose: wrap them in
  backticks. Vale skips inline code, and the docs read better too.
- **British forms flagged as inconsistent:** `proselint.Spelling` is
  US-centric. A British repository should turn it off; suggest that rather
  than changing the text.
- **Every "is" and "are" flagged:** `write-good.E-Prime`. Noise; suggest
  turning it off rather than rewriting.

## Worked example: declarative_laptop

[huwd/declarative_laptop](https://github.com/huwd/declarative_laptop) runs
markdownlint in CI and Vale locally, both through `just`:

```bash
just docs-lint                  # markdownlint-cli2, whole repository; also in CI
just docs-prose path/to/file.md # Vale, advisory; omit files for the whole repository
```

Its Vale is a Nix wrapper (`nix run .#vale`) that bundles the styles, the
repository's own `.vale/styles` and an en_GB dictionary, so there's no
`vale sync` step. Its `.vale.ini` has no `StylesPath` for that reason. Its
vocabulary is `.vale/styles/config/vocabularies/House/accept.txt`.
