#!/usr/bin/env python3
"""Publish the checked-out bundle version; safely resume interrupted releases.

Called only after CI succeeds on main. Requires gh and GH_TOKEN.
A VERSION increase (including initial adoption) is the release trigger.
"""

import hashlib
import json
import os
import subprocess
from pathlib import Path

from importlib.util import module_from_spec, spec_from_file_location

spec = spec_from_file_location("versions", Path(__file__).with_name("check-versions.py"))
versions = module_from_spec(spec)
spec.loader.exec_module(versions)


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def publish():
    base = os.environ.get("BASE_SHA") or versions.git("rev-parse", "HEAD^").strip()
    notes = versions.check(base)
    current = Path("VERSION").read_text().strip()
    previous = versions.old_file(base, "VERSION")
    if previous and previous.strip() == current:
        print("Bundle version unchanged; nothing to release")
        return
    sha = versions.git("rev-parse", "HEAD").strip()
    if subprocess.run(["git", "merge-base", "--is-ancestor", sha, "origin/main"]).returncode:
        raise ValueError("Release commit is not on main")
    tag = f"v{current}"
    # Reject a conflicting tag even when no release exists yet.
    refs = versions.git("ls-remote", "origin", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}")
    if refs:
        target = refs.splitlines()[-1].split()[0]
        if target != sha:
            raise ValueError(f"{tag} already identifies a different commit")
    subprocess.run(["python3", ".github/scripts/build-bundle.py", current, "dist"], check=True)
    existing = json.loads(gh("release", "list", "--limit", "1000", "--json", "tagName,isDraft"))
    release = next((r for r in existing if r["tagName"] == tag), None)
    notes_path = Path("dist/release-notes.md")
    notes_path.write_text(notes)
    if release is None:
        gh("release", "create", tag, "--target", sha, "--draft", "--title", tag,
           "--notes-file", str(notes_path))
    assets = json.loads(gh("release", "view", tag, "--json", "assets"))["assets"]
    names = {a["name"] for a in assets}
    for name in ("bundle.zip", "bundle.zip.sha256"):
        path = Path("dist") / current / name
        if name in names:
            downloaded = Path("dist/existing")
            downloaded.mkdir(exist_ok=True)
            gh("release", "download", tag, "--dir", str(downloaded), "--pattern", name)
            if hashlib.sha256((downloaded / name).read_bytes()).digest() != hashlib.sha256(path.read_bytes()).digest():
                raise ValueError(f"Existing {tag}/{name} differs; refusing to overwrite")
        elif release and not release["isDraft"]:
            raise ValueError(f"Published {tag} is missing {name}; refusing to modify it")
        else:
            gh("release", "upload", tag, str(path))
    if release is None or release["isDraft"]:
        gh("release", "edit", tag, "--draft=false")
    print(f"Published {tag}")


if __name__ == "__main__":
    publish()
