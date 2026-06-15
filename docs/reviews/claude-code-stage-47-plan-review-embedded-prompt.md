# Claude Code Stage 47 Embedded Plan Review Prompt

Plan review only. Do not edit files. Do not read repository files. Review only
the plan text below. Use maximum effort. Treat Critical and Important findings
as blockers.

## Stage 47 Goal

Make the GitHub first-run experience deterministic and testable: a new user can
clone the repository, run a local-only sample workflow from checked-in examples,
generate a report, and inspect candidate/trend JSON outputs without live
collection or external platform access.

## Technical Approach

- Add `scripts/check_first_run_smoke.py` using only Python standard library.
- The script accepts `--repo-root` and `--python`, creates a temp runtime
  workspace, and runs CLI commands via `python -m fashion_radar`.
- Every command runs with `cwd=repo_root`, `PYTHONPATH` prepending
  `repo_root/src`, and explicit temp path flags whenever supported. The smoke
  asserts that repo `data/` and `reports/` did not receive generated default
  artifacts.
- Use deterministic constants:
  - `AS_OF = "2026-06-13T12:00:00Z"`
  - `SOURCE_NAME = "Community Tool Export"`
  - `EXAMPLE_CSV = "examples/community-signals.example.csv"`
- Run only local/offline commands:
  - `init`
  - `migrate-db`
  - `doctor`
  - `community-signal-lint`
  - `community-candidates --format json`
  - `import-signals --dry-run`
  - `import-signals`
  - `imported-signals-summary --format json`
  - `imported-signals --format json`
  - `match`
  - `report`
  - `candidates --format json`
  - `trends --format json`
- Copy the checked-in CSV into a temp `exports/` directory and run local
  directory handoff commands:
  - `community-handoff-workflow`
  - `community-signal-lint-dir`
  - `community-candidates-dir --format json`
  - `import-signals-dir --dry-run`
- The temp exports contract is explicit: the script creates exactly
  `$tmp/exports/community-signals.csv` before directory commands;
  `community-handoff-workflow` is print-only and does not create files.
- `doctor` is included because the current CLI command checks only local paths,
  config loading, and SQLite schema status for the supplied `--data-dir`; it
  does not fetch URLs, validate live services, inspect accounts, or use
  external credentials.
- Assert:
  - example CSV exists;
  - temp config/data/reports dirs exist;
  - local SQLite database exists after import;
  - `reports/fashion-radar-2026-06-13.md` exists and is non-empty;
  - `reports/fashion-radar-2026-06-13.json` exists and is non-empty;
  - JSON outputs parse;
  - imported summary reports at least one imported row.
- Print `First-run sample smoke passed.` on success; print concise findings to
  stderr and return `1` on failure.
- Add `tests/test_first_run_smoke.py` with test-first coverage for constants,
  command builder, JSON validation, imported summary validation, and report path
  derivation.
- Update CI and `docs/github-upload-checklist.md` with:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

- Update README and `docs/community-signal-import.md` so first-run docs use
  checked-in examples instead of nonexistent `./signals.csv`,
  `./community-signals.csv`, or unexplained `./exports`.
- Add docs drift tests in `tests/test_cli_docs.py`.

## Tech Stack

Python 3.11 standard library (`argparse`, `dataclasses`, `json`, `shutil`,
`subprocess`, `sys`, `tempfile`, `pathlib`), pytest, Ruff, Typer CLI via
`python -m fashion_radar`, GitHub Actions YAML, Markdown, `uv`.

## Boundaries

Out of scope:

- live `collect`;
- RSS/GDELT network fetches;
- web scraping or crawling;
- browser automation;
- login/cookie/session handling;
- account automation;
- platform connectors;
- media download;
- monitoring/watching/scheduling;
- external services;
- product compliance-review functionality;
- dependency or lockfile changes;
- schema/scoring/entity-alias changes;
- committed generated runtime data or reports;
- launching a long-running dashboard server in CI.

## Planned Files

- Create `scripts/check_first_run_smoke.py`
- Create `tests/test_first_run_smoke.py`
- Modify `README.md`
- Modify `docs/community-signal-import.md`
- Modify `docs/github-upload-checklist.md`
- Modify `.github/workflows/ci.yml`
- Modify `tests/test_cli_docs.py`
- Add Stage 47 review artifacts

## Review Questions

1. Is this safe and useful as the next node after Stage 46 release hygiene?
2. Are the planned commands deterministic and fully local/offline?
3. Are the assertions strong enough without requiring non-empty candidate/trend
   business results?
4. Is the TDD/docs/CI plan credible?
5. Does the plan avoid all out-of-scope platform automation and compliance
   functionality?
6. Any Critical or Important blockers before implementation?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If acceptable, include exactly:

```text
APPROVED FOR STAGE 47 FIRST RUN SAMPLE SMOKE
```
