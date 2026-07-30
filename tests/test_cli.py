from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from repoready.cli import main


class CliTests(unittest.TestCase):
    def test_returns_one_below_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main([directory])

        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL", stdout.getvalue())

    def test_returns_zero_at_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "README.md").write_text("Hello\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main([directory, "--min-score", "15"])

        self.assertEqual(exit_code, 0)
        self.assertIn("15/100", stdout.getvalue())

    def test_json_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main([directory, "--format", "json", "--min-score", "0"])

        self.assertEqual(exit_code, 0)
        self.assertIn('"passes": true', stdout.getvalue())

    def test_markdown_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [directory, "--format", "markdown", "--min-score", "0"]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("| Status | Check | Points | Detail |", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
