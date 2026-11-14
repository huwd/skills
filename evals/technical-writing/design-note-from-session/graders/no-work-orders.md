---
type: regex
target: { source: file, path: docs/design/cache.md }
pattern: '(?:^|\n|[.:] )(?:[-*] )?(Implement the cache|Keep the schema|Do not cache|Don.t cache)\b'
match: not_contains
---
