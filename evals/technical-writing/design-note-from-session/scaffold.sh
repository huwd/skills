#!/usr/bin/env bash
# No style guide or lint config. The only source is a set of notes written
# from inside a working session: they refer to "the user", narrate what the
# agent did, use a relative date and mix decisions with work orders. The
# design note must keep the facts and drop that voice.
set -euo pipefail

mkdir -p notes docs/design
cat > README.md <<'MD'
# tidy

A command-line tool that keeps dependency manifests in step across a
monorepo. `tidy sync` reads every manifest and rewrites the ones that
have drifted.
MD

cat > notes/session-2026-03-04.md <<'MD'
# Session notes, 4 March

- User asked me to look at why `tidy sync` is slow on big repos. I checked
  and it re-parses every manifest on each run.
- We discussed three options yesterday: a JSON file cache, SQLite, or a
  background daemon.
- User decided on SQLite. JSON rejected because concurrent runs corrupt
  the file (I reproduced this with two parallel syncs). Daemon rejected as
  too much to maintain for one command.
- Implement the cache in `internal/cache`. Keep the schema to one table.
  Do not cache auth tokens.
- As requested, the cache lives at `$XDG_CACHE_HOME/tidy/cache.db`.
- I measured 41s before and 6s after on the monorepo fixture, 3 runs each.
- TODO: decide eviction. User leaning towards dropping entries after 30
  days.
MD

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com commit -qm "Initial commit"
