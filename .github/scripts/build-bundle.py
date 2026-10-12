#!/usr/bin/env python3
"""Build an agent-manager bundle of every skill in skills/.

Usage: build-bundle.py VERSION OUT_DIR

Writes, for the HTTP bundle source format agent-manager reads:

    OUT_DIR/VERSION/bundle.zip         each skill directory at the top level,
                                       plus manifest.json
    OUT_DIR/VERSION/bundle.zip.sha256  "<sha256>  bundle.zip"

Only files tracked by git are included, so local clutter never ships. The
zip is reproducible: entries are sorted and every timestamp, including the
manifest's "published" date, is the commit time of HEAD. Building the same
commit twice gives the same checksum.
"""

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


def git(*args):
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    version, out_dir = argv
    if not SEMVER.match(version):
        print(f"Not a semantic version: {version}", file=sys.stderr)
        return 2

    root = Path(git("rev-parse", "--show-toplevel").strip())
    files = sorted(
        f for f in git("-C", str(root), "ls-files", "-z", "skills").split("\0") if f
    )
    if not files:
        print("No skills found under skills/; discovery is broken", file=sys.stderr)
        return 1

    committed = int(git("-C", str(root), "log", "-1", "--format=%ct").strip())
    stamp = datetime.fromtimestamp(committed, tz=timezone.utc)
    # Zip timestamps can't predate 1980 and have two-second resolution.
    date_time = stamp.timetuple()[:6]

    manifest = {
        "version": version,
        "published": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    target = Path(out_dir) / version
    target.mkdir(parents=True, exist_ok=True)
    bundle = target / "bundle.zip"

    def entry(name, data, mode=0o644):
        info = zipfile.ZipInfo(name, date_time)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = (0o100000 | mode) << 16
        return info, data

    entries = [entry("manifest.json", json.dumps(manifest, indent=2) + "\n")]
    for f in files:
        path = root / f
        mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
        # skills/<name>/... becomes <name>/... at the top of the bundle.
        entries.append(entry(f.removeprefix("skills/"), path.read_bytes(), mode))

    with zipfile.ZipFile(bundle, "w") as z:
        for info, data in entries:
            z.writestr(info, data)

    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    (target / "bundle.zip.sha256").write_text(f"{digest}  bundle.zip\n")

    skills = sorted({f.split("/")[1] for f in files})
    print(f"Built {bundle} ({len(files)} files, skills: {', '.join(skills)})")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
