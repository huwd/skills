---
type: regex
target: { source: file, path: docs/retry-brief.md }
pattern: '\b(5|five)\b[^\n]{0,40}(attempts|tries|retries)|(attempts|tries|retries)[^\n]{0,40}\b(5|five)\b'
flags: i
---
