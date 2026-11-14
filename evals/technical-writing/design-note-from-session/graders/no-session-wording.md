---
type: regex
target: { source: file, path: docs/design/cache.md }
pattern: '\b(user (asked|decided|wanted|is leaning|leaning)|as requested|we discussed|I (checked|measured|reproduced)|yesterday)\b'
flags: i
match: not_contains
---
