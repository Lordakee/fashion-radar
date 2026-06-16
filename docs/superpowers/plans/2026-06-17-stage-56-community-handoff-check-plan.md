# Community Handoff Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local-only `community-handoff-check-dir` command that aggregates existing directory lint, candidate preview, and import dry-run checks into one handoff readiness report.

**Architecture:** Implement a thin orchestration module that reuses existing directory linter, candidate preview, and dry-run importer models without changing their behavior. Wire one Typer command to the builder, then update focused tests and docs drift guardrails for the new public command.

**Tech Stack:** Python 3.11+, Typer, Pydantic, pytest, existing community signal/import/candidate modules, Markdown docs. No new dependencies.

---

## File Structure

- Create `src/fashion_radar/community_handoff_check.py`
  - Combined result models, local read-only builder, and table renderer.
- Modify `src/fashion_radar/cli.py`
  - Import the new builder/renderer.
  - Add `CommunityHandoffCheckOutputFormat`.
  - Add `COMMUNITY_HANDOFF_CHECK_FORMAT_OPTION`.
  - Add `community-handoff-check-dir`.
- Create `tests/test_community_handoff_check.py`
  - Unit tests for builder and renderer.
- Modify `tests/test_cli.py`
  - CLI tests for help, JSON/table output, validation, no artifacts, and side-effect boundaries.
- Modify docs:
  - `README.md`
  - `docs/community-signal-import.md`
  - `docs/cli-reference.md`
  - `docs/source-boundaries.md`
  - `docs/architecture.md`
  - `docs/github-upload-checklist.md`
  - `AGENTS.md`
  - `CHANGELOG.md`
- Modify `tests/test_cli_docs.py`
  - Docs drift coverage for the new public command and boundary language.
- Add review artifacts:
  - `docs/reviews/opencode-stage-56-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-56-plan-review.md`
  - `docs/reviews/opencode-stage-56-release-review-prompt.md`
  - `docs/reviews/opencode-stage-56-release-review.md`

No package archive checker changes are planned because ordinary Python modules
under `src/fashion_radar` are already included by the package rule, and Stage 56
does not add package data, schemas, or public example files.

### Task 1: Add Builder And Renderer

**Files:**
- Create: `src/fashion_radar/community_handoff_check.py`
- Test: `tests/test_community_handoff_check.py`

- [ ] **Step 1: Write builder success tests**

Create `tests/test_community_handoff_check.py` with helpers that write a local
two-file CSV directory and minimal config:

```python
from __future__ import annotations

import json
from pathlib import Path

from fashion_radar.community_handoff_check import (
    check_community_handoff_directory,
    render_community_handoff_directory_check_table,
)
from fashion_radar.settings import (
    CandidateDiscoverySettings,
    EntityConfig,
    ScoringSettings,
    load_entity_config,
    load_scoring_config,
)


def _load_candidate_config(
    config_dir: Path,
) -> tuple[ScoringSettings, CandidateDiscoverySettings, EntityConfig | None]:
    scoring_config = load_scoring_config(config_dir / "scoring.yaml")
    entity_path = config_dir / "entities.yaml"
    entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    return scoring_config.scoring, scoring_config.candidate_discovery, entity_config


def _write_config(config_dir: Path) -> None:
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        "version: 1\n"
        "scoring: {}\n"
        "candidate_discovery:\n"
        "  review_min_current_mentions: 1\n"
        "  review_min_distinct_sources: 1\n"
        "  min_single_token_mentions: 1\n"
        "  min_single_token_distinct_sources: 1\n",
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")


def _write_csv_directory(directory: Path) -> None:
    directory.mkdir()
    header = "url,title,published_at,summary,source_name,platform,source_weight,collected_at\n"
    (directory / "first.csv").write_text(
        header
        + "https://example.com/check/the-row,The Row check,2026-06-12T12:00:00Z,"
        + "Synthetic check row,Community Tool Export,community,1.2,2026-06-12T12:05:00Z\n",
        encoding="utf-8",
    )
    (directory / "second.csv").write_text(
        header
        + "https://example.com/check/mesh-flat,Mesh flat check,2026-06-12T13:00:00Z,"
        + "Synthetic mesh row,Community Tool Export,community,1.1,2026-06-12T13:05:00Z\n",
        encoding="utf-8",
    )
```

Add:

```python
def test_check_community_handoff_directory_returns_combined_readiness_report(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    _write_csv_directory(directory)
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name=" Community Tool Export ",
        strict=False,
        limit=0,
    )

    assert result.model_dump_json(indent=2)
    assert result.directory == str(directory)
    assert result.input_format == "csv"
    assert result.pattern == "*.csv"
    assert result.as_of == "2026-06-16T00:00:00+00:00"
    assert result.config_dir == str(config_dir)
    assert result.source_name == "Community Tool Export"
    assert result.execution_mode == "local_read_only"
    assert result.strict is False
    assert result.limit == 0
    assert result.ok is True
    assert result.failed_check_count == 0
    assert result.warning_count == 0
    assert result.findings == []
    assert result.community_signal_lint.file_count == 2
    assert result.community_signal_lint.row_count == 2
    assert result.candidate_preview is not None
    assert result.candidate_preview.file_count == 2
    assert result.candidate_preview.row_count == 2
    assert result.candidate_preview.limit == 0
    assert result.candidate_preview.candidates == []
    assert result.import_dry_run.file_count == 2
    assert result.import_dry_run.valid_file_count == 2
    assert result.import_dry_run.row_count == 2
```

- [ ] **Step 2: Write failure and strict tests**

Add:

```python
def test_check_community_handoff_directory_preserves_lint_and_dry_run_on_candidate_failure(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    directory.mkdir()
    (directory / "bad.csv").write_text(
        "url,title,published_at,author_handle\n"
        "https://example.com/check/bad,Bad row,not-a-date,@raw\n",
        encoding="utf-8",
    )
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=50,
    )

    assert result.ok is False
    assert result.failed_check_count == 3
    assert result.community_signal_lint.error_count > 0
    assert result.candidate_preview is None
    assert result.import_dry_run.error_count > 0
    assert {finding.check for finding in result.findings} == {
        "community_signal_lint",
        "candidate_preview",
        "import_dry_run",
    }
```

Add:

```python
def test_check_community_handoff_directory_strict_warnings_fail_overall_check(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    directory.mkdir()
    (directory / "empty.csv").write_text(
        "url,title,published_at,summary,source_name,platform,source_weight,collected_at\n",
        encoding="utf-8",
    )
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    loose = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=0,
    )
    strict = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=True,
        limit=0,
    )

    assert loose.warning_count == 1
    assert loose.ok is True
    assert strict.warning_count == 1
    assert strict.ok is False
    assert strict.failed_check_count == 1
```

- [ ] **Step 3: Write source-name, JSON key order, and renderer tests**

Add:

```python
def test_check_community_handoff_directory_normalizes_blank_source_name(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    directory.mkdir()
    header = "url,title,published_at,summary,platform,source_weight,collected_at\n"
    (directory / "first.csv").write_text(
        header
        + "https://example.com/check/source-default,Source default check,"
        + "2026-06-12T12:00:00Z,Synthetic row,community,1.2,"
        + "2026-06-12T12:05:00Z\n",
        encoding="utf-8",
    )
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="   ",
        strict=False,
        limit=0,
    )

    assert result.source_name == "Community Tool Export"
    assert result.community_signal_lint.source_name_counts == {"Community Tool Export": 1}
    assert result.import_dry_run.source_name_counts == {"Community Tool Export": 1}
```

Add:

```python
def test_check_result_json_has_stable_top_level_keys(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    _write_csv_directory(directory)
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=0,
    )

    payload = json.loads(result.model_dump_json())

    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "source_name",
        "execution_mode",
        "strict",
        "limit",
        "ok",
        "failed_check_count",
        "warning_count",
        "findings",
        "community_signal_lint",
        "candidate_preview",
        "import_dry_run",
    ]
```

Add:

```python
def test_render_community_handoff_directory_check_table_sanitizes_cells(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals | unsafe"
    _write_config(config_dir)
    _write_csv_directory(directory)
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Source | Name\nWrapped",
        strict=False,
        limit=0,
    )
    lines = render_community_handoff_directory_check_table(result)

    assert lines[0] == "Community handoff directory check."
    assert "Execution mode: local_read_only" in lines
    assert "Directory: " in lines[2]
    assert "|" not in lines[2].split("Directory: ", 1)[1]
    assert "Source name: Source / Name Wrapped" in lines
    assert "Does not import rows or write SQLite." in lines
```

- [ ] **Step 4: Implement `community_handoff_check.py`**

Implement:

```python
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.community_candidates import (
    CommunityCandidateDirectoryPreview,
    preview_community_candidate_directory,
)
from fashion_radar.community_handoff_workflow import DEFAULT_COMMUNITY_SOURCE_NAME
from fashion_radar.community_signals import (
    CommunitySignalDirectoryLintResult,
    lint_community_signal_directory,
)
from fashion_radar.importers.manual_signals import (
    ManualSignalDirectoryDryRunResult,
    ManualSignalFormat,
    ManualSignalImportError,
    dry_run_manual_signal_directory,
)
from fashion_radar.settings import EntityConfig, ScoringSettings, CandidateDiscoverySettings
from fashion_radar.utils.dates import parse_datetime_utc
```

Define:

```python
CommunityHandoffCheckName = Literal[
    "community_signal_lint",
    "candidate_preview",
    "import_dry_run",
    "config",
    "as_of",
]
CommunityHandoffCheckFindingSeverity = Literal["error", "warning", "info"]
COMMUNITY_HANDOFF_CHECK_EXECUTION_MODE = "local_read_only"
```

Define Pydantic models with `ConfigDict(extra="forbid")`:

```python
class CommunityHandoffDirectoryCheckFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: CommunityHandoffCheckFindingSeverity
    code: str
    message: str
    check: CommunityHandoffCheckName


class CommunityHandoffDirectoryCheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directory: str
    input_format: ManualSignalFormat
    pattern: str
    as_of: str
    config_dir: str
    source_name: str
    execution_mode: Literal["local_read_only"] = COMMUNITY_HANDOFF_CHECK_EXECUTION_MODE
    strict: bool = False
    limit: int | None = 50
    ok: bool = False
    failed_check_count: int = 0
    warning_count: int = 0
    findings: list[CommunityHandoffDirectoryCheckFinding] = Field(default_factory=list)
    community_signal_lint: CommunitySignalDirectoryLintResult
    candidate_preview: CommunityCandidateDirectoryPreview | None = None
    import_dry_run: ManualSignalDirectoryDryRunResult
```

Implement:

```python
def check_community_handoff_directory(
    directory: Path,
    *,
    config_dir: Path,
    input_format: ManualSignalFormat,
    pattern: str,
    as_of: str | datetime,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    source_name: str = DEFAULT_COMMUNITY_SOURCE_NAME,
    strict: bool = False,
    limit: int | None = 50,
) -> CommunityHandoffDirectoryCheckResult:
    as_of_value = parse_datetime_utc(as_of)
    source_text = source_name.strip() or DEFAULT_COMMUNITY_SOURCE_NAME
    lint_result = lint_community_signal_directory(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_text,
    )
    candidate_preview = None
    findings: list[CommunityHandoffDirectoryCheckFinding] = []
    try:
        candidate_preview = preview_community_candidate_directory(
            directory,
            input_format=input_format,
            pattern=pattern,
            scoring=scoring,
            settings=settings,
            entity_config=entity_config,
            as_of=as_of_value,
            default_source_name=source_text,
            limit=limit,
        )
    except ManualSignalImportError:
        findings.append(
            CommunityHandoffDirectoryCheckFinding(
                severity="error",
                code="candidate_preview_unavailable",
                message="Candidate preview could not read or validate the handoff directory.",
                check="candidate_preview",
            )
        )
    dry_run_result = dry_run_manual_signal_directory(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_text,
    )
    if lint_result.error_count:
        findings.append(
            CommunityHandoffDirectoryCheckFinding(
                severity="error",
                code="community_signal_lint_failed",
                message="Community signal directory lint reported errors.",
                check="community_signal_lint",
            )
        )
    if strict and lint_result.warning_count:
        findings.append(
            CommunityHandoffDirectoryCheckFinding(
                severity="error",
                code="community_signal_lint_warnings",
                message="Community signal directory lint reported warnings and strict mode is enabled.",
                check="community_signal_lint",
            )
        )
    if dry_run_result.error_count:
        findings.append(
            CommunityHandoffDirectoryCheckFinding(
                severity="error",
                code="import_dry_run_failed",
                message="Import directory dry-run reported errors.",
                check="import_dry_run",
            )
        )
    failed_checks = {finding.check for finding in findings if finding.severity == "error"}
    return CommunityHandoffDirectoryCheckResult(
        directory=str(directory),
        input_format=input_format,
        pattern=pattern,
        as_of=as_of_value.isoformat(),
        config_dir=str(config_dir),
        source_name=source_text,
        strict=strict,
        limit=limit,
        ok=not failed_checks,
        failed_check_count=len(failed_checks),
        warning_count=lint_result.warning_count,
        findings=findings,
        community_signal_lint=lint_result,
        candidate_preview=candidate_preview,
        import_dry_run=dry_run_result,
    )
```

Implement table rendering with compact summary lines:

```python
def render_community_handoff_directory_check_table(
    result: CommunityHandoffDirectoryCheckResult,
) -> list[str]:
    lines = [
        "Community handoff directory check.",
        f"Execution mode: {result.execution_mode}",
        f"Directory: {_table_cell(result.directory)}",
        f"Input format: {result.input_format}",
        f"Pattern: {_table_cell(result.pattern)}",
        f"As of: {result.as_of}",
        f"Config dir: {_table_cell(result.config_dir)}",
        f"Source name: {_table_cell(result.source_name)}",
        f"Strict: {str(result.strict).lower()}",
        f"Limit: {result.limit if result.limit is not None else 'none'}",
        f"Overall: {'ok' if result.ok else 'failed'}",
        f"Failed checks: {result.failed_check_count}",
        f"Warnings: {result.warning_count}",
        (
            "Lint: "
            f"{result.community_signal_lint.file_count} files, "
            f"{result.community_signal_lint.valid_row_count}/"
            f"{result.community_signal_lint.row_count} import-ready rows, "
            f"{result.community_signal_lint.error_count} errors"
        ),
        (
            "Candidate preview: "
            + (
                "unavailable"
                if result.candidate_preview is None
                else (
                    f"{result.candidate_preview.candidate_count} candidates from "
                    f"{result.candidate_preview.row_count} rows"
                )
            )
        ),
        (
            "Import dry-run: "
            f"{result.import_dry_run.valid_file_count}/"
            f"{result.import_dry_run.file_count} valid files, "
            f"{result.import_dry_run.row_count} rows, "
            f"{result.import_dry_run.error_count} errors"
        ),
        "Does not import rows or write SQLite.",
    ]
    if result.findings:
        lines.append("Severity | Check | Code | Message")
        for finding in result.findings:
            lines.append(
                f"{finding.severity} | {_table_cell(finding.check)} | "
                f"{_table_cell(finding.code)} | {_table_cell(finding.message)}"
            )
    else:
        lines.append("No community handoff check findings.")
    return lines


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 5: Run unit tests**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_check.py -q
```

Expected: tests pass.

### Task 2: Add CLI Command And CLI Tests

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add CLI imports/options/command skeleton**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.community_handoff_check import (
    check_community_handoff_directory,
    render_community_handoff_directory_check_table,
)
```

Add output type:

```python
CommunityHandoffCheckOutputFormat = Literal["table", "json"]
```

Add option:

```python
COMMUNITY_HANDOFF_CHECK_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add command near handoff workflow/manifest:

```python
@app.command(name="community-handoff-check-dir")
def community_handoff_check_dir_command(
    directory: Path,
    config_dir: Path = CONFIG_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION,
    as_of: str = COMMUNITY_HANDOFF_WORKFLOW_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    limit: int | None = typer.Option(50, min=0, help="Maximum candidates to print."),
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
    output_format: CommunityHandoffCheckOutputFormat = COMMUNITY_HANDOFF_CHECK_FORMAT_OPTION,
) -> None:
    """Check a local community handoff directory without importing rows."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not check community handoff directory: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
        result = check_community_handoff_directory(
            directory,
            config_dir=config_dir,
            input_format=input_format,
            pattern=pattern,
            as_of=as_of_value,
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            source_name=source_name,
            strict=strict,
            limit=limit,
        )
    except typer.Exit:
        raise
    except ConfigError as exc:
        typer.echo(f"Invalid community handoff check config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"Could not check community handoff directory: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_community_handoff_directory_check_table(result):
            typer.echo(line)
    if not result.ok:
        raise typer.Exit(1)
```

- [ ] **Step 2: Add CLI fixture helpers in `tests/test_cli.py`**

Near existing community handoff tests, add helpers:

```python
def _prepare_community_handoff_check_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        "version: 1\n"
        "scoring: {}\n"
        "candidate_discovery:\n"
        "  review_min_current_mentions: 1\n"
        "  review_min_distinct_sources: 1\n"
        "  min_single_token_mentions: 1\n"
        "  min_single_token_distinct_sources: 1\n",
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    directory = tmp_path / "handoff-dir"
    directory.mkdir()
    header = "url,title,published_at,summary,source_name,platform,source_weight,collected_at\n"
    (directory / "first.csv").write_text(
        header
        + "https://example.com/check/first,The Row check,2026-06-12T12:00:00Z,"
        + "Synthetic row,Community Tool Export,community,1.2,2026-06-12T12:05:00Z\n",
        encoding="utf-8",
    )
    (directory / "second.csv").write_text(
        header
        + "https://example.com/check/second,Mesh flat check,2026-06-12T13:00:00Z,"
        + "Synthetic row,Community Tool Export,community,1.1,2026-06-12T13:05:00Z\n",
        encoding="utf-8",
    )
    return config_dir, data_dir, reports_dir, directory
```

- [ ] **Step 3: Add CLI help and JSON success tests**

Add:

```python
def test_community_handoff_check_dir_help_lists_options() -> None:
    result = CliRunner().invoke(app, ["community-handoff-check-dir", "--help"])

    assert result.exit_code == 0
    assert "Check a local community handoff directory without importing rows." in result.output
    for term in (
        "--config-dir",
        "--input-format",
        "--pattern",
        "--as-of",
        "--source-name",
        "--limit",
        "--strict",
        "--format",
    ):
        assert term in result.output
    assert "--dry-run" not in result.output
    assert "--output-format" not in result.output
```

Add:

```python
def test_community_handoff_check_dir_json_reports_readiness(tmp_path: Path) -> None:
    config_dir, data_dir, reports_dir, directory = _prepare_community_handoff_check_fixture(
        tmp_path
    )

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-check-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "2026-06-16T00:00:00Z",
            "--source-name",
            "Community Tool Export",
            "--limit",
            "0",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["execution_mode"] == "local_read_only"
    assert payload["ok"] is True
    assert payload["failed_check_count"] == 0
    assert payload["community_signal_lint"]["file_count"] == 2
    assert payload["candidate_preview"]["limit"] == 0
    assert payload["import_dry_run"]["valid_file_count"] == 2
    assert not data_dir.exists()
    assert not reports_dir.exists()
```

- [ ] **Step 4: Add CLI failure, strict, config, parser, and table tests**

Add tests that verify:

```python
def test_community_handoff_check_dir_strict_warning_exits_nonzero_but_prints_json(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir, directory = _prepare_community_handoff_check_fixture(
        tmp_path
    )
    for file in directory.glob("*.csv"):
        file.unlink()
    (directory / "empty.csv").write_text(
        "url,title,published_at,summary,source_name,platform,source_weight,collected_at\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-check-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "2026-06-16T00:00:00Z",
            "--strict",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload["warning_count"] == 1
    assert payload["ok"] is False
    assert payload["candidate_preview"] is not None
    assert payload["import_dry_run"]["error_count"] == 0
```

Add invalid file test:

```python
def test_community_handoff_check_dir_reports_invalid_files_without_traceback(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir, directory = _prepare_community_handoff_check_fixture(
        tmp_path
    )
    for file in directory.glob("*.csv"):
        file.unlink()
    (directory / "bad.csv").write_text(
        "url,title,published_at,author_handle\n"
        "https://example.com/check/bad,Bad row,not-a-date,@raw\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-check-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "2026-06-16T00:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1, result.output
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert payload["community_signal_lint"]["error_count"] > 0
    assert payload["candidate_preview"] is None
    assert payload["import_dry_run"]["error_count"] > 0
```

Add table and validation tests:

```python
def test_community_handoff_check_dir_table_output_is_summary_only(tmp_path: Path) -> None:
    config_dir, data_dir, reports_dir, directory = _prepare_community_handoff_check_fixture(
        tmp_path
    )
    result = CliRunner().invoke(
        app,
        [
            "community-handoff-check-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "2026-06-16T00:00:00Z",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Community handoff directory check." in result.output
    assert "Does not import rows or write SQLite." in result.output
    assert "https://example.com/check/first" not in result.output
```

```python
def test_community_handoff_check_dir_invalid_as_of_fails_before_directory_read(
    tmp_path: Path,
) -> None:
    missing_config = tmp_path / "missing-config"
    missing_directory = tmp_path / "missing-directory"

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-check-dir",
            str(missing_directory),
            "--config-dir",
            str(missing_config),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "invalid --as-of" in result.output
    assert "Traceback" not in result.output
```

```python
def test_community_handoff_check_dir_invalid_config_fails_without_reading_directory(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("not: valid: yaml\n", encoding="utf-8")
    directory = tmp_path / "signals"

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-check-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "2026-06-16T00:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid community handoff check config" in result.output
    assert "Traceback" not in result.output
```

Parser guard tests:

```python
def test_community_handoff_check_dir_rejects_negative_limit() -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-handoff-check-dir",
            "signals",
            "--as-of",
            "2026-06-16T00:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output
```

- [ ] **Step 5: Add side-effect guard test**

Add a monkeypatch test that fails if the command calls SQLite, schema, import
storage, collection, report, digest, subprocess, or dashboard paths:

```python
def test_community_handoff_check_dir_does_not_write_runtime_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_dir, data_dir, reports_dir, directory = _prepare_community_handoff_check_fixture(
        tmp_path
    )

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("write path should not be called")

    monkeypatch.setattr("fashion_radar.cli.create_sqlite_engine", forbidden)
    monkeypatch.setattr("fashion_radar.cli.initialize_schema", forbidden)
    monkeypatch.setattr("fashion_radar.cli.store_manual_signal_rows", forbidden)
    monkeypatch.setattr("fashion_radar.cli.collect_configured_sources", forbidden)
    monkeypatch.setattr("fashion_radar.cli.write_daily_report_files", forbidden)
    monkeypatch.setattr("fashion_radar.cli.package_daily_digest", forbidden)
    monkeypatch.setattr("fashion_radar.cli.subprocess.run", forbidden)

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-check-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "2026-06-16T00:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0, result.output
    assert not data_dir.exists()
    assert not reports_dir.exists()
```

- [ ] **Step 6: Run CLI targeted tests**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli.py -q
```

Expected: tests pass.

### Task 3: Documentation And Docs Drift

**Files:**
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Update user-facing docs**

Add `community-handoff-check-dir` to:

- README feature bullet near other handoff commands.
- README external community tool flow near directory handoff commands.
- `docs/community-signal-import.md` near preflight/directory handoff.
- `docs/cli-reference.md` under Local Import And Community Handoff.
- `docs/source-boundaries.md` local-only command boundaries and checklist.
- `docs/architecture.md` flow and manual import/community component section.
- `docs/github-upload-checklist.md` help-loop commands and historical boundary section.
- `AGENTS.md` maintainer guardrail.
- `CHANGELOG.md` Unreleased Added.

Use wording:

```text
`community-handoff-check-dir` is a local-only handoff readiness report for
user-controlled community signal directories. It reads only matched local
regular files and local config, and it does not import rows, open SQLite,
create config/data/report/dashboard/digest artifacts, fetch URLs, log in, call
platform APIs, download media, automate browsers, scrape/crawl, monitor,
watch, schedule, add connectors, acquire sources, prove demand, rank sources,
coverage verification, generate entities, or provide compliance,
policy, authorization, or safety-review features.
```

- [ ] **Step 2: Add docs drift test**

In `tests/test_cli_docs.py`, add a test similar to Stage 54/55 docs tests:

```python
def test_community_handoff_check_dir_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    cli_reference = _read(CLI_REFERENCE)
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")
    changelog = _read(ROOT / "CHANGELOG.md")

    for text in (readme, import_doc, cli_reference, checklist):
        assert "community-handoff-check-dir" in text

    boundary_terms = (
        "local-only handoff readiness",
        "matched local regular files",
        "does not import rows",
        "open SQLite",
        "create config/data/report/dashboard/digest artifacts",
        "fetch URLs",
        "platform APIs",
        "scrape/crawl",
        "monitor",
        "schedule",
        "connectors",
        "source acquisition",
        "demand proof",
        "rank sources",
        "coverage verification",
    )
    for text in (readme, import_doc, boundaries, architecture, agents):
        normalized = _normalized_text(text).casefold()
        assert "community-handoff-check-dir" in normalized
        for term in boundary_terms:
            assert term.casefold() in normalized

    normalized_changelog = _normalized_text(changelog).casefold()
    assert "community-handoff-check-dir" in normalized_changelog
    assert "local-only handoff readiness" in normalized_changelog
```

- [ ] **Step 3: Run docs targeted tests**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: tests pass.

### Task 4: Verification, Review, Commit, And Upload

**Files:**
- Add: `docs/reviews/opencode-stage-56-release-review-prompt.md`
- Add after review: `docs/reviews/opencode-stage-56-release-review.md`
- Modify if needed: files changed by Tasks 1-3 only.

- [ ] **Step 1: Run targeted verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_check.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_cli_docs.py -q
```

Expected: each command exits 0.

- [ ] **Step 2: Run full verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock
```

Expected: each command exits 0.

- [ ] **Step 3: Run release hygiene and smoke checks**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/fashion-radar" community-handoff-check-dir --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Expected: each command exits 0.

- [ ] **Step 4: Request local opencode release review**

Create `docs/reviews/opencode-stage-56-release-review-prompt.md` asking local
opencode with GLM 5.2 to review:

- the new command is local-only and read-only;
- no platform collection/connectors/scraping/browser automation/API/login/
  monitoring/scheduling/ranking/coverage verification/source acquisition was
  added;
- no compliance, legal, approval, authorization, or policy workflow feature was
  added;
- no profile/workflow/manifest ordering changed;
- docs and docs drift tests cover the command;
- `uv.lock` is unchanged and mirror-free.

Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-56-release-review-prompt.md)" > docs/reviews/opencode-stage-56-release-review.md 2> /tmp/opencode-stage56-release-review.err
```

Expected: no Critical or Important findings remain and the review approves
commit/upload.

- [ ] **Step 5: Commit and upload**

Run:

```bash
git status --short
git add src/fashion_radar/community_handoff_check.py src/fashion_radar/cli.py tests/test_community_handoff_check.py tests/test_cli.py tests/test_cli_docs.py README.md docs/community-signal-import.md docs/cli-reference.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md AGENTS.md CHANGELOG.md docs/superpowers/specs/2026-06-17-stage-56-community-handoff-check-design.md docs/superpowers/plans/2026-06-17-stage-56-community-handoff-check-plan.md docs/reviews/opencode-stage-56-plan-review-prompt.md docs/reviews/opencode-stage-56-plan-review.md docs/reviews/opencode-stage-56-release-review-prompt.md docs/reviews/opencode-stage-56-release-review.md
git commit -m "Add community handoff directory check"
```

Upload to `origin/main`. If normal `git push` fails, use the saved token with
the GitHub Git Data API, verify the remote tree matches the local tree, fetch
or reconstruct the remote commit object if needed, and align local
`main`/`origin/main` to the uploaded remote commit.

- [ ] **Step 6: Confirm GitHub Actions**

Use the GitHub API to confirm the workflow run for the uploaded commit completes
successfully.
