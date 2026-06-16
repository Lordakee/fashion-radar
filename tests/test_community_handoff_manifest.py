from datetime import UTC, datetime
from pathlib import Path

import pytest

from fashion_radar.community_handoff_manifest import (
    CommunityHandoffManifest,
    build_community_handoff_manifest,
    render_community_handoff_manifest_table,
)

DIRECTORY_EXAMPLE_PATHS = [
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
]


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
        "directory_example_paths",
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
        "examples/community-tool-handoff.example.csv",
        "examples/community-tool-handoff.example.json",
    ]
    assert manifest.directory_example_paths == DIRECTORY_EXAMPLE_PATHS
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
        directory_example_paths=[
            "examples/community-tool-handoff-directory.example/README.md",
        ],
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
        "Directory example paths: examples/community-tool-handoff-directory.example/README.md",
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
