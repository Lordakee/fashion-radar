# Community Handoff Manifest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar community-handoff-manifest DIRECTORY`, a local print-only producer manifest for external tools that write sanitized community signal directories.

**Architecture:** A new focused module builds a Pydantic manifest from existing community signal profile constants and the existing community handoff workflow builder. The CLI command only parses options and prints JSON/table output; it does not inspect paths or execute any workflow step.

**Tech Stack:** Python 3.11+, Typer, Pydantic, existing Fashion Radar CLI/test helpers, pytest, Ruff. No new dependencies.

---

## File Structure

- Create `src/fashion_radar/community_handoff_manifest.py`
  - Owns manifest models, builder, filename selection, table renderer, and table-cell sanitization.
- Modify `src/fashion_radar/cli.py`
  - Imports the builder/renderer.
  - Adds `CommunityHandoffManifestOutputFormat`.
  - Registers `community-handoff-manifest`.
- Create `tests/test_community_handoff_manifest.py`
  - Covers model shape, command reuse, filename selection, fallback source name, invalid timestamps, and table rendering.
- Modify `tests/test_cli.py`
  - Adds command help/output/no-side-effect coverage.
- Modify `tests/test_cli_docs.py`
  - Ensures documentation and installed-wheel help loop stay aligned with public CLI commands.
- Modify docs:
  - `README.md`
  - `docs/community-signal-import.md`
  - `docs/source-boundaries.md`
  - `docs/cli-reference.md`
  - `docs/github-upload-checklist.md`
- Add review records:
  - `docs/reviews/claude-code-stage-52-plan-review-prompt.md`
  - `docs/reviews/claude-code-stage-52-plan-review.md`
  - release review prompt/result after implementation.

### Task 1: Manifest Module Tests

**Files:**
- Create: `tests/test_community_handoff_manifest.py`
- Later implementation target: `src/fashion_radar/community_handoff_manifest.py`

- [ ] **Step 1: Write the failing module tests**

Create `tests/test_community_handoff_manifest.py`:

```python
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fashion_radar.community_handoff_manifest import (
    CommunityHandoffManifest,
    build_community_handoff_manifest,
    render_community_handoff_manifest_table,
)


def test_build_community_handoff_manifest_has_stable_directory_contract() -> None:
    manifest = build_community_handoff_manifest(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        input_format="csv",
        pattern="*.csv",
        as_of=datetime(2026, 6, 13, 12, 0, tzinfo=UTC),
        source_name="Community Tool Export",
    )

    payload = manifest.model_dump(mode="json")
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "producer_profile_command",
        "producer_contract_version",
        "supported_input_formats",
        "suggested_filename",
        "matched_file_rule",
        "manifest_storage_note",
        "schema_path",
        "example_paths",
        "csv_header",
        "required_fields",
        "optional_fields",
        "prohibited_fields",
        "json_envelopes",
        "field_notes",
        "field_rules",
        "unsupported_capabilities",
        "workflow",
        "boundaries",
    ]
    assert manifest.contract_version == "community-handoff-manifest/v1"
    assert manifest.execution_mode == "print_only"
    assert manifest.directory == "exports"
    assert manifest.input_format == "csv"
    assert manifest.pattern == "*.csv"
    assert manifest.as_of == "2026-06-13T12:00:00+00:00"
    assert manifest.config_dir == "configs"
    assert manifest.data_dir == "data"
    assert manifest.source_name == "Community Tool Export"
    assert manifest.producer_profile_command == (
        "fashion-radar community-signal-profile --format json"
    )
    assert manifest.producer_contract_version == "community-signals/v1"
    assert manifest.supported_input_formats == ["csv", "json"]
    assert manifest.suggested_filename == "community-signals.csv"
    assert manifest.matched_file_rule == (
        "Downstream lint, preview, and import commands treat matching regular "
        "files directly under the supplied directory as handoff files; they do "
        "not recurse into subdirectories."
    )
    assert manifest.manifest_storage_note == (
        "Do not save this manifest as a matched handoff file. For example, when "
        'using --pattern "*.json", do not save the manifest as a .json file '
        "inside the handoff directory; save it outside the directory or use an "
        "excluded filename/pattern."
    )
    assert manifest.schema_path == "schemas/community-signals.schema.json"
    assert manifest.example_paths == [
        "examples/community-signals.example.csv",
        "examples/community-signals.example.json",
    ]
    assert manifest.csv_header == [
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    ]
    assert manifest.required_fields == ["url", "title", "published_at"]
    assert manifest.optional_fields == [
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    ]
    assert "author_handle" in manifest.prohibited_fields
    assert manifest.json_envelopes == ["top_level_array", "object_with_items_only"]
    assert manifest.field_notes["url"] == (
        "Source URL or stable reference URL for the observed item."
    )
    assert manifest.field_rules["source_weight"] == {
        "exclusive_minimum": 0,
        "maximum": 5,
        "default": 1.0,
    }
    assert manifest.unsupported_capabilities[0] == "scraping"
    assert manifest.workflow.step_count == 5
    assert [step.name for step in manifest.workflow.steps] == [
        "lint_handoff_directory",
        "preview_candidate_phrases",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ]
    assert "Does not inspect the supplied directory." in manifest.boundaries


def test_build_community_handoff_manifest_uses_json_filename_and_quotes_workflow() -> None:
    manifest = build_community_handoff_manifest(
        directory=Path("exports ? # & %"),
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        input_format="json",
        pattern="*.json",
        as_of="2026-06-13T12:00:00Z",
        source_name="Community | Tool Export",
    )

    assert manifest.suggested_filename == "community-signals.json"
    assert manifest.source_name == "Community | Tool Export"
    assert "'exports ? # & %'" in manifest.workflow.steps[0].command
    assert "--pattern '*.json'" in manifest.workflow.steps[0].command
    assert "--source-name 'Community | Tool Export'" in manifest.workflow.steps[0].command
    assert "--config-dir 'config ? # & %'" in manifest.workflow.steps[1].command
    assert "--data-dir 'data ? # & %'" in manifest.workflow.steps[2].command


def test_build_community_handoff_manifest_blank_source_name_uses_workflow_default() -> None:
    manifest = build_community_handoff_manifest(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00Z",
        source_name=" ",
    )

    assert manifest.source_name == "Community Tool Export"
    assert manifest.workflow.source_name == "Community Tool Export"


def test_build_community_handoff_manifest_invalid_as_of_raises() -> None:
    with pytest.raises(ValueError):
        build_community_handoff_manifest(
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            input_format="csv",
            pattern="*.csv",
            as_of="not-a-date",
            source_name="Community Tool Export",
        )


def test_render_community_handoff_manifest_table_sanitizes_cells() -> None:
    manifest = CommunityHandoffManifest(
        contract_version="community-handoff-manifest/v1",
        execution_mode="print_only",
        directory="./exports",
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00+00:00",
        config_dir="./configs",
        data_dir="./data",
        source_name="Community | Tool",
        producer_profile_command="fashion-radar community-signal-profile --format json",
        producer_contract_version="community-signals/v1",
        supported_input_formats=["csv", "json"],
        suggested_filename="community-signals.csv",
        matched_file_rule="Direct | child\nfiles only.",
        manifest_storage_note="Keep manifest | outside\nmatched exports.",
        schema_path="schemas/community-signals.schema.json",
        example_paths=["examples/community-signals.example.csv"],
        csv_header=["url", "title", "published_at"],
        required_fields=["url", "title", "published_at"],
        optional_fields=["summary"],
        prohibited_fields=["author_handle"],
        json_envelopes=["top_level_array"],
        field_notes={"url": "Source | URL"},
        field_rules={"source_weight": {"exclusive_minimum": 0, "maximum": 5, "default": 1}},
        unsupported_capabilities=["scraping"],
        workflow={
            "directory": "./exports",
            "input_format": "csv",
            "pattern": "*.csv",
            "as_of": "2026-06-13T12:00:00+00:00",
            "config_dir": "./configs",
            "data_dir": "./data",
            "source_name": "Community | Tool",
            "execution_mode": "print_only",
            "step_count": 1,
            "steps": [
                {
                    "order": 1,
                    "name": "lint | first",
                    "purpose": "Lint | local\nfiles.",
                    "command": "fashion-radar community-signal-lint-dir ./exports",
                    "suggested_effect": "read_only",
                }
            ],
        },
        boundaries=["Does not inspect | supplied\ndirectory."],
    )

    assert render_community_handoff_manifest_table(manifest) == [
        "Community handoff manifest.",
        "Contract version: community-handoff-manifest/v1",
        "Execution mode: print_only",
        "Workflow commands were not executed.",
        "Directory: ./exports",
        "Input format: csv",
        "Pattern: *.csv",
        "As of: 2026-06-13T12:00:00+00:00",
        "Config dir: ./configs",
        "Data dir: ./data",
        "Source name: Community / Tool",
        "Suggested filename: community-signals.csv",
        "Matched file rule: Direct / child files only.",
        "Manifest storage note: Keep manifest / outside matched exports.",
        "Producer profile command: fashion-radar community-signal-profile --format json",
        "Producer contract version: community-signals/v1",
        "Supported input formats: csv, json",
        "Schema path: schemas/community-signals.schema.json",
        "Example paths: examples/community-signals.example.csv",
        "CSV header: url, title, published_at",
        "Required fields: url, title, published_at",
        "Optional fields: summary",
        "Prohibited fields: author_handle",
        "JSON envelopes: top_level_array",
        "Source weight: >0 and <=5, default 1",
        "Unsupported capabilities: scraping",
        "Workflow steps: 1",
        "Order | Step | Suggested Effect | Purpose | Command",
        "1 | lint / first | read_only | Lint / local files. | "
        "fashion-radar community-signal-lint-dir ./exports",
        "Boundaries:",
        "- Does not inspect / supplied directory.",
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_manifest.py -q
```

Expected: import error because `fashion_radar.community_handoff_manifest` does not exist.

### Task 2: Implement Manifest Module

**Files:**
- Create: `src/fashion_radar/community_handoff_manifest.py`
- Test: `tests/test_community_handoff_manifest.py`

- [ ] **Step 1: Add the module**

Create `src/fashion_radar/community_handoff_manifest.py`:

```python
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.community_handoff_workflow import (
    CommunityHandoffWorkflow,
    build_community_handoff_workflow,
)
from fashion_radar.community_signal_profile import build_community_signal_profile
from fashion_radar.importers.manual_signals import ManualSignalFormat

COMMUNITY_HANDOFF_MANIFEST_CONTRACT_VERSION = "community-handoff-manifest/v1"
COMMUNITY_HANDOFF_MANIFEST_EXECUTION_MODE = "print_only"
COMMUNITY_HANDOFF_MANIFEST_PROFILE_COMMAND = (
    "fashion-radar community-signal-profile --format json"
)
COMMUNITY_HANDOFF_MANIFEST_MATCHED_FILE_RULE = (
    "Downstream lint, preview, and import commands treat matching regular files "
    "directly under the supplied directory as handoff files; they do not recurse "
    "into subdirectories."
)
COMMUNITY_HANDOFF_MANIFEST_STORAGE_NOTE = (
    "Do not save this manifest as a matched handoff file. For example, when "
    'using --pattern "*.json", do not save the manifest as a .json file inside '
    "the handoff directory; save it outside the directory or use an excluded "
    "filename/pattern."
)
COMMUNITY_HANDOFF_MANIFEST_BOUNDARIES = [
    "Prints the local directory handoff manifest only.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not create config, data, report, dashboard, or workflow artifacts.",
    (
        "Does not fetch URLs, search platforms, log in, store cookies, automate "
        "browsers, call platform APIs, monitor communities, schedule work, add "
        "source/platform connectors, prove demand, verify platform coverage, or "
        "rank sources."
    ),
    "Does not provide a compliance-review workflow.",
]


class CommunityHandoffManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: Literal["print_only"]
    directory: str
    input_format: ManualSignalFormat
    pattern: str
    as_of: str
    config_dir: str
    data_dir: str
    source_name: str
    producer_profile_command: str
    producer_contract_version: str
    supported_input_formats: list[str]
    suggested_filename: str
    matched_file_rule: str
    manifest_storage_note: str
    schema_path: str
    example_paths: list[str]
    csv_header: list[str]
    required_fields: list[str]
    optional_fields: list[str]
    prohibited_fields: list[str]
    json_envelopes: list[str]
    field_notes: dict[str, str] = Field(default_factory=dict)
    field_rules: dict[str, dict[str, int | float]] = Field(default_factory=dict)
    unsupported_capabilities: list[str]
    workflow: CommunityHandoffWorkflow
    boundaries: list[str] = Field(default_factory=list)


def build_community_handoff_manifest(
    *,
    directory: Path,
    config_dir: Path,
    data_dir: Path,
    input_format: ManualSignalFormat,
    pattern: str,
    as_of: str | datetime,
    source_name: str,
) -> CommunityHandoffManifest:
    profile = build_community_signal_profile()
    workflow = build_community_handoff_workflow(
        directory=directory,
        config_dir=config_dir,
        data_dir=data_dir,
        input_format=input_format,
        pattern=pattern,
        as_of=as_of,
        source_name=source_name,
    )
    return CommunityHandoffManifest(
        contract_version=COMMUNITY_HANDOFF_MANIFEST_CONTRACT_VERSION,
        execution_mode=COMMUNITY_HANDOFF_MANIFEST_EXECUTION_MODE,
        directory=workflow.directory,
        input_format=workflow.input_format,
        pattern=workflow.pattern,
        as_of=workflow.as_of,
        config_dir=workflow.config_dir,
        data_dir=workflow.data_dir,
        source_name=workflow.source_name,
        producer_profile_command=COMMUNITY_HANDOFF_MANIFEST_PROFILE_COMMAND,
        producer_contract_version=profile.contract_version,
        supported_input_formats=[*profile.supported_input_formats],
        suggested_filename=_suggested_filename(input_format),
        matched_file_rule=COMMUNITY_HANDOFF_MANIFEST_MATCHED_FILE_RULE,
        manifest_storage_note=COMMUNITY_HANDOFF_MANIFEST_STORAGE_NOTE,
        schema_path=profile.schema_path,
        example_paths=[*profile.example_paths],
        csv_header=[*profile.csv_header],
        required_fields=[*profile.required_fields],
        optional_fields=[*profile.optional_fields],
        prohibited_fields=[*profile.prohibited_fields],
        json_envelopes=[*profile.json_envelopes],
        field_notes=dict(profile.field_notes),
        field_rules={
            key: dict(value) for key, value in profile.field_rules.items()
        },
        unsupported_capabilities=[*profile.unsupported_capabilities],
        workflow=workflow,
        boundaries=[*COMMUNITY_HANDOFF_MANIFEST_BOUNDARIES],
    )


def render_community_handoff_manifest_table(
    manifest: CommunityHandoffManifest,
) -> list[str]:
    lines = [
        "Community handoff manifest.",
        f"Contract version: {manifest.contract_version}",
        f"Execution mode: {manifest.execution_mode}",
        "Workflow commands were not executed.",
        f"Directory: {_table_cell(manifest.directory)}",
        f"Input format: {manifest.input_format}",
        f"Pattern: {_table_cell(manifest.pattern)}",
        f"As of: {manifest.as_of}",
        f"Config dir: {_table_cell(manifest.config_dir)}",
        f"Data dir: {_table_cell(manifest.data_dir)}",
        f"Source name: {_table_cell(manifest.source_name)}",
        f"Suggested filename: {_table_cell(manifest.suggested_filename)}",
        f"Matched file rule: {_table_cell(manifest.matched_file_rule)}",
        f"Manifest storage note: {_table_cell(manifest.manifest_storage_note)}",
        f"Producer profile command: {_table_cell(manifest.producer_profile_command)}",
        f"Producer contract version: {manifest.producer_contract_version}",
        f"Supported input formats: {', '.join(manifest.supported_input_formats)}",
        f"Schema path: {manifest.schema_path}",
        f"Example paths: {', '.join(manifest.example_paths)}",
        f"CSV header: {', '.join(manifest.csv_header)}",
        f"Required fields: {', '.join(manifest.required_fields)}",
        f"Optional fields: {', '.join(manifest.optional_fields)}",
        f"Prohibited fields: {', '.join(manifest.prohibited_fields)}",
        f"JSON envelopes: {', '.join(manifest.json_envelopes)}",
        (
            f"Source weight: >{manifest.field_rules['source_weight']['exclusive_minimum']:g} "
            f"and <={manifest.field_rules['source_weight']['maximum']:g}, default "
            f"{manifest.field_rules['source_weight']['default']:g}"
        ),
        f"Unsupported capabilities: {', '.join(manifest.unsupported_capabilities)}",
        f"Workflow steps: {manifest.workflow.step_count}",
        "Order | Step | Suggested Effect | Purpose | Command",
    ]
    for step in manifest.workflow.steps:
        lines.append(
            f"{step.order} | {_table_cell(step.name)} | {step.suggested_effect} | "
            f"{_table_cell(step.purpose)} | {_table_cell(step.command)}"
        )
    lines.append("Boundaries:")
    for boundary in manifest.boundaries:
        lines.append(f"- {_table_cell(boundary)}")
    return lines


def _suggested_filename(input_format: ManualSignalFormat) -> str:
    return f"community-signals.{input_format}"


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 2: Run module tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_manifest.py -q
```

Expected: all tests in `tests/test_community_handoff_manifest.py` pass.

### Task 3: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Add tests near the existing `community-handoff-workflow` tests in `tests/test_cli.py`:

```python
def test_community_handoff_manifest_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["community-handoff-manifest", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--input-format" in result.output
    assert "--pattern" in result.output
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--format" in result.output
    assert "Print a local community handoff producer manifest" in result.output


def test_community_handoff_manifest_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "config dir"
    data_dir = tmp_path / "data dir"

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-manifest",
            str(directory),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--source-name",
            "Community Tool Export",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "producer_profile_command",
        "producer_contract_version",
        "supported_input_formats",
        "suggested_filename",
        "matched_file_rule",
        "manifest_storage_note",
        "schema_path",
        "example_paths",
        "csv_header",
        "required_fields",
        "optional_fields",
        "prohibited_fields",
        "json_envelopes",
        "field_notes",
        "field_rules",
        "unsupported_capabilities",
        "workflow",
        "boundaries",
    ]
    assert payload["contract_version"] == "community-handoff-manifest/v1"
    assert payload["execution_mode"] == "print_only"
    assert payload["directory"] == str(directory)
    assert payload["producer_contract_version"] == "community-signals/v1"
    assert payload["suggested_filename"] == "community-signals.csv"
    assert 'using --pattern "*.json"' in payload["manifest_storage_note"]
    assert "author_handle" in payload["prohibited_fields"]
    assert payload["field_rules"]["source_weight"]["maximum"] == 5
    assert payload["unsupported_capabilities"][0] == "scraping"
    assert list(payload["workflow"]) == [
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "execution_mode",
        "step_count",
        "steps",
    ]
    assert list(payload["workflow"]["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]
    assert payload["workflow"]["step_count"] == 5
    assert payload["workflow"]["steps"][0]["name"] == "lint_handoff_directory"
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_community_handoff_manifest_command_prints_table_without_artifacts(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-manifest",
            str(directory),
            "--input-format",
            "json",
            "--pattern",
            "*.json",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Community handoff manifest." in result.output
    assert "Workflow commands were not executed." in result.output
    assert "Suggested filename: community-signals.json" in result.output
    assert "Manifest storage note:" in result.output
    assert "community-signal-profile --format json" in result.output
    assert "community-signal-lint-dir" in result.output
    assert "community-candidates-dir" in result.output
    assert "import-signals-dir" in result.output
    assert "imported-review-workflow" in result.output
    assert str(directory) in result.output
    assert str(config_dir) in result.output
    assert str(data_dir) in result.output
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_community_handoff_manifest_invalid_as_of_is_clean_error(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-handoff-manifest",
            str(tmp_path / "exports"),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not build community handoff manifest: invalid --as-of" in result.output


def test_community_handoff_manifest_does_not_read_directory_or_run_side_effects(
    tmp_path: Path,
    monkeypatch,
) -> None:
    directory = tmp_path / "exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    guarded_paths = {directory, config_dir, data_dir}

    def fail_side_effect(*args, **kwargs):
        raise AssertionError("side effect should not run")

    def guard_path_method(name: str):
        original = getattr(Path, name)

        def guarded(self: Path, *args, **kwargs):
            if self in guarded_paths:
                raise AssertionError(f"{name} should not inspect supplied paths")
            return original(self, *args, **kwargs)

        monkeypatch.setattr(Path, name, guarded)

    for name in ("exists", "is_dir", "is_file", "iterdir", "glob", "rglob"):
        guard_path_method(name)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail_side_effect)
    monkeypatch.setattr(cli_module, "initialize_schema", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_directory_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_file", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_directory", fail_side_effect)
    monkeypatch.setattr(cli_module, "store_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "collect_configured_sources", fail_side_effect)
    monkeypatch.setattr(cli_module, "write_daily_report_files", fail_side_effect)
    monkeypatch.setattr(cli_module, "package_daily_digest", fail_side_effect)

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-manifest",
            str(directory),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
```

- [ ] **Step 2: Run CLI tests to verify they fail**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py -q -k "community_handoff_manifest"
```

Expected: command is missing.

- [ ] **Step 3: Wire CLI command**

Modify `src/fashion_radar/cli.py`:

```python
from fashion_radar.community_handoff_manifest import (
    build_community_handoff_manifest,
    render_community_handoff_manifest_table,
)
```

Add the output type next to the existing community output format aliases:

```python
CommunityHandoffManifestOutputFormat = Literal["table", "json"]
```

Register the command after `community_handoff_workflow_command`:

```python
@app.command(name="community-handoff-manifest")
def community_handoff_manifest_command(
    directory: str,
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION,
    as_of: str = COMMUNITY_HANDOFF_WORKFLOW_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    output_format: CommunityHandoffManifestOutputFormat = (
        COMMUNITY_HANDOFF_WORKFLOW_FORMAT_OPTION
    ),
) -> None:
    """Print a local community handoff producer manifest without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build community handoff manifest: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        manifest = build_community_handoff_manifest(
            directory=Path(directory),
            config_dir=config_dir,
            data_dir=data_dir,
            input_format=input_format,
            pattern=pattern,
            as_of=as_of_value,
            source_name=source_name,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build community handoff manifest: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(manifest.model_dump_json(indent=2))
        return
    for line in render_community_handoff_manifest_table(manifest):
        typer.echo(line)
```

- [ ] **Step 4: Run focused CLI tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_manifest.py tests/test_cli.py -q -k "community_handoff_manifest"
```

Expected: focused tests pass.

### Task 4: Documentation And Release Checklist

**Files:**
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Update docs and docs tests**

Make these concrete documentation changes:

- In README's external community tools quickstart, add:

```bash
uv run fashion-radar community-handoff-manifest "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
```

- In README's explanatory text, add one paragraph stating
  `community-handoff-manifest` is local and print-only, and describes directory,
  file pattern, suggested filename, contract pointers, and workflow commands.
- In `docs/community-signal-import.md`, add a "Directory Manifest" subsection
  after "Producer Profile" with table and JSON examples.
- In that subsection, explicitly say a saved manifest file should live outside
  the matched export directory or use a filename excluded by `--pattern`,
  especially for JSON export directories using `--pattern "*.json"`.
- In `docs/source-boundaries.md`, add a boundary paragraph for
  `community-handoff-manifest`.
- In `docs/source-boundaries.md`, also add a README Requirements bullet for
  `community-handoff-manifest`.
- In `docs/cli-reference.md`, list `community-handoff-manifest` near
  `community-handoff-workflow`.
- In `docs/github-upload-checklist.md`, add the command to the installed-wheel
  help loop and add a small installed-wheel JSON smoke:

```bash
"$tmp_env/venv/bin/fashion-radar" community-handoff-manifest --help
"$tmp_env/venv/bin/fashion-radar" community-handoff-manifest "$tmp_run/missing ? # & %" --input-format csv --pattern "*.csv" --config-dir "$tmp_run/config ? # & %" --data-dir "$tmp_run/data ? # & %" --as-of "2026-06-13T12:00:00Z" --format json
```

- In `tests/test_cli_docs.py`, extend `test_community_signal_profile_docs_are_linked`
  or add a new test that asserts README, CLI reference, import doc, checklist,
  and source boundaries include `community-handoff-manifest`.

- [ ] **Step 2: Run docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: docs tests pass.

### Task 5: Full Verification, Review, Commit, Upload

**Files:**
- Add release review records under `docs/reviews/`.
- No product code changes unless verification or review finds defects.

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_manifest.py tests/test_cli.py tests/test_cli_docs.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
tmp_build="$(mktemp -d)" && UV_NO_CONFIG=1 uv build --out-dir "$tmp_build" && UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Expected: every command exits 0.

- [ ] **Step 3: Request local Claude Code release review**

Create `docs/reviews/claude-code-stage-52-release-review-prompt.md` with:

```markdown
Please review Stage 52 for Critical/Important issues.

Objective: add `fashion-radar community-handoff-manifest DIRECTORY`, a local
print-only producer manifest for external tools that write sanitized community
signal directories.

Review scope:
- `src/fashion_radar/community_handoff_manifest.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_handoff_manifest.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/community-signal-import.md`
- `docs/source-boundaries.md`
- `docs/cli-reference.md`
- `docs/github-upload-checklist.md`
- Stage 52 spec/plan docs

Check especially:
1. The new command is truly print-only and does not inspect directories, execute
   subprocesses, open SQLite, create artifacts, or use network/platform APIs.
2. The manifest fills a real local producer-contract gap beyond
   `community-signal-profile` and `community-handoff-workflow` without adding
   scraping/crawling/browser/account/cookie/session/API connectors.
3. JSON key order and table output are stable enough for external tools.
4. Docs and release checklist are synchronized with the public CLI command.
5. Tests cover invalid timestamps, JSON/table output, no side effects, and docs.

Verification already run:
- paste concise command results here
```

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-52-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-52-release-review.md
```

Expected: no Critical or Important findings. Fix any Critical/Important finding
and rerun the release review before committing.

- [ ] **Step 4: Commit and upload**

Run:

```bash
git status --short
git add README.md docs/community-signal-import.md docs/source-boundaries.md docs/cli-reference.md docs/github-upload-checklist.md docs/reviews/claude-code-stage-52-*.md docs/superpowers/specs/2026-06-16-stage-52-community-handoff-manifest-design.md docs/superpowers/plans/2026-06-16-stage-52-community-handoff-manifest-plan.md src/fashion_radar/cli.py src/fashion_radar/community_handoff_manifest.py tests/test_community_handoff_manifest.py tests/test_cli.py tests/test_cli_docs.py
git commit -m "Add community handoff manifest"
```

Upload with normal authenticated `git push` first. If the known TLS failure
recurs, use the already proven GitHub Git Data API path with the stored token
from `/home/ubuntu/.config/fashion-radar/github-token` without printing the
token.

- [ ] **Step 5: Confirm GitHub Actions**

After upload, confirm the new `origin/main` SHA and GitHub Actions result for
that SHA. Expected: Actions complete successfully.

## Plan Self-Review

- Spec coverage: the tasks cover the new module, CLI, tests, docs, review,
  verification, commit, and upload.
- Placeholder scan: no `TBD`, `TODO`, or underspecified implementation steps
  remain.
- Type consistency: the command, type aliases, builder, model names, and test
  references consistently use `community_handoff_manifest` /
  `CommunityHandoffManifest`.
