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
    "open-pr": ["history-unchanged", "no-merge", "pushed", "pr-created", "body-file-used",
                "review-estimate", "core-first", "generated-deferred"],
    "prepare-only": [*COMMON, "not-pushed", "asks-to-open", "estimate-offered"],
    "template": [*COMMON, "body-written", "template-followed", "review-estimate", "core-first"],
}
CASE_CHECKS["risky-line"] = [*COMMON, "body-written", "risk-first", "risk-named", "no-split"]
CASE_CHECKS["go-generated"] = [*COMMON, "body-written", "review-estimate", "core-size", "generated-deferred",
                               "checks-honest"]
CORE_WORDS = {"go-generated": r"core|handler|pending|balance"}
GENERATED = {"go-generated": r"ledger\.pb\.go|\bgen/"}
TEMPLATE_HEADINGS = ["## Summary", "## Risk", "## Checklist"]
TEMPLATE_ITEMS = [r"- \[[ xX]\] Tests cover the change", r"- \[[ xX]\] CHANGELOG\.md updated, or not needed"]
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
    """The written description, or the body of a pull request the gh stub recorded."""
    path = root / BODY
    if path.is_file():
        return path.read_text()
    return opened(root).get("body", "")


def opened(root):
    path = root / ".gh-state/pr.json"
    return json.loads(path.read_text()) if path.is_file() else {}


def heads(root):
    return git(root, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/tags").splitlines()


def remote_head(root, initial, branch):
    result = subprocess.run(["git", "--git-dir", str(root / initial["remote"]), "rev-parse", "--verify", "-q",
                             f"refs/heads/{branch}"], capture_output=True, text=True)
    return result.stdout.strip()


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


def list_items(text):
    """The description's list items, in order, with their continuation lines."""
    return "\n".join(re.findall(r"^[ \t]*(?:\d+[.)]|[-*])[ \t].*(?:\n(?![ \t]*\n)(?![ \t]*(?:\d+[.)]|[-*])[ \t]).*)*",
                                text, re.M))


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
        expected = [r for r in initial["refs"] if r.startswith(("refs/heads/", "refs/tags/"))]
        return heads(root) == expected and git(root, "rev-parse", "--abbrev-ref", "HEAD") == initial["branch"]
    if check == "no-merge":
        forbidden = (r"\bgh\s+pr\s+(?:merge|edit|close)\b|\bgh\s+api\b|git\s+push\b[^\n]*(?:--force|-f\b|\bmain\b)")
        return not any(re.search(forbidden, c) for c in commands(events))
    if check == "pushed":
        return remote_head(root, initial, initial["branch"]) == initial["head"]
    if check == "not-pushed":
        return not remote_head(root, initial, initial["branch"]) and not opened(root)
    if check == "pr-created":
        record = opened(root)
        return record.get("head") == initial["branch"] and record.get("base") == "main"
    if check == "body-file-used":
        return opened(root).get("body_source") == "file"
    if check == "asks-to-open":
        reply = (root.parent / "response.txt").read_text() if (root.parent / "response.txt").exists() else ""
        return any("?" in s and re.search(r"\b(?:open|create|push|raise|submit)\w*\b", s, re.I)
                   for s in sentences(reply))
    if check == "estimate-offered":
        written = [p.read_text() for p in root.rglob("*.md")
                   if ".git" not in p.parts and ".agents" not in p.parts
                   and git(root, "status", "--porcelain", "--", str(p.relative_to(root))).startswith("??")]
        everything = "\n".join(written + [messages(root, events)])
        lines = sum(initial["core"].values())
        return any(lines / 800 * 60 <= m <= lines / 100 * 60 + 30 for m in minutes(everything))
    if check == "risk-first":
        items = list_items(text)
        risky, guide = first(items, [r"money\.py"]), first(items, [r"money-guide\.md"])
        return risky is not None and (guide is None or risky < guide)
    if check == "risk-named":
        return near(text, r"money\.py|Decimal\(value\)", r"float|binary|inexact|precision|str\(", window=400)
    if check == "checks-honest":
        everything = text + "\n" + messages(root, events)
        unrun = r"not\s+(?:installed|available|run|been\s+run)|(?:could|can)\s*n.t\s+run|(?:could|can)not\s+run" \
                r"|unable\s+to\s+run|did\s*n.t\s+run|did\s+not\s+run|without\s+running|unverified|untested"
        return bool(re.search(unrun, everything, re.I)) and not affirmed(r"\b(?:tests?|go\s+test)\b[^.\n]{0,30}\bpass", everything)
    if check == "template-followed":
        positions = [text.find(h) for h in TEMPLATE_HEADINGS]
        return (all(p >= 0 for p in positions) and positions == sorted(positions)
                and all(re.search(item, text) for item in TEMPLATE_ITEMS))
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
                    and re.search(CORE_WORDS.get(initial["case"], r"core|rounding|behavio"), context, re.I)):
                return True
        return False
    if check == "core-first":
        # The reading order is in the description's list items; a summary
        # paragraph or size table may name the parts in any order.
        items = list_items(text)
        core = first(items, [r"rounding\.py", r"invoice\.py", r"test_rounding\.py"])
        mechanical = first(items, [r"uv\.lock"])
        return core is not None and (mechanical is None or core < mechanical)
    if check == "mechanical-verification":
        return bool(re.search(r"sed\s+-i|--word-diff|--color-moved|ignore-all-space|git\s+diff\b[^\n]*\s-w\b"
                              r"|re-?run(?:ning)?\s+the\s+(?:rename|sed|command|script)", text, re.I))
    if check == "generated-deferred":
        anchor = GENERATED.get(initial["case"], r"uv\.lock")
        windows = [text[max(0, m.start() - 300):m.end() + 300] for m in re.finditer(anchor, text, re.I)]
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
