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
For a pending build, poll at most three times with a ten-second interval.
Report the build identifier and final status. Do not cancel or rerun builds.
MD
cat > README.md <<'MD'
# Fixture skills

A small catalogue of agent skills. Each skill is a folder under `skills/`
containing a `SKILL.md`.

## Skills

- `check-build`: reports the state of a remote build.

## Install

Link each skill folder into your agent's skills directory:

```bash
mkdir -p ~/.agent/skills
ln -s "$PWD/skills/check-build" ~/.agent/skills/check-build
```

Restart the agent so it discovers the new skill.
MD

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com \
  -c commit.gpgsign=false commit -qm "Initial fixture"
