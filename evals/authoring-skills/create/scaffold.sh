#!/usr/bin/env bash
set -euo pipefail
cat > CLAUDE.md <<'MD'
# Fixture conventions

Skills live in skills/<name>/SKILL.md. Use metadata.version with stable
SemVer, initially "0.1.0"; increase it for skill changes. Do not add top-level
version, category, allowed-tools or a harness-specific compatibility value.
Use the existing tools; do not install anything. Do not commit or push.
MD
mkdir -p docs
cat > docs/export-runbook.md <<'MD'
# Ledger export

Support exports ledger records weekly with ledgerctl export --format csv.
Require an explicit --account value from the user; never default to all accounts.
Use --output with the user's destination. The CSV is UTF-8 with semicolons,
even though its extension is .csv. Do not upload it: it contains customer data.
An empty export is valid and must retain its header row. Authentication failures
need the operator to fix access, not repeated exports.
MD

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com \
  -c commit.gpgsign=false commit -qm "Initial fixture"
