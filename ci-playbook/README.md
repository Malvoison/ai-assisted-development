# CI Playbook (GitHub Actions)

A curated set of PR-time checks you can drop into any repo. Mix & match per project.

## What’s inside

- **provenance-check.yml** — Enforces AI provenance headers in test files.
- **openapi-drift-check.yml** — Fails if OpenAPI changed without corresponding tests.
- **style-analyzers.yml** — Runs `dotnet format` and builds with warnings as errors.
- **coverage-report.yml** — Runs tests with Coverlet and posts a summary.
- **markdown-quality.yml** — Spellcheck + link check for Markdown docs.
- **pr-title-lint.yml** — Semantic PR title linter.
- **secret-scan.yml** — Quick regex-based secret scanner on diffs.
- **size-labeler.yml** — Labels PR by diff size (XS/S/M/L/XL).
- **checklist-guard.yml** — Ensures coverage checklist appears in PR description.
- **hardcoded-id-guard.yml** — Blocks hard-coded GUIDs/IDs in tests.
- **large-file-guard.yml** — Blocks large (>5MB) files sneaking into PRs.

## Usage

Copy `.github/workflows/*` into your repo. Adjust paths (e.g., `tests/**/*.cs`) and thresholds as needed.

### Strict vs. relaxed
- Start relaxed (warnings/comments). Tighten later by exiting non-zero on failures.
- In `provenance-check.yml`, you can enable strict mode to require all six header fields.

## Requirements / Notes
- Some jobs assume .NET 8 and Coverlet for coverage. Adapt for other stacks.
- `markdown-quality.yml` expects a `.github/spellcheck.yml` config; create a minimal one if needed.
- Secret scanning here is heuristic. Consider enabling GitHub Advanced Security if available.

## Recommended companion files
- `PULL_REQUEST_TEMPLATE.md` — AI-assisted testing template w/ coverage checklist.
- `docs/testing-instructions.md` — Your v1.8 testing standards.
