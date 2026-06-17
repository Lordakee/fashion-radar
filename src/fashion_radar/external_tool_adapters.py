from __future__ import annotations

import shlex
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.community_signal_profile import build_community_signal_profile
from fashion_radar.importers.manual_signals import ManualSignalFormat
from fashion_radar.utils.dates import parse_datetime_utc

EXTERNAL_TOOL_ADAPTERS_CONTRACT_VERSION = "external-tool-adapters/v1"
EXTERNAL_TOOL_ADAPTERS_EXECUTION_MODE = "print_only"
DEFAULT_ADAPTER_AS_OF = "2026-06-13T12:00:00Z"
DEFAULT_EXPORT_DIRECTORY = "./exports"

EXTERNAL_TOOL_ADAPTER_REGISTRY_BOUNDARIES = [
    "Does not run adapters.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not create config, data, report, dashboard, or workflow artifacts.",
    (
        "Does not fetch URLs, search platforms, log in, store cookies, automate "
        "browsers, call platform APIs, monitor communities, schedule work, add "
        "source/platform connectors, acquire sources, prove demand, rank sources, "
        "or verify platform coverage."
    ),
    "Does not provide a compliance-review workflow.",
]

ADAPTER_BOUNDARIES = [
    "Local producer-discovery metadata only.",
    "Writes should target sanitized CSV/JSON local handoff rows.",
    "Platform label is local provenance only.",
    "No platform collection, connector execution, scraping, browser automation, or API calls.",
]

FIELD_NOTES = {
    "url": "Stable source URL or local reference URL for the observed item.",
    "title": "Short observed text, headline, caption summary, or normalized signal phrase.",
    "published_at": "ISO 8601-compatible publication or observation timestamp.",
    "summary": "Short sanitized local review note without raw comments or full post bodies.",
    "source_name": "Producer/export display name for the local handoff rows.",
    "platform": "Short local provenance label for review summaries.",
    "source_weight": "Optional local weight in the existing community signal range (0, 5].",
    "collected_at": "Timestamp for when the upstream tool produced the sanitized row.",
}


class ExternalToolAdapterFieldMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    required: bool
    note: str


class ExternalToolAdapter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    display_name: str
    platform_label: str
    suggested_source_name: str
    recommended_input_format: ManualSignalFormat
    recommended_pattern: str
    suggested_export_directory: str
    description: str
    upstream_tool_examples: list[str]
    field_mappings: list[ExternalToolAdapterFieldMapping]
    recommended_commands: list[str]
    boundaries: list[str]


class ExternalToolAdapterRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: Literal["print_only"]
    adapters: list[ExternalToolAdapter] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)

    def adapter_by_id(self, adapter_id: str) -> ExternalToolAdapter:
        for adapter in self.adapters:
            if adapter.id == adapter_id:
                return adapter
        raise KeyError(adapter_id)


def build_external_tool_adapter_registry(
    *,
    directory: Path,
    config_dir: Path,
    data_dir: Path,
    as_of: str,
) -> ExternalToolAdapterRegistry:
    profile = build_community_signal_profile()
    as_of_text = parse_datetime_utc(as_of).isoformat()
    directory_text = str(directory)
    config_text = str(config_dir)
    data_text = str(data_dir)
    field_mappings = _field_mappings(
        allowed_fields=profile.allowed_fields,
        required_fields=profile.required_fields,
    )

    adapters = [
        _adapter(
            adapter_id="rednote_mcp",
            display_name="Rednote MCP Export",
            platform_label="rednote",
            source_name="Rednote MCP Export",
            input_format="json",
            pattern="*.json",
            directory_text=directory_text,
            config_text=config_text,
            data_text=data_text,
            as_of_text=as_of_text,
            description=(
                "Metadata target for Rednote/Xiaohongshu MCP exports that already "
                "produce sanitized local observations."
            ),
            upstream_tool_examples=["rednote-mcp"],
            field_mappings=field_mappings,
        ),
        _adapter(
            adapter_id="xiaohongshu_crawler",
            display_name="Xiaohongshu Crawler Export",
            platform_label="xiaohongshu",
            source_name="Xiaohongshu Crawler Export",
            input_format="csv",
            pattern="*.csv",
            directory_text=directory_text,
            config_text=config_text,
            data_text=data_text,
            as_of_text=as_of_text,
            description=(
                "Metadata target for user-controlled Xiaohongshu crawler exports "
                "converted to the community signal row shape."
            ),
            upstream_tool_examples=["xiaohongshu-crawler"],
            field_mappings=field_mappings,
        ),
        _adapter(
            adapter_id="instaloader",
            display_name="Instaloader Export",
            platform_label="instagram",
            source_name="Instaloader Export",
            input_format="json",
            pattern="*.json",
            directory_text=directory_text,
            config_text=config_text,
            data_text=data_text,
            as_of_text=as_of_text,
            description=(
                "Metadata target for sanitized Instagram post or profile exports "
                "created outside Fashion Radar."
            ),
            upstream_tool_examples=["Instaloader"],
            field_mappings=field_mappings,
        ),
        _adapter(
            adapter_id="tiktok_api",
            display_name="TikTok-Api Export",
            platform_label="tiktok",
            source_name="TikTok-Api Export",
            input_format="json",
            pattern="*.json",
            directory_text=directory_text,
            config_text=config_text,
            data_text=data_text,
            as_of_text=as_of_text,
            description=(
                "Metadata target for sanitized TikTok observations exported by a "
                "user-controlled upstream tool."
            ),
            upstream_tool_examples=["TikTok-Api"],
            field_mappings=field_mappings,
        ),
        _adapter(
            adapter_id="yt_dlp",
            display_name="yt-dlp Metadata Export",
            platform_label="media",
            source_name="yt-dlp Metadata Export",
            input_format="json",
            pattern="*.json",
            directory_text=directory_text,
            config_text=config_text,
            data_text=data_text,
            as_of_text=as_of_text,
            description=(
                "Metadata target for sanitized media metadata exports, not media "
                "downloads or stored video assets."
            ),
            upstream_tool_examples=["yt-dlp"],
            field_mappings=field_mappings,
        ),
        _adapter(
            adapter_id="x_search_export",
            display_name="X Search Export",
            platform_label="x",
            source_name="X Search Export",
            input_format="csv",
            pattern="*.csv",
            directory_text=directory_text,
            config_text=config_text,
            data_text=data_text,
            as_of_text=as_of_text,
            description=(
                "Metadata target for sanitized X/search exports created outside Fashion Radar."
            ),
            upstream_tool_examples=["AnySearch X export", "snscrape export"],
            field_mappings=field_mappings,
        ),
        _adapter(
            adapter_id="generic_community_export",
            display_name="Generic Community Export",
            platform_label="community",
            source_name="Generic Community Export",
            input_format="csv",
            pattern="*.csv",
            directory_text=directory_text,
            config_text=config_text,
            data_text=data_text,
            as_of_text=as_of_text,
            description=(
                "Metadata target for any user-controlled community source already "
                "converted to sanitized local signal rows."
            ),
            upstream_tool_examples=["manual spreadsheet export", "community research export"],
            field_mappings=field_mappings,
        ),
    ]
    return ExternalToolAdapterRegistry(
        contract_version=EXTERNAL_TOOL_ADAPTERS_CONTRACT_VERSION,
        execution_mode=EXTERNAL_TOOL_ADAPTERS_EXECUTION_MODE,
        adapters=adapters,
        boundaries=[*EXTERNAL_TOOL_ADAPTER_REGISTRY_BOUNDARIES],
    )


def filter_external_tool_adapter_registry(
    registry: ExternalToolAdapterRegistry,
    *,
    adapter_id: str | None,
) -> ExternalToolAdapterRegistry:
    if adapter_id is None:
        return registry
    try:
        adapter = registry.adapter_by_id(adapter_id)
    except KeyError as exc:
        raise ValueError(f"Unknown external tool adapter: {adapter_id}") from exc
    return registry.model_copy(update={"adapters": [adapter]})


def render_external_tool_adapter_registry_table(
    registry: ExternalToolAdapterRegistry,
) -> list[str]:
    lines = [
        "External tool adapter registry.",
        f"Contract version: {registry.contract_version}",
        f"Execution mode: {registry.execution_mode}",
        f"Adapters: {len(registry.adapters)}",
        "Adapter | Platform | Source name | Format | Pattern | Directory",
    ]
    for adapter in registry.adapters:
        lines.append(
            f"{_table_cell(adapter.id)} | {_table_cell(adapter.platform_label)} | "
            f"{_table_cell(adapter.suggested_source_name)} | "
            f"{adapter.recommended_input_format} | {_table_cell(adapter.recommended_pattern)} | "
            f"{_table_cell(adapter.suggested_export_directory)}"
        )
    for adapter in registry.adapters:
        lines.append(f"Commands for {_table_cell(adapter.id)}:")
        for command in adapter.recommended_commands:
            lines.append(f"- {_table_cell(command)}")
    lines.append("Boundaries:")
    for boundary in registry.boundaries:
        lines.append(f"- {_table_cell(boundary)}")
    return lines


def _adapter(
    *,
    adapter_id: str,
    display_name: str,
    platform_label: str,
    source_name: str,
    input_format: ManualSignalFormat,
    pattern: str,
    directory_text: str,
    config_text: str,
    data_text: str,
    as_of_text: str,
    description: str,
    upstream_tool_examples: list[str],
    field_mappings: list[ExternalToolAdapterFieldMapping],
) -> ExternalToolAdapter:
    return ExternalToolAdapter(
        id=adapter_id,
        display_name=display_name,
        platform_label=platform_label,
        suggested_source_name=source_name,
        recommended_input_format=input_format,
        recommended_pattern=pattern,
        suggested_export_directory=directory_text,
        description=description,
        upstream_tool_examples=upstream_tool_examples,
        field_mappings=field_mappings,
        recommended_commands=_recommended_commands(
            adapter_id=adapter_id,
            directory_text=directory_text,
            config_text=config_text,
            data_text=data_text,
            input_format=input_format,
            pattern=pattern,
            as_of_text=as_of_text,
            source_name=source_name,
        ),
        boundaries=[*ADAPTER_BOUNDARIES],
    )


def _field_mappings(
    *,
    allowed_fields: list[str],
    required_fields: list[str],
) -> list[ExternalToolAdapterFieldMapping]:
    mapping_fields = list(FIELD_NOTES)
    if set(mapping_fields) != set(allowed_fields):
        raise ValueError(
            "External tool adapter field mappings differ from community signal contract."
        )
    required = set(required_fields)
    return [
        ExternalToolAdapterFieldMapping(
            field=field,
            required=field in required,
            note=FIELD_NOTES[field],
        )
        for field in allowed_fields
    ]


def _recommended_commands(
    *,
    adapter_id: str,
    directory_text: str,
    config_text: str,
    data_text: str,
    input_format: ManualSignalFormat,
    pattern: str,
    as_of_text: str,
    source_name: str,
) -> list[str]:
    return [
        _shell_command("fashion-radar", "community-signal-profile", "--format", "json"),
        _shell_command(
            "fashion-radar",
            "external-tool-readiness",
            "--adapter",
            adapter_id,
            "--directory",
            directory_text,
            "--config-dir",
            config_text,
            "--data-dir",
            data_text,
            "--as-of",
            as_of_text,
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--format",
            "table",
        ),
        _shell_command(
            "fashion-radar",
            "community-handoff-manifest",
            directory_text,
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--config-dir",
            config_text,
            "--data-dir",
            data_text,
            "--as-of",
            as_of_text,
            "--source-name",
            source_name,
            "--format",
            "json",
        ),
        _shell_command(
            "fashion-radar",
            "community-handoff-workflow",
            directory_text,
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--config-dir",
            config_text,
            "--data-dir",
            data_text,
            "--as-of",
            as_of_text,
            "--source-name",
            source_name,
        ),
        _shell_command(
            "fashion-radar",
            "community-signal-lint-dir",
            directory_text,
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--strict",
        ),
        _shell_command(
            "fashion-radar",
            "community-handoff-check-dir",
            directory_text,
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--config-dir",
            config_text,
            "--as-of",
            as_of_text,
            "--source-name",
            source_name,
            "--strict",
        ),
        _shell_command(
            "fashion-radar",
            "import-signals-dir",
            directory_text,
            "--format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--data-dir",
            data_text,
            "--imported-at",
            as_of_text,
            "--dry-run",
        ),
        _shell_command(
            "fashion-radar",
            "import-signals-dir",
            directory_text,
            "--format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--data-dir",
            data_text,
            "--imported-at",
            as_of_text,
        ),
        _shell_command(
            "fashion-radar",
            "imported-review-workflow",
            "--config-dir",
            config_text,
            "--data-dir",
            data_text,
            "--as-of",
            as_of_text,
            "--source-name",
            source_name,
        ),
    ]


def _shell_command(*parts: str) -> str:
    return shlex.join(str(part) for part in parts)


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
