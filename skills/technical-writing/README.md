# technical-writing

An agent skill for writing and editing Markdown documentation to a
repository's own standard. The agent:

- finds and follows the repository's style guide, falling back to plain
  British English in the GOV.UK style
- checks its work with the repository's markdownlint and Vale setup,
  through the repository's own recipes where there are any
- fixes lint errors, judges style warnings rather than obeying them, and
  never silences a problem by changing config
- reports which guide it followed, which checks ran, and any vocabulary it
  added

It installs nothing. Creating config, changing rules or editing existing
vocabulary entries needs the user's approval.

## Files

- `SKILL.md`: the procedure the agent follows
- `references/discovery.md`: finding the style guide, lint config and check
  commands
- `references/linters.md`: running and reading markdownlint and Vale, and
  the generic layer
- `references/style-defaults.md`: the fallback house style
- `assets/vale/`: the generic Vale layer (see below)

## Requirements

None, strictly. The checks need `markdownlint-cli2` and Vale, provided by
the repository (a recipe, a Nix app, a `package.json` script) or the
machine. Without them, the skill writes to the standard and reports which
checks it skipped.

## The generic Vale layer

`assets/vale/` holds Vale config to install in Vale's config directory
(`vale ls-dirs` shows it; `~/.config/vale/` on Linux):

- `.vale.ini`: the `Generic` vocabulary of common technical terms. Vale
  merges it into every repository's config, so it holds no rules: a rule
  here would also run in repositories that want different ones.
- `british.ini`: en_GB (`-ise`) spelling plus the vocabulary, used with
  `vale --config` in repositories that have no Vale config.

Inside a repository with its own `.vale.ini`, the repository's rules apply
and the generic vocabulary adds to its own. New project terms go in the
repository's vocabulary; the generic list changes only through pull
requests here.

### Installing it

Link the config and styles rather than copying them, so updates arrive
with this repository. Keep `styles/` itself a real directory, because the
dictionary goes inside it:

```bash
skill=~/Projects/skills/skills/technical-writing/assets/vale
config=~/.config/vale   # check with: vale ls-dirs

mkdir -p "$config/styles/config/vocabularies" "$config/styles/config/dictionaries"
ln -sfn "$skill/.vale.ini" "$config/.vale.ini"
ln -sfn "$skill/british.ini" "$config/british.ini"
ln -sfn "$skill/styles/Generic" "$config/styles/Generic"
ln -sfn "$skill/styles/config/vocabularies/Generic" "$config/styles/config/vocabularies/Generic"
```

Then add an `-ise` en_GB Hunspell dictionary as
`$config/styles/config/dictionaries/en_GB.aff` and `en_GB.dic`. On Nix,
`hunspellDicts.en_GB-ise` provides one; link its
`share/hunspell/en_GB.{aff,dic}`. Other distributions' en_GB dictionaries
may accept `-ize` spellings as well.

With Home Manager, the same layout can be built with `xdg.configFile`
entries pointing at this repository as a flake input.

## Provenance

The fallback style in `references/style-defaults.md` summarises the
[GOV.UK style guide](https://www.gov.uk/guidance/style-guide) and
[writing for GOV.UK](https://www.gov.uk/guidance/content-design/writing-for-gov-uk)
by the Government Digital Service, used under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

The linting lessons come from setting up documentation checks in
[huwd/declarative_laptop](https://github.com/huwd/declarative_laptop), the
skill's first user.

## Changelog

- **Unreleased:** first version. Discovers the style guide and tools,
  writes, checks, fixes and reports. Ships the generic Vale layer.
