# Discovering a repository's standard

How to find a repository's style guide, lint config and check commands.
Read whatever exists before writing.

## Where to look

| What | Where |
| ---- | ----- |
| Style guide | See [Finding the style guide](#finding-the-style-guide) |
| Agent instructions | `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` |
| Vale | `.vale.ini`, `.vale/`, `styles/`; vocabulary at `<StylesPath>/config/vocabularies/<Name>/accept.txt` |
| markdownlint | `.markdownlint-cli2.jsonc`, `.markdownlint-cli2.yaml`, `.markdownlint.json`, `.markdownlint.yaml` |
| Other prose tools | `cspell.json`, `.cspell.*`, `.textlintrc*`, `.alexrc` |
| How checks run | `justfile`, `Makefile`, `package.json` scripts, `flake.nix` apps and packages, `.github/workflows/` |

## Finding the style guide

The recommended home is `docs/style-guide.md`, but look wherever it lives,
in this order, and stop at the first you find:

1. **An explicit pointer.** A link or path to a style guide in
   `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` or
   `CONTRIBUTING.md`. This wins over any conventional path, because it is
   what the maintainers chose.
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

Read the whole guide. Guides often record only where the repository
differs from a base standard (for example, "follow GOV.UK, except…"), so
read the base standard's defaults as well: see
[style-defaults.md](style-defaults.md).

## Which checks are gates

Look in `.github/workflows/` (or the repository's CI config) for the
commands that run on pull requests. Those are hard gates: the work isn't
done until they pass. Checks that only run locally, or that a comment or
recipe marks as advisory, are advice: fix errors, judge warnings.

A repository may run the same tool both ways. For example, markdownlint in
CI as a gate, and Vale locally as advice.

## Recipes and wrappers

Prefer the repository's own command over calling a tool directly:

- **`just` or `make`:** run `just --list` or read the `Makefile` for
  targets named like `docs-lint`, `docs-prose`, `lint-docs` or `prose`.
- **`package.json`:** scripts such as `lint:md` or `lint:docs`, run with
  `npm run <script>`.
- **Nix flakes:** an app or package such as `nix run .#vale`. A wrapped
  Vale may set `VALE_STYLES_PATH` itself, so a `.vale.ini` with no
  `StylesPath` is normal there.

A recipe that takes file arguments should be given the files you changed.
One that always checks the whole repository is fine to run as it is.
