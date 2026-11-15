"""Known bad states and valid alternatives for the editorial graders."""

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


SUITE = Path(__file__).parents[1] / "technical-writing"
spec = importlib.util.spec_from_file_location("editorial_assess", SUITE / "editorial_assess.py")
assessor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assessor)


class EditorialControls(unittest.TestCase):
    def scaffold(self, case):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.root.mkdir()
        subprocess.run([str(SUITE / case / "scaffold.sh")], cwd=self.root, check=True, capture_output=True)
        self.target = self.root / "docs" / assessor.TARGET[case]
        return self.target.read_text()

    def passes(self, case):
        return {name: bool(assessor.assess(self.root, name)) for name in assessor.CHECKS[case]}

    def test_original_brief_fails_its_editorial_checks(self):
        self.scaffold("editorial-brief")
        result = self.passes("editorial-brief")
        self.assertFalse(result["opening-orients"])
        self.assertFalse(result["no-session-wording"])
        self.assertFalse(result["no-work-orders"])
        self.assertTrue(result["facts-kept"])
        self.assertTrue(result["others-unchanged"])

    def test_original_report_fails_its_editorial_checks(self):
        self.scaffold("editorial-report")
        result = self.passes("editorial-report")
        self.assertFalse(result["opening-orients"])
        self.assertFalse(result["no-work-orders"])
        self.assertTrue(result["facts-kept"])

    def oriented_brief(self, text):
        text = re.sub(r"\A# [^\n]+\n\n(?:[^\n]+\n)+",
                      "# Skill authoring and review design\n\nThis brief is for maintainers deciding whether to "
                      "accept the\nauthoring-skills and reviewing-skills design.\n", text)
        for old, new in [("as requested", "for distinct responsibilities"),
                         ("Retain these principles", "These principles are retained"),
                         ("Do not import custom", "Custom"),
                         ("Review all linked references", "All linked references were reviewed"),
                         ("Keep that responsibility there", "That responsibility stays there"),
                         ("Record those distinctions", "Those distinctions are recorded"),
                         ("Apply that to this pair", "This applies to the pair"),
                         ("Use its idea as a comparison", "Its idea serves as a comparison"),
                         ("Use precise triggers", "Precise triggers")]:
            text = text.replace(old, new)
        return text

    def test_oriented_brief_keeping_facts_passes(self):
        text = self.scaffold("editorial-brief")
        self.target.write_text(self.oriented_brief(text))
        self.assertEqual(self.passes("editorial-brief"),
                         {name: True for name in assessor.CHECKS["editorial-brief"]})

    def test_skill_user_wording_is_not_session_wording(self):
        text = self.scaffold("editorial-brief")
        self.assertIn("the user's requested scope", text)
        self.target.write_text(self.oriented_brief(text))
        self.assertTrue(assessor.assess(self.root, "no-session-wording"))
        self.target.write_text(self.oriented_brief(text) + "\nThe user asked for two skills.\n")
        self.assertFalse(assessor.assess(self.root, "no-session-wording"))
        self.target.write_text(self.oriented_brief(text) + "\nThe\nuser's decision was two skills.\n")
        self.assertFalse(assessor.assess(self.root, "no-session-wording"))

    def test_rewrite_that_drops_a_source_fails(self):
        text = self.scaffold("editorial-brief")
        self.target.write_text(self.oriented_brief(text).replace("szelemeh", "someone"))
        self.assertFalse(assessor.assess(self.root, "facts-kept"))

    def test_editing_the_other_document_fails(self):
        self.scaffold("editorial-brief")
        other = self.root / "docs/authoring-skills-evaluation.md"
        other.write_text(other.read_text() + "\nExtra.\n")
        self.assertFalse(assessor.assess(self.root, "others-unchanged"))

    def test_short_addition_in_place_passes(self):
        text = self.scaffold("coherent-addition")
        first = "Each skill's SKILL.md contains its instructions."
        self.assertIn(first, text)
        self.target.write_text(text.replace(first, first + " Both were released at 0.1.0 in\nbundle 0.2.0."))
        self.assertEqual(self.passes("coherent-addition"),
                         {name: True for name in assessor.CHECKS["coherent-addition"]})

    def test_addition_with_new_heading_or_rewrite_fails(self):
        text = self.scaffold("coherent-addition")
        self.target.write_text(text + "\n## Release\n\nBoth skills were released at 0.1.0 in bundle 0.2.0.\n")
        self.assertTrue(assessor.assess(self.root, "addition-made"))
        self.assertFalse(assessor.assess(self.root, "addition-proportionate"))
        rewritten = re.sub(r"(## Assessment and writing\n\n)(?:[^\n]+\n)+", r"\1Rewritten paragraph.\n", text)
        rewritten = re.sub(r"(## Workflow selection\n\n)(?:[^\n]+\n)+", r"\1Also rewritten.\n", rewritten)
        self.target.write_text(rewritten.replace("Each skill's SKILL.md contains its instructions.",
                                                 "Both were released at 0.1.0 in bundle 0.2.0."))
        self.assertFalse(assessor.assess(self.root, "addition-proportionate"))

    def test_one_word_correction_passes(self):
        text = self.scaffold("small-correction")
        self.target.write_text(text.replace("ran twice with the plugin and twice without",
                                            "ran three times with the plugin and three times without"))
        self.assertEqual(self.passes("small-correction"),
                         {name: True for name in assessor.CHECKS["small-correction"]})

    def test_correction_with_unrelated_edits_fails(self):
        text = self.scaffold("small-correction")
        text = text.replace("ran twice with the plugin and twice without",
                            "ran three times with the plugin and three times without")
        self.target.write_text(text.replace("Several checks are deliberately narrow.", "Some checks are narrow."))
        self.assertTrue(assessor.assess(self.root, "correction-made"))
        self.assertFalse(assessor.assess(self.root, "correction-proportionate"))

    def test_uncorrected_document_fails(self):
        self.scaffold("small-correction")
        self.assertFalse(assessor.assess(self.root, "correction-made"))


if __name__ == "__main__":
    unittest.main()
