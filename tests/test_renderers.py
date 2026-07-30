from __future__ import annotations

import json
import tempfile
import unittest

from repoready.checks import audit_repository
from repoready.renderers import render_json, render_text


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


if __name__ == "__main__":
    unittest.main()
