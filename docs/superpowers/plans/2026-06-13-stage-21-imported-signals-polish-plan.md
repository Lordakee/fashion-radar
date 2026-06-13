# Stage 21 Imported Signals Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clarify `imported-signals` table semantics and add missing validation/read-only regressions without expanding the command scope.

**Architecture:** Keep the existing `ImportedSignalsReview` model, query, JSON contract, and CLI options. Change one table-rendered label, then add focused tests around Typer validation and SQLite read-only path handling. Documentation changes are limited to the clarified table label and local-only wording.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, SQLAlchemy Core, SQLite read-only URI mode, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/imported_signals.py`: update only the table summary label in `render_imported_signals_table()`.
- Modify `tests/test_imported_signals.py`: update table renderer expectations and assert the old label is absent.
- Modify `tests/test_cli.py`: update table output expectation and add CLI validation/path tests.
- Modify `tests/test_db.py`: import `create_readonly_sqlite_engine` and add a read-only write-rejection regression for paths with URI-special characters.
- Modify user-facing docs only where they show the table summary label or describe the ambiguous count semantics.
- Modify `CHANGELOG.md`: add a Stage 21 unreleased bullet for the polish.
- Create `docs/reviews/claude-code-stage-21-code-review-prompt.md` and `docs/reviews/claude-code-stage-21-code-review.md` after implementation.

## Task 1: Table Label Semantics

**Files:**
- Modify: `src/fashion_radar/imported_signals.py`
- Modify: `tests/test_imported_signals.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing renderer expectations**

In `tests/test_imported_signals.py`, update the empty and populated renderer
expected output lines from:

```python
"Matches: 0 matched, 0 unmatched",
"Matches: 1 matched, 1 unmatched",
```

to:

```python
"Matched rows: 0 matched, 0 unmatched",
"Matched rows: 1 matched, 1 unmatched",
```

Add explicit absence checks after the list assertions:

```python
assert all(not line.startswith("Matches:") for line in render_imported_signals_table(review))
```

- [ ] **Step 2: Write failing CLI table expectation**

In `tests/test_cli.py::test_imported_signals_command_prints_table`, update:

```python
assert "Matches: 1 matched, 1 unmatched" in result.output
```

to:

```python
assert "Matched rows: 1 matched, 1 unmatched" in result.output
assert "Matches: 1 matched, 1 unmatched" not in result.output
```

- [ ] **Step 3: Run the focused failing tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py::test_render_imported_signals_table_empty tests/test_imported_signals.py::test_render_imported_signals_table_populated_sanitizes_cells tests/test_cli.py::test_imported_signals_command_prints_table -q
```

Expected: fail because production still prints `Matches:`.

- [ ] **Step 4: Implement the label change**

In `src/fashion_radar/imported_signals.py`, change:

```python
f"Matches: {review.matched_count} matched, {review.unmatched_count} unmatched",
```

to:

```python
f"Matched rows: {review.matched_count} matched, {review.unmatched_count} unmatched",
```

- [ ] **Step 5: Run the focused tests again**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py::test_render_imported_signals_table_empty tests/test_imported_signals.py::test_render_imported_signals_table_populated_sanitizes_cells tests/test_cli.py::test_imported_signals_command_prints_table -q
```

Expected: pass.

## Task 2: CLI Validation Regressions

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add a reusable no-query guard**

Near existing `imported-signals` CLI tests, add:

```python
def _fail_imported_signals_query(*args, **kwargs):
    raise AssertionError("query_imported_signals should not be called")
```

If a similar helper already exists by implementation time, reuse it instead of
adding a duplicate.

- [ ] **Step 2: Write failing test for invalid lookback days**

Add:

```python
def test_imported_signals_command_rejects_zero_lookback_days_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(cli_module, "query_imported_signals", _fail_imported_signals_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "0",
        ],
    )

    assert result.exit_code != 0
    assert "--lookback-days" in result.output
    assert "query_imported_signals should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()
```

- [ ] **Step 3: Write failing test for invalid negative limit**

Add:

```python
def test_imported_signals_command_rejects_negative_limit_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(cli_module, "query_imported_signals", _fail_imported_signals_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "--limit" in result.output
    assert "query_imported_signals should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()
```

- [ ] **Step 4: Write failing test for invalid output format**

Add:

```python
def test_imported_signals_command_rejects_invalid_format_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(cli_module, "query_imported_signals", _fail_imported_signals_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "query_imported_signals should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()
```

- [ ] **Step 5: Run the new validation tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_signals_command_rejects_zero_lookback_days_without_query or imported_signals_command_rejects_negative_limit_without_query or imported_signals_command_rejects_invalid_format_without_query"
```

Expected: pass if Typer validation already blocks command invocation. If a
test fails because the assertion expects a slightly different Typer message,
adjust only the assertion to the actual Typer output while preserving the
behavior requirements: non-zero exit, option name visible, no traceback, no
query call, and no data directory creation.

## Task 3: Read-Only Path Regressions

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `tests/test_db.py`

- [ ] **Step 1: Write CLI special-character data-dir test**

Add near the existing imported-signals JSON/table tests:

```python
def test_imported_signals_command_handles_special_character_data_dir(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path / "data ? # & %")

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["total_count"] == 2
    assert payload["row_count"] == 2
    assert payload["database"] == str(data_dir / "fashion-radar.sqlite")
```

If `_prepare_imported_signals_cli_fixture()` currently assumes it receives the
root `tmp_path` instead of a data directory, update this test to call the helper
with the existing signature and place the special characters in the appropriate
path argument. Do not change production code for this unless the test exposes a
real CLI bug.

- [ ] **Step 2: Write direct read-only engine write-rejection test**

In `tests/test_db.py`, add the import:

```python
from fashion_radar.trends import create_readonly_sqlite_engine
```

Add:

```python
def test_create_readonly_sqlite_engine_handles_uri_special_characters_and_rejects_writes(
    tmp_path,
) -> None:
    path = tmp_path / "data ? # & %" / "fashion.db"
    write_engine = create_sqlite_engine(path)
    initialize_schema(write_engine)
    write_engine.dispose()

    read_engine = create_readonly_sqlite_engine(path)
    try:
        with read_engine.connect() as connection:
            database_path = [
                row[2]
                for row in connection.execute(text("pragma database_list"))
                if row[1] == "main"
            ][0]
            version = connection.execute(text("select version from schema_metadata")).scalar_one()
            with pytest.raises(Exception, match="readonly|read-only|attempt to write"):
                connection.execute(text("create table should_fail (id integer)"))

        assert database_path == str(path)
        assert version == SCHEMA_VERSION
    finally:
        read_engine.dispose()
```

- [ ] **Step 3: Run the focused path tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py::test_imported_signals_command_handles_special_character_data_dir tests/test_db.py::test_create_readonly_sqlite_engine_handles_uri_special_characters_and_rejects_writes -q
```

Expected: pass if Stage 20 path handling is complete. If failures show a real
path bug, fix the helper in `src/fashion_radar/trends.py` or
`src/fashion_radar/db/engine.py` without changing command scope.

## Task 4: Documentation Polish

**Files:**
- Modify: `README.md` if needed
- Modify: `docs/manual-signal-import.md` if needed
- Modify: `docs/community-signal-import.md` if needed
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Find old table label references**

Run:

```bash
rg -n "Matches: [0-9]|match counts|match-count|match count" README.md docs CHANGELOG.md --glob '!docs/reviews/**'
```

Expected: references may appear in historical Stage 20 process docs and any
user docs that include table output examples.

- [ ] **Step 2: Update output examples**

In user-facing docs only, replace table-output examples:

```text
Matches: 1 matched, 2 unmatched
Matches: 0 matched, 0 unmatched
```

with:

```text
Matched rows: 1 matched, 2 unmatched
Matched rows: 0 matched, 0 unmatched
```

If prose says "match counts" for the table summary, change it to "matched-row
counts" or "counts of imported rows with or without stored matches".

Do not edit historical Stage 20 spec/plan files only to update their original
output examples. If a Stage 20 file is edited for another required reason,
keep the change narrow and document why in the final summary.

- [ ] **Step 3: Add a changelog bullet**

In `CHANGELOG.md`, under the current unreleased section, add:

```markdown
- Clarified `imported-signals` table output by labeling stored match presence
  as matched rows, and added CLI/read-only SQLite regressions.
```

- [ ] **Step 4: Run documentation boundary scan**

Run:

```bash
rg -n "platform-wide|market-wide|verified demand|real-time monitoring|source acquisition|source-acquisition|platform search|social monitoring|authorization verifier|approval workflow|audit workflow|policy workflow" README.md docs CHANGELOG.md --glob '!docs/reviews/**'
```

Expected: no new problematic wording from Stage 21. Existing deliberate scope
guard wording may appear only in process docs or boundary docs.

## Task 5: Review, Verification, And Release

**Files:**
- Create: `docs/reviews/claude-code-stage-21-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-21-code-review.md`
- Modify: any file needed to fix Critical or Important review findings

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py tests/test_cli.py tests/test_db.py -q -k "imported_signals or create_sqlite_engine_handles_uri_special_characters or readonly"
```

Expected: all selected tests pass.

- [ ] **Step 2: Run formatting and lint**

Run:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 3: Write Claude Code review prompt**

Create `docs/reviews/claude-code-stage-21-code-review-prompt.md` with:

```markdown
# Claude Code Stage 21 Code Review Prompt

You are reviewing Stage 21 for `/home/ubuntu/fashion-radar` in read-only mode.
Do not edit files. Use maximum reasoning.

## Goal

Stage 21 clarifies `imported-signals` table semantics and adds CLI/read-only
SQLite regressions without expanding scope.

## Scope Guard

Do not recommend scraping, crawling, browser automation, platform APIs, account
automation, schedulers, watch folders, source acquisition, compliance/audit
workflow features, matching/scoring changes, report generation changes,
dashboard writes, database migrations, or new dependencies.

## Review Focus

Review the diff from `fee145b` to `HEAD`.

Check:

1. Table output now says `Matched rows:` and JSON output remains unchanged.
2. CLI validation tests prove invalid `--lookback-days`, `--limit`, and
   `--format` fail before query/database access.
3. Special-character SQLite paths are covered through the full CLI path and
   direct read-only engine usage.
4. Existing databases remain read-only; no command path initializes, migrates,
   imports, matches, scores, reports, or writes artifacts.
5. Documentation wording stays local-first and does not imply platform
   coverage, source acquisition, market-wide ranking, or verified demand.
6. Tests are focused and deterministic.

Return findings by severity:

- Critical: must fix before release.
- Important: should fix before release.
- Minor: optional polish.

End with one of:

- `Approved for Stage 21 release checks`
- `Not approved`
```

- [ ] **Step 4: Request Claude Code code review**

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-21-code-review-prompt.md | tee docs/reviews/claude-code-stage-21-code-review.md
```

Expected: Claude Code returns either approval or findings. Fix every Critical
and Important finding before continuing.

- [ ] **Step 5: Run full release checks**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
uv lock --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
rm -rf /tmp/fashion-radar-dist-stage21
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage21
```

Expected: all commands pass.

- [ ] **Step 6: Run installed wheel smoke**

Run:

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv" --python 3.11
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" /tmp/fashion-radar-dist-stage21/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/fashion-radar" imported-signals --help
"$tmp_env/venv/bin/fashion-radar" imported-signals --data-dir "$tmp_env/data ? # & %" --as-of "2026-06-12T12:00:00Z" --format json
```

Expected: help commands exit zero, missing database JSON exits zero, and no
traceback is printed.

- [ ] **Step 7: Run repository hygiene scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Expected: no secrets or generated artifacts that should be committed.

- [ ] **Step 8: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/imported_signals.py tests/test_imported_signals.py tests/test_cli.py tests/test_db.py README.md docs CHANGELOG.md
git commit -m "Polish imported signals review output"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

Expected: commit succeeds and push updates `origin/main`.
