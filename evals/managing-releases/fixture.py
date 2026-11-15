"""Build synthetic repositories for release-workflow evaluations."""

import json
from pathlib import Path
import subprocess
import sys


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def write(root, name, text, executable=False):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if executable:
        path.chmod(0o755)


def commit(root, message, tag=None):
    git(root, "add", "-A")
    git(root, "-c", "commit.gpgsign=false", "commit", "-qm", message)
    if tag:
        git(root, "-c", "tag.gpgsign=false", "tag", "-a", tag, "-m", f"Release {tag}")


AGENTS = """# Repository instructions

Never commit directly to main. Work on a branch named
<type>/<short-description>, using Conventional Commits.
Run scripts/check before committing; it is required.
"""

CHECK = """#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-t', '.'])
with Path('.git/check-events').open('a') as log:
    log.write('pass\\n' if result.returncode == 0 else 'failure\\n')
raise SystemExit(result.returncode)
"""

TAG_WORKFLOW = """name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: write
  id-token: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: "Preflight: tag must match the project version"
        run: |
          version="$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
          test "v${version}" = "${GITHUB_REF_NAME}"
      - name: "Preflight: CHANGELOG must mention this version"
        run: grep -Eq "^## \\\\[${GITHUB_REF_NAME#v}\\\\]" CHANGELOG.md
      - run: python -m unittest discover -s tests -t .
      - run: python -m pip install build && python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
      - run: gh release create "$GITHUB_REF_NAME" --notes-from-tag
        env:
          GH_TOKEN: ${{ github.token }}
"""

CI_WORKFLOW = """name: Release

# Runs after CI passes on main. When VERSION has changed, creates the tag
# vX.Y.Z and a GitHub Release from the matching CHANGELOG section, then
# attaches the bundle. Nobody pushes release tags by hand.
on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Release when VERSION changed
        run: |
          version="$(cat VERSION)"
          if git ls-remote --exit-code --tags origin "v${version}"; then exit 0; fi
          ./scripts/build-bundle "$version"
          gh release create "v${version}" bundle.zip --target "$GITHUB_SHA" \\
            --notes "$(./scripts/changelog-section "$version")"
        env:
          GH_TOKEN: ${{ github.token }}
"""


def skill(name, version, description):
    return (f"---\nname: {name}\ndescription: {description}\nmetadata:\n"
            f"  version: \"{version}\"\n---\n\n# {name}\n\nFollow the repository's own process.\n")


def package(root, case):
    write(root, "pyproject.toml", '[project]\nname = "widget"\nversion = "1.2.0"\n'
          'requires-python = ">=3.11"\n\n[build-system]\nrequires = ["setuptools>=70"]\n'
          'build-backend = "setuptools.build_meta"\n')
    write(root, "src/widget/__init__.py", 'def slug(text):\n    return text.lower().replace(" ", "-")\n')
    write(root, "tests/__init__.py", "")
    write(root, "tests/test_slug.py", "import sys\nimport unittest\nsys.path.insert(0, 'src')\n"
          "from widget import slug\n\n\nclass SlugTests(unittest.TestCase):\n"
          "    def test_spaces_become_hyphens(self):\n"
          "        self.assertEqual(slug('Hello World'), 'hello-world')\n")
    write(root, "README.md", "# widget\n\nSmall text helpers.\n")
    write(root, ".github/workflows/release.yml", TAG_WORKFLOW)
    write(root, "CHANGELOG.md", "# Changelog\n\n## [Unreleased]\n\n"
          "## [1.2.0] - 2026-10-01\n\n### Added\n\n- `slug` helper for URL fragments.\n\n"
          "## [1.1.0] - 2026-08-14\n\n### Added\n\n- Package skeleton.\n")
    commit(root, "feat: add slug helper", tag="v1.2.0")

    with (root / "src/widget/__init__.py").open("a") as source:
        source.write('\n\ndef title(text):\n    return " ".join(word.capitalize() for word in text.split())\n')
    changelog = (root / "CHANGELOG.md").read_text()
    write(root, "CHANGELOG.md", changelog.replace(
        "## [Unreleased]\n\n", "## [Unreleased]\n\n### Added\n\n- `title` helper for headings.\n\n"))
    commit(root, "feat: add title helper")

    if case == "release-tag":
        write(root, "src/widget/__init__.py", (root / "src/widget/__init__.py").read_text().replace(
            "return text.lower()", "return text.strip().lower()"))
        with (root / "tests/test_slug.py").open("a") as test:
            test.write("\n    def test_surrounding_whitespace_is_removed(self):\n"
                       "        self.assertEqual(slug('  Hello  '), 'hello')\n")
        changelog = (root / "CHANGELOG.md").read_text()
        write(root, "CHANGELOG.md", changelog.replace(
            "- `title` helper for headings.\n\n",
            "- `title` helper for headings.\n\n### Fixed\n\n- `slug` removes surrounding whitespace.\n\n"))
        commit(root, "fix: strip whitespace in slug")
    if case == "ship-change":
        write(root, "notes/bug.md", "# Reported bug\n\n`slug('  Hello  ')` returns `--hello--`.\n"
              "Surrounding whitespace should be removed before converting.\n")
        commit(root, "docs: record slug whitespace report")


def catalogue(root):
    write(root, "VERSION", "0.2.0\n")
    write(root, "skills/check-build/SKILL.md", skill("check-build", "0.1.0", "Check a remote build."))
    write(root, "tests/__init__.py", "")
    write(root, "tests/test_catalogue.py", "from pathlib import Path\nimport re\nimport unittest\n\n\n"
          "class CatalogueTests(unittest.TestCase):\n"
          "    def test_skills_have_versions(self):\n"
          "        for path in Path('skills').glob('*/SKILL.md'):\n"
          "            self.assertRegex(path.read_text(), r'version: \"\\d+\\.\\d+\\.\\d+\"')\n\n"
          "    def test_bundle_version(self):\n"
          "        self.assertRegex(Path('VERSION').read_text(), r'^\\d+\\.\\d+\\.\\d+\\n$')\n")
    write(root, "README.md", "# Fixture skills\n\nA small catalogue of agent skills.\n\n## Releasing\n\n"
          "Record each skill change under `## [Unreleased]` in CHANGELOG.md and\n"
          "increase that skill's `metadata.version`. The root VERSION is the bundle\n"
          "version: patch for fixes, minor for new skills or compatible functionality,\n"
          "major for breaking changes. Skill versions are independent of it.\n")
    write(root, ".github/workflows/release.yml", CI_WORKFLOW)
    write(root, "CHANGELOG.md", "# Changelog\n\n## [Unreleased]\n\n## [0.2.0]\n\n"
          "- check-build 0.1.0: report remote build status.\n\n## [0.1.0]\n\n"
          "- Publish the first bundle.\n")
    commit(root, "chore: prepare v0.2.0 release", tag="v0.2.0")

    write(root, "skills/lint-docs/SKILL.md", skill("lint-docs", "0.1.0", "Lint Markdown with the repository's tools."))
    changelog = (root / "CHANGELOG.md").read_text()
    write(root, "CHANGELOG.md", changelog.replace(
        "## [Unreleased]\n\n", "## [Unreleased]\n\n- Add lint-docs 0.1.0: lint Markdown with the repository's tools.\n\n"))
    commit(root, "feat: add lint-docs skill")

    write(root, "skills/check-build/SKILL.md", skill("check-build", "0.1.1",
                                                      "Check a remote build. Do not retry access denials."))
    changelog = (root / "CHANGELOG.md").read_text()
    write(root, "CHANGELOG.md", changelog.replace(
        "tools.\n\n## [0.2.0]", "tools.\n- check-build 0.1.1: stop retrying access denials.\n\n## [0.2.0]"))
    commit(root, "fix(check-build): stop retrying access denials")


def create(root, case):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Fixture Maintainer")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "commit.gpgsign", "false")
    git(root, "config", "tag.gpgsign", "false")
    write(root, ".gitignore", ".agents/\n__pycache__/\n*.pyc\n")
    write(root, "AGENTS.md", AGENTS)
    write(root, "scripts/check", CHECK, True)
    if case in ("ship-change", "release-tag", "explain-only"):
        package(root, case)
    elif case == "release-ci":
        catalogue(root)
    else:
        raise ValueError(case)
    snapshot = {"case": case, "head": git(root, "rev-parse", "HEAD"),
                "tags": git(root, "tag", "--list").splitlines(),
                "changelog": (root / "CHANGELOG.md").read_text()}
    (root.parent / "fixture-initial.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    return snapshot


if __name__ == "__main__":
    create(Path.cwd(), sys.argv[1])
