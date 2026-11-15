"""Read-only checks for the technical-writing editorial cases.

These checks cover facts, session wording, work orders and the size of a
change. They cannot judge whether a document helps its reader; the
editorial rubric covers that with a person's assessment.
"""

import difflib
import json
from pathlib import Path
import re
import sys


TARGET = {"editorial-brief": "authoring-skills-brief.md",
          "editorial-report": "authoring-skills-evaluation.md",
          "coherent-addition": "authoring-skills-brief.md",
          "small-correction": "authoring-skills-evaluation.md"}

OPENING = r"\A# [^\n]+\n\n(?!Implement\b)(?:[^\n]+\n)*?[^\n]*\b(?:maintainers?|reviewers?|contributors?)\b"
# Narration of the authoring session. "The user's requested scope", meaning
# whoever uses the skill, is ordinary content and is not matched.
SESSION = r"(?i)\b(?:the\s+user's\s+decision|as\s+requested|the\s+user\s+(?:asked|decided|wants|requested|chose))\b"

NO_UPLIFT = (r"(?i)no\s+(?:measured\s+|demonstrated\s+)?(?:uplift|improvement|advantage|benefit)"
             r"|not\s+establish\w*\s+(?:a\s+)?(?:general\s+)?(?:benefit|improvement|uplift)")
# Facts a reader needs for the task's purpose. Incidental figures, such as
# run costs and durations, are judged with the rubric instead.
FACTS = {
    "editorial-brief": [r"\breviewing-skills\b", r"(?i)read-only|without\s+edit", r"0\.7\.1", r"\b0001\b",
                        r"\bMIT\b", r"(?i)instruction[- ]files?|AGENTS\.md", NO_UPLIFT, r"agentskills\.io",
                        r"developers\.openai\.com/blog/eval-skills", r"szelemeh", r"adr-review",
                        r"(?i)agent-manager"],
    "editorial-report": [r"2\.1\.318", r"claude-opus-5-5", r"508689f", r"\b36\b", r"(?i)heredoc|command guard",
                         r"(?i)wording|phrasing|phrase", r"issues/25", NO_UPLIFT],
}
ORDERS = {
    "editorial-brief": r"\b(?:Implement \[issue|Retain these principles|Do not import custom|Review all linked"
                       r" references|Keep that responsibility there|Record those distinctions|Apply that to"
                       r" this pair|Use its idea as a comparison|Use precise triggers)\b",
    "editorial-report": r"\b(?:Keep that limitation visible|Anchor that guard|Accept that wording)\b",
}
CHECKS = {
    "editorial-brief": ["opening-orients", "no-session-wording", "no-work-orders", "facts-kept", "others-unchanged"],
    "editorial-report": ["opening-orients", "no-session-wording", "no-work-orders", "facts-kept", "others-unchanged"],
    "coherent-addition": ["addition-made", "addition-proportionate"],
    "small-correction": ["correction-made", "correction-proportionate"],
}


def headings(text):
    return [line for line in text.splitlines() if line.startswith("#")]


def paragraphs(text):
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", text) if p.strip()]


def assess(root, check):
    root = Path(root)
    case = json.loads((root.parent / "editorial-case.json").read_text())["case"]
    originals = root.parent / "editorial-originals"
    target = TARGET[case]
    path = root / "docs" / target
    text = path.read_text() if path.is_file() else ""
    before = (originals / target).read_text()

    if check == "opening-orients":
        return re.search(OPENING, text) is not None
    if check == "no-session-wording":
        return bool(text) and re.search(SESSION, text) is None
    if check == "no-work-orders":
        return bool(text) and re.search(ORDERS[case], text) is None
    if check == "facts-kept":
        return all(re.search(pattern, text) for pattern in FACTS[case])
    if check == "others-unchanged":
        return all((root / "docs" / p.name).is_file() and (root / "docs" / p.name).read_text() == p.read_text()
                   for p in originals.iterdir() if p.name != target)
    if check == "addition-made":
        return re.search(r"0\.1\.0[\s\S]{0,120}0\.2\.0|0\.2\.0[\s\S]{0,120}0\.1\.0", text) is not None
    if check == "addition-proportionate":
        # Same headings, every original paragraph kept apart from at most one
        # extended in place, and a short addition.
        old, new = paragraphs(before), paragraphs(text)
        kept = sum(p in new for p in old)
        added = len(" ".join(new)) - len(" ".join(old))
        return headings(text) == headings(before) and kept >= len(old) - 1 and 0 < added <= 400
    if check == "correction-made":
        flat = " ".join(text.split())
        return ("three times" in flat or "three runs" in flat) and "ran twice with the plugin" not in flat
    if check == "correction-proportionate":
        # Every word-level difference lies within the corrected sentence.
        old, new = before.split(), text.split()
        anchor = next(i for i, word in enumerate(old) if word == "twice")
        spans = [(i1, i2) for tag, i1, i2, _, _ in
                 difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes() if tag != "equal"]
        return bool(spans) and all(anchor - 12 <= i1 and i2 <= anchor + 14 for i1, i2 in spans)
    raise ValueError(f"Unknown check: {check}")


if __name__ == "__main__":
    root = Path(sys.argv[1])
    check = sys.argv[2]
    json.load(sys.stdin)
    if check == "case":
        case = json.loads((root.parent / "editorial-case.json").read_text())["case"]
        checks = {name: bool(assess(root, name)) for name in CHECKS[case]}
        print(json.dumps({"passed": all(checks.values()), "checks": checks}))
    else:
        print(json.dumps({"passed": bool(assess(root, check)), "detail": check}))
