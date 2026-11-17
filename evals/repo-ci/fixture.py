"""Scaffold synthetic repositories for the repo-ci evals.

Run by each case's scaffold.sh with the workspace as the working directory.
Writes `fixture-initial.json` beside the workspace for the assessor.
"""

import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import upstream  # noqa: E402

PROJECT = {
    "pyproject.toml": """\
[project]
name = "tidyname"
version = "0.4.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.8"]

[tool.ruff]
line-length = 100
""",
    "uv.lock": "version = 1\nrequires-python = \">=3.12\"\n",
    "README.md": "# tidyname\n\nNormalise display names. Run `uv run pytest` for the tests.\n",
    "src/tidyname/__init__.py": '''\
def tidy(name: str) -> str:
    """Collapse whitespace and title-case a display name."""
    return " ".join(part.capitalize() for part in name.split())
''',
    "tests/test_tidy.py": '''\
from tidyname import tidy


def test_collapses_whitespace():
    assert tidy("  ada   lovelace ") == "Ada Lovelace"
''',
    "scripts/release-notes.sh": """\
#!/usr/bin/env bash
set -euo pipefail
git log --oneline "$(git describe --tags --abbrev=0)..HEAD"
""",
}

CHECKOUT, UV, PY = "actions/checkout", "astral-sh/setup-uv", "actions/setup-python"
SHARED = "acme-org/shared-workflows"

# Copied from "another project": checkout's SHA is v6.0.0's, labelled v7.0.1.
COPIED = f"""\
# Copied from our other project's .github/workflows/ci.yml
name: CI
on: [push, pull_request]
permissions: write-all
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: {CHECKOUT}@{upstream.sha(CHECKOUT, "v6.0.0")} # v7.0.1
      - uses: {UV}@{upstream.sha(UV, "v10.3.0")} # v10.3.0
      - run: uv sync
      - run: uv run ruff check
      - run: uv run pytest
      - run: shellcheck $(find . -name '*.sh')
"""

# Existing CI: checkout is right but one release behind (inside the cooldown);
# setup-python's SHA is v6.0.0's, labelled v6.1.0; the reusable workflow is right.
EXISTING = f"""\
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: {CHECKOUT}@{upstream.sha(CHECKOUT, "v7.0.1")} # v7.0.1
        with:
          persist-credentials: false
      - uses: {PY}@{upstream.sha(PY, "v6.0.0")} # v6.1.0
        with:
          python-version: "3.12"
      - run: pip install pytest && pytest

  zizmor:
    name: Audit workflows
    uses: {SHARED}/.github/workflows/zizmor.yml@{upstream.sha(SHARED, "v2.1.0")} # v2.1.0
    permissions:
      contents: read
"""

# The repository already runs zizmor, so new workflows must pass it.
PRE_COMMIT = """\
repos:
  - repo: https://github.com/zizmorcore/zizmor-pre-commit
    rev: v1.31.1
    hooks:
      - id: zizmor
"""

DEPENDABOT = """\
version: 2
updates:
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
"""

CASES = {
    "new-ci": {"docs/other-repo-ci.yml": COPIED, ".pre-commit-config.yaml": PRE_COMMIT},
    "check-pins": {".github/workflows/ci.yml": EXISTING, ".github/dependabot.yml": DEPENDABOT},
    "explain-only": {".github/workflows/ci.yml": EXISTING, ".github/dependabot.yml": DEPENDABOT},
}


def git(*args):
    subprocess.run(["git", *args], check=True, capture_output=True)


def main(case):
    root = Path.cwd()
    for name, text in {**PROJECT, **CASES[case]}.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    (root / "scripts/release-notes.sh").chmod(0o755)
    git("init", "-q", "-b", "main")
    git("add", "-A")
    git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-q", "-m", "chore: initial project")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    (root.parent / "fixture-initial.json").write_text(json.dumps({"case": case, "head": head}) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
