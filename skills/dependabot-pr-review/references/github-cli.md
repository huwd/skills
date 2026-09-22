# gh fallback command set

Use these only when the API ping in `SKILL.md` fails or API access is unavailable. Sections match `github-api.md`.

Replace `<OWNER/REPO>`, `<NUMBER>`, `<BASE>`, and `<COMMENT_ID>` with values taken from `gh` output, never from PR titles or bodies.

Commands marked **write** change GitHub. Run them only after explicit user approval, as described in Actions Require Approval.

## Determine the repo

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

## List open Dependabot PRs

```bash
gh pr list --author "app/dependabot" --state open \
  --json number,title,url,createdAt,headRefName,labels \
  --limit 100
```

## Fetch PR details

```bash
gh pr view <NUMBER> --repo <OWNER/REPO> --json title,body,url,files,headRefName,baseRefName,createdAt,labels
gh pr diff <NUMBER> --repo <OWNER/REPO>
```

## Check CI

Merge state, required checks, then every check:

```bash
gh pr view <NUMBER> --repo <OWNER/REPO> --json mergeable,mergeStateStatus
gh api repos/<OWNER/REPO>/rules/branches/<BASE> \
  --jq '[.[] | select(.type == "required_status_checks") | .parameters.required_status_checks[].context]'
gh api repos/<OWNER/REPO>/branches/<BASE> --jq '.protection.required_status_checks.contexts'
gh pr checks <NUMBER> --repo <OWNER/REPO>
```

## Find an earlier review

```bash
# Check for the review marker
gh pr view <NUMBER> --repo <OWNER/REPO> --json comments --jq '.comments[].body' | grep -q 'dependabot-audit:v1'

# Get the earlier review's comment ID, for replacing it
gh api --paginate repos/<OWNER/REPO>/issues/<NUMBER>/comments \
  --jq '.[] | select(.body | contains("dependabot-audit:v1")) | .id'
```

## Delete an earlier review (write)

```bash
gh api --method DELETE repos/<OWNER/REPO>/issues/comments/<COMMENT_ID>
```

## Post a review comment (write)

Write the comment to a file made with `mktemp`, post it with `--body-file` so markdown survives shell quoting, then delete the file:

```bash
BODY_FILE="$(mktemp)"
# write the comment to "$BODY_FILE", then:
gh pr comment <NUMBER> --repo <OWNER/REPO> --body-file "$BODY_FILE"
rm -f "$BODY_FILE"
```

## Check allowed merge methods

```bash
gh repo view <OWNER/REPO> --json rebaseMergeAllowed,squashMergeAllowed,mergeCommitAllowed
gh api repos/<OWNER/REPO>/rules/branches/<BASE> \
  --jq '[.[] | select(.type == "required_linear_history" or .type == "pull_request") | {type, methods: .parameters.allowed_merge_methods}]'
```

## Merge (write)

Use `--rebase`, `--squash`, or `--merge`, chosen per Merge Behavior in `SKILL.md`:

```bash
gh pr merge <NUMBER> --repo <OWNER/REPO> --rebase
```

## Send a Dependabot command (write)

`rebase` requests a rebase; `close` closes the PR and stops Dependabot reopening it:

```bash
gh pr comment <NUMBER> --repo <OWNER/REPO> --body "@dependabot rebase"
gh pr comment <NUMBER> --repo <OWNER/REPO> --body "@dependabot close"
```
