# RepoReady

[![CI](https://github.com/kanuwrld/repoready/actions/workflows/ci.yml/badge.svg)](https://github.com/kanuwrld/repoready/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-0a7f5a.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](pyproject.toml)

Know whether a repository is ready for contributors and releases before people
find the gaps.

RepoReady is a zero-runtime-dependency CLI and GitHub Action. It checks 13
high-signal repository health essentials, produces a score from 0 to 100, and
explains the next useful fix. It never uploads source code and needs no token.

```text
$ repoready .
RepoReady 100/100 · PASS

PASS  15  README                  README.md
PASS  12  Automated tests         tests/ contains test files
PASS  12  Continuous integration  .github/workflows/ci.yml
...

13/13 checks passed · required score: 80
```

## Why RepoReady

- Fast: one local filesystem scan, no network calls.
- Actionable: every failed check includes a concrete fix.
- Portable: Python 3.10+ and standard library only.
- CI-friendly: stable exit codes plus JSON output.
- Opinionated, not opaque: weights total exactly 100 and live in one rule set.

## Quick start

Run from a checkout:

```bash
python -m pip install .
repoready .
```

Fail CI when score is below a chosen threshold:

```bash
repoready . --min-score 90
```

Get machine-readable output:

```bash
repoready . --format json > repoready.json
```

Write a pull request or GitHub Actions job summary:

```bash
repoready . --format markdown >> "$GITHUB_STEP_SUMMARY"
```

Exit codes:

| Code | Meaning |
| ---: | --- |
| `0` | Score meets threshold |
| `1` | Score is below threshold |
| `2` | Invalid path or CLI input |

## GitHub Action

```yaml
name: Repository health

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  repoready:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - uses: kanuwrld/repoready@v1
        with:
          min-score: "80"
```

Until the first stable tag, pin the action to a commit SHA.

## Scoring

| Check | Points |
| --- | ---: |
| README | 15 |
| Automated tests | 12 |
| Continuous integration | 12 |
| License | 10 |
| Dependency manifest | 10 |
| Security policy | 8 |
| Contributing guide | 7 |
| Issue templates | 6 |
| Code of conduct | 5 |
| Pull request template | 5 |
| Changelog | 5 |
| `.gitignore` | 3 |
| Dependency updates | 2 |
| **Total** | **100** |

RepoReady detects common Python, JavaScript, TypeScript, Go, Rust, Java, Ruby,
PHP, .NET, and Swift manifests. Rules check repository structure, not product
quality or code correctness.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m repoready . --min-score 100
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow and review expectations.

## Roadmap

- Configurable weights and required checks
- SARIF output for GitHub code scanning
- Ecosystem-specific rule packs

Useful proposals belong in
[GitHub Issues](https://github.com/kanuwrld/repoready/issues). Focused pull
requests with tests are welcome.

## License

[MIT](LICENSE)
