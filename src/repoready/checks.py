"""Weighted repository readiness checks."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from .models import AuditReport, CheckResult

Detector = Callable[[Path], tuple[bool, str]]


@dataclass(frozen=True)
class Rule:
    key: str
    title: str
    weight: int
    hint: str
    detector: Detector


def _root_file(root: Path, names: Iterable[str]) -> Path | None:
    wanted = {name.lower() for name in names}
    return next(
        (
            candidate
            for candidate in root.iterdir()
            if candidate.is_file() and candidate.name.lower() in wanted
        ),
        None,
    )


def _root_prefix(root: Path, prefixes: Iterable[str]) -> Path | None:
    wanted = tuple(prefix.lower() for prefix in prefixes)
    return next(
        (
            candidate
            for candidate in root.iterdir()
            if candidate.is_file()
            and candidate.name.lower().startswith(wanted)
        ),
        None,
    )


def _first_file(directory: Path, suffixes: tuple[str, ...] | None = None) -> Path | None:
    if not directory.is_dir():
        return None
    for candidate in directory.rglob("*"):
        if not candidate.is_file():
            continue
        if suffixes is None or candidate.suffix.lower() in suffixes:
            return candidate
    return None


def _relative(candidate: Path, root: Path) -> str:
    return candidate.relative_to(root).as_posix()


def _readme(root: Path) -> tuple[bool, str]:
    candidate = _root_prefix(root, ("readme",))
    return (
        (True, candidate.name)
        if candidate
        else (False, "No root README file found")
    )


def _license(root: Path) -> tuple[bool, str]:
    candidate = _root_prefix(root, ("license", "licence", "copying"))
    return (
        (True, candidate.name)
        if candidate
        else (False, "No root license file found")
    )


def _manifest(root: Path) -> tuple[bool, str]:
    candidate = _root_file(
        root,
        (
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "package.json",
            "deno.json",
            "deno.jsonc",
            "bun.lock",
            "cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "gemfile",
            "composer.json",
            "pubspec.yaml",
            "package.swift",
        ),
    )
    if candidate is None:
        project_files = sorted(root.glob("*.csproj"))
        candidate = project_files[0] if project_files else None
    return (
        (True, candidate.name)
        if candidate
        else (False, "No supported dependency or build manifest found")
    )


def _tests(root: Path) -> tuple[bool, str]:
    suffixes = (
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".rs",
        ".java",
        ".rb",
        ".php",
        ".cs",
        ".swift",
    )
    for name in ("tests", "test", "spec", "__tests__"):
        directory = root / name
        candidate = _first_file(directory, suffixes)
        if candidate:
            return True, f"{name}/ contains test files"
    for candidate in root.rglob("*"):
        if not candidate.is_file() or candidate.suffix.lower() not in suffixes:
            continue
        lowered = candidate.name.lower()
        if lowered.startswith("test_") or ".test." in lowered or ".spec." in lowered:
            return True, _relative(candidate, root)
    return False, "No recognizable test files found"


def _ci(root: Path) -> tuple[bool, str]:
    workflows = root / ".github" / "workflows"
    if workflows.is_dir():
        candidates = sorted(
            path
            for path in workflows.iterdir()
            if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
        )
        if candidates:
            return True, _relative(candidates[0], root)
    alternatives = (
        ".gitlab-ci.yml",
        "azure-pipelines.yml",
        "bitbucket-pipelines.yml",
        ".circleci/config.yml",
        "Jenkinsfile",
    )
    for name in alternatives:
        candidate = root / name
        if candidate.is_file():
            return True, name
    return False, "No supported CI configuration found"


def _policy(root: Path, filename: str) -> tuple[bool, str]:
    for candidate in (root / filename, root / ".github" / filename):
        if candidate.is_file():
            return True, _relative(candidate, root)
    return False, f"No {filename} found"


def _issue_templates(root: Path) -> tuple[bool, str]:
    directory = root / ".github" / "ISSUE_TEMPLATE"
    candidate = _first_file(directory, (".md", ".yml", ".yaml"))
    if candidate and candidate.name.lower() not in {"config.yml", "config.yaml"}:
        return True, _relative(candidate, root)

    if directory.is_dir():
        for path in directory.iterdir():
            if (
                path.is_file()
                and path.suffix.lower() in {".md", ".yml", ".yaml"}
                and path.name.lower() not in {"config.yml", "config.yaml"}
            ):
                return True, _relative(path, root)
    return False, "No issue form or issue template found"


def _pull_request_template(root: Path) -> tuple[bool, str]:
    github = root / ".github"
    for candidate in (
        github / "PULL_REQUEST_TEMPLATE.md",
        github / "pull_request_template.md",
        root / "PULL_REQUEST_TEMPLATE.md",
        root / "pull_request_template.md",
    ):
        if candidate.is_file():
            return True, _relative(candidate, root)
    directory = github / "PULL_REQUEST_TEMPLATE"
    candidate = _first_file(directory, (".md",))
    return (
        (True, _relative(candidate, root))
        if candidate
        else (False, "No pull request template found")
    )


def _changelog(root: Path) -> tuple[bool, str]:
    candidate = _root_prefix(root, ("changelog", "history", "releases"))
    return (
        (True, candidate.name)
        if candidate
        else (False, "No changelog or release history found")
    )


def _gitignore(root: Path) -> tuple[bool, str]:
    candidate = root / ".gitignore"
    return (
        (True, candidate.name)
        if candidate.is_file()
        else (False, "No .gitignore found")
    )


def _dependency_updates(root: Path) -> tuple[bool, str]:
    candidates = (
        root / ".github" / "dependabot.yml",
        root / ".github" / "dependabot.yaml",
        root / "renovate.json",
        root / ".github" / "renovate.json",
    )
    candidate = next((path for path in candidates if path.is_file()), None)
    return (
        (True, _relative(candidate, root))
        if candidate
        else (False, "No Dependabot or Renovate configuration found")
    )


RULES: tuple[Rule, ...] = (
    Rule(
        "readme",
        "README",
        15,
        "Add README.md with purpose, setup, usage, and support details.",
        _readme,
    ),
    Rule(
        "tests",
        "Automated tests",
        12,
        "Add executable tests under tests/, test/, spec/, or __tests__/.",
        _tests,
    ),
    Rule(
        "ci",
        "Continuous integration",
        12,
        "Run tests on pushes and pull requests with a CI workflow.",
        _ci,
    ),
    Rule(
        "license",
        "License",
        10,
        "Add an OSI-approved LICENSE file.",
        _license,
    ),
    Rule(
        "manifest",
        "Dependency manifest",
        10,
        "Add a supported package, dependency, or build manifest.",
        _manifest,
    ),
    Rule(
        "security",
        "Security policy",
        8,
        "Add SECURITY.md with a private vulnerability-reporting path.",
        lambda root: _policy(root, "SECURITY.md"),
    ),
    Rule(
        "contributing",
        "Contributing guide",
        7,
        "Add CONTRIBUTING.md with setup, tests, and pull request workflow.",
        lambda root: _policy(root, "CONTRIBUTING.md"),
    ),
    Rule(
        "issue_templates",
        "Issue templates",
        6,
        "Add a bug report or feature request under .github/ISSUE_TEMPLATE/.",
        _issue_templates,
    ),
    Rule(
        "code_of_conduct",
        "Code of conduct",
        5,
        "Add CODE_OF_CONDUCT.md with behavior and enforcement expectations.",
        lambda root: _policy(root, "CODE_OF_CONDUCT.md"),
    ),
    Rule(
        "pull_request_template",
        "Pull request template",
        5,
        "Add .github/PULL_REQUEST_TEMPLATE.md with change and test prompts.",
        _pull_request_template,
    ),
    Rule(
        "changelog",
        "Changelog",
        5,
        "Add CHANGELOG.md and record user-visible changes.",
        _changelog,
    ),
    Rule(
        "gitignore",
        ".gitignore",
        3,
        "Add a .gitignore for generated and local-only files.",
        _gitignore,
    ),
    Rule(
        "dependency_updates",
        "Dependency updates",
        2,
        "Configure Dependabot or Renovate for maintained dependencies.",
        _dependency_updates,
    ),
)


def audit_repository(
    path: str | Path,
    *,
    min_score: int = 80,
) -> AuditReport:
    """Audit a local repository and return a weighted report."""

    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")
    if not 0 <= min_score <= 100:
        raise ValueError("Minimum score must be between 0 and 100")

    results = []
    for rule in RULES:
        passed, detail = rule.detector(root)
        results.append(
            CheckResult(
                key=rule.key,
                title=rule.title,
                weight=rule.weight,
                passed=passed,
                detail=detail,
                hint="" if passed else rule.hint,
            )
        )

    return AuditReport(root=root, results=tuple(results), min_score=min_score)
