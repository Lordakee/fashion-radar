# Stage 393 ROW ONE Strict Operations Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans`
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in strict exit mode to the local ROW ONE operations check
so automation can fail on an unhealthy or unknown site while preserving the
current human diagnostic behavior.

**Architecture:** Keep `build_row_one_ops_check_payload` read-only and preserve
the existing payload contract. Add one canonical healthy-status constant and a
pure predicate in `row_one/ops_check.py`; use it to harden top-level status
derivation and to implement a post-output `--strict` exit in the CLI. Update
only the relevant public docs and contract tests.

**Tech Stack:** Python 3.11+, Typer, existing ROW ONE ops-check models/helpers,
pytest, Ruff, uv, Markdown contract tests. No new dependency.

## Parallel Work Allocation

The coordinator owns plan/review records, integration, cross-cutting changes,
full verification, and commit/push. Workers have disjoint write scopes:

| Worker | Writable scope | Dependency | Completion |
| --- | --- | --- | --- |
| A | `src/fashion_radar/row_one/ops_check.py`, `tests/test_row_one_ops_check.py` | None after plan approval | Pure healthy-status predicate, strict local-article allowlist, focused ops-check tests pass. |
| B | `src/fashion_radar/cli.py`, `tests/test_row_one_cli.py` | Starts after A is integrated and its focused tests are green because CLI imports the canonical predicate. | `--strict` text/JSON exit behavior and output ordering pass. |
| C | `README.md`, `docs/row-one.md`, `docs/cli-reference.md`, `docs/scheduling.md`, `tests/test_row_one_docs.py`, `tests/test_scheduling_docs.py` | Can run in parallel with A. | Docs describe strict mode and preserve the no-auto-health-gate scheduling boundary. |

No worker may modify another worker's scope. B must not start until A's
changed symbols are reconciled. C must not add `--strict` to generated cron or
systemd refresh snippets. The coordinator reconciles each worker's changed
paths and verification before reclaiming it.

## Task 0: Review And Accept The Plan

**Files:**

- Create: `docs/reviews/claude-code-stage-393-plan-review.md` or record the
  honest timeout in scratch only
- Create: `docs/reviews/opencode-stage-393-plan-review.md` when fallback is used
- Create: rereview records only when a finding requires a revision

1. Submit the Stage 393 design and plan to local Claude Code in read-only plan
   mode with `--effort max`.
2. If Claude Code returns a coherent review, preserve only that body in the
   Claude review record. If it times out, do not create an approval stub.
3. Run OpenCode fallback with
   `zhipuai-coding-plan/glm-5.2 --variant max`, capture one coherent review,
   and record it without tool-status narration.
4. Resolve every Critical and Important finding before implementation. Re-run
   the applicable plan review after any material plan change.

## Task 1: Harden The Pure Health Contract (Worker A)

**Files:**

- Modify: `src/fashion_radar/row_one/ops_check.py`
- Modify: `tests/test_row_one_ops_check.py`

1. Add failing tests for a canonical strict healthy status, `attention`,
   `unknown`, empty/non-string statuses, an unrecognized status such as
   `degraded`, a missing status key, and `None`; also test `_overall_status`
   rejecting an unexpected local-article status.
2. Define a single constant for
   `site_ready_scheduler_unverified` and a pure status predicate with a narrow
   mapping/typing contract. Use the constant as `_overall_status`'s healthy
   return value and as the CLI predicate's comparison target. Separately
   require route and content statuses to be `ready` or `not_applicable`.
   Preserve existing literal-value assertions unless a test is specifically
   proving the new predicate.
3. Keep the existing `ok` field, nested payloads, filename-only systemd
   boundary, and default diagnostic status strings unchanged.
4. Run:

   ```bash
   UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
     tests/test_row_one_ops_check.py
   ```

## Task 2: Add The CLI Strict Exit (Worker B, after Task 1)

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_cli.py`

1. Add failing CLI tests that patch a read-only payload builder and verify:
   default `attention` remains exit 0; `--strict` healthy exits 0;
   `--strict` `attention` and `unknown` exit 1; both text and `--json` print
   the diagnostic before the exit; strict failure does not emit
   `ROW ONE ops check failed:`; `--strict --json` and ordinary `--json` emit
   byte-identical stdout for the same payload; and help exposes only
   `--strict`, not `--no-strict`.
2. Add a Typer boolean option:

   ```python
   strict: bool = typer.Option(
       False,
       "--strict",
       help="Exit nonzero when the ROW ONE ops status is not healthy.",
   )
   ```

   Verify the generated help exposes the intended `--strict` form and does not
   add an unwanted `--no-strict` alias.

3. Refactor only the final output branch so text or JSON is emitted exactly as
   before, then raise `typer.Exit(1)` when strict mode and the pure predicate
   returns false. The deliberate exit must be outside the existing
   `try/except Exception` block; do not route it through the generic error
   handler. Keep `ok: true` unchanged and document that strict callers use
   process exit status rather than `ok` to gate health.
4. Run:

   ```bash
   UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
     tests/test_row_one_cli.py
   ```

## Task 3: Document The Automation Contract (Worker C)

**Files:**

- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/scheduling.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_scheduling_docs.py`

1. Add the strict command and its success status to the ROW ONE CLI guidance.
2. State that default `ops-check` remains permissive/read-only, while
   `--strict` exits 1 for `attention` or `unknown` after printing diagnostics.
3. State that `site_ready_scheduler_unverified` is the only strict success and
   does not prove systemd activation or a future scheduled run. Explain that
   `ok: true` means diagnostic construction succeeded and is not the strict
   health result.
4. Keep `--strict` out of normal 04:00 cron/systemd refresh snippets and add
   the new guidance as a separate Stage 393 paragraph outside the existing
   Stage 329 boundary slice. Keep documentation tests as pure content checks;
   they must not invoke the CLI.
5. Run the focused document tests and Ruff on changed docs/tests.

## Task 4: Integrated Verification And Review

The coordinator reconciles all worker paths and runs, at minimum:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_ops_check.py tests/test_row_one_cli.py \
  tests/test_row_one_docs.py tests/test_scheduling_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
git diff --check
```

Then request a fresh Claude Code code review of the stable integrated diff.
Fix all Critical and Important findings and rerun affected tests. Use OpenCode
fallback only when Claude is unavailable, recording one coherent review body.

## Task 5: Release Gate And Handoff

Run the full pytest suite, `UV_NO_CONFIG=1 uv lock --check`, locked sync check,
release hygiene, package/archive and installed-wheel smoke checks, and secret/
generated-artifact scans. Stage only deliberate Stage 393 files, verify the
ignored local config remains unstaged, commit and push `main`, then verify
`HEAD == origin/main`.

The node handoff must state repo status, commit, verified commands, uncommitted
files, review verdict, and the next stage candidate. Do not include large diffs
or live tool logs.
