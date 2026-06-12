# Stage 19 Import Signals Directory Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `fashion-radar import-signals-dir` from dry-run-only diagnostics to validated local directory import for user-provided CSV/JSON manual signal files.

**Architecture:** Reuse the Stage 18 non-recursive directory matching and importer-model validation path. Add a directory load result that carries both the Stage 18 validation summary and the loaded `ManualSignalRow` objects; the CLI writes SQLite only after validation succeeds for every matched file.

**Tech Stack:** Python 3.11+, standard library `pathlib`, `fnmatch`, `collections.Counter`, and `datetime`; Typer; Pydantic v2; SQLAlchemy via existing repository helpers; pytest; ruff; uv. No new dependencies and no lockfile changes.

---

## Scope Guard

Stage 19 must not add or document:

- social/platform connectors, platform search, automated community ingestion, or
  source acquisition;
- scraping, crawler development, browser automation, Playwright, Selenium, MCP
  platform scraping servers, account automation, unofficial platform APIs, or
  export-acquisition instructions;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- recursive scanning, watch folders, schedulers, background jobs, DB migrations,
  source-health changes, collector changes, dashboard changes, report semantics
  changes, matcher behavior changes, scoring algorithm changes, persistent
  adapter tables, or network calls;
- product-facing approval, audit, policy checklist, authorization verification,
  or legal-review workflow features.

## File Structure

- Modify `src/fashion_radar/importers/manual_signals.py`: add directory load and
  import summary models, reuse non-recursive matching, and add an import summary
  table renderer.
- Modify `src/fashion_radar/cli.py`: allow `import-signals-dir` to import when
  `--dry-run` is absent, add `--data-dir` and `--imported-at`, validate
  `--imported-at` even when dry-running, and keep dry-run behavior compatible.
- Modify `tests/test_manual_signal_import.py`: cover the directory load helper
  and import summary rendering.
- Modify `tests/test_cli.py`: cover import execution, no-artifact failures, help
  text, JSON success output, and retained dry-run behavior.
- Modify docs listed in the design file.

## Task 1: Add Importer Models And Module Tests

**Files:**

- Modify: `src/fashion_radar/importers/manual_signals.py`
- Modify: `tests/test_manual_signal_import.py`

- [ ] **Step 1: Write failing tests for directory row loading**

Add tests that assert a clean directory returns both validation metadata and
loaded rows:

```python
def test_manual_signal_directory_load_returns_rows_and_validation_result(
    tmp_path: Path,
) -> None:
    (tmp_path / "b.csv").write_text(
        "url,title,published_at,source_name,platform\n"
        "https://example.com/b,Second,2026-06-12T09:00:00Z,Zulu,x\n",
        encoding="utf-8",
    )
    (tmp_path / "a.csv").write_text(
        "url,title,published_at,platform\n"
        "https://example.com/a,First,2026-06-12T08:00:00Z,instagram\n",
        encoding="utf-8",
    )

    loaded = load_manual_signal_directory_rows(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert loaded.result.ok is True
    assert loaded.result.file_count == 2
    assert loaded.result.row_count == 2
    assert [row.url for row in loaded.rows] == [
        "https://example.com/a",
        "https://example.com/b",
    ]
    assert loaded.result.source_name_counts == {"Fallback Source": 1, "Zulu": 1}
    assert loaded.result.platform_counts == {"instagram": 1, "x": 1}
```

Add a mixed-validity test:

```python
def test_manual_signal_directory_load_returns_no_rows_when_any_file_is_invalid(
    tmp_path: Path,
) -> None:
    (tmp_path / "clean.csv").write_text(
        "url,title,published_at\n"
        "https://example.com/clean,Clean,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    (tmp_path / "broken.csv").write_text(
        "url,title,published_at\n,Broken,not-a-date\n",
        encoding="utf-8",
    )

    loaded = load_manual_signal_directory_rows(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert loaded.result.ok is False
    assert loaded.rows == []
    assert loaded.result.file_count == 2
    assert loaded.result.valid_file_count == 1
    assert loaded.result.row_count == 1
    assert loaded.result.error_count == 1
```

- [ ] **Step 2: Write failing tests for import summary rendering**

Add:

```python
def test_render_manual_signal_directory_import_table() -> None:
    result = ManualSignalDirectoryImportResult(
        directory="exports",
        input_format="csv",
        pattern="*.csv",
        file_count=2,
        row_count=3,
        rows_imported=3,
        items_added=2,
        source_name_counts={"Manual Import": 1, "Tool": 2},
        platform_counts={"instagram": 2, "x": 1},
    )

    assert render_manual_signal_directory_import_table(result) == [
        "Validated 3 manual signal rows across 2 files",
        "Imported 3 manual signal rows",
        "Items added: 2",
        "Sources: Manual Import=1, Tool=2",
        "Platforms: instagram=2, x=1",
    ]
```

- [ ] **Step 3: Implement the minimal importer API**

Add `ManualSignalDirectoryLoadResult` and `ManualSignalDirectoryImportResult`:

```python
class ManualSignalDirectoryLoadResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result: ManualSignalDirectoryDryRunResult
    rows: list[ManualSignalRow] = Field(default_factory=list)


class ManualSignalDirectoryImportResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directory: str
    input_format: ManualSignalFormat
    pattern: str
    file_count: int = 0
    row_count: int = 0
    rows_imported: int = 0
    items_added: int = 0
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
```

Add `load_manual_signal_directory_rows(...)` by reusing the Stage 18 matching
logic. The function should:

- return the same `ManualSignalDirectoryDryRunResult` shape as Stage 18;
- include loaded rows only when `result.error_count == 0`;
- preserve deterministic file and row order;
- never open SQLite or create project directories.

Refactor `dry_run_manual_signal_directory(...)` to call
`load_manual_signal_directory_rows(...).result`.

Preserve the Stage 18 dry-run contract:

- `ManualSignalDirectoryDryRunResult` fields remain exactly as currently
  defined;
- no `rows` field or import summary field appears in dry-run JSON;
- `files[*]` and `findings[*]` field names and nesting remain unchanged;
- the CLI still prints dry-run JSON from
  `ManualSignalDirectoryDryRunResult.model_dump_json(indent=2)`.

- [ ] **Step 4: Add import summary renderer**

Add:

```python
def render_manual_signal_directory_import_table(
    result: ManualSignalDirectoryImportResult,
) -> list[str]:
    return [
        f"Validated {result.row_count} manual signal rows across {result.file_count} files",
        f"Imported {result.rows_imported} manual signal rows",
        f"Items added: {result.items_added}",
        f"Sources: {_format_counts(result.source_name_counts)}",
        f"Platforms: {_format_counts(result.platform_counts)}",
    ]
```

- [ ] **Step 5: Run focused module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_manual_signal_import.py -q -k "directory_load or directory_import"
```

Expected: new tests pass.

## Task 2: Add CLI Import Execution

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI help and CSV import tests**

Update `test_import_signals_dir_help_lists_options` so it expects `--data-dir`
and `--imported-at`, and no longer asserts that `--data-dir` is absent.

Add:

```python
def test_import_signals_dir_imports_csv_directory(tmp_path: Path) -> None:
    exports_dir = tmp_path / "exports"
    data_dir = tmp_path / "data"
    exports_dir.mkdir()
    (exports_dir / "b.csv").write_text(
        "url,title,published_at,source_name,platform\n"
        "https://example.com/b,Second,2026-06-12T09:00:00Z,Tool,x\n",
        encoding="utf-8",
    )
    (exports_dir / "a.csv").write_text(
        "url,title,published_at,summary\n"
        "https://example.com/a,First,2026-06-12T08:00:00Z,Signal\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(exports_dir),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Fallback Source",
            "--imported-at",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Validated 2 manual signal rows across 2 files" in result.output
    assert "Imported 2 manual signal rows" in result.output
    assert "Items added: 2" in result.output
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    repository = ItemRepository(engine)
    first = repository.get_item(1)
    second = repository.get_item(2)
    assert [first["url"], second["url"]] == [
        "https://example.com/a",
        "https://example.com/b",
    ]
    assert first["source_name"] == "Fallback Source"
    assert second["source_name"] == "Tool"
```

- [ ] **Step 2: Write failing JSON output and duplicate URL tests**

Add:

```python
def test_import_signals_dir_imports_json_directory_with_json_output(
    tmp_path: Path,
) -> None:
    exports_dir = tmp_path / "exports"
    data_dir = tmp_path / "data"
    exports_dir.mkdir()
    (exports_dir / "signals.json").write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/json",
                    "title": "JSON signal",
                    "published_at": "2026-06-12T08:00:00Z",
                    "source_name": "JSON Tool",
                    "platform": "instagram",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(exports_dir),
            "--format",
            "json",
            "--pattern",
            "*.json",
            "--data-dir",
            str(data_dir),
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "file_count",
        "row_count",
        "rows_imported",
        "items_added",
        "source_name_counts",
        "platform_counts",
    ]
    assert payload["file_count"] == 1
    assert payload["directory"] == str(exports_dir)
    assert payload["input_format"] == "json"
    assert payload["pattern"] == "*.json"
    assert payload["row_count"] == 1
    assert payload["rows_imported"] == 1
    assert payload["items_added"] == 1
    assert payload["source_name_counts"] == {"JSON Tool": 1}
    assert payload["platform_counts"] == {"instagram": 1}


def test_import_signals_dir_reports_duplicate_url_upserts(tmp_path: Path) -> None:
    exports_dir = tmp_path / "exports"
    data_dir = tmp_path / "data"
    exports_dir.mkdir()
    (exports_dir / "a.csv").write_text(
        "url,title,published_at\n"
        "https://example.com/shared,First,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    (exports_dir / "b.csv").write_text(
        "url,title,published_at\n"
        "https://example.com/shared,Second,2026-06-12T09:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(exports_dir),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Imported 2 manual signal rows" in result.output
    assert "Items added: 1" in result.output
```

- [ ] **Step 3: Write failing no-artifact error tests**

Add tests for:

- invalid `--imported-at` exits before reading files and before creating
  `--data-dir`;
- invalid `--dry-run --imported-at` exits before reading files and before
  creating `--data-dir`;
- one clean file plus one invalid file exits non-zero and creates no database;
- the mixed-validity test must make the first sorted matched file valid and a
  later sorted matched file invalid, proving the CLI validates the full batch
  before writing any row;
- no matching files exits non-zero and creates no database;
- invalid directory exits non-zero with Stage 18 diagnostics and creates no
  database;
- unreadable directory exits non-zero with Stage 18 diagnostics and creates no
  database;
- `--dry-run` still creates no database even when `--data-dir` is supplied.

Use existing `assert_no_community_lint_artifacts(...)` where it already checks
config/data/report directories. For the import command, also assert
`not (data_dir / "fashion-radar.sqlite").exists()`.

- [ ] **Step 4: Implement CLI behavior**

Update imports from `fashion_radar.importers.manual_signals` to include:

```python
ManualSignalDirectoryImportResult,
load_manual_signal_directory_rows,
render_manual_signal_directory_import_table,
```

Change `import_signals_dir_command` signature to include:

```python
data_dir: Path = DATA_DIR_OPTION,
imported_at: str | None = typer.Option(None, help="UTC import timestamp override."),
```

Behavior:

1. Normalize `source_name`.
2. If `imported_at` is present and invalid, print
   `Could not import signals directory: invalid --imported-at: {exc}` and exit
   before loading directory files. This validation also applies when
   `--dry-run` is supplied.
3. Call `load_manual_signal_directory_rows(...)`.
4. If `dry_run`, print the Stage 18 dry-run result and exit non-zero on errors.
5. If validation has errors, print the same diagnostics as dry-run and exit
   non-zero before opening SQLite.
6. If validation succeeds, initialize SQLite and call
   `store_manual_signal_rows(...)`.
7. Build `ManualSignalDirectoryImportResult` from the validation result plus
   `ManualSignalImportResult`.
8. Print table or JSON import summary.

- [ ] **Step 5: Run focused CLI tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k import_signals_dir
```

Expected: all `import_signals_dir` tests pass.

## Task 3: Update Documentation And Boundary Language

**Files:**

- Modify: `README.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update user docs**

Document:

- `import-signals-dir` supports dry-run and actual local import;
- actual import requires local files already present on disk;
- `--data-dir` and `--imported-at` are available for actual import;
- `--dry-run` remains the recommended preflight;
- validation failure imports nothing.
- `--dry-run --imported-at` validates the timestamp but writes nothing.
- installed wheel smoke checks include `import-signals-dir --help`, dry-run, and
  a tiny local directory import into a temporary `--data-dir`.

- [ ] **Step 2: Update architecture and boundaries**

State that directory import is a local importer surface and not a collector,
connector, scheduler, watcher, source acquisition system, or social platform
automation layer.

- [ ] **Step 3: Update changelog**

Add a Stage 19 entry:

```markdown
- Added validated local directory import execution for `import-signals-dir`,
  reusing Stage 18 dry-run diagnostics before any SQLite writes.
```

- [ ] **Step 4: Run docs boundary scan**

Run:

```bash
rg -n "import-signals-dir|platform-wide|market-wide|current-hotness|source acquisition|source-acquisition|platform search|social monitoring|exports|ranking|demand proof|authorization|audit|policy" README.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md CHANGELOG.md
```

Expected: hits are command examples or explicit negative boundary language.

## Task 4: Claude Code Review And Release Checks

**Files:**

- Create: `docs/reviews/claude-code-stage-19-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-19-code-review.md`

- [ ] **Step 1: Submit code review to Claude Code**

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-19-code-review-prompt.md | tee docs/reviews/claude-code-stage-19-code-review.md
```

Fix all Critical and Important findings. If fixes change code, rerun focused
tests and submit a rereview.

- [ ] **Step 2: Run release checks**

Run:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
rm -rf /tmp/fashion-radar-dist-stage19
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage19
```

Then install the wheel into a temporary virtual environment with the Tsinghua
mirror and smoke-test:

```bash
fashion-radar import-signals-dir /tmp/stage19-exports --format csv --pattern "*.csv" --data-dir /tmp/stage19-data --output-format json
```

- [ ] **Step 3: Secret and artifact scan**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Expected: no tracked secrets and no artifact output outside ignored local
environments. Remove local caches before staging.

- [ ] **Step 4: Commit and push after approval**

Only after Claude Code code review approval and release checks:

```bash
git add <stage-19-files>
git diff --cached --check
git commit -m "Add import signals directory execution"
git push origin main
```

Keep the GitHub remote URL token-free. Use a temporary `GIT_ASKPASS` only if
normal push reaches authentication and fails.
