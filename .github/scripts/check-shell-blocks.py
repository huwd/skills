#!/usr/bin/env python3
"""Run shellcheck on fenced bash and sh blocks in Markdown files.

Usage: check-shell-blocks.py FILE.md...

Each block is checked as its own script. Findings are reported against the
Markdown file and line, so they can be fixed in place.

Skills write placeholders as <NAME> or <OWNER/REPO>. Those are replaced with
a plain word before checking, so shellcheck doesn't read them as
redirections. Real redirections (`< file`, `<<EOF`, `<(cmd)`) don't match.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*(\w+)?")
SHELLS = {"bash", "sh", "shell"}
PLACEHOLDER = re.compile(r"<[A-Za-z][\w./-]*>")


def blocks(path):
    """Yield (first_line, indent, source) for each shell block in path."""
    lines = Path(path).read_text().splitlines()
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        indent, fence, lang = m.group(1), m.group(2), m.group(3)
        start = i + 1
        i += 1
        body = []
        while i < len(lines) and not lines[i].strip().startswith(fence):
            body.append(lines[i][len(indent):] if lines[i].startswith(indent) else lines[i])
            i += 1
        i += 1
        if lang in SHELLS:
            source = "\n".join(body) + "\n"
            yield start + 1, len(indent), PLACEHOLDER.sub("PLACEHOLDER", source)


def main(paths):
    failed = False
    with tempfile.TemporaryDirectory() as tmp:
        for path in paths:
            for n, (first, indent, source) in enumerate(blocks(path)):
                script = Path(tmp) / f"block{n}.sh"
                # The header line shifts shellcheck's line numbers by one.
                script.write_text("# shellcheck shell=bash\n" + source)
                result = subprocess.run(
                    ["shellcheck", "--format=gcc", str(script)],
                    capture_output=True,
                    text=True,
                )
                for line in result.stdout.splitlines():
                    _, lineno, col, message = line.split(":", 3)
                    print(f"{path}:{first + int(lineno) - 2}:{int(col) + indent}:{message}")
                failed |= result.returncode != 0
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
