# Stage 18 Import Signals Directory Dry Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar import-signals-dir`, a local read-only directory dry-run command for batches of user-provided community signal CSV/JSON handoff files.

**Architecture:** Extend the existing manual signal importer with a directory-level dry-run wrapper that reuses `load_manual_signal_rows()` for every matched file. Add a thin Typer command that prints aggregate table/JSON diagnostics and exits non-zero on errors, while never opening SQLite, importing rows, creating project directories, or running collectors.

**Tech Stack:** Python 3.11+, standard library `pathlib`, `fnmatch`, and `collections.Counter`, Typer, Pydantic v2, existing manual signal importer, pytest, ruff, uv, Markdown docs. No new dependencies and no lockfile changes.

---

## Scope Guard

Stage 18 must not add or document:

- social/platform connectors, platform search, automated community ingestion, or
  source acquisition;
- scraping, crawler development, browser automation, Playwright, Selenium, MCP
  platform scraping servers, account automation, unofficial platform APIs, or
  export-acquisition instructions;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- recursive scanning, watch folders, schedulers, background jobs, multi-file
  import, SQLite writes, DB migrations, source-health changes, collector
  changes, dashboard changes, report semantics changes, matcher behavior
  changes, scoring algorithm changes, persistent adapter tables, or network
  calls;
- product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, authorization verification, or legal review feature.

## File Structure

- Modify `src/fashion_radar/importers/manual_signals.py`: add directory dry-run
  result models, non-recursive path enumeration, aggregate counts, and table
  rendering.
- Modify `src/fashion_radar/cli.py`: add `import-signals-dir` command
  near the community signal lint commands.
- Modify `tests/test_manual_signal_import.py`: add focused module tests for
  directory dry-run aggregation and errors.
- Modify `tests/test_cli.py`: add CLI tests for help/output/exit/no-artifact
  behavior.
- Modify docs listed in the design.

## Task 1: Add Focused Failing Directory Dry-Run Tests

**Files:**

- Modify: `tests/test_manual_signal_import.py`

- [ ] **Step 1: Add imports**

Add `inspect` to the test imports:

```python
import inspect
```

Update the import from `fashion_radar.importers.manual_signals`:

```python
from fashion_radar.importers.manual_signals import (
    ManualSignalImportError,
    dry_run_manual_signal_directory,
    load_manual_signal_rows,
    render_manual_signal_directory_dry_run_table,
    store_manual_signal_rows,
)
```

- [ ] **Step 2: Add sorted aggregation test**

Append:

```python
def test_manual_signal_directory_dry_run_aggregates_files_in_sorted_order(
    tmp_path: Path,
) -> None:
    (tmp_path / "b.csv").write_text(
        "url,title,published_at,source_name,platform\n"
        "https://example.com/b,Second,2026-06-12T09:00:00Z,Zulu,forum\n",
        encoding="utf-8",
    )
    (tmp_path / "a.csv").write_text(
        "url,title,published_at,platform\n"
        "https://example.com/a,First,2026-06-12T08:00:00Z,community\n",
        encoding="utf-8",
    )

    result = dry_run_manual_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert result.ok is True
    assert result.file_count == 2
    assert result.valid_file_count == 2
    assert result.row_count == 2
    assert result.error_count == 0
    assert [Path(file.path).name for file in result.files] == ["a.csv", "b.csv"]
    assert result.source_name_counts == {"Fallback Source": 1, "Zulu": 1}
    assert list(result.source_name_counts) == ["Fallback Source", "Zulu"]
    assert result.platform_counts == {"community": 1, "forum": 1}
    assert list(result.platform_counts) == ["community", "forum"]
```

- [ ] **Step 3: Add mixed clean/invalid file and directory error tests**

Append:

```python
def test_manual_signal_directory_dry_run_keeps_clean_and_invalid_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "clean.csv").write_text(
        "url,title,published_at,source_name\n"
        "https://example.com/clean,Clean,2026-06-12T08:00:00Z,Tool\n",
        encoding="utf-8",
    )
    (tmp_path / "broken.csv").write_text(
        "url,title,published_at\n,Missing,not-a-date\n",
        encoding="utf-8",
    )

    result = dry_run_manual_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert result.ok is False
    assert result.file_count == 2
    assert result.valid_file_count == 1
    assert result.row_count == 1
    assert result.error_count == 1
    assert {Path(file.path).name for file in result.files} == {
        "broken.csv",
        "clean.csv",
    }
    broken = next(file for file in result.files if Path(file.path).name == "broken.csv")
    assert broken.error_count == 1
    assert broken.findings[0].code == "invalid_file"
    assert "row 2" in broken.findings[0].message


def test_manual_signal_directory_dry_run_reports_missing_directory(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    result = dry_run_manual_signal_directory(
        missing,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"
    assert result.findings[0].message == (
        "Manual signal directory does not exist or is not a directory."
    )


def test_manual_signal_directory_dry_run_reports_file_path_as_invalid_directory(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text("url,title,published_at\n", encoding="utf-8")

    result = dry_run_manual_signal_directory(
        path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"


def test_manual_signal_directory_dry_run_reports_unreadable_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    original_iterdir = Path.iterdir

    def fail_iterdir(path: Path):
        if path == tmp_path:
            raise PermissionError("no access")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_iterdir)

    result = dry_run_manual_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"
    assert result.findings[0].message == "Could not read manual signal directory."
```

- [ ] **Step 4: Add no-match, non-recursive, and renderer tests**

Append:

```python
def test_manual_signal_directory_dry_run_reports_no_matching_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "ignored.txt").write_text("ignore", encoding="utf-8")

    result = dry_run_manual_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "no_matching_files"


def test_manual_signal_directory_dry_run_is_non_recursive(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "nested.csv").write_text(
        "url,title,published_at\n"
        "https://example.com/nested,Nested,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    (tmp_path / "top.csv").write_text(
        "url,title,published_at\n"
        "https://example.com/top,Top,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = dry_run_manual_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )

    assert result.file_count == 1
    assert Path(result.files[0].path).name == "top.csv"


def test_manual_signal_directory_dry_run_double_star_pattern_does_not_recurse(
    tmp_path: Path,
) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "nested.csv").write_text(
        "url,title,published_at\n"
        "https://example.com/nested,Nested,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = dry_run_manual_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="**/*.csv",
        default_source_name="Fallback Source",
    )

    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "no_matching_files"


def test_render_manual_signal_directory_dry_run_table_includes_summary_and_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "signals.csv").write_text(
        "url,title,published_at\n"
        "https://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    lines = render_manual_signal_directory_dry_run_table(
        dry_run_manual_signal_directory(
            tmp_path,
            input_format="csv",
            pattern="*.csv",
            default_source_name="Fallback Source",
        )
    )

    assert lines[0] == f"Import signals directory dry run: {tmp_path}"
    assert "Input format: csv" in lines
    assert "Pattern: *.csv" in lines
    assert "Files: 1 total, 1 valid" in lines
    assert "Rows: 1 import-ready" in lines
    assert any(line.startswith(f"- {tmp_path / 'signals.csv'}:") for line in lines)
    assert "No manual signal directory dry-run errors." in lines


def test_manual_signal_directory_dry_run_does_not_use_path_glob() -> None:
    source = inspect.getsource(dry_run_manual_signal_directory)

    assert ".glob(" not in source
    assert ".rglob(" not in source
```

- [ ] **Step 5: Verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_manual_signal_import.py -q -k "directory_dry_run"
```

Expected: FAIL because `dry_run_manual_signal_directory` and
`render_manual_signal_directory_dry_run_table` do not exist.

## Task 2: Implement Directory Dry-Run Module API

**Files:**

- Modify: `src/fashion_radar/importers/manual_signals.py`
- Test: `tests/test_manual_signal_import.py`

- [ ] **Step 1: Add imports and result models**

Add `import fnmatch`, `Counter`, and `Iterable`:

```python
import fnmatch
from collections import Counter
from collections.abc import Iterable
```

Add these models after `ManualSignalImportResult`:

```python
class ManualSignalDryRunFindingSeverity(StrEnum):
    ERROR = "error"


class ManualSignalDirectoryDryRunFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: ManualSignalDryRunFindingSeverity
    code: str
    message: str
    path: str | None = None


class ManualSignalDirectoryDryRunFileResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    row_count: int = 0
    error_count: int = 0
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    findings: list[ManualSignalDirectoryDryRunFinding] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.error_count == 0


class ManualSignalDirectoryDryRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directory: str
    input_format: ManualSignalFormat
    pattern: str
    file_count: int = 0
    valid_file_count: int = 0
    row_count: int = 0
    error_count: int = 0
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    files: list[ManualSignalDirectoryDryRunFileResult] = Field(default_factory=list)
    findings: list[ManualSignalDirectoryDryRunFinding] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.error_count == 0
```

Also import `StrEnum` from `enum`.

Stable directory-level messages must be exactly:

| Code | Condition | Message |
| --- | --- | --- |
| `invalid_directory` | supplied path is missing or not a directory | `Manual signal directory does not exist or is not a directory.` |
| `invalid_directory` | directory existence check or direct-child enumeration raises `OSError` | `Could not read manual signal directory.` |
| `no_matching_files` | no regular direct-child files match `--pattern` | `No regular files matched the pattern in the directory.` |

- [ ] **Step 2: Add directory dry-run implementation**

Add:

```python
def dry_run_manual_signal_directory(
    directory: Path,
    *,
    input_format: ManualSignalFormat,
    pattern: str,
    default_source_name: str,
) -> ManualSignalDirectoryDryRunResult:
    findings: list[ManualSignalDirectoryDryRunFinding] = []
    try:
        if not directory.is_dir():
            return ManualSignalDirectoryDryRunResult(
                directory=str(directory),
                input_format=input_format,
                pattern=pattern,
                error_count=1,
                findings=[
                    ManualSignalDirectoryDryRunFinding(
                        severity=ManualSignalDryRunFindingSeverity.ERROR,
                        code="invalid_directory",
                        message="Manual signal directory does not exist or is not a directory.",
                    )
                ],
            )
        children = list(directory.iterdir())
    except OSError:
        return ManualSignalDirectoryDryRunResult(
            directory=str(directory),
            input_format=input_format,
            pattern=pattern,
            error_count=1,
            findings=[
                ManualSignalDirectoryDryRunFinding(
                    severity=ManualSignalDryRunFindingSeverity.ERROR,
                    code="invalid_directory",
                    message="Could not read manual signal directory.",
                )
            ],
        )

    paths: list[Path] = []
    for path in children:
        try:
            is_regular_file = path.is_file()
        except OSError:
            continue
        if is_regular_file and fnmatch.fnmatch(path.name, pattern):
            paths.append(path)
    paths = sorted(paths, key=lambda path: str(path))

    if not paths:
        findings.append(
            ManualSignalDirectoryDryRunFinding(
                severity=ManualSignalDryRunFindingSeverity.ERROR,
                code="no_matching_files",
                message="No regular files matched the pattern in the directory.",
            )
        )

    file_results = [
        _dry_run_manual_signal_file(
            path,
            input_format=input_format,
            default_source_name=default_source_name,
        )
        for path in paths
    ]
    return ManualSignalDirectoryDryRunResult(
        directory=str(directory),
        input_format=input_format,
        pattern=pattern,
        file_count=len(file_results),
        valid_file_count=sum(1 for file in file_results if file.ok),
        row_count=sum(file.row_count for file in file_results),
        error_count=len(findings) + sum(file.error_count for file in file_results),
        source_name_counts=_merge_count_dicts(
            file.source_name_counts for file in file_results
        ),
        platform_counts=_merge_count_dicts(file.platform_counts for file in file_results),
        files=file_results,
        findings=findings,
    )
```

Add helpers:

```python
def _dry_run_manual_signal_file(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    default_source_name: str,
) -> ManualSignalDirectoryDryRunFileResult:
    try:
        rows = load_manual_signal_rows(
            path,
            input_format=input_format,
            default_source_name=default_source_name,
        )
    except ManualSignalImportError as exc:
        return ManualSignalDirectoryDryRunFileResult(
            path=str(path),
            error_count=1,
            findings=[
                ManualSignalDirectoryDryRunFinding(
                    severity=ManualSignalDryRunFindingSeverity.ERROR,
                    code="invalid_file",
                    message=f"Could not dry-run import file: {exc}",
                    path=str(path),
                )
            ],
        )

    return ManualSignalDirectoryDryRunFileResult(
        path=str(path),
        row_count=len(rows),
        source_name_counts=dict(sorted(Counter(row.source_name for row in rows).items())),
        platform_counts=dict(sorted(Counter(row.platform for row in rows if row.platform).items())),
    )


def _merge_count_dicts(counts: Iterable[dict[str, int]]) -> dict[str, int]:
    merged: Counter[str] = Counter()
    for count_map in counts:
        merged.update(count_map)
    return dict(sorted(merged.items()))
```

- [ ] **Step 3: Add table renderer**

Add:

```python
def render_manual_signal_directory_dry_run_table(
    result: ManualSignalDirectoryDryRunResult,
) -> list[str]:
    lines = [
        f"Import signals directory dry run: {result.directory}",
        f"Input format: {result.input_format}",
        f"Pattern: {result.pattern}",
        f"Files: {result.file_count} total, {result.valid_file_count} valid",
        f"Rows: {result.row_count} import-ready",
        f"Sources: {_format_counts(result.source_name_counts)}",
        f"Platforms: {_format_counts(result.platform_counts)}",
        f"Errors: {result.error_count}",
    ]
    if result.files:
        lines.append("Files:")
        for file in result.files:
            lines.append(f"- {file.path}: {file.row_count} rows, {file.error_count} errors")
    if not result.findings and all(not file.findings for file in result.files):
        lines.append("No manual signal directory dry-run errors.")
        return lines

    lines.append("Severity | File | Code | Message")
    for finding in result.findings:
        lines.append(
            f"{finding.severity.value} | {finding.path or 'n/a'} | "
            f"{finding.code} | {finding.message}"
        )
    for file in result.files:
        for finding in file.findings:
            lines.append(
                f"{finding.severity.value} | {file.path} | "
                f"{finding.code} | {finding.message}"
            )
    return lines
```

Add `_format_counts(counts: dict[str, int]) -> str` if no existing helper is
available in this module:

```python
def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
```

- [ ] **Step 4: Verify module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_manual_signal_import.py -q -k "directory_dry_run"
```

Expected: PASS after implementation corrections.

## Task 3: Add CLI Command And CLI Tests

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Append near existing `community_signal_lint_dir` tests:

```python
def test_import_signals_dir_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["import-signals-dir", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--pattern" in result.output
    assert "--dry-run" in result.output
    assert "--output-format" in result.output
    assert "--source-name" in result.output
    assert "--data-dir" not in result.output
    assert "without importing rows" in result.output


def test_import_signals_dir_prints_table(tmp_path: Path) -> None:
    (tmp_path / "signals.csv").write_text(
        "url,title,published_at,source_name,platform\n"
        "https://example.com/a,Signal,2026-06-12T08:00:00Z,Tool,community\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert f"Import signals directory dry run: {tmp_path}" in result.output
    assert "Files: 1 total, 1 valid" in result.output
    assert "Rows: 1 import-ready" in result.output


def test_import_signals_dir_prints_json(tmp_path: Path) -> None:
    (tmp_path / "signals.json").write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/a",
                    "title": "Signal",
                    "published_at": "2026-06-12T08:00:00Z",
                    "source_name": "Tool",
                    "platform": "community",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "json",
            "--pattern",
            "*.json",
            "--dry-run",
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
        "valid_file_count",
        "row_count",
        "error_count",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["file_count"] == 1
    assert payload["valid_file_count"] == 1
    assert payload["row_count"] == 1
    assert payload["error_count"] == 0
    assert payload["source_name_counts"] == {"Tool": 1}
    assert payload["platform_counts"] == {"community": 1}
    assert payload["files"][0]["findings"] == []
```

Append failure/no-artifact tests:

```python
def test_import_signals_dir_json_failure_shape(tmp_path: Path) -> None:
    (tmp_path / "broken.csv").write_text(
        "url,title,published_at\n,Broken,not-a-date\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert payload["file_count"] == 1
    assert payload["valid_file_count"] == 0
    assert payload["row_count"] == 0
    assert payload["error_count"] == 1
    assert payload["findings"] == []
    assert payload["files"][0]["error_count"] == 1
    assert payload["files"][0]["findings"][0]["severity"] == "error"
    assert payload["files"][0]["findings"][0]["code"] == "invalid_file"
    assert "row 2" in payload["files"][0]["findings"][0]["message"]


def test_import_signals_dir_invalid_directory_exits_nonzero(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(missing),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output


def test_import_signals_dir_json_no_matching_files_shape(tmp_path: Path) -> None:
    (tmp_path / "ignored.txt").write_text("ignore", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "file_count",
        "valid_file_count",
        "row_count",
        "error_count",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["directory"] == str(tmp_path)
    assert payload["input_format"] == "csv"
    assert payload["pattern"] == "*.csv"
    assert payload["file_count"] == 0
    assert payload["valid_file_count"] == 0
    assert payload["row_count"] == 0
    assert payload["error_count"] == 1
    assert payload["source_name_counts"] == {}
    assert payload["platform_counts"] == {}
    assert payload["files"] == []
    assert payload["findings"] == [
        {
            "severity": "error",
            "code": "no_matching_files",
            "message": "No regular files matched the pattern in the directory.",
            "path": None,
        }
    ]


def test_import_signals_dir_unreadable_directory_exits_nonzero_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    original_iterdir = Path.iterdir

    def fail_iterdir(path: Path):
        if path == tmp_path:
            raise PermissionError("no access")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_iterdir)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output
    monkeypatch.setattr(Path, "iterdir", original_iterdir)
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_does_not_create_project_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "signals.csv").write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_requires_dry_run_before_reading_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing = tmp_path / "missing"
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(missing),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "Directory import is not implemented; rerun with --dry-run." in result.output
    assert "invalid_directory" not in result.output
    assert "Traceback" not in result.output
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )
```

- [ ] **Step 2: Verify CLI RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k import_signals_dir
```

Expected: FAIL because `import-signals-dir` is not registered.

- [ ] **Step 3: Implement CLI command**

Update imports:

```python
from fashion_radar.importers.manual_signals import (
    ManualSignalImportError,
    dry_run_manual_signal_directory,
    load_manual_signal_rows,
    render_manual_signal_directory_dry_run_table,
    store_manual_signal_rows,
)
```

Add output type and option near community signal lint output format:

```python
ImportSignalsDirOutputFormat = Literal["table", "json"]
IMPORT_SIGNALS_DIR_OUTPUT_FORMAT_OPTION = typer.Option(
    "table",
    "--output-format",
    help="Output format.",
)
MANUAL_SIGNAL_PATTERN_OPTION = typer.Option(
    ...,
    "--pattern",
    help="Non-recursive file glob pattern, for example *.csv or *.json.",
)
```

Add command near `community-signal-lint-dir`:

```python
@app.command(name="import-signals-dir")
def import_signals_dir_command(
    directory: Path,
    input_format: ManualSignalInputFormat = MANUAL_SIGNAL_FORMAT_OPTION,
    pattern: str = MANUAL_SIGNAL_PATTERN_OPTION,
    dry_run: bool = typer.Option(False, help="Validate without importing rows."),
    output_format: ImportSignalsDirOutputFormat = IMPORT_SIGNALS_DIR_OUTPUT_FORMAT_OPTION,
    source_name: str = typer.Option("Manual Import", help="Fallback source name."),
) -> None:
    """Dry-run local manual signal files in one directory without importing rows."""
    if not dry_run:
        typer.echo("Directory import is not implemented; rerun with --dry-run.", err=True)
        raise typer.Exit(1)

    result = dry_run_manual_signal_directory(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_name,
    )
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_manual_signal_directory_dry_run_table(result):
            typer.echo(line)

    if result.error_count:
        raise typer.Exit(1)
```

- [ ] **Step 4: Verify CLI tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k import_signals_dir
```

Expected: PASS.

## Task 4: Documentation Updates

**Files:**

- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update docs**

Add examples:

```bash
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --dry-run
uv run fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --dry-run --output-format json
```

Docs must state:

- reads matched regular files directly under one local directory;
- non-recursive;
- no row import;
- no SQLite;
- no config/data/report directory creation;
- no URL fetching, source collection, platform tooling, platform coverage check,
  authorization verification, or policy workflow feature;
- use `community-signal-lint-dir` first for strict handoff quality, then
  `import-signals-dir` for importer-level dry-run across files.

- [ ] **Step 2: Run docs boundary scan**

Run:

```bash
rg -n "import-signals-dir|platform-wide|market-wide|current-hotness|source acquisition|source-acquisition|platform search|social monitoring|exports|ranking|demand proof|compliance|audit|authorization" README.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md CHANGELOG.md
```

Expected: risky terms appear only in command examples or explicit
boundary/negative contexts.

## Task 5: Verification And Claude Code Review

**Files:**

- Create: `docs/reviews/claude-code-stage-18-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-18-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_manual_signal_import.py tests/test_cli.py -q -k "directory_dry_run or import_signals_dir"
```

Expected: PASS.

- [ ] **Step 2: Run full verification**

Run:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
codegraph status
```

Expected: PASS; CodeGraph index responds.

- [ ] **Step 3: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-18-code-review-prompt.md` asking Claude
Code to review Stage 18 in read-only plan mode with `--effort max`. Focus on:

- read-only directory dry-run behavior;
- non-recursive matching;
- stable directory-level errors;
- aggregate counts and JSON shape;
- CLI exit behavior;
- no-artifact tests;
- docs boundaries and out-of-scope exclusions.

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-18-code-review-prompt.md | tee docs/reviews/claude-code-stage-18-code-review.md
```

Expected: fix Critical and Important findings before upload.

## Post-Acceptance Release And Upload

This section is an operator/maintainer checklist after implementation and
Claude Code code review approval. It is not part of the Stage 18 product
implementation tasks above, and it must not be run until all Critical and
Important review findings are fixed.

Run these only after full local verification passes, Claude Code approves the
Stage 18 code review, and any Critical or Important review findings are fixed.

- [ ] **Step 1: Release checks**

Run:

```bash
uv lock --check --default-index https://pypi.org/simple
uv sync --locked --dev --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage18
```

Then run installed-wheel smoke for
`fashion-radar import-signals-dir --help` and one JSON run from a temp
venv, using the Tsinghua mirror for install.

- [ ] **Step 2: Secret and generated-artifact scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

The secret scan must return no matches. Generated artifacts should be deleted
before commit.

- [ ] **Step 3: Commit and push after review gates pass**

Commit:

```bash
git add src/fashion_radar/importers/manual_signals.py src/fashion_radar/cli.py tests/test_manual_signal_import.py tests/test_cli.py docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md README.md docs/architecture.md docs/source-boundaries.md CHANGELOG.md docs/superpowers/specs/2026-06-12-stage-18-import-signals-directory-dry-run-design.md docs/superpowers/plans/2026-06-12-stage-18-import-signals-directory-dry-run-plan.md docs/reviews/claude-code-stage-18-*.md
git commit -m "Add import signals directory dry run"
```

Push with temporary `GIT_ASKPASS` only if needed. Keep the remote URL token-free
and remove any askpass file immediately after the push.

## Plan Self-Review

- Spec coverage: module, CLI, tests, docs, review, verification, and upload
  tasks cover every Stage 18 requirement.
- Placeholder scan: no task depends on an undefined future decision.
- Type consistency: public names are consistently
  `dry_run_manual_signal_directory` and
  `render_manual_signal_directory_dry_run_table`.
- Boundary check: no task adds collectors, platform tooling, scraping, source
  acquisition, database writes, import side effects, matcher changes, scoring
  changes, dashboard changes, recursive scanning, watch folders, or
  product-facing policy workflow features.
