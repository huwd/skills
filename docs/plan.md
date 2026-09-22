# Skills Management — Plan

## Goal

Move from hand-symlinked skills in the standards repo to a managed, CI-gated skills
catalogue that installs into every harness I use (Claude Code, Codex,
OpenCode) with one command, and that other people could consume.

Starter set: **dependabot-pr-review**, **atomic-commits**, **general**.

Order of work:

1. Get one skill into a format we're happy with (dependabot-pr-review).
2. Settle the repository structure and a minimum CI.
3. Stand up a basic agent-manager setup and install end to end.
4. Bring the other two skills across, then build out the full CI/CD pipeline.

---

## Prior art: what we found

### agent-manager (`@ai-agent-manager/cli`)

These facts drive the structure decision:

- **Discovery document** at `<base>/.well-known/agents/discovery.json` lists
  `sources`. Each source is `git`, `http` (versioned bundle stream) or
  `artefact` (a zip plus a `.sha256` sidecar).
- **`git` sources only scan `skills/<id>/SKILL.md` at the repo root**
  (`src/bundle/repo-scanner.ts`). They don't read `.claude-plugin/`
  manifests or `plugins/*/skills/`. So thoughtbot's marketplace layout and
  their root-level `SKILL.md` repos would **not** be discovered as git sources.
- **A `git` source in discovery can't pin a ref.** The schema has
  `additionalProperties: false` and no `ref` field, so it tracks the default
  branch. `main` therefore *is* the release: whatever merges ships. Only the
  standalone CLI form (`.../tree/<ref>`) pins.
- **Artefact sources are the versioned path.** A zip URL with a semver in the
  filename, integrity-checked against a sidecar, served over HTTPS (for
  example as a GitHub Release asset).
- **Install identity comes from the source URL** for git and artefact sources:
  `github.com~huwd~skills~dependabot-pr-review/`. If a skill later moves to
  another repo, its identity changes. Choose a stable home up front.
- **Targets:** Claude Code, Cursor, Copilot, Kiro, Windsurf, and a generic
  `~/.agents/skills/`. There is **no Codex-specific target**. OpenCode reads
  `~/.agents/skills/`. Whether Codex does needs verifying (phase 3).
- **Headless mode:** `--config ai-skills.yml` with `tools`, `scope`, and
  `skills`. It's CI-friendly and gives a reproducible machine setup.
- Repo-scoped installs write a `.agentman.json` to commit.
- Its only asset type is the skill: **Claude plugin hooks are not installed.**

### govuk-one-login/agent-skills

A thin aggregator: a discovery document, a vendored copy of the discovery
schema, and one CI job that validates the document with ajv. Skills live in
other repos, each listed as a `git` source. Their README shows the
layout trap in practice: their dependabot skill sits under `.kiro/skills/` and
isn't discoverable. The aggregator pattern is cheap and worth copying,
whichever way the monorepo decision goes.

### thoughtbot/skills

- A Claude Code **plugin marketplace**. `marketplace.json` lists in-repo
  plugins (`plugins/<domain>/`) and external plugin repos.
- **`general` is an empty catch-all plugin**, a bucket for skills with no
  domain. It is not a skill.
- `atomic-commits-plugin` is a 39-line skill plus a Claude-only `PostToolUse`
  hook that nudges at 80 uncommitted and 200 branch lines.
- `dependabot-review-skill-thoughtbot` has `SKILL.md` at the repo root. Our
  `dependabot-pr-review` is clearly descended from it: same modes, output
  format and `dependabot-audit:v1` marker.
- Versioning: in-repo plugins carry no `version` and resolve by commit SHA,
  so every merge ships.
- They also distribute through the **skills CLI** (`npx skills add`,
  vercel-labs/skills), which copies skills into a project.
- I found no CI in their repos.

### Current state here

- `skills/dependabot-pr-review` (366 lines) and `skills/do-release` (233
  lines) lived in the standards repo, symlinked by hand into three harness
  directories. They have moved here with a fresh history; earlier history
  stays in `huwd/standards`.
- `standards/CLAUDE.md` holds commit, branching, TDD and verification rules
  that are loaded on every session, whether they're relevant or not.

---

## Decision: single repo or atomic repos

**Recommendation: one dedicated skills monorepo, `huwd/skills`, with
per-skill CI and per-skill versioned releases.**

Why:

1. **CI is the expensive part, and it's the part you want to get right.** A
   detailed pipeline (lint, format, frontmatter validation, SAST, secret scan,
   behavioural evals) replicated across N repos means N copies of rulesets,
   dependabot config, required-check names, secrets and eval harnesses.
   Reusable workflows (`workflow_call`) cut down the YAML but not the
   per-repo setup. In a monorepo it's one pipeline, run as a matrix over the
   changed `skills/*` paths.
2. **Atomic repos don't buy atomic versioning in agent-manager.** Git sources
   track the default branch either way. Real per-skill versioning comes from
   artefact sources, and a monorepo can build those per skill (tag
   `dependabot-pr-review/v1.2.0` → release asset
   `dependabot-pr-review-1.2.0.zip` + `.sha256`).
3. **The layout agent-manager wants is the monorepo layout**
   (`skills/<id>/SKILL.md` at the root). Adding a root
   `.claude-plugin/marketplace.json` makes the same repo a Claude Code
   marketplace as well, and the skills CLI reads this layout too. One layout
   serves all three installers.
4. **Stable identity.** Install names derive from the repo URL, so a single
   long-lived home avoids later renames.

Why a new repo rather than `standards/skills/`: the standards repo is docs and
templates. Security scanning and evals for executable skill content shouldn't
gate a README fix, and a public skills repo has a different audience. The
authoring conventions moved here too (`docs/skill-format.md`); the standards
repo keeps the *reusable workflow templates* and a pointer to this repo.

**When to split a skill out:** only if it picks up its own runtime
dependencies, a different licence or owner, or a release cadence the
monorepo tooling can't express. A discovery document can list the split repo
as another source, at the cost of an identity change. Aggregation stays
available through discovery without paying the replication cost up front.

Aggregation still happens, but at the **discovery layer**. `huwd/skills`
serves a `discovery.json` listing itself (git, tracking `main`), and later
optionally its own release artefacts and any third-party sources I trust
(pinned artefacts only, never untracked `main` branches of other people's
repos).

---

## Target structure: `huwd/skills`

```text
skills/                              # agent-manager + skills CLI scan root
  dependabot-pr-review/
    SKILL.md                         # < ~250 lines; procedure + gates + output
    README.md                        # human-facing: purpose, provenance, changelog
    references/
      github-api.md                  # curl/jq command set
      github-cli.md                  # gh fallback command set
      output-format.md               # report + comment templates
  atomic-commits/
    SKILL.md
    scripts/check-diff-size.sh       # optional nudge, harness-agnostic
    README.md
  general/
    SKILL.md
evals/<skill>/                       # trigger + behaviour evals, kept out of installs (Q5)
.claude-plugin/
  marketplace.json                   # one plugin at "./" (or one per skill group)
.well-known/agents/
  discovery.json                     # agent-manager entry point
schemas/discovery.schema.json        # vendored, as GOV.UK do
config/ai-skills.yml                 # headless install config for my machines
.github/
  workflows/ci.yml                   # matrix over changed skills
  workflows/release.yml              # per-skill tag → zip + sha256 release asset
  dependabot.yml
docs/
  skill-format.md                    # the format standard, extracted from skill #1
```

---

## Phase 1: dependabot-pr-review to gold-standard format

This skill is the reference implementation. Whatever format we settle on
here becomes `docs/skill-format.md` and the lint rules. It goes first because
it's real, in use, and has a direct comparator. It also exercises every CI
concern: shell snippets, credential handling, and outward-facing write
actions (comment, merge, rebase).

### Keep from ours (better than thoughtbot's)

- API-first access with a `gh` fallback, and no token handling (sandbox-safe).
- Hard gates: required CI, a cooldown for routine updates, and an advisory
  fast path.
- Package-family and workspace-split checks, ecosystem-agnostic changelog
  sourcing order, the risk table, and explicit non-goals.
- Merge commits rather than squash, for audit history.

### Take from thoughtbot

- A richer `description` trigger list ("bump" in the PR title, "which dep PRs
  are safe", pasted PR URLs).
- The "Found N open PRs, analysing…" progress line in audit mode.
- Explicit failure handling and confirmation output after posting.
- A human `README.md` alongside `SKILL.md`, plus `CODEOWNERS`.

### Fix

Done on the `fix/dependabot-review-*` and `feat/dependabot-review-structure`
branches:

- [x] **Remove personal hardcoding.** `@huwd` replaced by the maintainer from
      CODEOWNERS, falling back to the repo owner.
- [x] **Gate every write action on approval**: comment, delete, merge,
      rebase, close, and opening PRs.
- [x] **Progressive disclosure.** Command sets and output formats in
      `references/`; `SKILL.md` is 245 lines.
- [x] `mktemp` instead of predictable `/tmp` paths; `grep` instead of `rg`.
- [x] Declare requirements in `compatibility`.
- [x] Provenance in `metadata`, the skill README, and a skill-level `LICENSE`
      carrying thoughtbot's MIT notice.
- [x] Also fixed from the pre-push review: linear-history merges, CI judged
      against required checks, untrusted PR content, valid cooldown syntax,
      a relaxable cooldown rule, and defined ignore-rule and workspace-split
      holds.
- [ ] Write evals: 5–10 prompts that should trigger the skill and 5 that
      shouldn't, plus a fixture repo with a few Dependabot PRs (patch dev-dep,
      major runtime, failing CI, missing cooldown, advisory, a PR body with
      an injected instruction) and expected verdicts.
- [ ] Update `docs/skill-format.md` with this skill as the worked example.

**Done when:** the skill passes the phase-2 CI, the evals give the expected
verdicts on the fixture, and `docs/skill-format.md` describes the format with
this skill as the example.

---

## Phase 2: repository and minimum CI

- [x] Create the local repo and move the skills across (fresh history; old
      history stays in `huwd/standards`). Standards points here.
- [ ] Review `dependabot-pr-review` and settle attribution before the first
      push.
- [ ] Create `huwd/skills` (public), push, then import the `protect_main` and
      `prevent_tag_deletion` rulesets and dependabot config from `huwd/standards`.
- [ ] **Minimum CI** (required checks from day one):
  - frontmatter/spec validation (agentskills `skills-ref validate`, or a
    small script: name matches the directory, description length, allowed keys)
  - `claude plugin validate` on the marketplace manifest
  - markdownlint + prettier (Markdown/JSON/YAML)
  - shellcheck on `scripts/**` **and** on fenced `bash` blocks extracted from
    `SKILL.md` and `references/`
  - secret scan (betterleaks or gitleaks, as agent-manager uses)
  - discovery document schema validation (the GOV.UK script)
  - actions pinned to SHAs (zizmor or an equivalent workflow linter)

## Phase 3: basic agent-manager setup and trial

- [ ] Add `.well-known/agents/discovery.json` listing `huwd/skills` as a
      `git` source.
- [ ] Serve locally (`npx serve` / GOV.UK `serve.sh`) and run the TUI against
      `http://localhost:3000`.
- [ ] Install system-scope for `claude-code` and the generic `agents` target.
- [ ] **Verify:**
  - How the namespaced link name (`github.com~huwd~skills~…`) shows up in
    Claude Code. Is `/dependabot-pr-review` still the invocable name?
  - Whether Codex reads `~/.agents/skills/`. If not, keep a one-line manual
    symlink for Codex and raise it upstream with the maintainer.
  - The update flow after a new commit merges to `main`.
- [ ] Write `config/ai-skills.yml` and try a headless install from the raw
      GitHub URL. This replaces the manual symlink block in `CLAUDE.md`.
- [ ] Remove the old manual symlinks once parity is confirmed.

## Phase 4: atomic-commits and general

### atomic-commits

Merge our commit standards (Conventional Commits, 50/72, why-bodies, "no
'and' in the subject") with thoughtbot's atomic criteria (passes CI,
deployable, no dead code; one kind of work per commit; ~200-line PRs).

**One conflict to resolve first:** our TDD cycle commits and pushes a *red*
(failing-tests) commit. thoughtbot's rule is "every commit passes CI". Options:

- (a) Squash red into green before pushing.
- (b) Allow red commits on branches but require the PR tip to be green, with
  merge-commit history keeping the narrative.
- (c) Mark red tests pending/xfail so the red commit is still CI-green.

My lean is (c) or (a). It needs a call.

The diff-size nudge hook is Claude-only and agent-manager doesn't install
hooks. Ship it as an optional script in `scripts/`, with wiring documented
per harness, rather than making the skill depend on it.

### general

thoughtbot's `general` is a plugin *bucket*, and in a flat `skills/` layout a
bucket isn't needed. The proposal is a **`general` skill that carries the
portable parts of `standards/CLAUDE.md`**: branching, PR conventions, the
verification loop and security basics. `CLAUDE.md` then slims down to
personal preferences plus pointers. Payoff: the same rules reach Codex and
OpenCode, and they load when relevant rather than on every session.

## Phase 5: full CI/CD

- **SAST:** semgrep on `scripts/`. Policy lint over skill text for risky
  instructions (`curl | sh`, force-push, `rm -rf`, and write actions without an
  approval gate). Evaluate the available agent-skill and prompt-injection
  scanners.
- **DAST/behavioural:** run each skill's evals in a sandbox against fixture
  repos on PRs that touch the skill, using `claude plugin eval` or an
  equivalent harness. Trigger-accuracy evals catch description regressions.
- **Release:** per-skill tag → zip + `.sha256` GitHub Release asset. Add
  those as `artefact` sources for anyone (including my other repos' CI) who
  wants pinned versions rather than `main`.
- Run evals across harnesses (Claude Code and at least one other) to back up
  the cross-harness claim.

---

## Open questions

1. ~~New `huwd/skills` repo or keep skills in `standards`?~~ Decided: new
   repo, public from day one.
2. **What is `general`?** Paused until after dependabot-pr-review. Leading
   option: the base rules wanted in every repo, as a skill.
3. **Red-commit conflict** in atomic-commits: (a), (b) or (c)?
4. **`do-release`**: moved here with the others; bring it up to the new
   format in phase 4.
5. **Evals location:** inside each skill directory (installed to users, but
   noise) or in a parallel `evals/<skill>/` tree (clean install)? Lean:
   parallel tree.
6. ~~Public from day one?~~ Decided: yes. Attribution for thoughtbot-derived
   content is decided at the pre-push review.
