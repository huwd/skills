# Output formats

## Single-PR review

```markdown
## Dependabot Review: `<package>` (<old> -> <new>)

### Bump Type
[patch/minor/major/pre] - [one line about risk]

### What Changed
[Breaking changes first, then deprecations, security fixes, relevant bug fixes/features. If quiet: "No breaking changes or deprecations found."]

### Breaking Changes in This Codebase
[Only include if applicable: affected file plus concrete fix. Otherwise omit.]

### Codebase Impact
[Grouped list of touched areas, not an exhaustive file dump.]

### Recommendation
[Merge / Verify / Investigate / Hold] - [1-3 sentences with the reason and any specific check.]
```

## Audit report

In this order:

1. Preamble: `Reviewed N open Dependabot PRs in <repo>.`
2. Summary table.
3. Details: one subsection per PR in the single-PR format, condensed to roughly 15-25 lines each.
4. Overall recommendation grouped by verdict, with related package families called out as sets.

Summary table shape:

```markdown
| # | Package | Bump | Type | Age | Verdict | Why |
|---|---------|------|------|-----|---------|-----|
| [#123](url) | package-name | 1.2.3 -> 1.2.4 | patch | 7d | Merge | dev-only patch |
| [#124](url) | other-package | 2.0.1 -> 2.0.2 | 🔒 patch | 2d | Merge | advisory fix, CI green |
```

- Sort by verdict: `Merge`, `Verify`, `Investigate`, `Hold`. Within each verdict, oldest first.
- Advisory-driven PRs go first regardless of verdict, with `🔒` before their `Type`.
- For grouped PRs, comma-separate the packages.
- Keep `Why` concrete and short, about ten words. "dev-only, no breaking changes" beats "looks safe".
- Do not add columns; put extra details in the per-PR section.

## PR comment

```markdown
## Dependabot review

**Verdict:** <Merge / Verify / Investigate / Hold>

<one-line reason>

<details>
<summary>Full review</summary>

<full per-PR review>

</details>

<!-- dependabot-audit:v1 -->
```

- The verdict and one-line reason sit above the fold, so a teammate can triage without expanding the review.
- The `dependabot-audit:v1` marker is invisible when rendered and lets a later run find its earlier comment. thoughtbot's dependabot review skill uses the same marker, so each skill recognizes the other's comments.
- Do not add attribution or a generated-by signature.

## Confirmation after posting

- Single PR: `Posted comment on #<number>.`
- Audit mode: `Posted N comments: #12, #15. Skipped M: #18 (had a prior review).`
