## Stage 265 Code Review — `row-one local-ops`

**Verification performed:** Full diff review of all 11 changed + 2 new files; ran 288 relevant tests (scheduling, row_one_cli, row_one_docs, package_archives, first_run_smoke, row_one_app_contract, row_one_render) — all pass; `ruff check` clean; confirmed clean import (no cycle); validated every printed command against the actual `run`/`build`/`preview`/`serve` signatures.

### Critical
None.

### Important
None.

### Minor (non-blocking)
1. **Runbook `run` snippet is a reduced flag set.** The printed `fashion-radar run` omits all `--digest-*` options (ops.py:36-39). This is intentional and matches the existing `docs/row-one.md` snippet style, but operators wanting packaged digests from the manual refresh path won't see that hint in the runbook. Consider a one-line pointer in a future stage; not a Stage 265 blocker.
2. **`--port` rendered as bare int, `--host` via `shlex.quote`.** Correct for shell use; noting only that `shlex.quote("0.0.0.0")` returns unquoted `0.0.0.0`, which is the desired output and matches all test assertions. No action needed.

### Constraint checks (all clear)
- **No JSON contract drift:** `contract_version = "row-one-app/v1"` lives in `render.py:19` (unmodified this stage); `test_row_one_app_contract.py` passes (35 tests). The only `row_one` source touched is `__init__.py` (re-export) + new `ops.py`.
- **No semantic side effects:** `ops.py` imports only read-only formatters (`validate_hhmm`, `raw_as_of_shell`, `render_row_one_cron_example`, `format_row_one_site_access_message`) and returns a string. The CLI handler only `typer.echo`s it with a `ValueError`/exit-1 guard. No collection, scoring/ranking, scheduling-install, server-start, SQLite read, site build, or file mutation added.
- **Package archive guardrail:** `src/fashion_radar/row_one/ops.py` is consistently added to both `scripts/check_package_archives.py` (`SDIST_REQUIRED_PATHS`) and `tests/test_package_archives.py` (`SDIST_FILES`).
- **Smoke coverage:** `--help` and the live runbook output are both exercised in `check_first_run_smoke.py` and mirrored exactly in `test_first_run_smoke.py` (incl. the mocked subprocess fixture).
- **Docs consistency:** README, `cli-reference.md`, `row-one.md`, `github-upload-checklist.md` updated consistently; required phrases enforced by `test_row_one_docs.py`. `.row-one-site` marker reference is accurate (`render.py:39`, `server.py:54`).
- **Printed commands validated** against real signatures: `run` (cli.py:2413), `row-one build` (1389), `row-one preview` (1422), `row-one serve` (1497) — all flags exist and match.

### Verdict
**APPROVE — ship.** Clean, tightly-scoped, print-only addition with complete tests, guardrails, and docs. No release blockers, no correctness risks, no import cycles, no contract drift, and it stays within the AGENTS.md print-only boundary.
