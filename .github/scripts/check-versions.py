#!/usr/bin/env python3
"""Validate stable skill/bundle versions against a git revision.

Usage: check-versions.py [--base REV] [--notes]
Requires PyYAML 6.0.3. --notes prints the current changelog entry.
Missing versions in the base revision are allowed for initial adoption.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", re.ASCII)


def version(value):
    if not isinstance(value, str) or not SEMVER.fullmatch(value):
        raise ValueError(f"Invalid stable SemVer: {value!r}")
    return tuple(map(int, value.split(".")))


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def old_file(base, path):
    if not base or not git("ls-tree", base, "--", path).strip():
        return None
    return git("show", f"{base}:{path}")


def skill_version(text):
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not frontmatter:
        raise ValueError("Skill must have YAML frontmatter")
    data = yaml.safe_load(frontmatter[1])
    if not isinstance(data, dict) or not isinstance(data.get("metadata", {}), dict):
        raise ValueError("Skill frontmatter and metadata must be mappings")
    return data.get("metadata", {}).get("version")


def notes(text, current):
    sections = list(re.finditer(r"^## \[([^\]\n]+)\].*$", text, re.MULTILINE))
    matches = [i for i, section in enumerate(sections) if section[1] == current]
    if len(matches) != 1:
        raise ValueError(f"CHANGELOG.md needs exactly one ## [{current}] heading")
    i = matches[0]
    end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
    entry = text[sections[i].end():end].strip()
    if not entry:
        raise ValueError(f"Changelog entry for {current} is empty")
    return entry + "\n"


def check(base=None):
    current = Path("VERSION").read_text().strip()
    number = version(current)
    previous = old_file(base, "VERSION")
    if previous and number < version(previous.strip()):
        raise ValueError("Bundle version decreased")
    entry = notes(Path("CHANGELOG.md").read_text(), current)
    changed = set(git("diff", "--name-only", base, "--", "skills").splitlines()) if base else set()
    skills = list(Path("skills").glob("*/SKILL.md"))
    if not skills:
        raise ValueError("No skills found")
    for path in skills:
        value = skill_version(path.read_text())
        number = version(value)
        old = old_file(base, path.as_posix())
        before = skill_version(old) if old else None
        if before is None:
            continue
        previous_number = version(before)
        if number < previous_number:
            raise ValueError(f"{path}: version decreased")
        if any(p.startswith(path.parent.as_posix() + "/") for p in changed) and number <= previous_number:
            raise ValueError(f"{path}: changed skill needs a higher version")
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base")
    parser.add_argument("--notes", action="store_true")
    args = parser.parse_args()
    try:
        entry = check(args.base)
    except (ValueError, OSError, subprocess.CalledProcessError, yaml.YAMLError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(entry if args.notes else "Skill and bundle versions are valid", end="" if args.notes else "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
