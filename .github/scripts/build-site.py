#!/usr/bin/env python3
"""Write the index for the static site agent-manager installs skills from.

Usage: build-site.py SITE_DIR

SITE_DIR must already hold one directory per version, each with the
bundle.zip and bundle.zip.sha256 that build-bundle.py writes. This adds
SITE_DIR/index.json, listing every version oldest first: agent-manager
treats the last entry as the latest, so versions are sorted by semantic
version, with a prerelease before its release.

SITE_DIR is served as is, and is the URL to install from. There's
deliberately no discovery document: without one, agent-manager installs a
bundle's skills under their own names (technical-writing), where a
discovery source would prefix them (huwd-skills~technical-writing). See
docs/decisions/0004-install-from-versioned-bundles.md.
"""

import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$")


def sort_key(version):
    major, minor, patch, pre = SEMVER.match(version).groups()
    # A release sorts after its prereleases: (1, 2, 3, 1, "") > (1, 2, 3, 0, "rc.1").
    return (int(major), int(minor), int(patch), 0 if pre else 1, pre or "")


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    bundles = Path(argv[0])

    versions = []
    for d in sorted(bundles.iterdir()) if bundles.is_dir() else []:
        if not d.is_dir():
            continue
        if not SEMVER.match(d.name):
            print(f"Not a version directory: {d}", file=sys.stderr)
            return 1
        missing = [f for f in ("bundle.zip", "bundle.zip.sha256") if not (d / f).is_file()]
        if missing:
            print(f"{d} is missing {', '.join(missing)}", file=sys.stderr)
            return 1
        with zipfile.ZipFile(d / "bundle.zip") as z:
            manifest = json.loads(z.read("manifest.json"))
        if manifest.get("version") != d.name:
            print(f"{d}/bundle.zip says version {manifest.get('version')!r}", file=sys.stderr)
            return 1
        versions.append({"version": d.name, "published": manifest["published"]})

    if not versions:
        print(f"No bundles found under {bundles}", file=sys.stderr)
        return 1
    versions.sort(key=lambda v: sort_key(v["version"]))

    index = {
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agents": versions,
    }
    (bundles / "index.json").write_text(json.dumps(index, indent=2) + "\n")

    latest = versions[-1]["version"]
    print(f"Index in {bundles}: {len(versions)} version(s), latest {latest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
