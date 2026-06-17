from __future__ import annotations

import shlex
from pathlib import Path

import pytest
from pydantic import ValidationError

from fashion_radar.community_signal_profile import build_community_signal_profile
from fashion_radar.external_tool_adapters import (
    ExternalToolAdapterRegistry,
    build_external_tool_adapter_registry,
    filter_external_tool_adapter_registry,
    render_external_tool_adapter_registry_table,
)

EXPECTED_ADAPTER_IDS = [
    "rednote_mcp",
    "xiaohongshu_crawler",
    "instaloader",
    "tiktok_api",
    "yt_dlp",
    "x_search_export",
    "generic_community_export",
]


def test_registry_has_stable_contract_and_adapter_ids() -> None:
    registry = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    payload = registry.model_dump(mode="json")

    assert list(payload) == ["contract_version", "execution_mode", "adapters", "boundaries"]
    assert registry.contract_version == "external-tool-adapters/v1"
    assert registry.execution_mode == "print_only"
    assert [adapter.id for adapter in registry.adapters] == EXPECTED_ADAPTER_IDS
    assert len(registry.adapters) == 7
    assert "Does not run adapters." in registry.boundaries


def test_instaloader_adapter_has_expected_mapping_and_commands() -> None:
    registry = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    instaloader = registry.adapter_by_id("instaloader")
    commands = [shlex.split(command) for command in instaloader.recommended_commands]

    assert list(instaloader.model_dump(mode="json")) == [
        "id",
        "display_name",
        "platform_label",
        "suggested_source_name",
        "recommended_input_format",
        "recommended_pattern",
        "suggested_export_directory",
        "description",
        "upstream_tool_examples",
        "field_mappings",
        "recommended_commands",
        "boundaries",
    ]
    assert instaloader.platform_label == "instagram"
    assert instaloader.suggested_source_name == "Instaloader Export"
    assert instaloader.recommended_input_format == "json"
    assert instaloader.recommended_pattern == "*.json"
    assert instaloader.suggested_export_directory == "exports"
    assert instaloader.upstream_tool_examples == ["Instaloader"]
    assert [command[:2] for command in commands] == [
        ["fashion-radar", "community-signal-profile"],
        ["fashion-radar", "external-tool-readiness"],
        ["fashion-radar", "community-handoff-manifest"],
        ["fashion-radar", "community-handoff-workflow"],
        ["fashion-radar", "community-signal-lint-dir"],
        ["fashion-radar", "community-handoff-check-dir"],
        ["fashion-radar", "import-signals-dir"],
        ["fashion-radar", "import-signals-dir"],
        ["fashion-radar", "imported-review-workflow"],
    ]
    readiness_command = commands[1]
    assert readiness_command[readiness_command.index("--adapter") + 1] == "instaloader"
    assert readiness_command[readiness_command.index("--directory") + 1] == "exports"
    assert readiness_command[readiness_command.index("--config-dir") + 1] == "configs"
    assert readiness_command[readiness_command.index("--data-dir") + 1] == "data"
    assert readiness_command[readiness_command.index("--input-format") + 1] == "json"
    assert readiness_command[readiness_command.index("--pattern") + 1] == "*.json"
    assert readiness_command[readiness_command.index("--source-name") + 1] == "Instaloader Export"
    assert readiness_command[readiness_command.index("--as-of") + 1] == (
        "2026-06-13T12:00:00+00:00"
    )
    assert readiness_command[readiness_command.index("--format") + 1] == "table"
    assert commands[2][2] == "exports"
    assert commands[2][commands[2].index("--input-format") + 1] == "json"
    assert commands[2][commands[2].index("--pattern") + 1] == "*.json"
    assert commands[2][commands[2].index("--source-name") + 1] == "Instaloader Export"
    assert commands[2][commands[2].index("--as-of") + 1] == "2026-06-13T12:00:00+00:00"
    assert "--dry-run" in commands[6]
    assert "--dry-run" not in commands[7]


def test_adapter_field_mappings_match_community_signal_contract() -> None:
    profile = build_community_signal_profile()
    registry = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    for adapter in registry.adapters:
        fields = [mapping.field for mapping in adapter.field_mappings]
        assert fields == profile.allowed_fields
        assert {mapping.field for mapping in adapter.field_mappings if mapping.required} == set(
            profile.required_fields
        )
        assert all(mapping.note for mapping in adapter.field_mappings)


def test_registry_filter_returns_only_requested_adapter() -> None:
    registry = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    filtered = filter_external_tool_adapter_registry(registry, adapter_id="tiktok_api")

    assert [adapter.id for adapter in filtered.adapters] == ["tiktok_api"]
    assert filtered.contract_version == registry.contract_version
    assert filtered.boundaries == registry.boundaries


def test_registry_filter_rejects_unknown_adapter() -> None:
    registry = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    with pytest.raises(ValueError, match="Unknown external tool adapter: nope"):
        filter_external_tool_adapter_registry(registry, adapter_id="nope")


def test_registry_quotes_paths_pattern_and_source_names() -> None:
    registry = build_external_tool_adapter_registry(
        directory=Path("exports ? # & %"),
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        as_of="2026-06-13T12:00:00Z",
    )

    adapter = registry.adapter_by_id("x_search_export")

    assert "'exports ? # & %'" in adapter.recommended_commands[1]
    assert "'config ? # & %'" in adapter.recommended_commands[1]
    assert "'data ? # & %'" in adapter.recommended_commands[1]
    assert "--source-name 'X Search Export'" in adapter.recommended_commands[1]
    assert "'exports ? # & %'" in adapter.recommended_commands[2]
    assert "'config ? # & %'" in adapter.recommended_commands[2]
    assert "'data ? # & %'" in adapter.recommended_commands[2]
    assert "--source-name 'X Search Export'" in adapter.recommended_commands[2]


def test_registry_invalid_as_of_raises() -> None:
    with pytest.raises(ValueError):
        build_external_tool_adapter_registry(
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="not-a-date",
        )


def test_registry_model_rejects_extra_fields_and_missing_required_fields() -> None:
    payload = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    ).model_dump(mode="json")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ExternalToolAdapterRegistry.model_validate({**payload, "unexpected": "value"})

    without_contract_version = {
        key: value for key, value in payload.items() if key != "contract_version"
    }
    with pytest.raises(ValidationError, match="Field required"):
        ExternalToolAdapterRegistry.model_validate(without_contract_version)


def test_render_external_tool_adapter_registry_table_sanitizes_cells() -> None:
    registry = ExternalToolAdapterRegistry(
        contract_version="external-tool-adapters/v1",
        execution_mode="print_only",
        adapters=[
            {
                "id": "tool|one",
                "display_name": "Tool | One",
                "platform_label": "platform|one",
                "suggested_source_name": "Source | One",
                "recommended_input_format": "csv",
                "recommended_pattern": "*.csv",
                "suggested_export_directory": "./exports",
                "description": "Local | producer\nmetadata.",
                "upstream_tool_examples": ["Example | Tool"],
                "field_mappings": [
                    {
                        "field": "url",
                        "required": True,
                        "note": "Stable | URL",
                    }
                ],
                "recommended_commands": ["fashion-radar community-signal-profile --format json"],
                "boundaries": ["Does not run | adapters."],
            }
        ],
        boundaries=["No platform | collection."],
    )

    lines = render_external_tool_adapter_registry_table(registry)

    assert lines == [
        "External tool adapter registry.",
        "Contract version: external-tool-adapters/v1",
        "Execution mode: print_only",
        "Adapters: 1",
        "Adapter | Platform | Source name | Format | Pattern | Directory",
        "tool/one | platform/one | Source / One | csv | *.csv | ./exports",
        "Commands for tool/one:",
        "- fashion-radar community-signal-profile --format json",
        "Boundaries:",
        "- No platform / collection.",
    ]
