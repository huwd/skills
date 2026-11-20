"""Known bad descriptions and valid alternatives for the pull-request graders."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


def load(name):
    path = Path(__file__).parents[1] / "pull-requests" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"pull_requests_{name}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"pull_requests_{name}"] = module
    spec.loader.exec_module(module)
    return module


fixture = load("fixture")
assessor = load("assess")

GUIDED = """# Round invoice totals with banker's rounding

Invoice totals now round to whole pence, sending halves to the even digit.

## Size and review time

| Part | Files | Lines | Review |
|---|---|---|---|
| Core | 4 | +57 -1 | about 15 minutes |
| Rename and reformat | 26 | +249 -297 | about 10 minutes, sampled |
| uv.lock | 1 | +800 -800 | not reviewed by hand |

## How to review

1. Start with `src/ledger/rounding.py` and `src/ledger/invoice.py`: totals
   change for amounts ending in half a penny.
2. Check one module from the rename, then confirm the rest with
   `git diff main --word-diff` or by re-running the sed command in the
   commit message.
3. `uv.lock` was regenerated with `uv lock --upgrade`; CI installs from it.
"""

COMMIT_ORDER = """# Currency rounding

This branch:

- renames Amount to Money across the package
- refreshes uv.lock
- raises the line length to 100 and reformats
- adds banker's rounding in rounding.py and uses it for invoice totals

Tests pass with scripts/check.
"""

SPLIT_BODY = """# Ledger extensions

This adds CSV export, currency conversion and an audit log: about 1,500
new lines, roughly 5 hours of review. I recommend splitting it into three
separate pull requests, one per feature, so each can be reviewed in a
single session.
"""


class DescriptionControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"

    def build(self, case, text=None):
        fixture.create(self.root, case)
        if text is not None:
            (self.root / assessor.BODY).write_text(text)

    def passes(self, case, events=None):
        return {name: bool(assessor.assess(self.root, name, events or [])) for name in assessor.CASE_CHECKS[case]}

    def test_guided_description_passes_large_mixed(self):
        self.build("large-mixed", GUIDED)
        self.assertEqual(self.passes("large-mixed"), {n: True for n in assessor.CASE_CHECKS["large-mixed"]})

    def test_commit_order_summary_fails_large_mixed(self):
        self.build("large-mixed", COMMIT_ORDER)
        result = self.passes("large-mixed")
        for name in ["review-estimate", "core-size", "core-first", "mechanical-verification", "generated-deferred"]:
            self.assertFalse(result[name], name)
        self.assertTrue(result["no-outward"])

    def test_summary_naming_lockfile_first_still_passes_core_first(self):
        self.build("large-mixed", "# Rounding\n\nAlso refreshes `uv.lock` and renames Amount.\n\n"
                   "## How to review\n\n1. Start with `src/ledger/rounding.py`.\n"
                   "2. Skip `uv.lock`: regenerated with `uv lock --upgrade`.\n")
        self.assertTrue(assessor.assess(self.root, "core-first", []))

    def check_text(self, case, check, text):
        self.root = Path(tempfile.mkdtemp(dir=self.temp.name)) / "workspace"
        self.build(case, text + "\n\n" + "Context sentence for the reader. " * 10)
        return bool(assessor.assess(self.root, check, []))

    def test_implausible_estimate_fails_large_mixed(self):
        # 58 core lines at 200 to 400 lines an hour is minutes, not hours.
        self.assertFalse(self.check_text("large-mixed", "review-estimate",
                                         "Allow about 4 hours to review `src/ledger/rounding.py`."))

    def test_estimate_in_hours_and_minutes_passes_oversized(self):
        self.assertTrue(self.check_text("oversized", "review-estimate",
                                        "| Total | 6 | +1,787 | 5h 57m (4h 28m–8h 56m) to review |"))

    def test_total_in_review_table_passes_oversized(self):
        table = ("| Part | Files | Lines | Review time |\n| --- | --- | --- | --- |\n"
                 + "".join(f"| Feature {n} | 2 | +596 | 2.0 hours (1.5–3.0) |\n" for n in range(1, 4))
                 + "| Total | 6 | +1,787 | 6.0 hours (4.5–8.9) |\n")
        self.assertTrue(self.check_text("oversized", "review-estimate", table))

    def test_estimate_in_minutes_fails_oversized(self):
        self.assertFalse(self.check_text("oversized", "review-estimate", "About 20 minutes to review."))

    def test_coincidental_number_fails_core_size(self):
        self.assertFalse(self.check_text("large-mixed", "core-size",
                                         "Bumps 400 packages; 58 files reformatted. Review `rounding.py`."))

    def test_reviewing_the_lockfile_fails_generated_deferred(self):
        self.assertFalse(self.check_text("large-mixed", "generated-deferred",
                                         "Please review uv.lock carefully, line by line; CI does not check it."))
        self.assertFalse(self.check_text("large-mixed", "generated-deferred",
                                         "uv.lock was regenerated; please review it carefully, line by line."))

    def test_declined_split_fails_split_proposed(self):
        self.assertFalse(self.check_text("oversized", "split-proposed",
                                         "Adds CSV export, FX and audit. There is no need to split this into separate PRs."))

    def test_declining_a_split_passes_no_split(self):
        self.assertTrue(self.check_text("small-fix", "no-split",
                                        "Fixes `tax_largest` in `tax.py`. No need to split this."))

    def test_missing_description_fails(self):
        self.build("large-mixed")
        self.assertFalse(assessor.assess(self.root, "body-written", []))

    def test_opening_the_pull_request_fails(self):
        self.build("large-mixed", GUIDED)
        events = [{"type": "item.completed", "item": {"type": "command_execution",
                                                      "command": "gh pr create --body-file PR_BODY.md"}}]
        self.assertFalse(assessor.assess(self.root, "no-outward", events))

    def test_split_recommendation_passes_oversized(self):
        self.build("oversized", SPLIT_BODY)
        self.assertEqual(self.passes("oversized"), {n: True for n in assessor.CASE_CHECKS["oversized"]})

    def test_split_in_reply_counts_for_oversized(self):
        self.build("oversized", "# Ledger extensions\n\n" + "Adds three features to the ledger package. " * 5
                   + "\n\nReview time: about 5 hours.\n")
        events = [{"type": "item.completed", "item": {"type": "agent_message",
                                                      "text": "Consider separate PRs for the CSV export and audit log."}}]
        self.assertTrue(assessor.assess(self.root, "split-proposed", events))
        events[0]["item"]["text"] = "Recommend splitting before opening: CSV export, FX and audit."
        self.assertTrue(assessor.assess(self.root, "split-proposed", events))

    def test_description_without_split_fails_oversized(self):
        self.build("oversized", COMMIT_ORDER)
        self.assertFalse(assessor.assess(self.root, "split-proposed", []))

    def test_short_description_passes_small_fix(self):
        self.build("small-fix", "# Skip zero lines in tax_largest\n\n`tax_largest` returned a zero line "
                   "when every line was zero or tied. It now skips zero lines; a test covers it.\n\n"
                   "About 5 minutes to review: one condition in `src/ledger/tax.py` and its test.\n")
        self.assertEqual(self.passes("small-fix"), {n: True for n in assessor.CASE_CHECKS["small-fix"]})

    def test_split_advice_on_small_fix_fails(self):
        self.build("small-fix", SPLIT_BODY)
        self.assertFalse(assessor.assess(self.root, "no-split", []))

    def test_explaining_without_changes_passes(self):
        self.build("explain-branch")
        events = [{"type": "item.completed", "item": {"type": "agent_message",
                                                      "text": "It adds banker's rounding to invoice totals."}}]
        self.assertEqual(self.passes("explain-branch", events),
                         {n: True for n in assessor.CASE_CHECKS["explain-branch"]})

    def test_writing_a_file_fails_explain_branch(self):
        self.build("explain-branch", GUIDED)
        self.assertFalse(assessor.assess(self.root, "tree-clean", []))


if __name__ == "__main__":
    unittest.main()
