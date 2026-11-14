---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

Thanks, I've read notes/retry-options.md. Let's go with exponential
backoff with jitter, capped at 5 attempts. Skip the dead-letter queue for
now: I don't want a new dependency and nobody would watch it. Before you
implement anything, record the research and my decision as
docs/retry-brief.md. It's for issue 14.
