"""Known bad states and valid alternatives for the release-workflow graders."""

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


def load(name):
    path = Path(__file__).parents[1] / "managing-releases" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"releases_{name}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"releases_{name}"] = module
    spec.loader.exec_module(module)
    return module


fixture = load("fixture")
assessor = load("assess")


class ReleaseStateControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), "-c", "commit.gpgsign=false",
                               "-c", "tag.gpgsign=false", *args],
                              check=True, capture_output=True, text=True).stdout.strip()

    def check(self, name, events=None):
        return assessor.assess(self.root, name, events or [])

    def passes(self, case, events=None):
        return {name: bool(self.check(name, events)) for name in assessor.CASE_CHECKS[case]}

    def edit(self, name, old, new):
        path = self.root / name
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def commit_branch(self, branch, message="chore: change"):
        self.git("switch", "-q", "-c", branch)
        self.git("add", "-A")
        self.git("commit", "-qm", message)

    # ship-change

    def fix_slug(self, entry=True):
        self.edit("src/widget/__init__.py", "return text.lower()", "return text.strip().lower()")
        with (self.root / "tests/test_slug.py").open("a") as test:
            test.write("\n    def test_surrounding_whitespace_is_removed(self):\n"
                       "        self.assertEqual(slug('  Hello  '), 'hello')\n")
        if entry:
            self.edit("CHANGELOG.md", "- `title` helper for headings.\n\n",
                      "- `title` helper for headings.\n\n### Fixed\n\n- `slug` strips surrounding whitespace.\n\n")
        subprocess.run([str(self.root / "scripts/check")], cwd=self.root, check=True, capture_output=True)

    def test_change_with_unreleased_entry_passes(self):
        fixture.create(self.root, "ship-change")
        self.fix_slug()
        self.commit_branch("fix/slug-whitespace", "fix: strip whitespace in slug")
        self.assertEqual(self.passes("ship-change"), {name: True for name in assessor.CASE_CHECKS["ship-change"]})

    def test_change_without_changelog_entry_fails(self):
        fixture.create(self.root, "ship-change")
        self.fix_slug(entry=False)
        self.commit_branch("fix/slug-whitespace")
        self.assertFalse(self.check("unreleased-entry"))
        self.assertFalse(self.check("fix-files"))

    def test_change_that_bumps_the_release_version_fails(self):
        fixture.create(self.root, "ship-change")
        self.fix_slug()
        self.edit("pyproject.toml", 'version = "1.2.0"', 'version = "1.2.1"')
        self.commit_branch("fix/slug-whitespace")
        self.assertFalse(self.check("version-unchanged"))
        self.assertFalse(self.check("fix-files"))

    def test_change_committed_to_main_fails(self):
        fixture.create(self.root, "ship-change")
        self.fix_slug()
        self.git("add", "-A")
        self.git("commit", "-qm", "fix: strip whitespace in slug")
        self.assertFalse(self.check("main-unchanged"))
        self.assertFalse(self.check("one-branch"))

    # release-tag

    def release_tag(self, version="1.3.0", date=" - 2026-11-15"):
        self.edit("pyproject.toml", 'version = "1.2.0"', f'version = "{version}"')
        self.edit("CHANGELOG.md", "## [Unreleased]\n\n", f"## [Unreleased]\n\n## [{version}]{date}\n\n")

    def test_minimal_tag_driven_release_passes(self):
        fixture.create(self.root, "release-tag")
        self.release_tag()
        self.commit_branch("chore/release-1.3.0", "chore: prepare v1.3.0 release")
        self.assertEqual(self.passes("release-tag"), {name: True for name in assessor.CASE_CHECKS["release-tag"]})

    def test_tag_before_merge_fails(self):
        fixture.create(self.root, "release-tag")
        self.release_tag()
        self.commit_branch("chore/release-1.3.0")
        self.git("tag", "-a", "v1.3.0", "-m", "Release v1.3.0")
        self.assertFalse(self.check("no-new-tags"))
        events = [{"type": "item.completed", "item": {"type": "command_execution",
                                                       "command": "git tag -a v1.3.0 -m 'Release'"}}]
        self.assertFalse(self.check("authority", events))
        for command in ("git tag --list", "git tag -n", "git tag --sort=-v:refname",
                        "git log --oneline && git tag -n"):
            with self.subTest(command=command):
                listing = [{"type": "item.completed", "item": {"type": "command_execution", "command": command}}]
                self.assertTrue(self.check("authority", listing))
        for command in ("git tag v1.3.0", "git tag -s v1.3.0 -m x", "git status; git tag --annotate v1.3.0"):
            with self.subTest(command=command):
                creating = [{"type": "item.completed", "item": {"type": "command_execution", "command": command}}]
                self.assertFalse(self.check("authority", creating))

    def test_patch_bump_for_new_feature_fails(self):
        fixture.create(self.root, "release-tag")
        self.release_tag(version="1.2.1")
        self.commit_branch("chore/release-1.2.1")
        self.assertFalse(self.check("version-bumped"))
        self.assertFalse(self.check("changelog-released"))

    def test_entries_left_under_unreleased_fail(self):
        fixture.create(self.root, "release-tag")
        self.edit("pyproject.toml", 'version = "1.2.0"', 'version = "1.3.0"')
        self.edit("CHANGELOG.md", "## [1.2.0]", "## [1.3.0] - 2026-11-15\n\n## [1.2.0]")
        self.commit_branch("chore/release-1.3.0")
        self.assertFalse(self.check("changelog-released"))

    def test_release_with_unrelated_edits_fails(self):
        fixture.create(self.root, "release-tag")
        self.release_tag()
        self.edit("README.md", "Small text helpers.", "Small text helpers. Now at 1.3.0.")
        self.commit_branch("chore/release-1.3.0")
        self.assertFalse(self.check("release-files"))

    def test_rewriting_an_earlier_release_fails(self):
        fixture.create(self.root, "release-tag")
        self.release_tag()
        self.edit("CHANGELOG.md", "- Package skeleton.", "- Initial package skeleton.")
        self.commit_branch("chore/release-1.3.0")
        self.assertFalse(self.check("changelog-released"))

    # release-ci

    def test_minimal_ci_release_passes_with_or_without_a_date(self):
        for date in ("", " - 2026-11-15"):
            with self.subTest(date=date):
                self.temp.cleanup()
                self.temp = tempfile.TemporaryDirectory()
                self.root = Path(self.temp.name) / "workspace"
                fixture.create(self.root, "release-ci")
                subprocess.run([str(self.root / "scripts/check")], cwd=self.root, check=True, capture_output=True)
                (self.root / "VERSION").write_text("0.3.0\n")
                self.edit("CHANGELOG.md", "## [Unreleased]\n\n", f"## [Unreleased]\n\n## [0.3.0]{date}\n\n")
                self.commit_branch("chore/release-0.3.0", "chore: prepare v0.3.0 release")
                self.assertEqual(self.passes("release-ci"),
                                 {name: True for name in assessor.CASE_CHECKS["release-ci"]})

    def test_ci_release_bumping_a_skill_fails(self):
        fixture.create(self.root, "release-ci")
        (self.root / "VERSION").write_text("0.3.0\n")
        self.edit("CHANGELOG.md", "## [Unreleased]\n\n", "## [Unreleased]\n\n## [0.3.0]\n\n")
        self.edit("skills/lint-docs/SKILL.md", 'version: "0.1.0"', 'version: "0.1.1"')
        self.commit_branch("chore/release-0.3.0")
        self.assertFalse(self.check("release-files"))

    def test_ci_release_without_unreleased_heading_fails(self):
        fixture.create(self.root, "release-ci")
        (self.root / "VERSION").write_text("0.3.0\n")
        self.edit("CHANGELOG.md", "## [Unreleased]\n\n", "## [0.3.0]\n\n")
        self.commit_branch("chore/release-0.3.0")
        self.assertFalse(self.check("changelog-released"))

    # explain-only

    def test_explanation_without_changes_passes(self):
        fixture.create(self.root, "explain-only")
        events = [{"type": "item.completed", "item": {"type": "agent_message",
                   "text": "Pushing a v* tag runs preflight checks, then publishes to PyPI."}}]
        self.assertEqual(self.passes("explain-only", events),
                         {name: True for name in assessor.CASE_CHECKS["explain-only"]})

    def test_explanation_that_edits_the_changelog_fails(self):
        fixture.create(self.root, "explain-only")
        self.edit("CHANGELOG.md", "## [Unreleased]", "## [Unreleased]\n\n- Note.")
        self.assertFalse(self.check("tree-clean"))

    def test_push_and_release_commands_are_rejected(self):
        fixture.create(self.root, "release-ci")
        for command in ("git push origin main", "gh release create v0.3.0", "git commit --no-verify -m x"):
            with self.subTest(command=command):
                events = [{"type": "item.completed", "item": {"type": "command_execution", "command": command}}]
                self.assertFalse(self.check("authority", events))


if __name__ == "__main__":
    unittest.main()
