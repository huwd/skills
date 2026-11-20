"""Checks for the pull-request evals: the written description, git state and commands.

Usage: assess.py WORKSPACE CHECK < events.json
CHECK is a named check, or `case` for every check the case lists.
"""

import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

COMMON = ["no-outward", "history-unchanged"]
CASE_CHECKS = {
    "large-mixed": [*COMMON, "body-written", "review-estimate", "core-size", "core-first",
                    "mechanical-verification", "generated-deferred", "no-split"],
    "oversized": [*COMMON, "body-written", "review-estimate", "split-proposed"],
    "small-fix": [*COMMON, "body-written", "concise", "no-split"],
    "explain-branch": [*COMMON, "tree-clean", "explained"],
}
BODY = "PR_BODY.md"
DURATION = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(hours?|hrs?|h)\b(?:\s*(\d+)\s*(?:m|mins?|minutes?)\b)?"
                      r"|(?<![\w.])(\d+(?:\.\d+)?)\s*(?:mins?|minutes?)\b", re.I)
NEGATION = re.compile(r"\b(?:no|not|never|without|unnecessary)\b|n[’']t\b", re.I)
SPLIT = re.compile(r"\bsplit(?:s|ting)?\b|\bseparate\s+(?:pull\s+requests|PRs)\b|\b(?:two|three|several|multiple)\s+"
                   r"(?:smaller\s+)?(?:pull\s+requests|PRs)\b|\bstack(?:ed)?\s+(?:of\s+)?(?:pull\s+requests|PRs)\b",
                   re.I)
FEATURES = [r"csv|export", r"\bfx\b|currenc|conver", r"audit"]


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def command_text(item):
    command = item.get("command", "")
    try:
        args = shlex.split(command)
        for flag in ("-lc", "-c"):
            if flag in args:
                return args[args.index(flag) + 1]
    except (ValueError, IndexError):
        pass
    return command


def commands(events):
    return [command_text(e["item"]) for e in events
            if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "command_execution"]


def messages(root, events):
    text = [e["item"].get("text", "") for e in events
            if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "agent_message"]
    path = root.parent / "response.txt"
    if path.exists():
        text.append(path.read_text())
    return "\n".join(text)


def body(root):
    path = root / BODY
    return path.read_text() if path.is_file() else ""


def first(text, patterns):
    positions = [m.start() for p in patterns for m in re.finditer(p, text, re.I)]
    return min(positions) if positions else None


def minutes(text):
    """Durations near the word "review", in minutes."""
    # A table whose header row mentions review counts throughout.
    tables = [(m.start(), m.end()) for m in re.finditer(r"(?:^[ \t]*\|.*\n?)+", text, re.M)
              if re.search(r"review", m.group().splitlines()[0], re.I)]
    found = []
    for match in DURATION.finditer(text):
        context = text[max(0, match.start() - 200):match.end() + 200]
        in_table = any(start <= match.start() < end for start, end in tables)
        if not (in_table or re.search(r"review", context, re.I)):
            continue
        if match.group(1):
            found.append(float(match.group(1)) * 60 + float(match.group(3) or 0))
        else:
            found.append(float(match.group(4)))
    return found


def sentences(text):
    return re.split(r"(?<=[.!?])\s+|\n\s*\n|\n(?=\s*(?:[-*|]|\d+[.)])\s)", text)


def affirmed(pattern, text):
    """Whether a sentence matches the pattern without a negation before it."""
    for sentence in sentences(text):
        for match in re.finditer(pattern, sentence, re.I):
            if not NEGATION.search(sentence[:match.start()]):
                return True
    return False


def near(text, anchor, pattern, window=300):
    for match in re.finditer(anchor, text, re.I):
        context = text[max(0, match.start() - window):match.end() + window]
        if re.search(pattern, context, re.I):
            return True
    return False


def assess(root, check, events):
    root = Path(root)
    initial = json.loads((root.parent / "fixture-initial.json").read_text())
    text = body(root)
    if check == "no-outward":
        forbidden = (r"(?:^|[;|&\n])\s*git\s+(?:-[cC]\s+\S+\s+)*push\b|\bgh\s+pr\s+(?:create|edit|merge)\b"
                     r"|\bgh\s+api\b[^\n]*(?:-X\s*(?:POST|PATCH|PUT)|--method\s+(?:POST|PATCH|PUT))")
        return not any(re.search(forbidden, c) for c in commands(events))
    if check == "history-unchanged":
        refs = git(root, "for-each-ref", "--format=%(refname) %(objectname)").splitlines()
        return refs == initial["refs"] and git(root, "rev-parse", "--abbrev-ref", "HEAD") == initial["branch"]
    if check == "tree-clean":
        return git(root, "status", "--porcelain") == initial["status"]
    if check == "body-written":
        return len(text.split()) >= 20
    if check == "review-estimate":
        # Plausible: within half the fast rate and twice the slow rate
        # (400 and 200 lines an hour), plus half an hour for sampling.
        lines = sum((initial.get("core") or initial["total"]).values())
        low, high = lines / 400 * 60 / 2, lines / 200 * 60 * 2 + 30
        found = minutes(text)
        return any(low <= m <= high for m in found) and not any(m > high for m in found)
    if check == "core-size":
        core = initial["core"]
        targets = {core["added"], core["added"] + core["deleted"]}
        for match in re.finditer(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?![\w.])|(?<![\w.])\d+(?![\w.])", text):
            n = int(match.group().replace(",", ""))
            after = text[match.end():match.end() + 15]
            context = text[max(0, match.start() - 150):match.end() + 150]
            if (any(0.65 * target <= n <= 1.35 * target for target in targets)
                    and not re.match(r"\s*(?:files?|packages?|tests?|modules?|min|hours?|%)", after, re.I)
                    and re.search(r"core|rounding|behavio", context, re.I)):
                return True
        return False
    if check == "core-first":
        # The reading order is in the description's list items; a summary
        # paragraph or size table may name the parts in any order.
        items = "\n".join(re.findall(r"^[ \t]*(?:\d+[.)]|[-*])[ \t].*(?:\n(?![ \t]*\n)(?![ \t]*(?:\d+[.)]|[-*])[ \t]).*)*",
                                     text, re.M))
        core = first(items, [r"rounding\.py", r"invoice\.py", r"test_rounding\.py"])
        mechanical = first(items, [r"uv\.lock"])
        return core is not None and (mechanical is None or core < mechanical)
    if check == "mechanical-verification":
        return bool(re.search(r"sed\s+-i|--word-diff|--color-moved|ignore-all-space|git\s+diff\b[^\n]*\s-w\b"
                              r"|re-?run(?:ning)?\s+the\s+(?:rename|sed|command|script)", text, re.I))
    if check == "generated-deferred":
        windows = [text[max(0, m.start() - 300):m.end() + 300] for m in re.finditer(r"uv\.lock", text, re.I)]
        deferred = r"generat|uv\s+lock|skip|skim|no\s+need|need\s+not|don.t\s+need|not\s+(?:be\s+)?(?:reviewed|read)" \
                   r"|(?:no|not|without)\s+(?:reading\s+|reviewing\s+)?line[- ]by[- ]line|without\s+(?:reading|reviewing)"
        demanded = r"\b(?:review|read|check)\w*\b[^.\n]{0,40}\b(?:carefully|line[- ]by[- ]line|every\s+line|each\s+line)"
        return (any(re.search(deferred, w, re.I) for w in windows)
                and not any(affirmed(demanded, w) for w in windows))
    if check == "split-proposed":
        everything = text + "\n" + messages(root, events)
        return affirmed(SPLIT.pattern, everything) and sum(bool(re.search(p, everything, re.I)) for p in FEATURES) >= 2
    if check == "concise":
        return 0 < len(text.split()) <= 250
    if check == "no-split":
        return not affirmed(SPLIT.pattern, text)
    if check == "explained":
        return bool(re.search(r"round", messages(root, events), re.I))
    raise ValueError(f"unknown check: {check}")


if __name__ == "__main__":
    root = Path(sys.argv[1])
    check = sys.argv[2]
    events = json.load(sys.stdin)
    if check == "case":
        case = json.loads((root.parent / "fixture-initial.json").read_text())["case"]
        checks = {name: bool(assess(root, name, events)) for name in CASE_CHECKS[case]}
        print(json.dumps({"passed": all(checks.values()), "checks": checks}))
    else:
        print(json.dumps({"passed": bool(assess(root, check, events)), "detail": check}))
