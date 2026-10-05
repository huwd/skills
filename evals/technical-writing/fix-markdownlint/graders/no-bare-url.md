---
type: regex
target: { source: file, path: docs/install.md }
pattern: '(^|\s)https://example\.com/download'
flags: m
match: not_contains
---
