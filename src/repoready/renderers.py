"""Human and machine-readable audit renderers."""

from __future__ import annotations

import json

from .models import AuditReport


def render_text(report: AuditReport) -> str:
    """Render a compact terminal report."""

    outcome = "PASS" if report.passes_threshold else "FAIL"
    lines = [f"RepoReady {report.score}/{report.max_score} · {outcome}", ""]

    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(
            f"{status:<4}  {result.weight:>2}  {result.title:<23} {result.detail}"
        )
        if result.hint:
            lines.append(f"      ↳ {result.hint}")

    lines.extend(
        (
            "",
            f"{report.passed_count}/{len(report.results)} checks passed"
            f" · required score: {report.min_score}",
        )
    )
    return "\n".join(lines)


def render_json(report: AuditReport) -> str:
    """Render stable, pretty JSON."""

    return json.dumps(report.as_dict(), indent=2, sort_keys=True)


def _markdown_cell(value: str) -> str:
    """Escape content that would break a GitHub-flavored Markdown table."""

    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def render_markdown(report: AuditReport) -> str:
    """Render a GitHub-flavored Markdown report."""

    outcome = "✅ PASS" if report.passes_threshold else "❌ FAIL"
    lines = [
        f"## RepoReady: {report.score}/{report.max_score} · {outcome}",
        "",
        "| Status | Check | Points | Detail |",
        "| :---: | --- | ---: | --- |",
    ]

    failed = []
    for result in report.results:
        status = "✅" if result.passed else "❌"
        points = result.weight if result.passed else 0
        lines.append(
            f"| {status} | {_markdown_cell(result.title)}"
            f" | {points}/{result.weight} | {_markdown_cell(result.detail)} |"
        )
        if not result.passed:
            failed.append(result)

    lines.extend(
        (
            "",
            f"**{report.passed_count}/{len(report.results)} checks passed.** "
            f"Required score: **{report.min_score}**.",
        )
    )

    if failed:
        lines.extend(("", "### Next fixes", ""))
        lines.extend(
            f"- **{_markdown_cell(result.title)}:** {_markdown_cell(result.hint)}"
            for result in failed
        )

    return "\n".join(lines)
