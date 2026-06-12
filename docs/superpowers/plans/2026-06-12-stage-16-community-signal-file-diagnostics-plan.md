# Stage 16 Community Signal File Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar community-signal-lint`, a pure local diagnostics command for community signal CSV/JSON handoff files.

**Architecture:** Add a new `community_signals.py` diagnostics module that reads local CSV/JSON, checks the strict community signal contract, validates import-readiness with the existing `ManualSignalRow` model, and returns deterministic table/JSON findings. Add a thin Typer command with no config/data/report directory options and no SQLite, import, collection, matching, scoring, report, dashboard, network, or platform-tool side effects.

**Tech Stack:** Python 3.11+, standard library `csv`/`json`, Typer, Pydantic v2, existing manual signal import model, pytest, ruff, uv, Markdown docs, JSON Schema as static repo metadata.

---

## Scope Guard

Stage 16 must not add or document:

- social/platform connectors, platform search, automated community ingestion, or
  source acquisition;
- scraping, crawler development, browser automation, Playwright, Selenium, MCP
  platform scraping servers, account automation, unofficial platform APIs, or
  export-acquisition instructions;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
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
  UI, policy checklist, or legal review feature.

## File Structure

- Create `src/fashion_radar/community_signals.py`: community signal diagnostics
  models, local CSV/JSON raw readers, contract field checks, import-readiness
  validation, deterministic table rendering.
- Create `tests/test_community_signal_lint.py`: focused module tests.
- Modify `src/fashion_radar/cli.py`: import diagnostics API, add output/input
  format aliases, add `community-signal-lint` command near `import-signals`.
- Modify `tests/test_cli.py`: CLI tests mirroring source/entity lint command
  patterns.
- Create `docs/community-signal-quality.md`: user documentation.
- Modify `docs/community-signal-import.md`: recommend lint before dry-run/import.
- Modify `README.md`: add short command and docs link.
- Modify `docs/architecture.md`: mention optional local community-signal linting.
- Modify `CHANGELOG.md`: record Stage 16 diagnostics.

## Task 1: Add Focused Failing Community-Signal Lint Tests

**Files:**
- Create: `tests/test_community_signal_lint.py`

- [ ] **Step 1: Create test helpers and example smoke tests**

Create `tests/test_community_signal_lint.py`:

```python
import json
from pathlib import Path
from textwrap import dedent

from fashion_radar.community_signals import (
    CommunitySignalFindingSeverity,
    lint_community_signal_file,
    render_community_signal_lint_table,
)
from fashion_radar.importers.manual_signals import load_manual_signal_rows


ROOT = Path(__file__).resolve().parents[1]
CSV_EXAMPLE = ROOT / "examples" / "community-signals.example.csv"
JSON_EXAMPLE = ROOT / "examples" / "community-signals.example.json"


def write_text(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def finding_codes(result) -> list[str]:
    return [finding.code for finding in result.findings]


def findings_by_code(result, code: str):
    return [finding for finding in result.findings if finding.code == code]


def test_repository_csv_example_lints_cleanly() -> None:
    result = lint_community_signal_file(CSV_EXAMPLE, input_format="csv")

    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.row_count == 2
    assert result.valid_row_count == 2
    assert result.source_name_counts == {"Community Tool Export": 2}
    assert result.platform_counts == {"community": 2}


def test_repository_json_example_lints_cleanly() -> None:
    result = lint_community_signal_file(JSON_EXAMPLE, input_format="json")

    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.row_count == 2
    assert result.valid_row_count == 2
    assert result.source_name_counts == {"Community Tool Export": 2}
    assert result.platform_counts == {"community": 2}
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_lint.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'fashion_radar.community_signals'`.

- [ ] **Step 3: Add contract and validation tests**

Append tests:

```python
def test_unknown_and_prohibited_csv_fields_are_errors(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at,author_handle,unexpected
        https://example.com/a,Signal,2026-06-12T08:00:00Z,@private,value
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")

    prohibited = findings_by_code(result, "prohibited_field")[0]
    unknown = findings_by_code(result, "unknown_field")[0]
    assert prohibited.severity == CommunitySignalFindingSeverity.ERROR
    assert prohibited.row == 2
    assert prohibited.field == "author_handle"
    assert unknown.severity == CommunitySignalFindingSeverity.ERROR
    assert unknown.field == "unexpected"
    assert [finding.field for finding in findings_by_code(result, "unknown_field")] == [
        "unexpected"
    ]


def test_invalid_row_is_error_using_import_validation(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.json",
        """
        {
          "items": [
            {
              "url": "",
              "title": "Broken",
              "published_at": "2026-06-12T08:00:00Z"
            }
          ]
        }
        """,
    )

    result = lint_community_signal_file(path, input_format="json")

    finding = findings_by_code(result, "invalid_row")[0]
    assert finding.severity == CommunitySignalFindingSeverity.ERROR
    assert finding.row == 1
    assert finding.field == "row"
    assert result.valid_row_count == 0


def test_invalid_json_shape_is_invalid_file_error(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.json",
        """
        {"items": {}}
        """,
    )

    result = lint_community_signal_file(path, input_format="json")

    finding = findings_by_code(result, "invalid_file")[0]
    assert result.error_count == 1
    assert finding.severity == CommunitySignalFindingSeverity.ERROR


def test_csv_extra_cells_are_specific_errors(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z,unexpected-cell
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")

    finding = findings_by_code(result, "csv_extra_cells")[0]
    assert finding.severity == CommunitySignalFindingSeverity.ERROR
    assert finding.row == 2
    assert finding.field == "row"
    assert "more cells than headers" in finding.message


def test_source_name_fallback_matches_manual_importer(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at,source_name
        https://example.com/a,Signal,2026-06-12T08:00:00Z,
        """,
    )

    result = lint_community_signal_file(
        path,
        input_format="csv",
        default_source_name="  ",
    )
    manual_rows = load_manual_signal_rows(
        path,
        input_format="csv",
        default_source_name="  ",
    )

    assert result.source_name_counts == {manual_rows[0].source_name: 1}
    assert result.source_name_counts == {"Manual Import": 1}
    assert findings_by_code(result, "missing_source_name")[0].row == 2
```

- [ ] **Step 4: Add warning and info tests**

Append tests:

```python
def test_duplicate_url_and_missing_provenance_are_warnings(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at
        https://example.com/a,First,2026-06-12T08:00:00Z
        https://example.com/a,Second,2026-06-12T09:00:00Z
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")

    assert "duplicate_url" in finding_codes(result)
    assert "missing_source_name" in finding_codes(result)
    assert "missing_platform" in finding_codes(result)
    assert "missing_summary" in finding_codes(result)
    assert "implicit_source_weight" in finding_codes(result)
    assert "implicit_collected_at" in finding_codes(result)
    assert result.warning_count >= 4
    assert result.info_count >= 2


def test_collected_before_published_is_warning(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.json",
        """
        [
          {
            "url": "https://example.com/a",
            "title": "Signal",
            "published_at": "2026-06-12T10:00:00Z",
            "source_name": "External Tool",
            "platform": "community",
            "summary": "Sanitized note",
            "source_weight": 1.0,
            "collected_at": "2026-06-12T09:00:00Z"
          }
        ]
        """,
    )

    result = lint_community_signal_file(path, input_format="json")

    finding = findings_by_code(result, "collected_before_published")[0]
    assert finding.severity == CommunitySignalFindingSeverity.WARNING
    assert finding.row == 1
    assert finding.field == "collected_at"


def test_empty_signal_file_is_warning(tmp_path: Path) -> None:
    path = write_text(tmp_path / "signals.csv", "url,title,published_at")

    result = lint_community_signal_file(path, input_format="csv")

    finding = findings_by_code(result, "empty_signal_file")[0]
    assert result.error_count == 0
    assert finding.severity == CommunitySignalFindingSeverity.WARNING
```

- [ ] **Step 5: Add JSON shape and table render tests**

Append:

```python
def test_lint_result_json_shape_is_stable(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at,summary,source_name,platform,source_weight,collected_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z,Note,Tool,community,1.2,2026-06-12T08:30:00Z
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")
    payload = json.loads(result.model_dump_json(indent=2))

    assert list(payload) == [
        "path",
        "input_format",
        "row_count",
        "valid_row_count",
        "field_counts",
        "source_name_counts",
        "platform_counts",
        "findings",
    ]
    assert payload["path"] == str(path)
    assert payload["input_format"] == "csv"
    assert payload["row_count"] == 1
    assert payload["valid_row_count"] == 1
    assert payload["findings"] == []


def test_render_community_signal_lint_table_includes_summary_and_findings(
    tmp_path: Path,
) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z
        """,
    )

    lines = render_community_signal_lint_table(
        lint_community_signal_file(path, input_format="csv")
    )

    assert lines[0] == f"Community signal file: {path}"
    assert "Input format: csv" in lines
    assert "Rows: 1 total, 1 import-ready" in lines
    assert "Severity | Code | Row | Field | Message" in lines
    assert any("missing_source_name" in line for line in lines)
```

- [ ] **Step 6: Verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_lint.py -q
```

Expected: FAIL because `fashion_radar.community_signals` does not exist yet.

## Task 2: Implement Community Signal Diagnostics Module

**Files:**
- Create: `src/fashion_radar/community_signals.py`
- Test: `tests/test_community_signal_lint.py`

- [ ] **Step 1: Add module skeleton, constants, models, and public API**

Create `src/fashion_radar/community_signals.py` with:

```python
from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from fashion_radar.importers.manual_signals import ManualSignalFormat, ManualSignalRow

ALLOWED_COMMUNITY_SIGNAL_FIELDS = {
    "url",
    "title",
    "published_at",
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at",
}
PROHIBITED_COMMUNITY_SIGNAL_FIELDS = {
    "author_handle",
    "raw_comment",
    "account_id",
    "follower_count",
    "image_url",
    "video_url",
    "profile_url",
    "full_post_body",
    "direct_message",
    "cookie",
    "session",
    "token",
}


class CommunitySignalFindingSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class CommunitySignalFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: CommunitySignalFindingSeverity
    code: str
    message: str
    row: int | None = None
    field: str | None = None


class CommunitySignalLintResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    input_format: ManualSignalFormat
    row_count: int = 0
    valid_row_count: int = 0
    field_counts: dict[str, int] = Field(default_factory=dict)
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    findings: list[CommunitySignalFinding] = Field(default_factory=list)

    @property
    def error_count(self) -> int:
        return _count_findings(self.findings, CommunitySignalFindingSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return _count_findings(self.findings, CommunitySignalFindingSeverity.WARNING)

    @property
    def info_count(self) -> int:
        return _count_findings(self.findings, CommunitySignalFindingSeverity.INFO)

    @property
    def ok(self) -> bool:
        return self.error_count == 0
```

- [ ] **Step 2: Implement raw readers and lint orchestration**

Add:

```python
def lint_community_signal_file(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    default_source_name: str = "Community Signal Import",
) -> CommunitySignalLintResult:
    raw_rows, read_error = _read_raw_signal_rows(path, input_format=input_format)
    if read_error is not None:
        return CommunitySignalLintResult(
            path=str(path),
            input_format=input_format,
            findings=[read_error],
        )

    findings: list[CommunitySignalFinding] = []
    if not raw_rows:
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="empty_signal_file",
                message="Community signal file contains no rows.",
            )
        )

    valid_rows: list[ManualSignalRow] = []
    field_counts: Counter[str] = Counter()
    url_rows: dict[str, list[int]] = {}
    for row_number, raw in raw_rows:
        if None in raw:
            findings.append(
                CommunitySignalFinding(
                    severity=CommunitySignalFindingSeverity.ERROR,
                    code="csv_extra_cells",
                    message="CSV row has more cells than headers.",
                    row=row_number,
                    field="row",
                )
            )
            raw = {field: value for field, value in raw.items() if field is not None}
        findings.extend(_raw_field_findings(raw, row_number=row_number))
        for field, value in raw.items():
            if field is None or not str(field).strip():
                continue
            if value is not None and str(value).strip():
                field_counts[str(field)] += 1
        row, row_findings = _validate_import_ready_row(
            raw,
            row_number=row_number,
            default_source_name=default_source_name,
        )
        findings.extend(row_findings)
        if row is None:
            continue
        valid_rows.append(row)
        url_rows.setdefault(row.url, []).append(row_number)
        findings.extend(_quality_findings(raw, row, row_number=row_number))

    findings.extend(_duplicate_url_findings(url_rows))
    return CommunitySignalLintResult(
        path=str(path),
        input_format=input_format,
        row_count=len(raw_rows),
        valid_row_count=len(valid_rows),
        field_counts=dict(sorted(field_counts.items())),
        source_name_counts=dict(sorted(Counter(row.source_name for row in valid_rows).items())),
        platform_counts=dict(
            sorted(Counter(row.platform for row in valid_rows if row.platform).items())
        ),
        findings=_sort_findings(findings),
    )
```

Implement `_read_raw_signal_rows()` so CSV row numbers start at 2 and JSON row
numbers start at 1. JSON must accept a top-level list or an object with an
`items` list. Return `invalid_file` for unreadable files, invalid CSV headers,
invalid JSON, invalid top-level JSON shape, or non-object rows. Do not collapse
over-wide CSV rows into `invalid_file`; rows containing the `csv.DictReader`
`None` overflow key must emit `csv_extra_cells` with the offending row number.

- [ ] **Step 3: Implement finding helpers and rendering**

Add helpers:

- `_raw_field_findings(raw, row_number)` emits `prohibited_field` for fields in
  `PROHIBITED_COMMUNITY_SIGNAL_FIELDS`; it emits `unknown_field` only for other
  fields outside `ALLOWED_COMMUNITY_SIGNAL_FIELDS`, so fields like
  `author_handle` are not double-reported.
- `_validate_import_ready_row(raw, row_number, default_source_name)` applies the
  same fallback semantics as `load_manual_signal_rows()`:
  `default_source_name.strip() or "Manual Import"`. It validates with
  `ManualSignalRow.model_validate()` and returns `invalid_row` on validation
  error. Keep `test_source_name_fallback_matches_manual_importer` as the drift
  guard for this behavior.
- `_quality_findings(raw, row, row_number)` emits missing provenance,
  missing summary, implicit default, and `collected_before_published` findings.
- `_duplicate_url_findings(url_rows)` emits `duplicate_url` for every row in a
  duplicate URL group.
- `render_community_signal_lint_table(result)` mirrors source/entity lint table
  style.
- `_sort_findings()`, `_count_findings()`, and `_format_counts()` mirror existing
  lint modules.

- [ ] **Step 4: Run focused module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_lint.py -q
```

Expected: PASS after minimal implementation corrections.

## Task 3: Add CLI Command And CLI Tests

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Append tests near existing import-signals CLI tests:

```python
def test_community_signal_lint_help_lists_input_format_output_format_and_strict() -> None:
    result = CliRunner().invoke(
        app,
        ["community-signal-lint", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--input-format" in result.output
    assert "--format" in result.output
    assert "--source-name" in result.output
    assert "--strict" in result.output
    assert "without importing rows" in result.output


def test_community_signal_lint_prints_table_for_csv_example() -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint",
            "examples/community-signals.example.csv",
            "--input-format",
            "csv",
        ],
    )

    assert result.exit_code == 0
    assert "Community signal file: examples/community-signals.example.csv" in result.output
    assert "Rows: 2 total, 2 import-ready" in result.output
    assert "Findings:" in result.output


def test_community_signal_lint_prints_json_for_json_example() -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint",
            "examples/community-signals.example.json",
            "--input-format",
            "json",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["path"] == "examples/community-signals.example.json"
    assert payload["input_format"] == "json"
    assert payload["row_count"] == 2
    assert payload["valid_row_count"] == 2


def test_community_signal_lint_strict_exits_nonzero_on_warnings(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        ["community-signal-lint", str(path), "--input-format", "csv", "--strict"],
    )

    assert result.exit_code == 1
    assert "missing_source_name" in result.output


def test_community_signal_lint_invalid_file_exits_nonzero_without_traceback(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.json"
    path.write_text("{", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["community-signal-lint", str(path), "--input-format", "json"],
    )

    assert result.exit_code == 1
    assert "invalid_file" in result.output
    assert "Traceback" not in result.output
```

Add this explicit no-artifact test:

```python
def test_community_signal_lint_does_not_create_project_artifacts(
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
        ["community-signal-lint", str(path), "--input-format", "csv"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not Path("configs").exists()
    assert not Path("data").exists()
    assert not Path("reports").exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite-*")) == []
    assert list(tmp_path.rglob("*.db")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("*.eml")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []
    assert list(tmp_path.rglob("collection-workflow*.json")) == []
```

- [ ] **Step 2: Run CLI tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k community_signal_lint
```

Expected: FAIL because the command is not registered yet.

- [ ] **Step 3: Implement CLI command**

Modify `src/fashion_radar/cli.py`:

```python
from fashion_radar.community_signals import (
    CommunitySignalFindingSeverity,
    lint_community_signal_file,
    render_community_signal_lint_table,
)
```

Add aliases/options:

```python
CommunitySignalLintOutputFormat = Literal["table", "json"]
COMMUNITY_SIGNAL_LINT_FORMAT_OPTION = typer.Option("table", "--format", help="Output format.")
COMMUNITY_SIGNAL_INPUT_FORMAT_OPTION = typer.Option(..., "--input-format", help="Input file format.")
COMMUNITY_SIGNAL_SOURCE_NAME_OPTION = typer.Option(
    "Community Signal Import",
    "--source-name",
    help="Fallback source name for rows that omit source_name.",
)
```

Add command:

```python
@app.command(name="community-signal-lint")
def community_signal_lint_command(
    path: Path,
    input_format: ManualSignalInputFormat = COMMUNITY_SIGNAL_INPUT_FORMAT_OPTION,
    output_format: CommunitySignalLintOutputFormat = COMMUNITY_SIGNAL_LINT_FORMAT_OPTION,
    source_name: str = COMMUNITY_SIGNAL_SOURCE_NAME_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Lint a local community signal file without importing rows."""
    result = lint_community_signal_file(
        path,
        input_format=input_format,
        default_source_name=source_name,
    )
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_community_signal_lint_table(result):
            typer.echo(line)

    has_errors = any(
        finding.severity == CommunitySignalFindingSeverity.ERROR for finding in result.findings
    )
    has_warnings = any(
        finding.severity == CommunitySignalFindingSeverity.WARNING for finding in result.findings
    )
    if has_errors or (strict and has_warnings):
        raise typer.Exit(1)
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k community_signal_lint
```

Expected: PASS.

## Task 4: Add Documentation

**Files:**
- Create: `docs/community-signal-quality.md`
- Modify: `docs/community-signal-import.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Create community signal quality docs**

Create `docs/community-signal-quality.md` with:

- command examples for CSV, JSON, JSON output, and `--strict`;
- table output example;
- JSON output example;
- severity meanings;
- finding code reference;
- why findings matter for local handoff files;
- guidance for external tools writing sanitized local rows;
- limits.

Limits must say the command reads one local file only, does not import rows,
does not open SQLite, does not collect or fetch sources, does not search or
monitor platforms, does not create artifacts, and is not ranking, demand proof,
platform coverage, compliance review, audit workflow, or legal review.

- [ ] **Step 2: Update existing docs**

Update:

- `docs/community-signal-import.md`: add lint step before dry run.
- `README.md`: add command near community/manual import docs and docs index.
- `docs/architecture.md`: add optional community-signal lint step before import.
- `CHANGELOG.md`: add Stage 16 bullet.

- [ ] **Step 3: Run docs boundary searches**

Run:

```bash
rg -n "community-signal-lint|Community Signal Quality|platform-wide|market-wide|current-hotness|source acquisition|platform search|social monitoring|exports|ranking|demand proof" README.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md CHANGELOG.md
```

Expected: any boundary terms appear only where docs explicitly say the command
does not provide those capabilities.

## Task 5: Verification And Claude Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-16-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-16-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_manual_signal_import.py tests/test_cli.py -q -k "community_signal or import_signals"
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

Create `docs/reviews/claude-code-stage-16-code-review-prompt.md` asking Claude
Code to review Stage 16 in read-only plan mode with `--effort max`. Focus on
contract correctness, read-only behavior, field handling, import validation
alignment, CLI behavior, tests, docs boundaries, and out-of-scope exclusions.

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-16-code-review-prompt.md | tee docs/reviews/claude-code-stage-16-code-review.md
```

Expected: fix Critical and Important findings before upload.

## Post-Acceptance Release And Upload

These steps are not part of Stage 16 implementation acceptance. Run them only
after full local verification passes, Claude Code approves the Stage 16 code
review, and any Critical or Important review findings are fixed.

- [ ] **Step 1: Optional release checks before GitHub upload**

Run after code review approval:

```bash
uv lock --check --default-index https://pypi.org/simple
uv sync --locked --dev --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage16
```

Then run installed-wheel smoke for `fashion-radar community-signal-lint --help`
and example JSON output from a temp venv, using the Tsinghua mirror for install.

- [ ] **Step 2: Commit and push after review gates pass**

Before commit:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Commit:

```bash
git add src/fashion_radar/community_signals.py src/fashion_radar/cli.py tests/test_community_signal_lint.py tests/test_cli.py docs/community-signal-quality.md docs/community-signal-import.md README.md docs/architecture.md CHANGELOG.md docs/superpowers/specs/2026-06-12-stage-16-community-signal-file-diagnostics-design.md docs/superpowers/plans/2026-06-12-stage-16-community-signal-file-diagnostics-plan.md docs/reviews/claude-code-stage-16-plan-review-prompt.md docs/reviews/claude-code-stage-16-plan-review.md docs/reviews/claude-code-stage-16-code-review-prompt.md docs/reviews/claude-code-stage-16-code-review.md
git commit -m "Add community signal file diagnostics"
```

Push with temporary `GIT_ASKPASS` only. Keep the remote URL token-free and remove
the askpass file immediately after the push.

## Plan Self-Review

- Spec coverage: module, CLI, tests, docs, review, verification, and upload
  tasks cover every Stage 16 requirement.
- Placeholder scan: no task depends on an undefined future decision.
- Type consistency: public names are consistently
  `CommunitySignalFindingSeverity`, `CommunitySignalFinding`,
  `CommunitySignalLintResult`, `lint_community_signal_file`, and
  `render_community_signal_lint_table`.
- Boundary check: no task adds collectors, platform tooling, scraping, source
  acquisition, database changes, import side effects, matcher changes, scoring
  changes, dashboard changes, or product-facing compliance/audit features.
