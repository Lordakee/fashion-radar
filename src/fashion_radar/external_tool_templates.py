from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

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
    (
        "Does not write files, inspect directories, read handoff files, validate files, "
        "import rows, or open SQLite."
    ),
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


def render_external_tool_template_json(
    template_or_collection: ExternalToolTemplate | ExternalToolTemplateCollection,
) -> str:
    return json.dumps({"items": template_or_collection.items}, indent=2) + "\n"


def render_external_tool_template_csv(
    template_or_collection: ExternalToolTemplate | ExternalToolTemplateCollection,
) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=template_or_collection.csv_header,
        lineterminator="\n",
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
        for index, template in enumerate(templates, start=1):
            lines.append(f"Adapter {index}:")
            lines.extend(_render_single_external_tool_template_table(template))
        return lines

    return _render_single_external_tool_template_table(templates[0])


def _render_single_external_tool_template_table(template: ExternalToolTemplate) -> list[str]:
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
    lines.append("Field mappings:")
    for mapping in template.field_mappings:
        required_label = "required" if mapping.required else "optional"
        lines.append(
            f"- {_table_cell(mapping.field)} ({required_label}): {_table_cell(mapping.note)}"
        )
    lines.append("Recommended commands:")
    for command in template.recommended_commands:
        lines.append(f"- {_table_cell(command)}")
    lines.append("Boundaries:")
    for boundary in template.boundaries:
        lines.append(f"- {_table_cell(boundary)}")
    return lines


def _template_items(
    *,
    adapter_id: str,
    platform_label: str,
    source_name: str,
    as_of_dt: datetime,
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


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
