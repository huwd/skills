---
timeout_seconds: 300
---

Stop should_retry in src/retry.py retrying HTTP 403 access denials, and
add a regression test. notes/reason.md explains why. Commit the fix once
the checks pass. Do not push.
