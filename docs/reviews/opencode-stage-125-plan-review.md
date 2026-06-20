# Stage 125 Plan Review

## Critical Findings

None.

## Important Findings

None.

## Minor Findings

1. **Design architecture could note the intentional sync-command exclusion.** The bug report template is correctly added to the positive no-config/frozen `else` branch (lines 778-779 of `tests/test_cli_docs.py`) and the stale-command ban loop (lines 801-808), but is *not* added to the `isolated_lock_and_sync_commands` loop (lines 783-790) since it only carries `UV_NO_CONFIG=1 uv lock --check` (not the two sync commands). The plan handles this correctly (Step 5 asserts the lock-check directly), but the design's Architecture/Expected Behavior sections don't explicitly state this intentional asymmetry. Purely cosmetic — no functional impact.

2. **`first_run_doc` is in the negative ban but not the positive `else` branch**, whereas `bug_report_template` is added to both. This is the correct and desired divergence (the bug report *is* a verification-command surface like the PR template; first-run is only drift-guarded against regression). Worth a one-line note in the design for future maintainers, but the plan is correct as written.

3. **Plan review artifacts are committed in Task 4 Step 3 but have no explicit creation task step** — `opencode-stage-125-plan-review-prompt.md` already exists and `opencode-stage-125-plan-review.md` is produced by *this* review. The code-review pair has explicit Task 3 steps. The workflow is sound; just noting the asymmetry for traceability.

## Detailed Verification

**Focus 1 — Drift addressed, ordinary CLI examples preserved:** Confirmed. The three stale forms (`uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`) at `bug_report.yml:97-99` are replaced with no-config/frozen equivalents. `uv run fashion-radar doctor` (`bug_report.yml:68,96`) and `UV_NO_CONFIG=1 uv lock --check` (`bug_report.yml:100`) are untouched. The stale ban is exact-string based — none of `uv run pytest`/`uv run ruff ...` are substrings of `uv run fashion-radar doctor`, so no false positive.

**Focus 2 — Docs tests are specific enough:** Confirmed. Two-layer guard:
- *Positive* (`tests/test_cli_docs.py:778-779`): bug_report_template joins the `else` branch, requiring all three `uv --no-config run --frozen` ruff/pytest forms present.
- *Negative* (`tests/test_cli_docs.py:801-810`): bug_report_template joins the stale ban, rejecting all three stale forms (plus the four `UV_NO_CONFIG=1 uv run ...` forms).
- *Preservation* (new Step 5 assertions): locks `uv run fashion-radar doctor` and `UV_NO_CONFIG=1 uv lock --check`.

**Focus 3 — `uv run fashion-radar doctor` and `UV_NO_CONFIG=1 uv lock --check` preserved:** Confirmed in both Task 1 Step 5 (test assertions) and Task 2 Step 1 (explicit "keep unchanged" instruction).

**Focus 4 — Scope isolation:** Confirmed. `scripts/check_release_hygiene.py` has zero references to issue templates or stale uv commands. The only `uv run pytest`/`uv run ruff` occurrences outside historical plan/review docs are the stale-ban tuples in `test_cli_docs.py:793-795`. Scope touches only YAML placeholder text, test additions, and review artifacts. No runtime/CLI/dependency/connector/scraping/platform-API/monitoring/scheduling/source-acquisition/demand-proof/ranking/coverage/compliance behavior.

**Focus 5 — Verification commands sufficient:** Confirmed. Focused docs test + ruff check/format on the test file, then full release gate (`check_release_hygiene.py`, full pytest, ruff check/format `.`, `UV_NO_CONFIG=1 uv lock --check`, `git diff --exit-code -- uv.lock`, `git diff --check`). All use `uv --no-config run --frozen` consistently.

## TDD Soundness

- RED (Task 1): Adding bug_report_template to both the positive `else` branch and the negative stale-ban loop will fail because the template currently has stale forms and lacks no-config forms.
- GREEN (Task 2): Replacing the three lines makes both layers pass simultaneously.
- Anchors verified exact against `tests/test_cli_docs.py:756,779,801-808,812-813`.

## Final Statement

**There are no Critical or Important blockers before implementation.** The design and plan are sound, precise, correctly scoped, and the test edits are anchored to the actual current code. The Stage 125 implementation may proceed.
