"""Data models for repository audit results."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    """Result from one weighted repository check."""

    key: str
    title: str
    weight: int
    passed: bool
    detail: str
    hint: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return {
            "key": self.key,
            "title": self.title,
            "weight": self.weight,
            "passed": self.passed,
            "detail": self.detail,
            "hint": self.hint,
        }


@dataclass(frozen=True)
class AuditReport:
    """Complete audit for one repository root."""

    root: Path
    results: tuple[CheckResult, ...]
    min_score: int = 80

    @property
    def score(self) -> int:
        return sum(result.weight for result in self.results if result.passed)

    @property
    def max_score(self) -> int:
        return sum(result.weight for result in self.results)

    @property
    def passed_count(self) -> int:
        return sum(result.passed for result in self.results)

    @property
    def passes_threshold(self) -> bool:
        return self.score >= self.min_score

    def as_dict(self) -> dict[str, object]:
        """Return a stable, JSON-serializable report."""

        return {
            "root": str(self.root),
            "score": self.score,
            "max_score": self.max_score,
            "min_score": self.min_score,
            "passes": self.passes_threshold,
            "passed_checks": self.passed_count,
            "total_checks": len(self.results),
            "checks": [result.as_dict() for result in self.results],
        }
