# Contributing

RepoReady accepts focused changes that make repository audits clearer, more
portable, or more accurate.

## Workflow

1. Search existing issues and open one for non-trivial changes.
2. Create a branch from `main`.
3. Add or update tests with the implementation.
4. Run local checks:

   ```bash
   python -m unittest discover -s tests -v
   python -m repoready . --min-score 100
   ```

5. Open a pull request that explains the behavior change and validation.

## Rule changes

Rule weights must total 100. A new rule needs:

- a clear signal that works across repositories;
- a useful failure hint;
- positive and negative tests;
- documentation of score impact.

Avoid network-dependent checks, hidden heuristics, and rules that reward file
quantity over maintainability.

## Commit and review expectations

- Keep commits scoped and descriptive.
- Do not include generated build artifacts.
- Link the issue with `Closes #<number>` when the pull request completes it.
- Maintainers may request a smaller change when a proposal mixes concerns.
