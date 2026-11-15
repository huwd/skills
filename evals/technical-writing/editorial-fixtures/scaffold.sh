#!/usr/bin/env bash
# Shared scaffold for the editorial cases: a small skills catalogue holding
# the documents named by the case, with the originals saved outside the
# model's working directory for the assessor.
set -euo pipefail
case_name="$1"
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p docs ../editorial-originals

cat > README.md <<'MD'
# skills

Reusable agent skills for Claude Code, Codex and OpenCode. Each skill
lives in `skills/<name>/SKILL.md`; design notes and evaluation reports
live in `docs/`.
MD

case "$case_name" in
  editorial-brief|editorial-report)
    cp "$here/original-brief.md" docs/authoring-skills-brief.md
    cp "$here/original-report.md" docs/authoring-skills-evaluation.md
    ;;
  coherent-addition)
    cp "$here/coherent-brief.md" docs/authoring-skills-brief.md
    ;;
  small-correction)
    cp "$here/report-with-error.md" docs/authoring-skills-evaluation.md
    ;;
  *) echo "unknown case: $case_name" >&2; exit 1 ;;
esac

cp docs/*.md ../editorial-originals/
printf '{"case": "%s"}\n' "$case_name" > ../editorial-case.json
