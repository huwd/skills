---
type: regex
target: { source: file, path: docs/retry-brief.md }
pattern: '^#[^\n]*\n+(?:[^\n]+\n)*?[^\n]*\b(records|explains|describes|is for|backoff)\b'
flags: i
---
