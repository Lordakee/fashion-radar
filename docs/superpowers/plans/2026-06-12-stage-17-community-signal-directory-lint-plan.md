# Stage 17 Community Signal Directory Lint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar community-signal-lint-dir`, a pure local diagnostics command for batches of community signal CSV/JSON handoff files in one directory.

**Architecture:** Extend `community_signals.py` with a directory-level batch result that wraps existing `lint_community_signal_file()` results instead of reimplementing row validation. Add a thin Typer command with explicit `--input-format`, `--pattern`, `--format`, `--source-name`, and `--strict`; keep the command read-only with no config/data/report directory options and no SQLite, import, collection, matching, scoring, report, dashboard, digest, network, or platform-tool side effects.

**Tech Stack:** Python 3.11+, standard library `pathlib` and `fnmatch`, Typer, Pydantic v2, existing community signal linter, pytest, ruff, uv, Markdown docs. No new dependencies and no lockfile changes.

---

## Scope Guard

Stage 17 must not add or document:

- social/platform connectors, platform search, automated community ingestion, or
  source acquisition;
- scraping, crawler development, browser automation, Playwright, Selenium, MCP
  platform scraping servers, account automation, unofficial platform APIs, or
  export-acquisition instructions;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- recursive scanning, watch folders, schedulers, background jobs, multi-file
  import, or multi-file dry-run;
- current-hotness claims, platform-wide claims, social-wide claims,
  community-wide claims, market-wide trend proof, verified demand outside
  configured local signals, real-time monitoring, or top social trend rankings;
- raw comment/body storage, author handles, account IDs, follower lists, profile
  URLs, image/video URLs, media downloading, reposting, or archive
  redistribution;
- Google News RSS or any new source type;
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, matcher behavior changes, scoring algorithm changes,
  persistent adapter tables, or network calls;
- product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, authorization verification, or legal review feature.

## File Structure

- Modify `src/fashion_radar/community_signals.py`: add directory lint result
  model, directory-level findings, non-recursive path enumeration, aggregate
  counts, and directory table rendering.
- Modify `src/fashion_radar/cli.py`: add `community-signal-lint-dir` command near
  `community-signal-lint`.
- Modify `tests/test_community_signal_lint.py`: add focused unit tests for
  directory aggregation.
- Modify `tests/test_cli.py`: add CLI tests for help/output/exit/no-artifact
  behavior.
- Modify docs listed in the design.

## Task 1: Add Focused Failing Directory Lint Tests

**Files:**
- Modify: `tests/test_community_signal_lint.py`

- [ ] **Step 1: Add imports**

Update the import from `fashion_radar.community_signals`:

```python
from fashion_radar.community_signals import (
    CommunitySignalFindingSeverity,
    lint_community_signal_directory,
    lint_community_signal_file,
    render_community_signal_directory_lint_table,
    render_community_signal_lint_table,
)
```

- [ ] **Step 2: Add deterministic aggregation tests**

Append:

```python
def test_directory_lint_aggregates_matched_files_in_sorted_order(
    tmp_path: Path,
) -> None:
    write_text(
        tmp_path / "b.csv",
        """
        url,title,published_at,source_name,platform,summary,source_weight
        https://example.com/b,Second,2026-06-12T09:00:00Z,Zulu,forum,Note,1.1
        """,
    )
    write_text(
        tmp_path / "a.csv",
        """
        url,title,published_at,source_name,platform,summary
        https://example.com/a,First,2026-06-12T08:00:00Z,Alpha,community,Note
        """,
    )

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is True
    assert result.file_count == 2
    assert result.row_count == 2
    assert result.valid_row_count == 2
    assert [Path(file.path).name for file in result.files] == ["a.csv", "b.csv"]
    assert result.source_name_counts == {"Alpha": 1, "Zulu": 1}
    assert list(result.source_name_counts) == ["Alpha", "Zulu"]
    assert result.platform_counts == {"community": 1, "forum": 1}
    assert list(result.platform_counts) == ["community", "forum"]
    assert list(result.field_counts) == sorted(result.field_counts)
    assert result.field_counts["source_weight"] == 1
```

- [ ] **Step 3: Add invalid file and no-match tests**

Append:

```python
def test_directory_lint_keeps_clean_and_invalid_file_results(
    tmp_path: Path,
) -> None:
    write_text(
        tmp_path / "clean.csv",
        """
        url,title,published_at,source_name,platform,summary
        https://example.com/clean,Clean,2026-06-12T08:00:00Z,Tool,community,Note
        """,
    )
    write_text(tmp_path / "broken.csv", "url,title,published_at\n,Missing,not-a-date")

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 2
    assert result.row_count == 2
    assert result.valid_row_count == 1
    assert result.error_count == 1
    assert {Path(file.path).name for file in result.files} == {"clean.csv", "broken.csv"}


def test_directory_lint_reports_no_matching_files(tmp_path: Path) -> None:
    write_text(tmp_path / "ignored.txt", "not a signal file")

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "no_matching_files"


def test_directory_lint_reports_missing_directory(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    result = lint_community_signal_directory(
        missing,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"


def test_directory_lint_reports_file_path_as_invalid_directory(
    tmp_path: Path,
) -> None:
    path = write_text(tmp_path / "signals.csv", "url,title,published_at")

    result = lint_community_signal_directory(
        path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"


def test_directory_lint_reports_unreadable_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    original_iterdir = Path.iterdir

    def fail_iterdir(path: Path):
        if path == tmp_path:
            raise PermissionError("no access")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_iterdir)

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"
```

- [ ] **Step 4: Add non-recursive and render tests**

Append:

```python
def test_directory_lint_is_non_recursive(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    write_text(
        nested / "nested.csv",
        """
        url,title,published_at
        https://example.com/nested,Nested,2026-06-12T08:00:00Z
        """,
    )
    write_text(
        tmp_path / "top.csv",
        """
        url,title,published_at
        https://example.com/top,Top,2026-06-12T08:00:00Z
        """,
    )

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.file_count == 1
    assert Path(result.files[0].path).name == "top.csv"


def test_directory_lint_double_star_pattern_does_not_recurse(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    write_text(
        nested / "nested.csv",
        """
        url,title,published_at
        https://example.com/nested,Nested,2026-06-12T08:00:00Z
        """,
    )

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="**/*.csv",
    )

    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "no_matching_files"


def test_render_community_signal_directory_lint_table_includes_aggregate_and_file_lines(
    tmp_path: Path,
) -> None:
    write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z
        """,
    )

    lines = render_community_signal_directory_lint_table(
        lint_community_signal_directory(
            tmp_path,
            input_format="csv",
            pattern="*.csv",
        )
    )

    assert lines[0] == f"Community signal directory: {tmp_path}"
    assert "Input format: csv" in lines
    assert "Pattern: *.csv" in lines
    assert "Files: 1" in lines
    assert any(line.startswith(f"- {tmp_path / 'signals.csv'}:") for line in lines)
    assert "Severity | File | Code | Row | Field | Message" in lines


def test_render_community_signal_directory_lint_table_clean_directory(
    tmp_path: Path,
) -> None:
    write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at,source_name,platform,summary,source_weight,collected_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z,Tool,community,Note,1.0,2026-06-12T08:30:00Z
        """,
    )

    lines = render_community_signal_directory_lint_table(
        lint_community_signal_directory(
            tmp_path,
            input_format="csv",
            pattern="*.csv",
        )
    )

    assert "Findings: 0 errors, 0 warnings, 0 info" in lines
    assert "No community-signal directory findings." in lines
```

- [ ] **Step 5: Verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_lint.py -q -k directory_lint
```

Expected: FAIL because `lint_community_signal_directory` and
`render_community_signal_directory_lint_table` do not exist.

## Task 2: Implement Directory Lint Module API

**Files:**
- Modify: `src/fashion_radar/community_signals.py`
- Test: `tests/test_community_signal_lint.py`

- [ ] **Step 1: Add directory result model and findings**

Add:

```python
class CommunitySignalDirectoryLintResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directory: str
    input_format: ManualSignalFormat
    pattern: str
    file_count: int = 0
    row_count: int = 0
    valid_row_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    field_counts: dict[str, int] = Field(default_factory=dict)
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    files: list[CommunitySignalLintResult] = Field(default_factory=list)
    findings: list[CommunitySignalFinding] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.error_count == 0
```

- [ ] **Step 2: Add directory lint implementation**

Add:

```python
def lint_community_signal_directory(
    directory: Path,
    *,
    input_format: ManualSignalFormat,
    pattern: str,
    default_source_name: str = "Community Signal Import",
) -> CommunitySignalDirectoryLintResult:
    findings: list[CommunitySignalFinding] = []
    try:
        if not directory.is_dir():
            return CommunitySignalDirectoryLintResult(
                directory=str(directory),
                input_format=input_format,
                pattern=pattern,
                error_count=1,
                findings=[
                    CommunitySignalFinding(
                        severity=CommunitySignalFindingSeverity.ERROR,
                        code="invalid_directory",
                        message="Community signal directory does not exist or is not a directory.",
                    )
                ],
            )
        children = list(directory.iterdir())
    except OSError as exc:
        return CommunitySignalDirectoryLintResult(
            directory=str(directory),
            input_format=input_format,
            pattern=pattern,
            error_count=1,
            findings=[
                CommunitySignalFinding(
                    severity=CommunitySignalFindingSeverity.ERROR,
                    code="invalid_directory",
                    message=f"Could not read community signal directory: {exc}",
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
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.ERROR,
                code="no_matching_files",
                message="No regular files matched the pattern in the directory.",
            )
        )

    file_results = [
        lint_community_signal_file(
            path,
            input_format=input_format,
            default_source_name=default_source_name,
        )
        for path in paths
    ]
    error_count = _count_findings(findings, CommunitySignalFindingSeverity.ERROR) + sum(
        file.error_count for file in file_results
    )
    warning_count = _count_findings(findings, CommunitySignalFindingSeverity.WARNING) + sum(
        file.warning_count for file in file_results
    )
    info_count = _count_findings(findings, CommunitySignalFindingSeverity.INFO) + sum(
        file.info_count for file in file_results
    )
    return CommunitySignalDirectoryLintResult(
        directory=str(directory),
        input_format=input_format,
        pattern=pattern,
        file_count=len(file_results),
        row_count=sum(file.row_count for file in file_results),
        valid_row_count=sum(file.valid_row_count for file in file_results),
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
        field_counts=_merge_count_dicts(file.field_counts for file in file_results),
        source_name_counts=_merge_count_dicts(
            file.source_name_counts for file in file_results
        ),
        platform_counts=_merge_count_dicts(file.platform_counts for file in file_results),
        files=file_results,
        findings=_sort_findings(findings),
    )
```

Add `import fnmatch` near the top of `community_signals.py`. Add
`_merge_count_dicts(counts)` using `Counter`, and return
`dict(sorted(counter.items()))` for deterministic JSON/table output. Directory
findings should be `_sort_findings(findings)` before they are stored.

- [ ] **Step 3: Add directory table renderer**

Add:

```python
def render_community_signal_directory_lint_table(
    result: CommunitySignalDirectoryLintResult,
) -> list[str]:
    lines = [
        f"Community signal directory: {result.directory}",
        f"Input format: {result.input_format}",
        f"Pattern: {result.pattern}",
        f"Files: {result.file_count}",
        f"Rows: {result.row_count} total, {result.valid_row_count} import-ready",
        f"Fields: {_format_counts(result.field_counts)}",
        f"Sources: {_format_counts(result.source_name_counts)}",
        f"Platforms: {_format_counts(result.platform_counts)}",
        (
            f"Findings: {result.error_count} errors, {result.warning_count} warnings, "
            f"{result.info_count} info"
        ),
    ]
    if result.files:
        lines.append("Files:")
        for file in result.files:
            lines.append(
                f"- {file.path}: {file.row_count} rows, "
                f"{file.valid_row_count} import-ready, {file.error_count} errors, "
                f"{file.warning_count} warnings, {file.info_count} info"
            )
    if not result.findings and all(not file.findings for file in result.files):
        lines.append("No community-signal directory findings.")
        return lines

    lines.append("Severity | File | Code | Row | Field | Message")
    for finding in result.findings:
        lines.append(
            f"{finding.severity.value} | n/a | {finding.code} | "
            f"{finding.row or 'n/a'} | {finding.field or 'n/a'} | {finding.message}"
        )
    for file in result.files:
        for finding in file.findings:
            lines.append(
                f"{finding.severity.value} | {file.path} | {finding.code} | "
                f"{finding.row or 'n/a'} | {finding.field or 'n/a'} | "
                f"{finding.message}"
            )
    return lines
```

- [ ] **Step 4: Verify module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_lint.py -q -k directory_lint
```

Expected: PASS after implementation corrections.

## Task 3: Add CLI Command And CLI Tests

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Append near the existing `community_signal_lint` tests:

```python
def assert_no_community_lint_artifacts(
    tmp_path: Path,
    *,
    config_dir: Path,
    data_dir: Path,
    reports_dir: Path,
) -> None:
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not Path("configs").exists()
    assert not Path("data").exists()
    assert not Path("reports").exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite-*")) == []
    assert list(tmp_path.rglob("*.sqlite3")) == []
    assert list(tmp_path.rglob("*.db")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("*.eml")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []
    assert list(tmp_path.rglob("collection-workflow*.json")) == []


def test_community_signal_lint_dir_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["community-signal-lint-dir", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--input-format" in result.output
    assert "--pattern" in result.output
    assert "--format" in result.output
    assert "--source-name" in result.output
    assert "--strict" in result.output
    assert "without importing rows" in result.output


def test_community_signal_lint_dir_prints_table(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,source_name,platform,summary\n"
        "https://example.com/a,Signal,2026-06-12T08:00:00Z,Tool,community,Note\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
    )

    assert result.exit_code == 0
    assert f"Community signal directory: {tmp_path}" in result.output
    assert "Files: 1" in result.output
    assert "Rows: 1 total, 1 import-ready" in result.output


def test_community_signal_lint_dir_prints_json(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/a",
                    "title": "Signal",
                    "published_at": "2026-06-12T08:00:00Z",
                    "source_name": "Tool",
                    "platform": "community",
                    "summary": "Note",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "json",
            "--pattern",
            "*.json",
            "--format",
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
        "valid_row_count",
        "error_count",
        "warning_count",
        "info_count",
        "field_counts",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["file_count"] == 1
    assert payload["row_count"] == 1
    assert payload["valid_row_count"] == 1
    assert payload["error_count"] == 0
    assert payload["warning_count"] == 0
    assert payload["info_count"] == 2
    assert payload["files"][0]["row_count"] == 1


def test_community_signal_lint_dir_json_counts_and_file_order(
    tmp_path: Path,
) -> None:
    (tmp_path / "b.csv").write_text(
        "url,title,published_at\n"
        "https://example.com/b,Warning Only,2026-06-12T09:00:00Z\n",
        encoding="utf-8",
    )
    (tmp_path / "a.csv").write_text(
        "url,title,published_at\n"
        ",Broken,not-a-date\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert [Path(file["path"]).name for file in payload["files"]] == [
        "a.csv",
        "b.csv",
    ]
    assert payload["file_count"] == 2
    assert payload["row_count"] == 2
    assert payload["valid_row_count"] == 1
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 3
    assert payload["info_count"] == 2
    assert list(payload["field_counts"]) == sorted(payload["field_counts"])
    assert payload["source_name_counts"] == {"Community Signal Import": 1}
    assert payload["platform_counts"] == {}


def test_community_signal_lint_dir_json_invalid_directory_shape(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(missing),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--format",
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
        "row_count",
        "valid_row_count",
        "error_count",
        "warning_count",
        "info_count",
        "field_counts",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["directory"] == str(missing)
    assert payload["input_format"] == "csv"
    assert payload["pattern"] == "*.csv"
    assert payload["file_count"] == 0
    assert payload["row_count"] == 0
    assert payload["valid_row_count"] == 0
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 0
    assert payload["info_count"] == 0
    assert payload["field_counts"] == {}
    assert payload["source_name_counts"] == {}
    assert payload["platform_counts"] == {}
    assert payload["files"] == []
    assert payload["findings"] == [
        {
            "severity": "error",
            "code": "invalid_directory",
            "message": "Community signal directory does not exist or is not a directory.",
            "row": None,
            "field": None,
        }
    ]


def test_community_signal_lint_dir_json_no_matching_files_shape(
    tmp_path: Path,
) -> None:
    (tmp_path / "ignored.txt").write_text("ignore", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--format",
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
        "row_count",
        "valid_row_count",
        "error_count",
        "warning_count",
        "info_count",
        "field_counts",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["directory"] == str(tmp_path)
    assert payload["input_format"] == "csv"
    assert payload["pattern"] == "*.csv"
    assert payload["file_count"] == 0
    assert payload["row_count"] == 0
    assert payload["valid_row_count"] == 0
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 0
    assert payload["info_count"] == 0
    assert payload["field_counts"] == {}
    assert payload["source_name_counts"] == {}
    assert payload["platform_counts"] == {}
    assert payload["files"] == []
    assert payload["findings"] == [
        {
            "severity": "error",
            "code": "no_matching_files",
            "message": "No regular files matched the pattern in the directory.",
            "row": None,
            "field": None,
        }
    ]
```

Append exit behavior and no-artifact tests:

```python
def test_community_signal_lint_dir_invalid_directory_exits_nonzero(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(missing),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output


def test_community_signal_lint_dir_file_path_as_directory_exits_nonzero(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text("url,title,published_at\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output


def test_community_signal_lint_dir_unreadable_directory_exits_nonzero_without_artifacts(
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
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
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
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output
    monkeypatch.setattr(Path, "iterdir", original_iterdir)
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_community_signal_lint_dir_warning_only_exits_zero_without_strict(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
    )

    assert result.exit_code == 0
    assert "missing_source_name" in result.output


def test_community_signal_lint_dir_warning_only_exits_nonzero_with_strict(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--strict",
        ],
    )

    assert result.exit_code == 1
    assert "missing_source_name" in result.output


def test_community_signal_lint_dir_does_not_create_project_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
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
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
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

    assert result.exit_code == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )
```

- [ ] **Step 2: Run CLI tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k community_signal_lint_dir
```

Expected: FAIL because the command is not registered yet.

- [ ] **Step 3: Implement CLI command**

Modify imports:

```python
from fashion_radar.community_signals import (
    CommunitySignalFindingSeverity,
    lint_community_signal_directory,
    lint_community_signal_file,
    render_community_signal_directory_lint_table,
    render_community_signal_lint_table,
)
```

Add option:

```python
COMMUNITY_SIGNAL_PATTERN_OPTION = typer.Option(
    ...,
    "--pattern",
    help="Non-recursive file glob pattern, for example *.csv or *.json.",
)
```

Add command:

```python
@app.command(name="community-signal-lint-dir")
def community_signal_lint_dir_command(
    directory: Path,
    input_format: ManualSignalInputFormat = COMMUNITY_SIGNAL_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_SIGNAL_PATTERN_OPTION,
    output_format: CommunitySignalLintOutputFormat = COMMUNITY_SIGNAL_LINT_FORMAT_OPTION,
    source_name: str = COMMUNITY_SIGNAL_SOURCE_NAME_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Lint local community signal files in one directory without importing rows."""
    result = lint_community_signal_directory(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_name,
    )
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_community_signal_directory_lint_table(result):
            typer.echo(line)

    if result.error_count or (strict and result.warning_count):
        raise typer.Exit(1)
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k community_signal_lint_dir
```

Expected: PASS.

## Task 4: Documentation Updates

**Files:**
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/community-signal-import.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update docs**

Add directory examples:

```bash
uv run fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv"
uv run fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json" --format json
```

Docs must state:

- reads matched regular files directly under one local directory;
- non-recursive in Stage 17;
- no import rows;
- no SQLite;
- no config/data/report directory creation;
- no URL fetching, source collection, platform tooling, platform coverage check,
  authorization verification, or policy workflow feature.

- [ ] **Step 2: Run docs boundary scan**

Run:

```bash
rg -n "community-signal-lint-dir|platform-wide|market-wide|current-hotness|source acquisition|source-acquisition|platform search|social monitoring|exports|ranking|demand proof|compliance|audit|authorization" README.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md CHANGELOG.md
```

Expected: risky terms appear only in explicit boundary/negative contexts.

## Task 5: Verification And Claude Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-17-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-17-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_lint.py tests/test_cli.py -q -k "community_signal_lint_dir or directory_lint"
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

Expected: PASS; CodeGraph index up to date.

- [ ] **Step 3: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-17-code-review-prompt.md` asking Claude
Code to review Stage 17 in read-only plan mode with `--effort max`. Focus on
read-only directory behavior, deterministic aggregation, strict exit behavior,
no-artifact tests, docs boundaries, and out-of-scope exclusions.

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-17-code-review-prompt.md | tee docs/reviews/claude-code-stage-17-code-review.md
```

Expected: fix Critical and Important findings before upload.

## Post-Acceptance Release And Upload

These steps are not part of Stage 17 implementation acceptance. Run them only
after full local verification passes, Claude Code approves the Stage 17 code
review, and any Critical or Important review findings are fixed.

- [ ] **Step 1: Release checks**

Run:

```bash
uv lock --check --default-index https://pypi.org/simple
uv sync --locked --dev --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage17
```

Then run installed-wheel smoke for `fashion-radar community-signal-lint-dir --help`
and JSON output from a temp venv, using the Tsinghua mirror for install.

- [ ] **Step 2: Commit and push after review gates pass**

Before commit:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Commit:

```bash
git add src/fashion_radar/community_signals.py src/fashion_radar/cli.py tests/test_community_signal_lint.py tests/test_cli.py docs/community-signal-quality.md docs/community-signal-import.md README.md docs/architecture.md docs/source-boundaries.md CHANGELOG.md docs/superpowers/specs/2026-06-12-stage-17-community-signal-directory-lint-design.md docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md docs/reviews/claude-code-stage-17-plan-review-prompt.md docs/reviews/claude-code-stage-17-plan-review.md docs/reviews/claude-code-stage-17-code-review-prompt.md docs/reviews/claude-code-stage-17-code-review.md
git commit -m "Add community signal directory diagnostics"
```

Push with temporary `GIT_ASKPASS` only if needed. Keep the remote URL token-free
and remove any askpass file immediately after the push.

## Plan Self-Review

- Spec coverage: module, CLI, tests, docs, review, verification, and upload
  tasks cover every Stage 17 requirement.
- Placeholder scan: no task depends on an undefined future decision.
- Type consistency: public names are consistently
  `CommunitySignalDirectoryLintResult`, `lint_community_signal_directory`, and
  `render_community_signal_directory_lint_table`.
- Boundary check: no task adds collectors, platform tooling, scraping, source
  acquisition, database changes, import side effects, matcher changes, scoring
  changes, dashboard changes, recursive scanning, watch folders, or
  product-facing policy workflow features.
