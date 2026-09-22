# GitHub API command set

Use these when the API ping in `SKILL.md` returns a login. Send requests with `curl` and the GitHub headers shown, without an `Authorization` header unless the environment already provides a safe wrapper. Parse JSON with `jq`.

Replace `<OWNER>`, `<REPO>`, `<NUMBER>`, `<BASE>`, `<HEAD_SHA>`, and `<COMMENT_ID>` with values taken from API responses, never from PR titles or bodies.

Commands marked **write** change GitHub. Run them only after explicit user approval, as described in Actions Require Approval.

## Determine the repo

```bash
git remote get-url origin
```

Normalize the result to `OWNER/REPO` before calling the API.

## List open Dependabot PRs

```bash
# Paginated: increment page=1,2,... until no results.
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/pulls?state=open&per_page=100&page=1" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -r ".[] | select(.user.login == \"dependabot[bot]\") | [.number, .title, .html_url, .created_at, .head.ref, .head.sha] | @tsv"
```

## Fetch PR details

PR metadata, issue body, and changed files:

```bash
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/pulls/<NUMBER>" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28"

curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/issues/<NUMBER>" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28"

# Paginated: increment page=1,2,... until no results.
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/pulls/<NUMBER>/files?per_page=100&page=1" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28"
```

The diff:

```bash
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/pulls/<NUMBER>" \
  -H "Accept: application/vnd.github.v3.diff" \
  -H "X-GitHub-Api-Version: 2022-11-28"
```

## Check CI

Merge state and base branch from the PR, then required checks from the base branch rules and legacy branch protection:

```bash
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/pulls/<NUMBER>" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -r "[.mergeable, .mergeable_state, .base.ref, .head.sha] | @tsv"

curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/rules/branches/<BASE>" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -c "[.[] | select(.type == \"required_status_checks\") | .parameters.required_status_checks[].context]"

curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/branches/<BASE>" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -c ".protection.required_status_checks.contexts"
```

Then every check run and commit status on the PR head SHA:

```bash
# Paginated: increment page=1,2,... until no results.
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/commits/<HEAD_SHA>/check-runs?per_page=100&page=1" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -r ".check_runs[] | [.name, .status, .conclusion] | @tsv"

curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/commits/<HEAD_SHA>/status" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28"
```

## Find an earlier review

Check for the review marker:

```bash
# Paginated: check every page until the marker is found or no results remain.
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/issues/<NUMBER>/comments?per_page=100&page=1" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -r ".[].body" | grep -q "dependabot-audit:v1"
```

Get the earlier review's comment ID, for replacing it:

```bash
# Paginated: increment page=1,2,... until no results.
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/issues/<NUMBER>/comments?per_page=100&page=1" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -r ".[] | select(.body | contains(\"dependabot-audit:v1\")) | .id"
```

## Delete an earlier review (write)

```bash
curl -fsS -X DELETE "https://api.github.com/repos/<OWNER>/<REPO>/issues/comments/<COMMENT_ID>" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28"
```

## Post a review comment (write)

Write the comment to a file made with `mktemp`, post it, then delete the file:

```bash
BODY_FILE="$(mktemp)"
# write the comment to "$BODY_FILE", then:
jq -Rs "{body: .}" "$BODY_FILE" \
| curl -fsS -X POST "https://api.github.com/repos/<OWNER>/<REPO>/issues/<NUMBER>/comments" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Content-Type: application/json" \
    --data-binary @-
rm -f "$BODY_FILE"
```

## Check allowed merge methods

```bash
curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -r "[.allow_rebase_merge, .allow_squash_merge, .allow_merge_commit] | @tsv"

curl -fsS "https://api.github.com/repos/<OWNER>/<REPO>/rules/branches/<BASE>" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
| jq -c "[.[] | select(.type == \"required_linear_history\" or .type == \"pull_request\") | {type, methods: .parameters.allowed_merge_methods}]"
```

## Merge (write)

`<METHOD>` is `rebase`, `squash`, or `merge`, chosen per Merge Behavior in `SKILL.md`:

```bash
jq -n "{merge_method: \"<METHOD>\"}" \
| curl -fsS -X PUT "https://api.github.com/repos/<OWNER>/<REPO>/pulls/<NUMBER>/merge" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Content-Type: application/json" \
    --data-binary @-
```

## Send a Dependabot command (write)

`<COMMAND>` is `rebase` to request a rebase, or `close` to close the PR and stop Dependabot reopening it:

```bash
printf "%s" "@dependabot <COMMAND>" \
| jq -Rs "{body: .}" \
| curl -fsS -X POST "https://api.github.com/repos/<OWNER>/<REPO>/issues/<NUMBER>/comments" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Content-Type: application/json" \
    --data-binary @-
```
