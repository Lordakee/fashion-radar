# Claude Code Stage 16 Code Review Prompt

You are reviewing the Stage 16 implementation for Fashion Radar. Run this as a
read-only code review. Do not edit files, do not commit, do not call the
network, do not run collectors, do not create directories, do not open SQLite
except through read-only tests that already exist, and do not execute
platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-16-code-review-prompt.md
```

## Stage Goal

Stage 16 adds a local, read-only community signal file diagnostics command:

```bash
fashion-radar community-signal-lint PATH --input-format csv
fashion-radar community-signal-lint PATH --input-format json
fashion-radar community-signal-lint PATH --input-format csv --format json
fashion-radar community-signal-lint PATH --input-format csv --strict
fashion-radar community-signal-lint PATH --input-format csv --source-name "Community Tool Export"
```

The command should help external tools controlled by the user produce sanitized
local CSV/JSON files that fit the existing community signal import contract
before `import-signals --dry-run` or `import-signals` is used.

This is not a product-facing compliance review, audit workflow, safety workflow,
policy checklist, approval UI, platform connector, scraper, crawler, browser
automation flow, social monitoring system, source acquisition tool, or
current-hotness ranking.

## Files To Review

New:

- `src/fashion_radar/community_signals.py`
- `tests/test_community_signal_lint.py`
- `docs/community-signal-quality.md`
- `docs/superpowers/specs/2026-06-12-stage-16-community-signal-file-diagnostics-design.md`
- `docs/superpowers/plans/2026-06-12-stage-16-community-signal-file-diagnostics-plan.md`
- `docs/reviews/claude-code-stage-16-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-16-plan-review.md`
- `docs/reviews/claude-code-stage-16-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-16-plan-rereview.md`
- `docs/reviews/claude-code-stage-16-plan-rereview-2.md`

Modified:

- `src/fashion_radar/cli.py`
- `tests/test_cli.py`
- `tests/test_community_signal_import_contract.py`
- `docs/community-signal-import.md`
- `docs/manual-signal-import.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `README.md`
- `CHANGELOG.md`

## Implementation Summary

- Added `CommunitySignalFindingSeverity`, `CommunitySignalFinding`, and
  `CommunitySignalLintResult`.
- Added `lint_community_signal_file()` with local CSV/JSON raw reading,
  strict allowed-field checks, prohibited-field checks, `csv_extra_cells`
  detection, duplicate URL warnings, provenance/default info findings, and
  import-readiness validation through existing `ManualSignalRow`.
- Added `render_community_signal_lint_table()` with deterministic table output.
- Added `fashion-radar community-signal-lint` with `--input-format`,
  `--format`, `--source-name`, and `--strict`.
- Kept `import-signals`, manual import storage, SQLite schema, collectors,
  matching, scoring, reports, dashboard, source packs, and entity packs
  unchanged.
- Added unit, CLI, and contract drift tests.
- Added docs that frame the command as local file diagnostics only.

## Verification Already Run

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
codegraph status
```

Observed results:

- `git diff --check`: passed.
- `pytest`: 342 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `codegraph status`: index up to date.

## Review Focus

Please inspect for:

1. Correct strict community contract handling:
   - allowed fields match `schemas/community-signals.schema.json`;
   - prohibited fields emit `prohibited_field`, not duplicate `unknown_field`;
   - unrelated extras emit `unknown_field`;
   - over-wide CSV rows emit `csv_extra_cells`;
   - JSON top-level shape is strict.
2. Import-readiness alignment:
   - validation uses `ManualSignalRow`;
   - fallback source-name behavior matches `load_manual_signal_rows()`;
   - existing `import-signals` behavior remains backward-compatible.
3. Read-only/no-artifact behavior:
   - linter does not create config/data/report directories;
   - linter does not open SQLite, import rows, run collectors, run matching,
     score, generate reports, package digests, or touch dashboard state.
4. CLI behavior:
   - table/json output is deterministic;
   - errors exit non-zero;
   - warnings exit non-zero only with `--strict`;
   - invalid files avoid tracebacks.
5. Tests:
   - meaningful coverage for module behavior, CLI behavior, no-artifact
     behavior, and schema/example drift.
6. Documentation boundaries:
   - docs avoid platform/source acquisition instructions;
   - docs avoid platform/community-wide or market-wide claims;
   - docs do not present a compliance/audit/legal feature.

## Next-Stage Plan If Approved

If this code review approves Stage 16 upload, the next stage is release/upload
verification only:

1. Run default-registry lock/sync checks:
   `uv lock --check --default-index https://pypi.org/simple` and
   `uv sync --locked --dev --check --default-index https://pypi.org/simple`.
2. Run mirror sync check without modifying lockfile:
   `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`.
3. Build a wheel/sdist into `/tmp/fashion-radar-dist-stage16`.
4. Smoke-test an installed wheel in a temp venv, using the Tsinghua mirror for
   install if needed.
5. Scan for secrets and generated artifacts.
6. Commit Stage 16.
7. Push to GitHub with temporary `GIT_ASKPASS` only, keeping the remote URL
   token-free.

## Response Format

Start with one of:

- `Approved for Stage 16 upload`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before upload.
- `Important:` issues that should be fixed before upload.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about exact files/sections and required changes.
