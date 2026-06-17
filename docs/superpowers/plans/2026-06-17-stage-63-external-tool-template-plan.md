# Stage 63 External Tool Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local, print-only `fashion-radar external-tool-template` command that prints adapter-specific sanitized CSV/JSON community handoff template rows for user-controlled external/community tools.

**Architecture:** Create a focused template module that reuses the Stage 62 external tool adapter registry as its source of adapter metadata. The new CLI command renders one adapter template, or one row per adapter when `--adapter` is omitted, to table, importable JSON, or importable CSV on stdout only and does not read directories, write files, validate/import rows, open SQLite, run upstream tools, or perform platform collection.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, pytest, ruff, existing `uv --no-config` workflow.

---

## File Structure

- Create `src/fashion_radar/external_tool_templates.py`: template models, deterministic builder, table renderer, importable JSON renderer, and CSV renderer.
- Modify `src/fashion_radar/cli.py`: import template helpers, add output format alias, register `external-tool-template`.
- Create `tests/test_external_tool_templates.py`: unit tests for model shape, adapter alignment, row validity, rendering, CSV quoting, and invalid adapter/timestamp behavior.
- Modify `tests/test_cli.py`: CLI smoke tests for JSON, CSV, table output, unknown adapter, and invalid `--as-of`.
- Modify `scripts/check_first_run_smoke.py`: validate `external-tool-template --adapter rednote_mcp --format json` as importable `{"items": [...]}` JSON.
- Modify `tests/test_first_run_smoke.py`: fake-command sequence and validator coverage for the new smoke command.
- Modify `tests/test_cli_docs.py`: docs-drift tests for the new command and boundary language.
- Modify docs: `README.md`, `docs/community-signal-import.md`, `docs/community-signal-quality.md`, `docs/source-boundaries.md`, `docs/architecture.md`, `docs/cli-reference.md`, `docs/github-upload-checklist.md`, `AGENTS.md`, and `CHANGELOG.md`.
- Add review artifacts under `docs/reviews/`.

## Task 1: Template Module

**Files:**
- Create: `src/fashion_radar/external_tool_templates.py`
- Create: `tests/test_external_tool_templates.py`

- [ ] **Step 1: Write failing template shape tests**

Create `tests/test_external_tool_templates.py` with tests that import:

```python
from pathlib import Path
import json

import pytest
from pydantic import ValidationError

from fashion_radar.community_signals import lint_community_signal_file
from fashion_radar.external_tool_templates import (
    ExternalToolTemplate,
    build_external_tool_template,
    build_external_tool_template_collection,
    render_external_tool_template_csv,
    render_external_tool_template_json,
    render_external_tool_template_table,
)
```

Add this test:

```python
def test_template_has_stable_contract_and_instaloader_metadata() -> None:
    template = build_external_tool_template(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )
    payload = template.model_dump(mode="json")
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "adapter_id",
        "display_name",
        "platform_label",
        "source_name",
        "recommended_input_format",
        "recommended_pattern",
        "suggested_export_directory",
        "csv_header",
        "items",
        "field_mappings",
        "recommended_commands",
        "boundaries",
    ]
    assert template.contract_version == "external-tool-template/v1"
    assert template.execution_mode == "print_only"
    assert template.adapter_id == "instaloader"
    assert template.platform_label == "instagram"
    assert template.source_name == "Instaloader Export"
    assert template.recommended_input_format == "json"
    assert template.recommended_pattern == "*.json"
    assert template.suggested_export_directory == "exports"
    assert template.csv_header == [
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    ]
    assert [item["source_name"] for item in template.items] == ["Instaloader Export"] * 2
    assert [item["platform"] for item in template.items] == ["instagram"] * 2
    assert template.items[0]["published_at"] == "2026-06-13T12:00:00+00:00"
    assert template.items[0]["collected_at"] == "2026-06-13T12:15:00+00:00"
```

Add this validity test:

```python
def test_template_rows_lint_cleanly_when_written_as_json_and_csv(tmp_path: Path) -> None:
    template = build_external_tool_template(
        adapter_id="tiktok_api",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    rows_path = tmp_path / "items.json"
    rows_path.write_text(render_external_tool_template_json(template), encoding="utf-8")
    rows_result = lint_community_signal_file(rows_path, input_format="json")
    assert rows_result.ok is True
    assert rows_result.valid_row_count == 2

    csv_path = tmp_path / "template.csv"
    csv_path.write_text(render_external_tool_template_csv(template), encoding="utf-8")
    csv_result = lint_community_signal_file(csv_path, input_format="csv")
    assert csv_result.ok is True
    assert csv_result.valid_row_count == 2
```

Add renderer/error tests:

```python
def test_template_json_renderer_outputs_importable_items_only() -> None:
    template = build_external_tool_template(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )
    payload = json.loads(render_external_tool_template_json(template))
    assert list(payload) == ["items"]
    assert payload["items"] == template.items


def test_template_collection_includes_two_rows_per_adapter_when_unfiltered() -> None:
    collection = build_external_tool_template_collection(
        adapter_id=None,
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )
    assert [template.adapter_id for template in collection.templates] == [
        "rednote_mcp",
        "xiaohongshu_crawler",
        "instaloader",
        "tiktok_api",
        "yt_dlp",
        "x_search_export",
        "generic_community_export",
    ]
    assert len(collection.items) == 14


def test_template_csv_renderer_uses_header_order_and_quotes_cells() -> None:
    template = build_external_tool_template(
        adapter_id="x_search_export",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )
    csv_text = render_external_tool_template_csv(template)
    assert csv_text.splitlines()[0] == (
        "url,title,published_at,summary,source_name,platform,source_weight,collected_at"
    )
    assert "X Search Export" in csv_text
    assert "x" in csv_text


def test_template_table_renderer_sanitizes_cells() -> None:
    template = ExternalToolTemplate(
        contract_version="external-tool-template/v1",
        execution_mode="print_only",
        adapter_id="tool|one",
        display_name="Tool | One",
        platform_label="platform|one",
        source_name="Source | One",
        recommended_input_format="csv",
        recommended_pattern="*.csv",
        suggested_export_directory="./exports",
        csv_header=["url", "title", "published_at"],
        items=[
            {
                "url": "https://example.com/a",
                "title": "Title | One",
                "published_at": "2026-06-13T12:00:00+00:00",
            }
        ],
        field_mappings=[],
        recommended_commands=["fashion-radar community-signal-profile --format json"],
        boundaries=["No platform | collection."],
    )
    lines = render_external_tool_template_table(template)
    assert "Adapter: tool/one" in lines
    assert "- title: Title / One" in lines
    assert "- No platform / collection." in lines


def test_template_rejects_unknown_adapter_and_invalid_as_of() -> None:
    with pytest.raises(ValueError, match="Unknown external tool adapter: missing"):
        build_external_tool_template(
            adapter_id="missing",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
        )
    with pytest.raises(ValueError):
        build_external_tool_template(
            adapter_id="instaloader",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="not-a-date",
        )


def test_template_model_rejects_extra_fields_and_missing_required_fields() -> None:
    payload = build_external_tool_template(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    ).model_dump(mode="json")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ExternalToolTemplate.model_validate({**payload, "unexpected": "value"})

    without_contract_version = {
        key: value for key, value in payload.items() if key != "contract_version"
    }
    with pytest.raises(ValidationError, match="Field required"):
        ExternalToolTemplate.model_validate(without_contract_version)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_templates.py -q
```

Expected: fail because the module does not exist.

- [ ] **Step 3: Implement template models and builder**

Create `src/fashion_radar/external_tool_templates.py` with:

```python
from __future__ import annotations

import csv
import io
from datetime import timedelta
from pathlib import Path
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.external_tool_adapters import (
    DEFAULT_ADAPTER_AS_OF,
    DEFAULT_EXPORT_DIRECTORY,
    ExternalToolAdapterFieldMapping,
    build_external_tool_adapter_registry,
)
from fashion_radar.importers.manual_signals import ManualSignalFormat
from fashion_radar.utils.dates import parse_datetime_utc

EXTERNAL_TOOL_TEMPLATE_CONTRACT_VERSION = "external-tool-template/v1"
EXTERNAL_TOOL_TEMPLATE_EXECUTION_MODE = "print_only"

EXTERNAL_TOOL_TEMPLATE_BOUNDARIES = [
    "Prints adapter-specific template rows only.",
    "Does not write files, inspect directories, read handoff files, validate files, import rows, or open SQLite.",
    "Does not run adapters or upstream tools.",
    (
        "Does not fetch URLs, search platforms, log in, store cookies, automate "
        "browsers, call platform APIs, download media, monitor communities, "
        "schedule work, acquire sources, prove demand, rank sources, or verify "
        "platform coverage."
    ),
    "Does not provide a compliance-review workflow.",
]


class ExternalToolTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: Literal["print_only"]
    adapter_id: str
    display_name: str
    platform_label: str
    source_name: str
    recommended_input_format: ManualSignalFormat
    recommended_pattern: str
    suggested_export_directory: str
    csv_header: list[str]
    items: list[dict[str, str | float]] = Field(default_factory=list)
    field_mappings: list[ExternalToolAdapterFieldMapping] = Field(default_factory=list)
    recommended_commands: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


class ExternalToolTemplateCollection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    templates: list[ExternalToolTemplate]

    @property
    def csv_header(self) -> list[str]:
        if not self.templates:
            return []
        return [*self.templates[0].csv_header]

    @property
    def items(self) -> list[dict[str, str | float]]:
        return [item for template in self.templates for item in template.items]
```

Implement:

```python
def build_external_tool_template(
    *,
    adapter_id: str,
    directory: Path = Path(DEFAULT_EXPORT_DIRECTORY),
    config_dir: Path = Path("./configs"),
    data_dir: Path = Path("./data"),
    as_of: str = DEFAULT_ADAPTER_AS_OF,
) -> ExternalToolTemplate:
    registry = build_external_tool_adapter_registry(
        directory=directory,
        config_dir=config_dir,
        data_dir=data_dir,
        as_of=as_of,
    )
    try:
        adapter = registry.adapter_by_id(adapter_id)
    except KeyError as exc:
        raise ValueError(f"Unknown external tool adapter: {adapter_id}") from exc
    csv_header = [mapping.field for mapping in adapter.field_mappings]
    as_of_dt = parse_datetime_utc(as_of)
    return ExternalToolTemplate(
        contract_version=EXTERNAL_TOOL_TEMPLATE_CONTRACT_VERSION,
        execution_mode=EXTERNAL_TOOL_TEMPLATE_EXECUTION_MODE,
        adapter_id=adapter.id,
        display_name=adapter.display_name,
        platform_label=adapter.platform_label,
        source_name=adapter.suggested_source_name,
        recommended_input_format=adapter.recommended_input_format,
        recommended_pattern=adapter.recommended_pattern,
        suggested_export_directory=adapter.suggested_export_directory,
        csv_header=csv_header,
        items=_template_items(
            adapter_id=adapter.id,
            platform_label=adapter.platform_label,
            source_name=adapter.suggested_source_name,
            as_of_dt=as_of_dt,
        ),
        field_mappings=[*adapter.field_mappings],
        recommended_commands=[*adapter.recommended_commands],
        boundaries=[*EXTERNAL_TOOL_TEMPLATE_BOUNDARIES],
    )


def build_external_tool_template_collection(
    *,
    adapter_id: str | None,
    directory: Path = Path(DEFAULT_EXPORT_DIRECTORY),
    config_dir: Path = Path("./configs"),
    data_dir: Path = Path("./data"),
    as_of: str = DEFAULT_ADAPTER_AS_OF,
) -> ExternalToolTemplateCollection:
    registry = build_external_tool_adapter_registry(
        directory=directory,
        config_dir=config_dir,
        data_dir=data_dir,
        as_of=as_of,
    )
    if adapter_id is None:
        adapter_ids = [adapter.id for adapter in registry.adapters]
    else:
        try:
            registry.adapter_by_id(adapter_id)
        except KeyError as exc:
            raise ValueError(f"Unknown external tool adapter: {adapter_id}") from exc
        adapter_ids = [adapter_id]
    return ExternalToolTemplateCollection(
        templates=[
            build_external_tool_template(
                adapter_id=known_adapter_id,
                directory=directory,
                config_dir=config_dir,
                data_dir=data_dir,
                as_of=as_of,
            )
            for known_adapter_id in adapter_ids
        ]
    )
```

Implement deterministic rows:

```python
def _template_items(
    *,
    adapter_id: str,
    platform_label: str,
    source_name: str,
    as_of_dt,
) -> list[dict[str, str | float]]:
    first = as_of_dt
    second = as_of_dt + timedelta(hours=1)
    return [
        {
            "url": f"https://example.com/external-tool-template/{adapter_id}/the-row-bag",
            "title": f"{source_name} The Row bag observed signal",
            "published_at": first.isoformat(),
            "summary": (
                "Synthetic sanitized observation about The Row bag interest from a "
                "user-controlled external/community tool."
            ),
            "source_name": source_name,
            "platform": platform_label,
            "source_weight": 1.2,
            "collected_at": (first + timedelta(minutes=15)).isoformat(),
        },
        {
            "url": f"https://example.com/external-tool-template/{adapter_id}/silver-flat-shoe",
            "title": f"{source_name} silver flat shoe observed signal",
            "published_at": second.isoformat(),
            "summary": (
                "Synthetic sanitized observation about silver flat shoes and styling "
                "from a user-controlled external/community tool."
            ),
            "source_name": source_name,
            "platform": platform_label,
            "source_weight": 1.1,
            "collected_at": (second + timedelta(minutes=15)).isoformat(),
        },
    ]
```

- [ ] **Step 4: Implement renderers**

Add:

```python
def render_external_tool_template_json(
    template_or_collection: ExternalToolTemplate | ExternalToolTemplateCollection,
) -> str:
    return json.dumps({"items": template_or_collection.items}, indent=2) + "\n"


def render_external_tool_template_csv(
    template_or_collection: ExternalToolTemplate | ExternalToolTemplateCollection,
) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer, fieldnames=template_or_collection.csv_header, lineterminator="\n"
    )
    writer.writeheader()
    for item in template_or_collection.items:
        writer.writerow({field: item.get(field, "") for field in template_or_collection.csv_header})
    return buffer.getvalue()


def render_external_tool_template_table(
    template_or_collection: ExternalToolTemplate | ExternalToolTemplateCollection,
) -> list[str]:
    templates = (
        template_or_collection.templates
        if isinstance(template_or_collection, ExternalToolTemplateCollection)
        else [template_or_collection]
    )
    if len(templates) != 1:
        lines = [
            "External tool templates.",
            f"Templates: {len(templates)}",
        ]
        for template in templates:
            lines.append(f"Adapter: {_table_cell(template.adapter_id)}")
            for item in template.items:
                lines.append(f"- {item['title']}")
        return lines
    template = templates[0]
    lines = [
        "External tool template.",
        f"Contract version: {template.contract_version}",
        f"Execution mode: {template.execution_mode}",
        f"Adapter: {_table_cell(template.adapter_id)}",
        f"Platform: {_table_cell(template.platform_label)}",
        f"Source name: {_table_cell(template.source_name)}",
        f"Recommended format: {template.recommended_input_format}",
        f"Recommended pattern: {_table_cell(template.recommended_pattern)}",
        f"Suggested directory: {_table_cell(template.suggested_export_directory)}",
        f"CSV header: {', '.join(template.csv_header)}",
        "Items:",
    ]
    for index, item in enumerate(template.items, start=1):
        lines.append(f"Item {index}:")
        for field in template.csv_header:
            if field in item:
                lines.append(f"- {field}: {_table_cell(str(item[field]))}")
    lines.append("Recommended commands:")
    for command in template.recommended_commands:
        lines.append(f"- {_table_cell(command)}")
    lines.append("Boundaries:")
    for boundary in template.boundaries:
        lines.append(f"- {_table_cell(boundary)}")
    return lines


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_templates.py -q
```

Expected: pass.

## Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

In `tests/test_cli.py`, add:

```python
def test_external_tool_template_command_prints_json() -> None:
    result = CliRunner().invoke(
        app,
        ["external-tool-template", "--adapter", "instaloader", "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == ["items"]
    assert payload["items"][0]["source_name"] == "Instaloader Export"
    assert payload["items"][0]["platform"] == "instagram"
    assert "adapter_id" not in payload["items"][0]


def test_external_tool_template_command_prints_csv() -> None:
    result = CliRunner().invoke(
        app,
        ["external-tool-template", "--adapter", "x_search_export", "--format", "csv"],
    )

    assert result.exit_code == 0
    assert result.output.splitlines()[0] == (
        "url,title,published_at,summary,source_name,platform,source_weight,collected_at"
    )
    assert "X Search Export" in result.output
    assert ",x," in result.output


def test_external_tool_template_command_prints_all_adapters_when_unfiltered() -> None:
    result = CliRunner().invoke(app, ["external-tool-template", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == ["items"]
    assert len(payload["items"]) == 14
    assert {item["platform"] for item in payload["items"]} >= {"rednote", "instagram", "tiktok"}


def test_external_tool_template_command_prints_table() -> None:
    result = CliRunner().invoke(app, ["external-tool-template", "--adapter", "rednote_mcp"])

    assert result.exit_code == 0
    assert "External tool template." in result.output
    assert "Contract version: external-tool-template/v1" in result.output
    assert "Adapter: rednote_mcp" in result.output
    assert "Source name: Rednote MCP Export" in result.output


def test_external_tool_template_command_rejects_unknown_adapter() -> None:
    result = CliRunner().invoke(app, ["external-tool-template", "--adapter", "missing"])

    assert result.exit_code == 1
    assert (
        "Could not build external tool template: Unknown external tool adapter: missing"
        in result.output
    )


def test_external_tool_template_command_rejects_invalid_as_of() -> None:
    result = CliRunner().invoke(
        app,
        [
            "external-tool-template",
            "--adapter",
            "instaloader",
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not build external tool template:" in result.output
```

- [ ] **Step 2: Run CLI tests to verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q
```

Expected: fail because the command is not wired.

- [ ] **Step 3: Wire CLI command**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.external_tool_templates import (
    build_external_tool_template,
    render_external_tool_template_csv,
    render_external_tool_template_json,
    render_external_tool_template_table,
)
```

Add type alias:

```python
ExternalToolTemplateOutputFormat = Literal["table", "json", "csv"]
```

Add option:

```python
EXTERNAL_TOOL_TEMPLATE_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add command after `external-tool-adapters`:

```python
@app.command(name="external-tool-template")
def external_tool_template_command(
    adapter: str | None = typer.Option(None, "--adapter", help="Adapter id to print a template for."),
    directory: str = typer.Option(
        DEFAULT_EXPORT_DIRECTORY,
        "--directory",
        help="Suggested local export directory used in printed commands only.",
    ),
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    as_of: str = typer.Option(
        DEFAULT_ADAPTER_AS_OF,
        "--as-of",
        help="UTC timestamp used in template rows and printed commands only.",
    ),
    output_format: ExternalToolTemplateOutputFormat = EXTERNAL_TOOL_TEMPLATE_FORMAT_OPTION,
) -> None:
    """Print one adapter's local handoff template without writing files."""
    try:
        template = build_external_tool_template_collection(
            adapter_id=adapter,
            directory=Path(directory),
            config_dir=Path(config_dir),
            data_dir=Path(data_dir),
            as_of=as_of,
        )
    except ValueError as exc:
        typer.echo(f"Could not build external tool template: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(render_external_tool_template_json(template), nl=False)
        return
    if output_format == "csv":
        typer.echo(render_external_tool_template_csv(template), nl=False)
        return
    for line in render_external_tool_template_table(template):
        typer.echo(line)
```

- [ ] **Step 4: Run focused CLI tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_templates.py tests/test_cli.py -q
```

Expected: pass.

## Task 3: Smoke Tests And Docs Drift

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add first-run smoke validator**

In `scripts/check_first_run_smoke.py`, add:

```python
def validate_external_tool_template(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} keys", list(payload), ["items"])
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise SmokeError(f"{command_name} items must be a non-empty list")
    first_item = items[0]
    if not isinstance(first_item, dict):
        raise SmokeError(f"{command_name} first item must be a JSON object")
    assert_equal(f"{command_name} first item platform", first_item.get("platform"), "rednote")
```

In `run_first_run_flow`, after `external-tool-adapters`, add:

```python
external_tool_template = validate_json_output(
    "external-tool-template",
    run_cli(
        context,
        "external-tool-template",
        "--adapter",
        "rednote_mcp",
        "--format",
        "json",
    ).stdout,
)
validate_external_tool_template("external-tool-template", external_tool_template)
```

- [ ] **Step 2: Update first-run smoke tests**

In `tests/test_first_run_smoke.py`, update the fake command sequence to include:

```python
(
    "external-tool-template",
    "--adapter",
    "rednote_mcp",
    "--format",
    "json",
)
```

Also update the `stdout_by_command` fake output map with an
`"external-tool-template"` entry:

```python
"external-tool-template": json.dumps(
    {
        "items": [
            {
                "url": "https://example.com/external-tool-template/rednote_mcp/the-row-bag",
                "title": "Rednote MCP Export The Row bag observed signal",
                "published_at": "2026-06-13T12:00:00+00:00",
                "summary": "Synthetic sanitized observation about The Row bag interest.",
                "source_name": "Rednote MCP Export",
                "platform": "rednote",
                "source_weight": 1.2,
                "collected_at": "2026-06-13T12:15:00+00:00",
            }
        ]
    }
),
```

Because the new command is inserted after `external-tool-adapters`, update the
hardcoded captured command assertions that currently reference later positions:

```python
external_tool_adapters = captured[3]
external_tool_template = captured[4]
...
assert captured[16] == (...)
assert captured[17] == (...)
assert captured[18] == (...)
assert captured[19] == (...)
```

Do not leave the old post-insertion assertions at indices `15`, `16`, `17`,
or `18`; they must shift by one when `external-tool-template` is added.

Add payload fixture/validator coverage equivalent to:

```python
smoke.validate_external_tool_template(
    "external-tool-template",
    {
        "items": [{"platform": "rednote"}],
    },
)
```

- [ ] **Step 3: Add docs-drift tests**

In `tests/test_cli_docs.py`, add:

```python
def test_external_tool_template_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    quality_doc = _read(ROOT / "docs" / "community-signal-quality.md")
    cli_reference = _read(CLI_REFERENCE)
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")
    changelog = _read(ROOT / "CHANGELOG.md")

    for text in (
        readme,
        import_doc,
        quality_doc,
        cli_reference,
        checklist,
        boundaries,
        architecture,
        agents,
        changelog,
    ):
        normalized = _normalized_text(text).casefold()
        assert "external-tool-template" in normalized
        assert "adapter-specific template rows" in normalized
        assert "sanitized CSV/JSON local file handoff" in normalized

    for command in (
        "fashion-radar external-tool-template --adapter instaloader --format table",
        "fashion-radar external-tool-template --adapter instaloader --format json",
        "fashion-radar external-tool-template --adapter instaloader --format csv",
    ):
        assert command in cli_reference
        assert command in checklist

    assert "external-tool-template" in _upload_checklist_help_loop_commands()
    assert '"$tmp_env/venv/bin/fashion-radar" external-tool-template --help' in checklist
    assert (
        '"$tmp_env/venv/bin/fashion-radar" external-tool-template '
        '--adapter instaloader --format json'
    ) in checklist

    boundary_terms = (
        "local",
        "print-only",
        "sanitized CSV/JSON local file handoff",
        "user-controlled external/community tools",
        "not platform collection",
        "no connectors",
        "no scraping",
        "no browser automation",
        "no platform APIs",
        "no monitoring",
        "no scheduling",
        "no source acquisition",
        "no demand proof",
        "no ranking",
        "no coverage verification",
    )
    for doc_text in (readme, import_doc, quality_doc, boundaries, architecture, agents):
        normalized = _normalized_text(doc_text).casefold()
        for term in boundary_terms:
            assert term.casefold() in normalized

    normalized_changelog = _normalized_text(changelog).casefold()
    for term in boundary_terms:
        assert term.casefold() in normalized_changelog
```

- [ ] **Step 4: Run focused smoke/docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_cli_docs.py -q
```

Expected: fail until docs are updated.

## Task 4: Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update docs with exact command examples**

Add these command examples anywhere the Stage 62 adapter registry examples are described:

```bash
fashion-radar external-tool-template --adapter instaloader --format table
fashion-radar external-tool-template --adapter instaloader --format json
fashion-radar external-tool-template --adapter instaloader --format csv
```

Use this description consistently:

```text
`external-tool-template` prints adapter-specific template rows for sanitized
CSV/JSON local file handoff by user-controlled external/community tools.
```

Use this boundary wording consistently:

```text
It is local and print-only. It is not platform collection and has no connectors,
no scraping, no browser automation, no platform APIs, no monitoring, no
scheduling, no source acquisition, no demand proof, no ranking, and no coverage
verification.
```

Mention that the command does not write files, read handoff files, validate
files, import rows, open SQLite, run upstream tools, fetch URLs, log in, store
cookies, download media, or provide a compliance-review workflow.

- [ ] **Step 2: Update upload checklist command loop**

In `docs/github-upload-checklist.md`, add `external-tool-template` to the
installed command help loop near `external-tool-adapters`.

Add installed smoke examples:

```bash
"$tmp_env/venv/bin/fashion-radar" external-tool-template --help
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format json
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format csv
```

- [ ] **Step 3: Run docs-focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

Expected: pass after docs are updated.

## Task 5: Review, Verification, Commit, Push

**Files:**
- Create: `docs/reviews/opencode-stage-63-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-63-plan-review.md`
- Create: `docs/reviews/opencode-stage-63-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-63-release-review.md`

- [ ] **Step 1: Plan review before implementation**

Write `docs/reviews/opencode-stage-63-plan-review-prompt.md` asking local
opencode with model `zhipuai-coding-plan/glm-5.2` and variant `max` to review:

- Objective, architecture, tech stack, implementation method, and plan.
- Print-only scope.
- No platform collection, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product feature.

Run:

```bash
opencode run --dir /home/ubuntu/fashion-radar --model zhipuai-coding-plan/glm-5.2 --variant max "$(cat docs/reviews/opencode-stage-63-plan-review-prompt.md)"
```

Save output to `docs/reviews/opencode-stage-63-plan-review.md`.

Fix any Critical or Important findings before implementation.

- [ ] **Step 2: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_templates.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config lock --check
git diff --check
```

- [ ] **Step 3: Run full verification**

Run:

```bash
uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
codegraph status
```

- [ ] **Step 4: Run package and installed-wheel verification**

Run:

```bash
tmp_build="$(mktemp -d)"
tmp_env="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
python3 scripts/check_package_archives.py "$tmp_build"
uv --no-config venv "$tmp_env/venv"
uv --no-config pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format json | "$tmp_env/venv/bin/python" -m json.tool >/dev/null
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format csv >/dev/null
```

- [ ] **Step 5: Release review**

Write `docs/reviews/opencode-stage-63-release-review-prompt.md` with:

- Base commit before Stage 63.
- Changed files.
- Stage 63 objective.
- Verification commands and results.
- Explicit request for Critical/Important/Minor findings.

Run:

```bash
opencode run --dir /home/ubuntu/fashion-radar --model zhipuai-coding-plan/glm-5.2 --variant max "$(cat docs/reviews/opencode-stage-63-release-review-prompt.md)"
```

Save output to `docs/reviews/opencode-stage-63-release-review.md`.

Fix any Critical or Important findings and rerun relevant verification.

- [ ] **Step 6: Commit and push**

Before commit, verify:

```bash
git status --short
rg -n "pypi\\.tuna|tsinghua" uv.lock || true
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**' || true
```

Stage all Stage 63 files, excluding `uv.lock`, then:

```bash
git commit -m "Add external tool template output"
```

Push with the repository's approved release credential flow without committing
token values, local token paths, or generated authentication headers.

- [ ] **Step 7: Poll CI**

Use the GitHub Actions API with the saved token to poll the pushed commit until
the CI run completes. If it fails, inspect logs, fix, verify, recommit, push,
and poll again.

- [ ] **Step 8: Handoff Summary**

End the node with:

- Repo status.
- Verified commands.
- Uncommitted files.
- Next step.

Do not paste large diffs or logs.
