#!/usr/bin/env bash
set -euo pipefail
cat > CLAUDE.md <<'MD'
# Fixture conventions

Skills live in skills/<name>/SKILL.md. Use metadata.version with stable
SemVer, initially "0.1.0"; increase it for skill changes. Do not add top-level
version, category, allowed-tools or a harness-specific compatibility value.
Use the existing tools; do not install anything. Do not commit or push.
MD
mkdir -p skills/check-build
cat > skills/check-build/SKILL.md <<'MD'
---
name: check-build
description: Check the remote build state when asked whether a build succeeded.
metadata:
  version: "0.1.0"
---

# Check build

Read the build identifier from the user's request. Run buildctl status ID.
Retry every failed status call up to three times, then report the error.
For a pending build, poll at most three times with a ten-second interval.
Report the build identifier and final status. Do not cancel or rerun builds.
MD
cat > failure.txt <<'TXT'
Observed run: buildctl status build-42 returned HTTP 403, access denied.
The agent sent the same request three more times without changing credentials.
The command ran correctly; retries did not help a permanent access failure.
The user wants transient transport failures retried, not permanent auth failures.
TXT

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com \
  -c commit.gpgsign=false commit -qm "Initial fixture"
