"""Offline tests for grading Codex transcripts; no model calls."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("run_codex", Path(__file__).parents[1] / "run-codex.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class GradingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)

    def grade(self, spec, events=None):
        return runner.grade(spec, self.workspace, events or [])

    def test_missing_file_fails_even_for_negative_pattern(self):
        result = self.grade({"type": "regex", "target": {"source": "file", "path": "missing.md"},
                             "pattern": "recieve", "match": "not_contains"})
        self.assertFalse(result["passed"])

    def test_case_insensitive_multiline_vocabulary(self):
        (self.workspace / "accept.txt").write_text("WezTerm\nZellij\n")
        result = self.grade({"type": "regex", "target": {"source": "file", "path": "accept.txt"},
                             "pattern": r"^(\(\?i\))?zellij$", "flags": "im"})
        self.assertTrue(result["passed"])

    def test_negative_pattern_detects_typo(self):
        (self.workspace / "accept.txt").write_text("recieve\n")
        result = self.grade({"type": "regex", "target": {"source": "file", "path": "accept.txt"},
                             "pattern": "recieve", "match": "not_contains"})
        self.assertFalse(result["passed"])

    def test_response_grader_ignores_command_output(self):
        events = [{"type": "item.completed", "item": {
            "type": "command_execution", "command": "echo receive", "aggregated_output": "receive"}}]
        self.assertFalse(self.grade({"type": "regex", "pattern": "receive"}, events)["passed"])
        events.append({"type": "item.completed", "item": {"type": "agent_message", "text": "receive"}})
        self.assertTrue(self.grade({"type": "regex", "pattern": "receive"}, events)["passed"])

    def test_command_event_is_counted_once(self):
        item = {"type": "command_execution", "command": "scripts/lint-prose docs/terminal.md"}
        events = [{"type": event, "item": item} for event in ("item.started", "item.completed")]
        result = self.grade({"type": "tool_used", "tool": "Bash", "input_match": "lint-prose",
                             "min": 1, "max": 1}, events)
        self.assertTrue(result["passed"])
        self.assertEqual(result["count"], 1)

    def test_skill_diagnostic_requires_successful_read_of_tested_copy(self):
        path = self.workspace / ".agents/skills/technical-writing/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("# Technical Writing\nInstructions unique to tested copy.\n")
        item = {"type": "command_execution", "command": f"cat {path}",
                "aggregated_output": "", "exit_code": 0}
        events = [{"type": "item.completed", "item": item}]
        spec = {"type": "tool_used", "tool": "Skill"}
        self.assertFalse(self.grade(spec, events)["passed"])
        item["aggregated_output"] = path.read_text()
        result = self.grade(spec, events)
        self.assertTrue(result["passed"])
        self.assertTrue(result["diagnostic"])
        item["exit_code"] = 1
        self.assertFalse(self.grade(spec, events)["passed"])

    def test_unknown_grader_is_rejected(self):
        with self.assertRaises(ValueError):
            self.grade({"type": "llm"})


if __name__ == "__main__":
    unittest.main()
