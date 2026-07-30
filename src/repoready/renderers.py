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
