from __future__ import annotations

import csv
import io
import json
import shlex
from pathlib import Path

import pytest

from fashion_radar.community_signal_profile import build_community_signal_profile
from fashion_radar.community_signals import lint_community_signal_file
from fashion_radar.external_tool_adapters import (
    build_external_tool_adapter_registry,
)
from fashion_radar.external_tool_readiness import build_external_tool_readiness
from fashion_radar.external_tool_templates import (
    build_external_tool_template,
    render_external_tool_template_csv,
    render_external_tool_template_json,
)
from fashion_radar.external_tool_workflow import build_external_tool_workflow

DIRECTORY = Path("./exports")
CONFIG_DIR = Path("./configs")
DATA_DIR = Path("./data")
AS_OF = "2026-06-13T12:00:00Z"

EXPECTED_ADAPTER_IDS = [
    "rednote_mcp",
    "xiaohongshu_crawler",
    "instaloader",
    "tiktok_api",
    "yt_dlp",
    "x_search_export",
    "generic_community_export",
]

WORKFLOW_RECOMMENDED_COMMAND_STEPS = {
    "check_external_tool_readiness": 1,
    "print_signal_profile": 0,
    "print_handoff_manifest": 2,
    "print_handoff_workflow": 3,
    "lint_export_directory": 4,
    "review_handoff_readiness": 5,
    "dry_run_directory_import": 6,
    "import_directory_signals": 7,
    "print_post_import_review": 8,
}

READINESS_RECOMMENDED_COMMAND_STEPS = {
    "print_signal_profile": 0,
    "lint_export_directory": 4,
    "review_handoff_readiness": 5,
    "dry_run_directory_import": 6,
}

BANNED_COMMAND_TOKENS = {
    "api",
    "browser",
    "cookie",
    "crawl",
    "download",
    "login",
    "monitor",
    "playwright",
    "proxy",
    "schedule",
    "scrape",
    "session",
    "token",
    "watch",
}


@pytest.fixture(scope="module")
def registry():
    return build_external_tool_adapter_registry(
        directory=DIRECTORY,
        config_dir=CONFIG_DIR,
        data_dir=DATA_DIR,
        as_of=AS_OF,
    )


def test_every_adapter_field_mapping_matches_community_signal_profile(registry) -> None:
    profile = build_community_signal_profile()

    assert [adapter.id for adapter in registry.adapters] == EXPECTED_ADAPTER_IDS

    for adapter in registry.adapters:
        mappings = [mapping.model_dump(mode="json") for mapping in adapter.field_mappings]

        assert [mapping["field"] for mapping in mappings] == profile.allowed_fields
        assert {mapping["field"] for mapping in mappings if mapping["required"]} == set(
            profile.required_fields
        )
        assert all(mapping["note"].strip() for mapping in mappings)
        assert adapter.platform_label in profile.suggested_platform_labels

    assert "suggested_platform_labels" not in profile.allowed_fields
    assert "suggested_platform_labels" not in set(profile.csv_header)


def test_every_template_model_mirrors_adapter_contract(registry) -> None:
    for adapter in registry.adapters:
        template = build_external_tool_template(
            adapter_id=adapter.id,
            directory=DIRECTORY,
            config_dir=CONFIG_DIR,
            data_dir=DATA_DIR,
            as_of=AS_OF,
        )

        assert template.adapter_id == adapter.id
        assert template.display_name == adapter.display_name
        assert template.platform_label == adapter.platform_label
        assert template.source_name == adapter.suggested_source_name
        assert template.recommended_input_format == adapter.recommended_input_format
        assert template.recommended_pattern == adapter.recommended_pattern
        assert template.suggested_export_directory == adapter.suggested_export_directory
        assert [mapping.field for mapping in template.field_mappings] == [
            mapping.field for mapping in adapter.field_mappings
        ]
        assert [mapping.model_dump(mode="json") for mapping in template.field_mappings] == [
            mapping.model_dump(mode="json") for mapping in adapter.field_mappings
        ]
        assert template.csv_header == [mapping.field for mapping in adapter.field_mappings]
        assert template.recommended_commands == adapter.recommended_commands


def test_every_template_json_and_csv_output_lints_cleanly(registry, tmp_path: Path) -> None:
    profile_fields = set(build_community_signal_profile().allowed_fields)

    for adapter in registry.adapters:
        template = build_external_tool_template(
            adapter_id=adapter.id,
            directory=DIRECTORY,
            config_dir=CONFIG_DIR,
            data_dir=DATA_DIR,
            as_of=AS_OF,
        )

        payload = json.loads(render_external_tool_template_json(template))
        assert list(payload) == ["items"]
        assert len(payload["items"]) == 2
        assert all(set(item) == profile_fields for item in payload["items"])
        assert all("suggested_platform_labels" not in item for item in payload["items"])

        json_path = tmp_path / f"{adapter.id}.json"
        json_path.write_text(render_external_tool_template_json(template), encoding="utf-8")
        json_result = lint_community_signal_file(json_path, input_format="json")
        assert json_result.ok is True
        assert json_result.valid_row_count == 2

        csv_path = tmp_path / f"{adapter.id}.csv"
        csv_text = render_external_tool_template_csv(template)
        csv_header = next(csv.reader(io.StringIO(csv_text)))
        assert "suggested_platform_labels" not in csv_header
        csv_path.write_text(csv_text, encoding="utf-8")
        csv_result = lint_community_signal_file(csv_path, input_format="csv")
        assert csv_result.ok is True
        assert csv_result.valid_row_count == 2


def test_every_workflow_reuses_adapter_commands_for_shared_steps(registry) -> None:
    for adapter in registry.adapters:
        workflow = build_external_tool_workflow(
            adapter_id=adapter.id,
            directory=DIRECTORY,
            config_dir=CONFIG_DIR,
            data_dir=DATA_DIR,
            as_of=AS_OF,
        )
        workflow_commands = {step.name: step.command for step in workflow.steps}

        for step_name, command_index in WORKFLOW_RECOMMENDED_COMMAND_STEPS.items():
            assert workflow_commands[step_name] == adapter.recommended_commands[command_index]

        assert "--dry-run" in shlex.split(workflow_commands["dry_run_directory_import"])
        assert "--dry-run" not in shlex.split(workflow_commands["import_directory_signals"])


def test_every_readiness_reuses_adapter_commands_for_shared_steps(registry) -> None:
    for adapter in registry.adapters:
        readiness = build_external_tool_readiness(
            adapter_id=adapter.id,
            directory=DIRECTORY,
            config_dir=CONFIG_DIR,
            data_dir=DATA_DIR,
            as_of=AS_OF,
            which=lambda _command: None,
        )
        readiness_commands = {step.name: step.command for step in readiness.steps}

        for step_name, command_index in READINESS_RECOMMENDED_COMMAND_STEPS.items():
            assert readiness_commands[step_name] == adapter.recommended_commands[command_index]

        assert "--dry-run" in shlex.split(readiness_commands["dry_run_directory_import"])


def test_generated_fashion_radar_guidance_excludes_platform_acquisition_tokens(
    registry,
) -> None:
    commands: list[str] = []
    for adapter in registry.adapters:
        commands.extend(adapter.recommended_commands)
        commands.extend(
            step.command
            for step in build_external_tool_workflow(
                adapter_id=adapter.id,
                directory=DIRECTORY,
                config_dir=CONFIG_DIR,
                data_dir=DATA_DIR,
                as_of=AS_OF,
            ).steps
        )
        commands.extend(
            step.command
            for step in build_external_tool_readiness(
                adapter_id=adapter.id,
                directory=DIRECTORY,
                config_dir=CONFIG_DIR,
                data_dir=DATA_DIR,
                as_of=AS_OF,
                which=lambda _command: None,
            ).steps
        )

    for command in commands:
        tokens = {token.lower() for token in shlex.split(command)}
        assert tokens.isdisjoint(BANNED_COMMAND_TOKENS), command
