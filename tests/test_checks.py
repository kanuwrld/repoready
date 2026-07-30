from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from repoready.checks import RULES, audit_repository


class AuditRepositoryTests(unittest.TestCase):
    def test_rule_weights_total_one_hundred(self) -> None:
        self.assertEqual(sum(rule.weight for rule in RULES), 100)
        self.assertEqual(len({rule.key for rule in RULES}), len(RULES))

    def test_empty_directory_scores_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = audit_repository(directory)

        self.assertEqual(report.score, 0)
        self.assertFalse(report.passes_threshold)
        self.assertTrue(all(result.hint for result in report.results))

    def test_complete_repository_scores_one_hundred(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = (
                "README.md",
                "LICENSE",
                "pyproject.toml",
                "SECURITY.md",
                "CONTRIBUTING.md",
                "CODE_OF_CONDUCT.md",
                "CHANGELOG.md",
                ".gitignore",
                "tests/test_sample.py",
                ".github/workflows/ci.yml",
                ".github/ISSUE_TEMPLATE/bug.yml",
                ".github/PULL_REQUEST_TEMPLATE.md",
                ".github/dependabot.yml",
            )
            for filename in files:
                path = root / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("content\n", encoding="utf-8")

            report = audit_repository(root, min_score=100)

        self.assertEqual(report.score, 100)
        self.assertTrue(report.passes_threshold)
        self.assertEqual(report.passed_count, len(RULES))

    def test_detects_test_file_outside_standard_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_test = root / "src" / "widget.test.ts"
            source_test.parent.mkdir(parents=True)
            source_test.write_text("test('works', () => {});\n", encoding="utf-8")

            report = audit_repository(root)

        tests_result = next(result for result in report.results if result.key == "tests")
        self.assertTrue(tests_result.passed)
        self.assertEqual(tests_result.detail, "src/widget.test.ts")

    def test_rejects_file_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "file.txt"
            path.write_text("content", encoding="utf-8")

            with self.assertRaises(NotADirectoryError):
                audit_repository(path)


if __name__ == "__main__":
    unittest.main()
