#!/usr/bin/env bash
# A repository whose markdownlint config runs in CI, and a doc that already
# breaks MD040 (fence language), MD034 (bare URL) and MD032 (list spacing).
set -euo pipefail

# The repository provides its own lint command, as many do. Resolve the
# binary now: the agent's sandbox may not have it on PATH.
mdl="$(command -v markdownlint-cli2)" || {
  echo "markdownlint-cli2 not on PATH; see evals/technical-writing/run.sh" >&2
  exit 1
}

mkdir -p docs scripts .github/workflows

cat > scripts/lint-docs <<SH
#!/usr/bin/env bash
# Lint Markdown: scripts/lint-docs [FILE...] (default: every .md file)
if [ "\$#" -eq 0 ]; then set -- '**/*.md'; fi
exec "$mdl" "\$@"
SH
chmod +x scripts/lint-docs

cat > .markdownlint-cli2.yaml <<'YAML'
config:
  MD013: false
YAML

cat > .github/workflows/docs.yml <<'YAML'
name: Docs
on: [pull_request]
jobs:
  markdown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: scripts/lint-docs
YAML

cat > docs/install.md <<'MD'
# Install

Download the latest release from https://example.com/download and unpack it.

Steps:
- unpack the archive
- run the installer

```
make install
```
MD

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com commit -qm "Initial commit"
