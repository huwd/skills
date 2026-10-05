---
type: regex
target: { source: file, path: docs/themes.md }
pattern: '\b(organize|behavior|customize|color)\b(?!")'
flags: i
match: not_contains
---
