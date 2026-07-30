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

    def test_writes_selected_format_to_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "reports" / "repoready.md"
            destination.parent.mkdir()
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        directory,
                        "--format",
                        "markdown",
                        "--min-score",
                        "0",
                        "--output",
                        str(destination),
                    ]
                )

            output = destination.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")
        self.assertTrue(output.startswith("## RepoReady:"))
        self.assertTrue(output.endswith("\n"))
        self.assertFalse(output.endswith("\n\n"))

    def test_output_file_requires_existing_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "missing" / "report.json"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main(
                        [
                            directory,
                            "--format",
                            "json",
                            "--output",
                            str(destination),
                        ]
                    )

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("Could not write report", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
