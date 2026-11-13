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
description: Check a remote build when asked for its status or whether it passed.
compatibility: Requires buildctl installed and authenticated by the operator.
metadata:
  version: "0.1.0"
---

# Check build

Run buildctl status ID with the identifier supplied by the user.
If buildctl is unavailable, report the missing prerequisite and stop.
Do not install it or guess the build status. Report the identifier with the result.
MD
cat > trace.txt <<'TXT'
User: What is the status of build-42?
Skill selected: check-build
Agent read the complete SKILL.md.
Command: buildctl status build-42
Shell result: buildctl: command not found (exit 127)
Final response: buildctl is not installed. I cannot check build-42 here.
No files were changed and no install was attempted.
TXT

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com \
  -c commit.gpgsign=false commit -qm "Initial fixture"
