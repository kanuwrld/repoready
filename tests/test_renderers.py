from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from repoready.checks import audit_repository
from repoready.models import AuditReport, CheckResult
from repoready.renderers import render_json, render_markdown, render_text


class RendererTests(unittest.TestCase):
    def test_text_renderer_contains_score_and_hint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = render_text(audit_repository(directory))

        self.assertIn("RepoReady 0/100 · FAIL", output)
        self.assertIn("Add README.md", output)
        self.assertIn("0/13 checks passed", output)

    def test_json_renderer_has_stable_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = json.loads(render_json(audit_repository(directory, min_score=20)))

        self.assertEqual(payload["score"], 0)
        self.assertEqual(payload["max_score"], 100)
        self.assertEqual(payload["min_score"], 20)
        self.assertFalse(payload["passes"])
        self.assertEqual(len(payload["checks"]), 13)

    def test_markdown_renderer_contains_table_and_next_fixes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = render_markdown(audit_repository(directory))

        self.assertIn("## RepoReady: 0/100 · ❌ FAIL", output)
        self.assertIn("| Status | Check | Points | Detail |", output)
        self.assertIn("| ❌ | README | 0/15 |", output)
        self.assertIn("### Next fixes", output)
        self.assertIn("**README:** Add README.md", output)

    def test_markdown_renderer_escapes_table_delimiters(self) -> None:
        report = AuditReport(
            root=Path("."),
            results=(
                CheckResult(
                    key="example",
                    title="Build | package",
                    weight=5,
                    passed=False,
                    detail="Missing | broken",
                    hint="Add build | release workflow.",
                ),
            ),
            min_score=0,
        )

        output = render_markdown(report)

        self.assertIn("Build \\| package", output)
        self.assertIn("Missing \\| broken", output)
        self.assertIn("Add build \\| release workflow.", output)


if __name__ == "__main__":
    unittest.main()
