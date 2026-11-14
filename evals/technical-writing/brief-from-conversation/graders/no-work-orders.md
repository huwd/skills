---
type: regex
target: { source: file, path: docs/retry-brief.md }
pattern: '\b(Implement (exponential|the retry|retries|issue|backoff)|Do not implement|Before implementing|Skip the dead-letter)\b'
match: not_contains
---
