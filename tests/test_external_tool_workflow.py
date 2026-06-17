from pathlib import Path

import pytest
from pydantic import ValidationError

from fashion_radar.external_tool_workflow import (
    EXTERNAL_TOOL_WORKFLOW_BOUNDARIES,
    ExternalToolWorkflow,
    build_external_tool_workflow,
    render_external_tool_workflow_table,
)


def test_workflow_has_stable_instaloader_contract_and_steps() -> None:
    workflow = build_external_tool_workflow(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )
    payload = workflow.model_dump(mode="json")

    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "adapter_id",
        "display_name",
        "platform_label",
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "step_count",
        "steps",
        "boundaries",
    ]
    assert workflow.contract_version == "external-tool-workflow/v1"
    assert workflow.execution_mode == "print_only"
    assert workflow.adapter_id == "instaloader"
    assert workflow.display_name == "Instaloader Export"
    assert workflow.platform_label == "instagram"
    assert workflow.directory == "exports"
    assert workflow.input_format == "json"
    assert workflow.pattern == "*.json"
    assert workflow.as_of == "2026-06-13T12:00:00+00:00"
    assert workflow.config_dir == "configs"
    assert workflow.data_dir == "data"
    assert workflow.source_name == "Instaloader Export"
    assert workflow.step_count == 12
    assert [step.name for step in workflow.steps] == [
        "inspect_adapter_registry",
        "check_external_tool_readiness",
        "print_adapter_template_json",
        "print_signal_profile",
        "print_handoff_manifest",
        "print_handoff_workflow",
        "lint_export_directory",
        "preview_candidate_phrases",
        "review_handoff_readiness",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ]
    assert [step.suggested_effect for step in workflow.steps] == [
        "print_only",
        "read_only",
        "print_only",
        "print_only",
        "print_only",
        "print_only",
        "read_only",
        "read_only",
        "read_only",
        "read_only",
        "updates_local_imports",
        "print_only",
    ]
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]


def test_workflow_commands_use_adapter_defaults_and_shell_quote_paths() -> None:
    workflow = build_external_tool_workflow(
        adapter_id="instaloader",
        directory=Path("exports ? # & %"),
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        as_of="2026-06-13T12:00:00Z",
    )
    commands = {step.name: step.command for step in workflow.steps}

    assert commands["inspect_adapter_registry"] == (
        "fashion-radar external-tool-adapters --adapter instaloader "
        "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--format table"
    )
    assert commands["check_external_tool_readiness"] == (
        "fashion-radar external-tool-readiness --adapter instaloader "
        "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--input-format json --pattern '*.json' "
        "--source-name 'Instaloader Export' --format table"
    )
    assert commands["print_adapter_template_json"] == (
        "fashion-radar external-tool-template --adapter instaloader "
        "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--format json"
    )
    assert "community-handoff-manifest 'exports ? # & %'" in commands["print_handoff_manifest"]
    assert "--input-format json" in commands["print_handoff_manifest"]
    assert "--pattern '*.json'" in commands["print_handoff_manifest"]
    assert "--source-name 'Instaloader Export'" in commands["print_handoff_manifest"]
    assert "--dry-run" in commands["dry_run_directory_import"]
    assert "--dry-run" not in commands["import_directory_signals"]


def test_workflow_defaults_to_generic_adapter_and_accepts_local_overrides() -> None:
    workflow = build_external_tool_workflow(
        adapter_id=None,
        directory=Path("./handoff"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        input_format="json",
        pattern="*.handoff.json",
        source_name="Local Desk Export",
    )

    assert workflow.adapter_id == "generic_community_export"
    assert workflow.input_format == "json"
    assert workflow.pattern == "*.handoff.json"
    assert workflow.source_name == "Local Desk Export"
    assert "--source-name 'Local Desk Export'" in workflow.steps[1].command
    assert "--source-name 'Local Desk Export'" in workflow.steps[4].command


def test_workflow_blank_source_name_falls_back_to_adapter_source_name() -> None:
    workflow = build_external_tool_workflow(
        adapter_id="x_search_export",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        source_name="   ",
    )

    assert workflow.source_name == "X Search Export"


def test_workflow_rejects_unknown_adapter_and_invalid_as_of() -> None:
    with pytest.raises(ValueError, match="Unknown external tool adapter: missing"):
        build_external_tool_workflow(
            adapter_id="missing",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
        )

    with pytest.raises(ValueError):
        build_external_tool_workflow(
            adapter_id="instaloader",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="not-a-date",
        )


def test_workflow_table_renderer_sanitizes_cells_and_prints_boundaries() -> None:
    workflow = build_external_tool_workflow(
        adapter_id="generic_community_export",
        directory=Path("exports|one"),
        config_dir=Path("configs|one"),
        data_dir=Path("data|one"),
        as_of="2026-06-13T12:00:00Z",
        source_name="Source | One",
    )

    lines = render_external_tool_workflow_table(workflow)

    assert lines[0] == "External tool handoff workflow."
    assert "Execution mode: print_only" in lines
    assert "Commands were not executed." in lines
    assert "Directory: exports/one" in lines
    assert "Source name: Source / One" in lines
    assert "Order | Step | Suggested Effect | Purpose | Command" in lines
    assert any(line == "Boundaries:" for line in lines)
    assert any("No platform collection" in line for line in lines)


def test_workflow_table_renderer_sanitizes_step_boundaries() -> None:
    workflow = ExternalToolWorkflow(
        contract_version="external-tool-workflow/v1",
        execution_mode="print_only",
        adapter_id="tool|one",
        display_name="Tool | One",
        platform_label="platform|one",
        directory="./exports",
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00+00:00",
        config_dir="./configs",
        data_dir="./data",
        source_name="Source | One",
        step_count=1,
        steps=[
            {
                "order": 1,
                "name": "first | step\nname",
                "purpose": "Read | local\rstate.",
                "command": (
                    "fashion-radar community-signal-lint-dir ./exports "
                    "--source-name 'A | B'\n--strict"
                ),
                "suggested_effect": "read_only",
            }
        ],
        boundaries=["Does not run | generated\ncommands."],
    )

    assert render_external_tool_workflow_table(workflow) == [
        "External tool handoff workflow.",
        "Contract version: external-tool-workflow/v1",
        "Execution mode: print_only",
        "Commands were not executed.",
        "Adapter: tool/one",
        "Display name: Tool / One",
        "Platform label: platform/one",
        "Directory: ./exports",
        "Input format: csv",
        "Pattern: *.csv",
        "As of: 2026-06-13T12:00:00+00:00",
        "Config dir: ./configs",
        "Data dir: ./data",
        "Source name: Source / One",
        "Steps: 1",
        "Order | Step | Suggested Effect | Purpose | Command",
        "1 | first / step name | read_only | Read / local state. | "
        "fashion-radar community-signal-lint-dir ./exports --source-name 'A / B' --strict",
        "Boundaries:",
        "- Does not run / generated commands.",
    ]


def test_workflow_boundaries_include_external_tool_no_scope_terms() -> None:
    boundary_text = " ".join(EXTERNAL_TOOL_WORKFLOW_BOUNDARIES)

    for term in (
        "Does not run generated commands.",
        "Does not inspect the supplied directory.",
        "No platform collection",
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
    ):
        assert term in boundary_text


def test_workflow_model_rejects_extra_fields() -> None:
    payload = build_external_tool_workflow(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    ).model_dump(mode="json")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ExternalToolWorkflow.model_validate({**payload, "unexpected": "value"})
