---
type: regex
target: { source: file, path: docs/install.md }
pattern: '^```[ \t]*\n\s*make install'
flags: m
match: not_contains
---
