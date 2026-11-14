"""A mixed-file change whose review units differ from file boundaries."""

import ast
import json
from pathlib import Path
import sys

from fixture import create as create_base, files, git, index, write


def source(refactor=False, feature=False, fix=False):
    prefix = "normalize" if refactor else "clean"
    parts = []
    for field in ("title", "owner", "code", "group", "tag"):
        if field == "title" and feature:
            parts.append(f"def {prefix}_{field}(value, preserve_case=False):\n"
                         "    value = value.strip()\n"
                         "    return value if preserve_case else value.lower()\n")
        else:
            parts.append(f"def {prefix}_{field}(value):\n    return value.strip().lower()\n")
    signature = "def render(record, preserve_case=False):" if feature else "def render(record):"
    parts.append(signature + "\n    return {\n" + "".join(
        f"        '{field}': {prefix}_{field}(record['{field}']"
        + (", preserve_case=preserve_case" if feature and field == "title" else "") + "),\n"
        for field in ("title", "owner", "code", "group", "tag")) + "    }\n")
    parts.append("def should_retry(status):\n    return " + ("status != 403" if fix else "True") + "\n")
    return "\n\n".join(parts)


def tests(refactor=False, feature=False, fix=False):
    prefix = "normalize" if refactor else "clean"
    text = (f"import unittest\nfrom src.report import {prefix}_title, {prefix}_owner, render, should_retry\n\n"
            "class ReportTests(unittest.TestCase):\n"
            "    def test_title(self):\n"
            f"        self.assertEqual({prefix}_title(' Example '), 'example')\n\n"
            "    def test_owner(self):\n"
            f"        self.assertEqual({prefix}_owner(' ALEX '), 'alex')\n\n"
            "    def test_render(self):\n"
            "        row = {name: ' Example ' for name in ('title', 'owner', 'code', 'group', 'tag')}\n"
            "        self.assertTrue(all(value == 'example' for value in render(row).values()))\n\n"
            "    def test_transient_retry(self):\n"
            "        self.assertTrue(should_retry(503))\n")
    if feature:
        text += ("\n    def test_preserve_case(self):\n"
                 "        row = {name: ' Example ' for name in ('title', 'owner', 'code', 'group', 'tag')}\n"
                 "        self.assertEqual(render(row, preserve_case=True)['title'], 'Example')\n")
    if fix:
        text += ("\n    def test_access_denied(self):\n"
                 "        self.assertFalse(should_retry(403))\n")
    return text


def create(root):
    root = Path(root)
    create_base(root, "history-only")
    write(root, "src/report.py", source())
    write(root, "tests/test_report.py", tests())
    write(root, "notes/report-change.md", "# Report maintenance context\n\n"
          "The helper names are being aligned with the terminology in the data\n"
          "normalisation guide; this rename is not meant to alter output.\n\n"
          "Display callers need an opt-in preserve_case argument for report\n"
          "titles; existing calls should keep their lower-case output. The\n"
          "prepared implementation uses the renamed helper.\n\n"
          "The report client also retries access-denied responses. Repeating\n"
          "a 403 cannot repair access; 503 should remain retryable.\n")
    write(root, "scripts/check", "#!/usr/bin/env python3\n"
          "import hashlib\nimport json\nfrom pathlib import Path\nimport subprocess\nimport sys\n"
          "paths = ['src/report.py', 'tests/test_report.py']\n"
          "snapshot = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}\n"
          "result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'])\n"
          "with Path('.git/check-events').open('a') as log:\n"
          "    log.write('pass\\n' if result.returncode == 0 else 'failure\\n')\n"
          "with Path('.git/check-snapshots').open('a') as log:\n"
          "    log.write(json.dumps({'files': snapshot, 'code': result.returncode}) + '\\n')\n"
          "raise SystemExit(result.returncode)\n", True)
    git(root, "add", "src/report.py", "tests/test_report.py", "notes/report-change.md", "scripts/check")
    git(root, "-c", "commit.gpgsign=false", "commit", "-qm", "feat: add report rendering")
    write(root, "src/report.py", source(True, True, True))
    write(root, "tests/test_report.py", tests(True, True, True))
    git(root, "add", "src/report.py", "tests/test_report.py")
    for name in ("hook-events", "check-events", "check-snapshots"):
        (root / ".git" / name).unlink(missing_ok=True)
    variants = {}
    for refactor, feature, fix in ((r, f, b) for r in (False, True) for f in (False, True) for b in (False, True) if r or not f):
        key = f"{int(refactor)}{int(feature)}{int(fix)}"
        variants[key] = {"src/report.py": ast.dump(ast.parse(source(refactor, feature, fix)), include_attributes=False),
                         "tests/test_report.py": ast.dump(ast.parse(tests(refactor, feature, fix)), include_attributes=False)}
    initial = {"case": "reviewable-series", "head": git(root, "rev-parse", "HEAD"),
               "index": index(root), "files": files(root), "targets": ["src/report.py", "tests/test_report.py"],
               "hooks": {name: (root / ".git/hooks" / name).read_text() for name in ("pre-commit", "commit-msg")},
               "variants": variants}
    (root.parent / "fixture-initial.json").write_text(json.dumps(initial, indent=2) + "\n")
    return initial


if __name__ == "__main__":
    create(Path.cwd())
