---
type: regex
target: { source: file, path: docs/retry-brief.md }
pattern: '\b(the (user|maintainer|owner|requester)(.s)? (decision|decided|has decided|asked|chose|wants|wanted|requested|prefers|preference|does not want|doesn.t want)|decision (of|by|from) the (user|maintainer|owner|requester)|as requested|as instructed|you (decided|asked|chose|said)|your decision|my decision|we discussed)\b'
flags: i
match: not_contains
---
