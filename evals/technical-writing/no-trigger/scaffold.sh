#!/usr/bin/env bash
# A README with an install section, including a spelling the skill would
# change if it were (wrongly) invoked.
set -euo pipefail

cat > README.md <<'MD'
# Widget

A small tool to organize your notes.

## Install

Run `make install`, then `widget init` in your notes folder.
MD

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com commit -qm "Initial commit"
