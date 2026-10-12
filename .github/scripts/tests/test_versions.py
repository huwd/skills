"""Version checks use real git history; publication tests fake GitHub only."""

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent.parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


versions = load("check-versions")
publisher = load("publish-release")


class VersionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.cwd = Path.cwd()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.cwd)
        self.git("init", "-q")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        Path("skills/alpha/references").mkdir(parents=True)
        self.skill("0.1.0")
        Path("VERSION").write_text("0.1.0\n")
        Path("CHANGELOG.md").write_text("# Changelog\n\n## [0.1.0]\n\n- Initial release.\n")
        self.commit()
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "change")

    def skill(self, value):
        Path("skills/alpha/SKILL.md").write_text(
            f'---\nname: alpha\ndescription: Test\nmetadata:\n  version: "{value}"\n---\n\n# Alpha\n')

    def test_stable_semver(self):
        for value in ("01.2.3", "1.02.3", "1.2", "1.2.3-rc.1", "1.2.3+build", "v1.2.3", "1.2.3\n", 1.2):
            with self.subTest(value=value), self.assertRaises(ValueError):
                versions.version(value)
        self.assertGreater(versions.version("0.10.0"), versions.version("0.9.0"))

    def test_unchanged_skills_and_repository_docs_need_no_bump(self):
        Path("README.md").write_text("Docs")
        versions.check(self.base)

    def test_changed_reference_requires_skill_bump(self):
        Path("skills/alpha/references/guide.md").write_text("New reference")
        self.git("add", "-A")
        with self.assertRaisesRegex(ValueError, "higher version"):
            versions.check(self.base)
        self.skill("0.1.1")
        versions.check(self.base)  # Bundle bump is deliberately a soft rule.

    def test_skill_and_bundle_decreases_fail(self):
        self.skill("0.0.9")
        with self.assertRaisesRegex(ValueError, "decreased"):
            versions.check(self.base)
        self.skill("0.1.0")
        Path("VERSION").write_text("0.0.9\n")
        with self.assertRaisesRegex(ValueError, "decreased"):
            versions.check(self.base)

    def test_bundle_bump_requires_nonempty_unique_changelog_entry(self):
        Path("VERSION").write_text("0.1.1\n")
        with self.assertRaisesRegex(ValueError, "heading"):
            versions.check(self.base)
        Path("CHANGELOG.md").write_text("## [0.1.1]\n")
        with self.assertRaisesRegex(ValueError, "empty"):
            versions.check(self.base)
        Path("CHANGELOG.md").write_text("## [0.1.1]\n\n- Fix.\n\n## [0.1.1]\n\n- Duplicate.\n")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            versions.check(self.base)

    def test_notes_exclude_other_versions(self):
        text = "# Changelog\n\n## [0.2.0] - 2026-10-12\n\n- New.\n\n## [0.1.0]\n\n- Old.\n"
        self.assertEqual(versions.notes(text, "0.2.0"), "- New.\n")

    def test_initial_adoption_and_new_skills(self):
        self.git("rm", "VERSION", "CHANGELOG.md")
        Path("skills/alpha/SKILL.md").write_text("---\nname: alpha\ndescription: Test\n---\n")
        self.commit()
        base = self.git("rev-parse", "HEAD").strip()
        self.skill("0.1.0")
        Path("VERSION").write_text("0.1.0\n")
        Path("CHANGELOG.md").write_text("## [0.1.0]\n\n- Adopt versions.\n")
        versions.check(base)
        Path("skills/beta").mkdir()
        Path("skills/beta/SKILL.md").write_text('---\nname: beta\nmetadata:\n  version: "0.1.0"\n---\n')
        versions.check(base)

    def test_missing_skill_version_fails(self):
        Path("skills/alpha/SKILL.md").write_text("---\nname: alpha\n---\n")
        with self.assertRaisesRegex(ValueError, "SemVer"):
            versions.check(self.base)

    def prepare_release(self):
        Path("VERSION").write_text("0.1.1\n")
        Path("CHANGELOG.md").write_text("## [0.1.1]\n\n- Fix.\n")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")

    def test_unchanged_bundle_does_not_publish(self):
        Path("README.md").write_text("Docs")
        self.commit()
        with patch.object(publisher, "gh") as gh:
            publisher.publish()
        gh.assert_not_called()

    def test_conflicting_tag_fails_before_publication(self):
        self.prepare_release()
        with patch.object(publisher.versions, "git", wraps=versions.git) as git:
            git.side_effect = lambda *args: "deadbeef\trefs/tags/v0.1.1\n" if args[0] == "ls-remote" else versions.git(*args)
            with patch.object(publisher, "gh") as gh, self.assertRaisesRegex(ValueError, "different commit"):
                publisher.publish()
            gh.assert_not_called()

    def test_release_uses_draft_and_changelog_then_publishes(self):
        self.prepare_release()
        Path(".github/scripts").mkdir(parents=True)
        (Path(".github/scripts") / "build-bundle.py").write_bytes((SCRIPTS / "build-bundle.py").read_bytes())
        calls = []

        def fake_gh(*args):
            calls.append(args)
            if args[:2] == ("release", "list"):
                return "[]"
            if args[:2] == ("release", "view"):
                return json.dumps({"assets": []})
            return ""

        with patch.object(publisher.versions, "git", wraps=versions.git) as git:
            git.side_effect = lambda *args: "" if args[0] == "ls-remote" else versions.git(*args)
            with patch.object(publisher, "gh", side_effect=fake_gh):
                publisher.publish()
        self.assertIn("--draft", calls[1])
        self.assertEqual(Path("dist/release-notes.md").read_text(), "- Fix.\n")
        self.assertEqual(calls[-1], ("release", "edit", "v0.1.1", "--draft=false"))

    def test_retry_verifies_assets_and_resumes_draft_without_overwriting(self):
        for mismatch in (False, True):
            with self.subTest(mismatch=mismatch):
                # Each subcase reuses the same committed release version.
                if not Path(".github/scripts/build-bundle.py").exists():
                    self.prepare_release()
                    Path(".github/scripts").mkdir(parents=True)
                    Path(".github/scripts/build-bundle.py").write_bytes((SCRIPTS / "build-bundle.py").read_bytes())
                calls = []
                existing = Path("dist/existing/bundle.zip")
                if existing.exists():
                    existing.unlink()

                def fake_gh(*args):
                    calls.append(args)
                    if args[:2] == ("release", "list"):
                        return json.dumps([{"tagName": "v0.1.1", "isDraft": True}])
                    if args[:2] == ("release", "view"):
                        return json.dumps({"assets": [{"name": "bundle.zip"}]})
                    if args[:2] == ("release", "download"):
                        existing.write_bytes(b"different" if mismatch else Path("dist/0.1.1/bundle.zip").read_bytes())
                    return ""

                with patch.object(publisher.versions, "git", wraps=versions.git) as git:
                    git.side_effect = lambda *args: "" if args[0] == "ls-remote" else versions.git(*args)
                    with patch.object(publisher, "gh", side_effect=fake_gh):
                        if mismatch:
                            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                                publisher.publish()
                        else:
                            publisher.publish()
                uploads = [c for c in calls if c[:2] == ("release", "upload")]
                self.assertEqual(uploads, [] if mismatch else [("release", "upload", "v0.1.1", "dist/0.1.1/bundle.zip.sha256")])
                self.assertFalse(any(c[:2] == ("release", "create") for c in calls))


if __name__ == "__main__":
    unittest.main()
