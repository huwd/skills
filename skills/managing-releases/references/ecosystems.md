# Ecosystem release details

Read the section for the repository's ecosystem. The repository's own
workflow and documentation take precedence over these defaults.

## Version sources and checks

| Ecosystem | Common version source | Common checks |
| --------- | --------------------- | ------------- |
| RubyGems | `lib/**/version.rb`, `*.gemspec` | `bundle exec rake build`, `gem build`, `gem install pkg/*.gem` |
| npm | `package.json`, lockfile | `npm pack --dry-run`, `npm publish --dry-run` |
| Cargo | `Cargo.toml`, `Cargo.lock` for binaries | `cargo test`, `cargo package`, `cargo publish --dry-run` |
| PyPI | `pyproject.toml`, `__version__` if used | `python -m build`, `twine check dist/*` |
| Go modules | Tags are usually the source of truth | `go test ./...`, module-aware tags in a monorepo |
| Skill bundles | A root `VERSION`, with per-skill `metadata.version` | The repository's validation and version-check scripts |

All visible version data must agree before tagging. Search for the old
version to catch documentation, install snippets and lockfiles:

```bash
rg -n "<old-version>" .
```

Do not regenerate lockfiles or package metadata unless the ecosystem
expects it. When a gem's `Gemfile` uses `gemspec`, `Gemfile.lock` lists the
gem's own version under `PATH`; an npm package's `package-lock.json` also
records its own version. Update those entries with the version.

## RubyGems with a tag-driven workflow

Release workflows often check that the tag matches the version constant and
that the changelog names the version. Run the local equivalents:

```bash
ruby -r ./lib/<package>/version -e "puts <Module>::VERSION"
grep -Eq "^##[[:space:]]+\[?<version>\]?([[:space:]-]|$)" CHANGELOG.md
bundle exec rspec
bundle exec rubocop
bundle exec rake build
gem install pkg/*.gem --no-document
```

Adapt `<package>` and `<Module>`. Run any further workflow checks, such as
documentation generation. Trusted publishing through
`rubygems/release-gem` needs no local credentials.

## npm, Cargo and PyPI

```bash
npm test && npm run build --if-present && npm pack --dry-run
cargo test && cargo package && cargo publish --dry-run
python -m build && python -m twine check dist/*
```

## Tagging

Use the repository's tag format, such as `v1.2.3` or `1.2.3`, and type.
For an annotated tag on the merged release commit:

```bash
git fetch origin
git tag -a v<version> -m "Release v<version>" <merged-commit>
git push origin v<version>
gh run list --workflow release.yml --limit 5
gh run watch <run-id>
```

If the workflow supports `workflow_dispatch` with a dry run, run that first:

```bash
gh workflow run release.yml -f dry_run=true
```

## GitHub Releases

Use the changelog section as the notes. Do not invent notes; update the
changelog first if it is incomplete.

```bash
gh release view v<version>
gh release create v<version> --title "v<version>" --notes-file <notes-file>
gh release edit v<version> --title "v<version>" --notes-file <notes-file>
```

## Registry verification

```bash
gem info <gem-name> --remote --version <version>
npm view <package-name>@<version> version
cargo search <crate-name> --limit 5
python -m pip index versions <package-name>
git ls-remote --tags origin "v<version>"
```
