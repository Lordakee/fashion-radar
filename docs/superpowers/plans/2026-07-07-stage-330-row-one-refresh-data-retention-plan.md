# Stage 330 ROW ONE Refresh Data Retention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add default 1-day SQLite retention to `row-one refresh`, with opt-out and reporting, so the daily ROW ONE local website workflow does not retain old collected item rows indefinitely.

**Architecture:** Reuse the existing `clean_old_data()` workflow primitive after the successful ROW ONE refresh pipeline. Keep retention orchestration in the CLI command because the existing refresh command already coordinates collect, match, report, site generation, and artifact pruning. Update docs/tests only around ROW ONE refresh behavior; keep the standalone `clean-old-data` command unchanged.

**Tech Stack:** Python Typer CLI, existing SQLite repository/workflow helpers, pytest, Ruff, `UV_NO_CONFIG=1 uv --no-config run --frozen`, Claude Code review gates.

---

## Files

- Modify: `src/fashion_radar/cli.py`
  - Add ROW ONE retention options to `row_one_refresh`.
  - Call `clean_old_data()` after stale report artifact pruning.
  - Print retention counts or skipped message.
- Modify: `tests/test_row_one_cli.py`
  - Update mocked refresh pipeline test.
  - Add skip-retention and real SQLite integration tests.
  - Update help coverage.
- Modify: `README.md`, `docs/row-one.md`, `docs/first-run.md`,
  `docs/data-retention.md`, `docs/cli-reference.md`
  - Document ROW ONE refresh retention behavior and default.
- Modify: `tests/test_row_one_docs.py`, `tests/test_data_retention_docs.py`,
  `tests/test_cli_docs.py` if needed
  - Add docs sentinels and remove stale boundary expectations.
- Create review artifacts under `docs/reviews/`.

## Task 1: CLI Refresh Retention

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_cli.py`

**Verified existing API:** `PruneResult` is defined in
`src/fashion_radar/db/repositories.py` with fields `items_deleted`,
`item_entities_deleted`, and `dry_run`. `ItemRepository.count_items()` exists
and returns `SELECT COUNT(*) FROM items`.

- [ ] **Step 1: Write failing mocked pipeline test updates**

In `test_row_one_refresh_runs_pipeline_and_writes_site`, add a monkeypatched
`clean_old_data`:

```python
def clean_old_data(**kwargs: object) -> SimpleNamespace:
    assert kwargs == {
        "data_dir": data_dir,
        "as_of": AS_OF,
        "retention_days": 1,
    }
    calls.append("clean_old_data")
    return SimpleNamespace(items_deleted=5, item_entities_deleted=7, dry_run=False)
```

Patch it:

```python
monkeypatch.setattr(cli_module, "clean_old_data", clean_old_data)
```

Update expected call order so `clean_old_data` runs after
`prune_stale_daily_report_files`:

```python
assert calls == [
    "collect_configured_sources",
    "match_stored_items",
    "write_daily_report_files",
    "_write_row_one_site_from_cli_options",
    "prune_stale_daily_report_files",
    "clean_old_data",
]
```

Add output assertion:

```python
assert "SQLite retention: pruned 5 old items and 7 item/entity matches; retention window 1 days" in result.output
```

- [ ] **Step 2: Add failing skip-retention test**

Add a local helper near the ROW ONE refresh tests:

```python
def _patch_successful_row_one_refresh_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    *,
    config_dir: Path,
    data_dir: Path,
    reports_dir: Path,
    output_dir: Path,
    calls: list[str],
) -> None:
    class StoredMatches:
        matches_stored = 4

    def collect_configured_sources(**kwargs: object) -> None:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["sources"] == []
        assert kwargs["now"] == AS_OF
        calls.append("collect_configured_sources")

    def match_stored_items(**kwargs: object) -> StoredMatches:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["entities"] == []
        calls.append("match_stored_items")
        return StoredMatches()

    def write_daily_report_files(**kwargs: object) -> tuple[Path, Path]:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["reports_dir"] == reports_dir
        assert kwargs["as_of"] == AS_OF
        calls.append("write_daily_report_files")
        return reports_dir / "daily.md", reports_dir / "daily.json"

    def prune_stale_daily_report_files(**kwargs: object) -> SimpleNamespace:
        assert kwargs["reports_dir"] == reports_dir
        assert kwargs["as_of"] == AS_OF
        calls.append("prune_stale_daily_report_files")
        return SimpleNamespace(
            current_date="2026-07-02",
            removed_count=3,
            kept_current_count=3,
        )

    def write_row_one_site_from_cli_options(**kwargs: object) -> SimpleNamespace:
        assert kwargs == {
            "config_dir": config_dir,
            "data_dir": data_dir,
            "reports_dir": reports_dir,
            "output_dir": output_dir,
            "as_of": AS_OF,
            "latest_only": True,
        }
        calls.append("_write_row_one_site_from_cli_options")
        return SimpleNamespace(
            index_path=output_dir / "index.html",
            output_dir=output_dir,
            story_count=0,
            edition=build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
            local_article_metrics=RowOneLocalArticleSiteMetrics(),
        )

    monkeypatch.setattr(cli_module, "collect_configured_sources", collect_configured_sources)
    monkeypatch.setattr(cli_module, "match_stored_items", match_stored_items)
    monkeypatch.setattr(cli_module, "write_daily_report_files", write_daily_report_files)
    monkeypatch.setattr(
        cli_module,
        "prune_stale_daily_report_files",
        prune_stale_daily_report_files,
    )
    monkeypatch.setattr(
        cli_module,
        "_write_row_one_site_from_cli_options",
        write_row_one_site_from_cli_options,
    )
```

Refactor `test_row_one_refresh_runs_pipeline_and_writes_site` to use this
helper, then add:

```python
def test_row_one_refresh_can_skip_sqlite_retention(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    calls: list[str] = []
    _patch_successful_row_one_refresh_pipeline(
        monkeypatch,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        calls=calls,
    )

    def clean_old_data(**_kwargs: object) -> object:
        raise AssertionError("clean_old_data must not run with --skip-data-retention")

    monkeypatch.setattr(cli_module, "clean_old_data", clean_old_data)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "refresh",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
            "--skip-data-retention",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "SQLite retention: skipped" in result.output
    assert "clean_old_data" not in calls
```

Add retention failure warning coverage:

```python
def test_row_one_refresh_warns_when_sqlite_retention_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    calls: list[str] = []
    _patch_successful_row_one_refresh_pipeline(
        monkeypatch,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        calls=calls,
    )

    def clean_old_data(**_kwargs: object) -> object:
        calls.append("clean_old_data")
        raise RuntimeError("database locked")

    monkeypatch.setattr(cli_module, "clean_old_data", clean_old_data)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "refresh",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
        ],
    )

    assert result.exit_code == 0, result.output
    assert "SQLite retention: failed: database locked" in result.output
    assert "ROW ONE refresh failed" not in result.output
    assert calls[-1] == "clean_old_data"
```

- [ ] **Step 3: Run CLI tests for RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "row_one_refresh"
```

Expected: fail because `row-one refresh` has no retention options/output.

- [ ] **Step 4: Implement CLI options and call**

In `src/fashion_radar/cli.py`, add a ROW ONE-specific option constant near
`RETENTION_DAYS_OPTION`:

```python
ROW_ONE_RETENTION_DAYS_OPTION = typer.Option(
    1,
    min=1,
    help="ROW ONE SQLite retention window in days after refresh.",
)
```

Extend `row_one_refresh`:

```python
retention_days: int = ROW_ONE_RETENTION_DAYS_OPTION,
skip_data_retention: bool = typer.Option(
    False,
    "--skip-data-retention",
    is_flag=True,
    help="Skip ROW ONE SQLite item retention after refresh.",
),
```

After `report_retention = prune_stale_daily_report_files(...)`, initialize:

```python
data_retention = None
data_retention_error = None
if not skip_data_retention:
    try:
        data_retention = clean_old_data(
            data_dir=data_dir,
            as_of=as_of,
            retention_days=retention_days,
        )
    except Exception as exc:
        data_retention_error = exc
```

After printing latest-only report cleanup, print:

```python
if skip_data_retention:
    typer.echo("SQLite retention: skipped")
elif data_retention_error is not None:
    typer.echo(f"SQLite retention: failed: {data_retention_error}")
else:
    typer.echo(
        "SQLite retention: "
        f"pruned {data_retention.items_deleted} old items and "
        f"{data_retention.item_entities_deleted} item/entity matches; "
        f"retention window {retention_days} days"
    )
```

- [ ] **Step 5: Run CLI tests for GREEN**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "row_one_refresh"
```

Expected: refresh CLI tests pass.

## Task 2: Real SQLite Retention Integration

**Files:**
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Write failing integration test**

Add a test that uses real SQLite but monkeypatches network/report/site-heavy
helpers:

```python
def test_row_one_refresh_prunes_old_sqlite_items_after_successful_refresh(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    repository = ItemRepository(engine)
    old_id = repository.upsert_item(
        CollectedItem(
            source_name="Old Source",
            source_type=SourceType.RSS,
            url="https://example.com/old",
            title="Old signal",
            published_at="2026-07-01T00:00:00Z",
            summary="old",
        ),
        collected_at=parse_datetime_utc("2026-07-01T00:00:00Z"),
    )
    repository.replace_item_matches(
        old_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    repository.upsert_item(
        CollectedItem(
            source_name="Current Source",
            source_type=SourceType.RSS,
            url="https://example.com/current",
            title="Current signal",
            published_at=AS_OF,
            summary="current",
        ),
        collected_at=parse_datetime_utc(AS_OF),
    )

    calls: list[str] = []
    _patch_successful_row_one_refresh_pipeline(
        monkeypatch,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        calls=calls,
    )
    # Do not patch clean_old_data; this test verifies the real SQLite retention path.

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "refresh",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
            "--retention-days",
            "1",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "SQLite retention: pruned 1 old items and 1 item/entity matches" in result.output
    assert repository.count_items() == 1
```

- [ ] **Step 2: Run integration test for RED or GREEN depending on Task 1**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "prunes_old_sqlite"
```

Expected before Task 1 implementation: fail. Expected after Task 1: pass.

- [ ] **Step 3: Add help assertions**

Update `test_row_one_refresh_help_is_discoverable`:

```python
assert "--retention-days" in result.output
assert "--skip-data-retention" in result.output
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "row_one_refresh"
```

## Task 3: Docs And Sentinels

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/first-run.md`
- Modify: `docs/data-retention.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_data_retention_docs.py`

- [ ] **Step 1: Write failing docs tests**

Add docs assertions:

```python
def test_row_one_docs_describe_refresh_sqlite_retention() -> None:
    docs = "\n".join(_normalized(_read(path)) for path in (README, ROW_ONE_DOC, FIRST_RUN_DOC))
    for phrase in (
        "row-one refresh",
        "sqlite retention",
        "default 1-day retention",
        "`--retention-days`",
        "`--skip-data-retention`",
        "after the current site and reports are generated",
        "scoring window",
        "heat scores",
        "does not prune `collector_runs`",
        "does not prune `source_health`",
        "does not prune `entity_first_seen`",
    ):
        assert phrase in docs

    cli_reference = _normalized(_read(CLI_REFERENCE))
    for phrase in (
        "`row-one refresh`",
        "`--retention-days`",
        "`--skip-data-retention`",
        "sqlite retention",
    ):
        assert phrase in cli_reference
```

Update data-retention docs test so it distinguishes:

- `clean-old-data` remains standalone/manual.
- `row-one refresh` now runs default SQLite item retention for ROW ONE.

- [ ] **Step 2: Run docs tests for RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_data_retention_docs.py -q
```

- [ ] **Step 3: Update docs**

Update docs to say:

- `row-one refresh` includes default 1-day SQLite item retention after
  successful site/report generation.
- Use `--retention-days N` for a longer local window.
- Use `--skip-data-retention` to opt out.
- `clean-old-data` remains the standalone/manual cleanup command.
- `collector_runs`, `source_health`, `entity_first_seen`, config files, and
  generated site files are not pruned by this SQLite retention path.
- `docs/cli-reference.md` should add a `row-one refresh` entry if one is not
  already present, including `--retention-days` and `--skip-data-retention`.

- [ ] **Step 4: Run docs tests for GREEN**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_data_retention_docs.py -q
```

## Task 4: Review, Verification, Commit

**Files:**
- Add: `docs/reviews/claude-code-stage-330-code-review-prompt.md`
- Add review/rereview outputs as needed.

- [ ] **Step 1: Focused verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_data_retention_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/cli.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_data_retention_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/cli.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_data_retention_docs.py
```

- [ ] **Step 2: Claude Code review**

Create `docs/reviews/claude-code-stage-330-code-review-prompt.md` and run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-330-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-330-code-review.md
rm -f "$tmp_review"
```

Fix Critical/Important findings and rereview if needed.

- [ ] **Step 3: Full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
git diff --check
if git grep -n -E 'ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' -- . ':!docs/reviews/*'; then exit 1; else exit 0; fi
```

- [ ] **Step 4: Commit and push**

```bash
git add README.md docs/row-one.md docs/first-run.md docs/data-retention.md docs/cli-reference.md docs/scheduling.md docs/superpowers/specs/2026-07-07-stage-330-row-one-refresh-data-retention-design.md docs/superpowers/plans/2026-07-07-stage-330-row-one-refresh-data-retention-plan.md docs/reviews scripts/check_first_run_smoke.py scripts/check_release_hygiene.py src/fashion_radar/cli.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_data_retention_docs.py tests/test_first_run_smoke.py tests/test_release_hygiene.py tests/test_scheduling_docs.py
git diff --cached --name-only
git commit -m "Stage 330: add row one refresh data retention"
git push origin main
```
