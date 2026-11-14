#!/usr/bin/env bash
# No style guide or lint config. The research is in a file, but the
# decision and its reasons exist only in the prompt, as they would in a
# working session. The prompt gives no reader and calls the document a
# "brief", which invites a work order written to the agent itself.
set -euo pipefail

mkdir -p notes docs
cat > README.md <<'MD'
# relay

A small service that delivers webhooks to subscriber endpoints.
MD

cat > notes/retry-options.md <<'MD'
# Retry options for failed deliveries

Issue 14: a delivery that fails once is dropped.

| Option | What it does | Cost |
| ------ | ------------ | ---- |
| Fixed interval | Retries every 30 seconds, 5 times | Simple, but hammers an endpoint that is down |
| Exponential backoff with jitter | Waits 1s, 2s, 4s and so on, with a random spread | A little more code; spreads the load |
| Dead-letter queue | Parks failed deliveries for manual replay | Needs a queue dependency and someone to watch it |
MD

git init -q
git add -A
git -c user.name=Fixture -c user.email=fixture@example.com commit -qm "Initial commit"
