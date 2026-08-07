# ROW ONE Daily Content Acceptance Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent an unattended ROW ONE refresh from publishing an empty or
stale daily edition while preserving the existing site and generated reports on
rejection.

**Architecture:** A pure acceptance evaluator inspects only the current run's
`CollectorResult` objects and typed configuration thresholds. `row-one refresh`
calls it after collection and before matching or any report/site/cleanup work;
normal rejection exits with a dedicated diagnostic, while an explicit one-shot
flag permits intentional manual bypass.

**Tech Stack:** Python 3.11, Pydantic v2 settings models, Typer CLI, existing
collector models, pytest, Ruff, uv. No new dependency is required.

**Reviewed Plan:** Local Claude Code was invoked in read-only plan mode with
`--effort max` but produced no review output before the bounded timeout. Local
OpenCode fallback (`zhipuai-coding-plan/glm-5.2`, `max`) reviewed this plan and
approved it with revisions. The revisions are incorporated below.

---

## Parallel Work Allocation

The coordinator owns integration, CLI wiring, and final verification. Parallel
workers may begin only after Task 1's stable settings type is integrated.

| Worker | Writable scope | Expected completion |
| --- | --- | --- |
| A | `src/fashion_radar/row_one/daily_content_acceptance.py`, `tests/test_row_one_daily_content_acceptance.py` | Pure evaluator and focused tests pass. |
| B | `src/fashion_radar/settings.py`, `configs/scoring.example.yaml`, `configs/scoring.yaml`, `tests/test_config.py` | Backward-compatible settings and config tests pass. |
| C | `README.md`, `docs/row-one.md`, `docs/scheduling.md`, `docs/cli-reference.md`, `docs/scoring.md`, `tests/test_row_one_docs.py`, `tests/test_scheduling_docs.py`, `tests/test_data_retention_docs.py` | Documentation and documentation tests pass after final CLI spelling is fixed. |

The coordinator must not start the CLI integration worker until workers A and B
are reconciled, because it consumes both public interfaces. Worker C must use
the final flag spelling `--allow-unaccepted-content` and must not alter product
code. Each worker reports changed paths, focused commands, results, and any
unfinished scope before it is closed.

### Task 1: Add Backward-Compatible Acceptance Settings

**Files:**
- Modify: `src/fashion_radar/settings.py:100-147`
- Modify: `configs/scoring.example.yaml`
- Modify: `src/fashion_radar/templates/configs/scoring.example.yaml` (keep the packaged example byte-identical to the root example)
- Modify: `configs/scoring.yaml`
- Modify: `tests/test_config.py`

- [ ] **Step 1: Write failing configuration tests.**

Add tests that validate the existing minimal scoring document and assert that
the new configuration defaults are available without a YAML migration:

```python
config = load_scoring_config(path)
assert config.daily_content_acceptance.min_successful_collectors == 1
assert config.daily_content_acceptance.min_fresh_items == 1
assert config.daily_content_acceptance.max_fresh_item_age_hours == 48
```

Add parametrized invalid documents for zero and negative values. Each must raise
the project `ConfigError` through `load_scoring_config`.

- [ ] **Step 2: Run the focused tests and confirm they fail.**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_config.py
```

Expected: failures identifying the missing `daily_content_acceptance` field or
the missing validation behavior.

- [ ] **Step 3: Add the dedicated settings model.**

In `settings.py`, define a separate model before `ScoringConfig`:

```python
class DailyContentAcceptanceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_successful_collectors: int = Field(default=1, gt=0)
    min_fresh_items: int = Field(default=1, gt=0)
    max_fresh_item_age_hours: int = Field(default=48, gt=0)
```

Add it to `ScoringConfig` without changing `version: Literal[1]`:

```python
daily_content_acceptance: DailyContentAcceptanceSettings = Field(
    default_factory=DailyContentAcceptanceSettings
)
```

Do not put these values on `ScoringSettings`: they do not alter heat scoring.

- [ ] **Step 4: Document defaults in both tracked scoring examples.**

Add an explanatory `daily_content_acceptance` YAML section after
`candidate_discovery` in both tracked config files. State that the threshold is
used only by `row-one refresh`, applies to the current run, and can be bypassed
one time through the CLI flag.

- [ ] **Step 5: Re-run focused config tests.**

Run the command from Step 2. Expected: PASS.

- [ ] **Step 6: Commit the settings slice.**

```bash
git add src/fashion_radar/settings.py configs/scoring.example.yaml \
  configs/scoring.yaml tests/test_config.py
git commit -m "feat: configure ROW ONE content acceptance"
```

### Task 2: Implement the Pure Acceptance Evaluator

**Files:**
- Create: `src/fashion_radar/row_one/daily_content_acceptance.py`
- Create: `tests/test_row_one_daily_content_acceptance.py`
- Modify: `src/fashion_radar/row_one/__init__.py` only if the package's existing
  public-export pattern requires it

- [ ] **Step 1: Write failing evaluator tests.**

Use real `CollectorResult` and `CollectedItem` fixtures with fixed UTC dates.
Cover the following observable verdicts:

```python
verdict = evaluate_daily_content_acceptance(
    results=[successful_result_with_item("2026-08-07T03:00:00Z")],
    settings=DailyContentAcceptanceSettings(),
    as_of=datetime(2026, 8, 7, 4, tzinfo=UTC),
)
assert verdict.accepted is True
assert verdict.successful_collector_count == 1
assert verdict.fresh_item_count == 1
assert verdict.reasons == ()
```

Add independent tests for empty results, all failed results, skipped-only
results, a successful result with zero items, stale-only explicit dates, and a
future item date. Assert deterministic reason codes/messages and that calling
the evaluator never changes inputs.

- [ ] **Step 2: Run the new tests and confirm they fail.**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_daily_content_acceptance.py
```

Expected: collection failure because the module does not exist.

- [ ] **Step 3: Implement typed, no-I/O evaluation.**

Create a frozen verdict dataclass or Pydantic model with these fields:

```python
accepted: bool
successful_collector_count: int
fresh_item_count: int
min_successful_collectors: int
min_fresh_items: int
max_fresh_item_age_hours: int
reasons: tuple[str, ...]
```

The evaluator must:

1. Normalize `as_of` through the existing UTC utility.
2. Count only `CollectorRunStatus.SUCCESS` values as successful collectors.
3. Consider only items in successful results.
4. Treat an item as fresh only when
   `0 <= as_of - item.published_at <= timedelta(hours=max_fresh_item_age_hours)`.
5. Reject when either count is below its configured minimum.
6. Return reasons in a stable order: insufficient successful collectors before
   insufficient fresh items.
7. Never call `datetime.now`, read files, open SQLite, or make network calls.

Document that dateless collector entries have a synthesized `published_at` in
the current item model and therefore count according to that normalized value.

- [ ] **Step 4: Re-run evaluator tests.**

Run the command from Step 2. Expected: PASS.

- [ ] **Step 5: Commit the evaluator slice.**

```bash
git add src/fashion_radar/row_one/daily_content_acceptance.py \
  tests/test_row_one_daily_content_acceptance.py src/fashion_radar/row_one/__init__.py
git commit -m "feat: evaluate ROW ONE daily content acceptance"
```

Only stage `__init__.py` when it was intentionally changed.

### Task 3: Gate the Refresh Transaction Before Later Writes

**Files:**
- Modify: `src/fashion_radar/cli.py:1527-1628`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Update the shared happy-path test harness first.**

Find `_patch_successful_row_one_refresh_pipeline`. It currently returns `None`
from the collection mock. Change it to return a synthetic list containing one
successful collector result with one fresh item relative to the fixed test
`as_of`. Update `_assert_refresh_stopped_after_site_publication` to include the
acceptance evaluator between collection and matching. Preserve every existing
expected call after a healthy accepted verdict.

- [ ] **Step 2: Add rejection-path CLI tests.**

Use a preexisting marked live site and dated report files. Patch the collector
to return each bad result set. For each normal rejected invocation assert:

```python
assert result.exit_code == 1
assert "ROW ONE refresh rejected:" in result.output
assert existing_index.read_bytes() == original_index
assert old_report.read_bytes() == original_report
mock_match.assert_not_called()
mock_write_report.assert_not_called()
mock_write_site.assert_not_called()
mock_prune_reports.assert_not_called()
mock_clean_old_data.assert_not_called()
```

Cover all-failed, successful-with-zero-items, and stale-only results. Add an
override test asserting `--allow-unaccepted-content` emits a warning and allows
the ordinary mocked downstream pipeline to run.

- [ ] **Step 3: Run the focused CLI test file and confirm failure.**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_cli.py
```

Expected: new rejection tests fail and existing happy-path helper tests fail
until CLI wiring is complete.

- [ ] **Step 4: Wire the gate.**

Add a Typer boolean option:

```python
allow_unaccepted_content: bool = typer.Option(
    False,
    "--allow-unaccepted-content",
    help="Publish even when the current refresh fails daily content acceptance.",
)
```

In `row_one_refresh`, retain `collection_results` from
`collect_configured_sources`, evaluate them using
`scoring_config.daily_content_acceptance` and parsed `as_of`, and handle a
rejected verdict before `match_stored_items`:

```python
if not verdict.accepted and not allow_unaccepted_content:
    typer.echo(
        "ROW ONE refresh rejected: " + "; ".join(verdict.reasons) +
        "; existing site and generated reports were preserved.",
        err=True,
    )
    raise typer.Exit(1)
if not verdict.accepted:
    typer.echo(
        "Warning: ROW ONE refresh content acceptance bypassed: " +
        "; ".join(verdict.reasons),
        err=True,
    )
```

Use the existing datetime parser so invalid `--as-of` behavior remains
unchanged. Do not add the gate to `run`, `report`, `row-one build`, or
`row-one preview`. Do not catch the deliberate `typer.Exit(1)` in the generic
exception handler.

- [ ] **Step 5: Re-run the focused CLI tests.**

Run the command from Step 3. Expected: PASS.

- [ ] **Step 6: Commit the CLI slice.**

```bash
git add src/fashion_radar/cli.py tests/test_row_one_cli.py
git commit -m "feat: reject unaccepted ROW ONE refreshes"
```

### Task 4: Update User-Facing Operations Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/scheduling.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/scoring.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_scheduling_docs.py`
- Modify: `tests/test_data_retention_docs.py`

- [ ] **Step 1: Add failing documentation-contract assertions.**

Require the documentation to state all of the following:

```text
row-one refresh applies daily content acceptance before matching, report writing,
site publication, report pruning, and SQLite retention;
the default thresholds are one successful collector, one fresh current-run item,
and 48 hours;
failed/skipped results do not count;
rejection returns exit 1 and preserves the existing site and generated reports;
collection metadata/items are not rolled back;
--allow-unaccepted-content is a one-shot manual override and logs a warning.
```

Keep existing Stage 391 recovery and retention wording intact except where its
operation order must now say "after content acceptance succeeds." Ensure the
scheduling text says a rejected timer/cron run is intentionally visible as a
failure rather than a successful empty edition.

- [ ] **Step 2: Run documentation tests and confirm failure.**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_docs.py tests/test_scheduling_docs.py \
  tests/test_data_retention_docs.py
```

Expected: failures for absent Stage 392 documentation phrases.

- [ ] **Step 3: Update documentation and sample commands.**

Document configuration under `daily_content_acceptance`, the exact override
flag, the age semantics including synthesized dates, the preserved-output
contract, and the retained collection-write caveat. Do not advertise the flag
in normal cron or systemd commands; it is for an intentional manual run only.

- [ ] **Step 4: Re-run documentation tests.**

Run the command from Step 2. Expected: PASS.

- [ ] **Step 5: Commit the documentation slice.**

```bash
git add README.md docs/row-one.md docs/scheduling.md docs/cli-reference.md \
  docs/scoring.md tests/test_row_one_docs.py tests/test_scheduling_docs.py \
  tests/test_data_retention_docs.py
git commit -m "docs: explain ROW ONE refresh content acceptance"
```

### Task 5: Integrate, Verify, and Review

**Files:**
- Modify or create only review records under `docs/reviews/` after completed
  review output has been captured and inspected

- [ ] **Step 1: Reconcile parallel workers.**

Verify every worker's changed-file list stays within its assigned scope. Resolve
any conflicts locally. Confirm no unfinished worker has untracked or unstaged
partial writes before releasing it.

- [ ] **Step 2: Run targeted checks from the integrated tree.**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_config.py tests/test_row_one_daily_content_acceptance.py \
  tests/test_row_one_cli.py tests/test_row_one_docs.py \
  tests/test_scheduling_docs.py tests/test_data_retention_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
```

Expected: all selected tests pass and Ruff reports no violations.

- [ ] **Step 3: Run full release verification.**

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
git status --short
```

Expected: all checks pass, no mirror URL enters `uv.lock`, and only deliberate
Stage 392 changes remain.

- [ ] **Step 4: Obtain fresh code and release review.**

First retry the required Claude Code review with:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 392 ROW ONE daily content acceptance changes..."
```

If Claude Code again cannot produce a complete review, use the documented
OpenCode GLM-5.2/max fallback. Capture only the completed coherent review body
under `docs/reviews/`; never commit timeout stubs or tool-status text. Fix every
Critical and Important finding, then rerun impacted tests and review.

- [ ] **Step 5: Commit review records and final changes.**

```bash
git add docs/reviews/ src/ tests/ configs/ README.md docs/
git commit -m "feat: gate ROW ONE daily content acceptance"
```

Use the actual changed path list rather than blindly staging unrelated files.
