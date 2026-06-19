from __future__ import annotations

import json
from pathlib import Path

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


def test_template_command_guidance_includes_external_tool_readiness() -> None:
    template = build_external_tool_template(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    assert any(
        "fashion-radar external-tool-readiness" in command
        for command in template.recommended_commands
    )
    json_output = render_external_tool_template_json(template)
    csv_output = render_external_tool_template_csv(template)

    assert "external-tool-readiness" not in json_output
    assert "external-tool-readiness" not in csv_output


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
        "xpoz_mcp",
        "generic_community_export",
    ]
    assert len(collection.items) == 16


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


def test_template_table_renderer_includes_field_mappings() -> None:
    template = build_external_tool_template(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    lines = render_external_tool_template_table(template)

    assert "Field mappings:" in lines
    url_mapping_line = (
        "- url (required): Stable source URL or local reference URL for the observed item."
    )
    summary_mapping_line = (
        "- summary (optional): Short sanitized local review note without raw comments "
        "or full post bodies."
    )
    assert url_mapping_line in lines
    assert summary_mapping_line in lines


def test_template_collection_table_renderer_includes_each_full_template() -> None:
    collection = build_external_tool_template_collection(
        adapter_id=None,
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    lines = render_external_tool_template_table(collection)

    assert lines[0] == "External tool templates."
    assert "Templates: 8" in lines
    assert "Adapter 1:" in lines
    assert "Adapter: rednote_mcp" in lines
    assert "Contract version: external-tool-template/v1" in lines
    header_line = (
        "CSV header: url, title, published_at, summary, source_name, "
        "platform, source_weight, collected_at"
    )
    assert header_line in lines
    assert "Field mappings:" in lines
    assert "Recommended commands:" in lines
    assert "Boundaries:" in lines
    assert "Adapter 8:" in lines
    assert "Adapter: generic_community_export" in lines


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
