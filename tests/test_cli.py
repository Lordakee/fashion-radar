import json
import os
import shlex
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import select
from typer.testing import CliRunner

import fashion_radar.cli as cli_module
from fashion_radar.cli import app
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import (
    SCHEMA_VERSION,
    initialize_schema,
    item_entities,
    items,
    schema_metadata,
)
from fashion_radar.digests import DigestOptions, DigestResult
from fashion_radar.heat_movers import HeatMoversReport
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.models.trend import TrendComparison

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY_EXAMPLE_PATHS = [
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
]


def test_cli_help() -> None:
    result = CliRunner().invoke(app, ["--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "Fashion Radar" in result.output
    assert "trends" in result.output


def test_cli_help_lists_migrate_db() -> None:
    result = CliRunner().invoke(app, ["--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "migrate-db" in result.output


def test_dashboard_command_help_lists_config_dir() -> None:
    result = CliRunner().invoke(app, ["dashboard", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "--config-dir" in result.output


def test_import_signals_command_imports_csv(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,platform,author_handle,raw_comment,account_id\n"
        "https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z,Short note,"
        "manual,@private,do not store,secret\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Manual Export",
            "--imported-at",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Validated 1 manual signal rows" in result.output
    assert "Imported 1 manual signal rows" in result.output
    database_path = data_dir / "fashion-radar.sqlite"
    assert database_path.exists()
    engine = create_sqlite_engine(database_path)
    item = ItemRepository(engine).get_item(1)
    assert item["source_type"] == "manual_import"
    assert item["source_name"] == "Manual Export"
    assert item["summary"] == "Short note"
    assert item["platform"] == "manual"
    assert "author_handle" not in item
    assert "raw_comment" not in item
    assert "account_id" not in item


def test_import_signals_command_imports_json(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/json",
                    "title": "East-west tote",
                    "published_at": "2026-06-12T08:00:00Z",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "json",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Manual JSON Export",
        ],
    )

    assert result.exit_code == 0
    assert "Imported 1 manual signal rows" in result.output
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    item = ItemRepository(engine).get_item(1)
    assert item["source_type"] == "manual_import"
    assert item["source_name"] == "Manual JSON Export"


def test_import_signals_command_dry_run_writes_nothing(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Dry run: no rows imported" in result.output
    assert not data_dir.exists()
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_import_signals_command_rejects_invalid_file_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Valid,2026-06-12T08:00:00Z\n"
        ",Missing URL,2026-06-12T09:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Could not import signals: row 3" in result.output
    assert not data_dir.exists()
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_import_signals_command_rejects_null_published_at_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/null-date",
                    "title": "Null date",
                    "published_at": None,
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "json",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Could not import signals: row 1" in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_import_signals_command_rejects_invalid_imported_at(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
            "--imported-at",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not import signals: invalid --imported-at" in result.output
    assert not data_dir.exists()


def test_import_signals_command_rejects_unsupported_format_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.xml"
    path.write_text("<signals />", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "xml",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code != 0
    assert not data_dir.exists()


def test_community_signal_lint_help_lists_input_format_output_format_and_strict() -> None:
    result = CliRunner().invoke(
        app,
        ["community-signal-lint", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--input-format" in result.output
    assert "--format" in result.output
    assert "--source-name" in result.output
    assert "--strict" in result.output
    assert "without importing rows" in result.output


def test_community_signal_lint_prints_table_for_csv_example() -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint",
            "examples/community-signals.example.csv",
            "--input-format",
            "csv",
        ],
    )

    assert result.exit_code == 0
    assert "Community signal file: examples/community-signals.example.csv" in result.output
    assert "Rows: 2 total, 2 import-ready" in result.output
    assert "Findings:" in result.output


def test_community_signal_lint_prints_json_for_json_example() -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint",
            "examples/community-signals.example.json",
            "--input-format",
            "json",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["path"] == "examples/community-signals.example.json"
    assert payload["input_format"] == "json"
    assert payload["row_count"] == 2
    assert payload["valid_row_count"] == 2


def test_community_signal_lint_strict_exits_nonzero_on_warnings(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        ["community-signal-lint", str(path), "--input-format", "csv", "--strict"],
    )

    assert result.exit_code == 1
    assert "missing_source_name" in result.output


def test_community_signal_lint_non_strict_exits_zero_on_warnings(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        ["community-signal-lint", str(path), "--input-format", "csv"],
    )

    assert result.exit_code == 0
    assert "missing_source_name" in result.output


def test_community_signal_lint_invalid_file_exits_nonzero_without_traceback(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.json"
    path.write_text("{", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["community-signal-lint", str(path), "--input-format", "json"],
    )

    assert result.exit_code == 1
    assert "invalid_file" in result.output
    assert "Traceback" not in result.output


def test_community_signal_lint_does_not_create_project_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        ["community-signal-lint", str(path), "--input-format", "csv"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not Path("configs").exists()
    assert not Path("data").exists()
    assert not Path("reports").exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite-*")) == []
    assert list(tmp_path.rglob("*.db")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("*.eml")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []
    assert list(tmp_path.rglob("collection-workflow*.json")) == []


def assert_no_community_lint_artifacts(
    tmp_path: Path,
    *,
    config_dir: Path,
    data_dir: Path,
    reports_dir: Path,
) -> None:
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not Path("configs").exists()
    assert not Path("data").exists()
    assert not Path("reports").exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite-*")) == []
    assert list(tmp_path.rglob("*.sqlite3")) == []
    assert list(tmp_path.rglob("*.db")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("*.eml")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []
    assert list(tmp_path.rglob("collection-workflow*.json")) == []


def test_community_signal_profile_help_lists_format() -> None:
    result = CliRunner().invoke(
        app,
        ["community-signal-profile", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--format" in result.output
    assert "producer contract" in result.output
    for forbidden in (
        "--config-dir",
        "--data-dir",
        "--reports-dir",
        "--pattern",
        "--input-format",
        "--source-name",
        "--imported-at",
        "--dry-run",
    ):
        assert forbidden not in result.output


def test_community_signal_profile_prints_table() -> None:
    result = CliRunner().invoke(app, ["community-signal-profile"])

    assert result.exit_code == 0
    assert "Community signal producer profile" in result.output
    assert "Contract version: community-signals/v1" in result.output
    assert "CSV header: url, title, published_at" in result.output
    assert "Directory example paths:" in result.output
    assert "fashion-radar community-signal-lint-dir" in result.output
    assert "Does not create config, data, report, dashboard, or SQLite artifacts." in result.output


def test_community_signal_profile_prints_json() -> None:
    result = CliRunner().invoke(app, ["community-signal-profile", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "schema_path",
        "example_paths",
        "directory_example_paths",
        "supported_input_formats",
        "csv_header",
        "required_fields",
        "optional_fields",
        "allowed_fields",
        "prohibited_fields",
        "json_envelopes",
        "field_notes",
        "field_rules",
        "unsupported_capabilities",
        "recommended_commands",
        "boundaries",
    ]
    assert payload["contract_version"] == "community-signals/v1"
    assert payload["execution_mode"] == "print_only"
    assert payload["schema_path"] == "schemas/community-signals.schema.json"
    assert payload["example_paths"] == [
        "examples/community-signals.example.csv",
        "examples/community-signals.example.json",
        "examples/community-tool-handoff.example.csv",
        "examples/community-tool-handoff.example.json",
    ]
    assert payload["directory_example_paths"] == DIRECTORY_EXAMPLE_PATHS
    assert payload["supported_input_formats"] == ["csv", "json"]
    assert payload["csv_header"] == payload["allowed_fields"]
    assert payload["required_fields"] == ["url", "title", "published_at"]
    assert payload["unsupported_capabilities"][0] == "scraping"


def test_external_tool_adapters_command_prints_json() -> None:
    result = CliRunner().invoke(app, ["external-tool-adapters", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    expected_adapters = {
        "rednote_mcp": ("rednote", "Rednote MCP Export", "json", "*.json"),
        "xiaohongshu_crawler": (
            "xiaohongshu",
            "Xiaohongshu Crawler Export",
            "csv",
            "*.csv",
        ),
        "instaloader": ("instagram", "Instaloader Export", "json", "*.json"),
        "tiktok_api": ("tiktok", "TikTok-Api Export", "json", "*.json"),
        "yt_dlp": ("media", "yt-dlp Metadata Export", "json", "*.json"),
        "x_search_export": ("x", "X Search Export", "csv", "*.csv"),
        "generic_community_export": (
            "community",
            "Generic Community Export",
            "csv",
            "*.csv",
        ),
    }
    expected_adapter_keys = [
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
    expected_command_names = [
        "community-signal-profile",
        "external-tool-readiness",
        "community-handoff-manifest",
        "community-handoff-workflow",
        "community-signal-lint-dir",
        "community-handoff-check-dir",
        "import-signals-dir",
        "import-signals-dir",
        "imported-review-workflow",
    ]

    def flag_value(parts: list[str], flag: str) -> str:
        index = parts.index(flag)
        assert index + 1 < len(parts)
        value = parts[index + 1]
        assert value
        assert not value.startswith("--")
        return value

    assert payload["contract_version"] == "external-tool-adapters/v1"
    assert payload["execution_mode"] == "print_only"
    adapters = payload["adapters"]
    assert [adapter["id"] for adapter in adapters] == list(expected_adapters)
    expected_field_mappings = adapters[0]["field_mappings"]
    config_dirs: list[str] = []
    data_dirs: list[str] = []
    assert expected_field_mappings[0] == {
        "field": "url",
        "required": True,
        "note": "Stable source URL or local reference URL for the observed item.",
    }

    for adapter in adapters:
        adapter_id = adapter["id"]
        platform_label, source_name, input_format, pattern = expected_adapters[adapter_id]
        assert list(adapter) == expected_adapter_keys
        assert adapter["display_name"] == source_name
        assert adapter["platform_label"] == platform_label
        assert adapter["suggested_source_name"] == source_name
        assert adapter["recommended_input_format"] == input_format
        assert adapter["recommended_pattern"] == pattern
        assert adapter["suggested_export_directory"] == "exports"
        assert adapter["upstream_tool_examples"]
        assert adapter["field_mappings"] == expected_field_mappings

        commands = adapter["recommended_commands"]
        command_parts = [shlex.split(command) for command in commands]
        assert [parts[:2] for parts in command_parts] == [
            ["fashion-radar", name] for name in expected_command_names
        ]
        readiness_parts = command_parts[1]

        assert readiness_parts[:2] == ["fashion-radar", "external-tool-readiness"]
        assert flag_value(readiness_parts, "--adapter") == adapter_id
        assert flag_value(readiness_parts, "--directory") == "exports"
        config_dirs.append(flag_value(readiness_parts, "--config-dir"))
        data_dirs.append(flag_value(readiness_parts, "--data-dir"))
        assert flag_value(readiness_parts, "--as-of") == "2026-06-13T12:00:00+00:00"
        assert flag_value(readiness_parts, "--input-format") == input_format
        assert flag_value(readiness_parts, "--pattern") == pattern
        assert flag_value(readiness_parts, "--source-name") == source_name
        assert flag_value(readiness_parts, "--format") == "table"

    assert len(set(config_dirs)) == 1
    assert len(set(data_dirs)) == 1


def test_external_tool_adapters_command_filters_adapter_and_quotes_paths() -> None:
    result = CliRunner().invoke(
        app,
        [
            "external-tool-adapters",
            "--adapter",
            "instaloader",
            "--directory",
            "exports ? # & %",
            "--config-dir",
            "config ? # & %",
            "--data-dir",
            "data ? # & %",
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert [adapter["id"] for adapter in payload["adapters"]] == ["instaloader"]
    commands = payload["adapters"][0]["recommended_commands"]
    readiness_command = commands[1]
    manifest_command = commands[2]
    for command in (readiness_command, manifest_command):
        assert "'exports ? # & %'" in command
        assert "'config ? # & %'" in command
        assert "'data ? # & %'" in command
        assert "--source-name 'Instaloader Export'" in command
    assert "fashion-radar external-tool-readiness" in readiness_command
    readiness_parts = shlex.split(readiness_command)
    assert readiness_parts[readiness_parts.index("--directory") + 1] == "exports ? # & %"
    assert readiness_parts[readiness_parts.index("--config-dir") + 1] == "config ? # & %"
    assert readiness_parts[readiness_parts.index("--data-dir") + 1] == "data ? # & %"
    assert "fashion-radar community-handoff-manifest" in manifest_command


def test_external_tool_adapters_command_rejects_unknown_adapter() -> None:
    result = CliRunner().invoke(app, ["external-tool-adapters", "--adapter", "missing"])

    assert result.exit_code == 1
    assert (
        "Could not build external tool adapter registry: Unknown external tool adapter: missing"
    ) in result.output


def test_external_tool_adapters_command_prints_table() -> None:
    result = CliRunner().invoke(app, ["external-tool-adapters"])

    assert result.exit_code == 0
    assert "External tool adapter registry." in result.output
    assert "Contract version: external-tool-adapters/v1" in result.output
    assert "rednote_mcp | rednote | Rednote MCP Export | json | *.json | exports" in (result.output)
    assert "Commands for instaloader:" in result.output


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


def test_external_tool_template_command_is_print_only_for_paths(tmp_path: Path) -> None:
    export_dir = tmp_path / "missing-exports"
    config_dir = tmp_path / "missing-config"
    data_dir = tmp_path / "missing-data"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-template",
            "--adapter",
            "instaloader",
            "--directory",
            str(export_dir),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert len(payload["items"]) == 2
    assert not export_dir.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not (data_dir / "fashion-radar.sqlite").exists()


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


def test_external_tool_workflow_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["external-tool-workflow", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--adapter" in result.output
    assert "--directory" in result.output
    assert "--input-format" in result.output
    assert "--pattern" in result.output
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--format" in result.output
    assert "generic_community_export" in result.output
    assert "Print local external tool workflow commands" in result.output


def test_external_tool_workflow_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "exports ? # & %"
    config_dir = tmp_path / "config ? # & %"
    data_dir = tmp_path / "data ? # & %"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-workflow",
            "--adapter",
            "instaloader",
            "--directory",
            str(directory),
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
    payload = json.loads(result.output)
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
    assert payload["contract_version"] == "external-tool-workflow/v1"
    assert payload["execution_mode"] == "print_only"
    assert payload["adapter_id"] == "instaloader"
    assert payload["step_count"] == 12
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]
    assert [step["name"] for step in payload["steps"]] == [
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
    assert payload["steps"][1]["suggested_effect"] == "read_only"
    assert "fashion-radar external-tool-readiness" in payload["steps"][1]["command"]
    assert payload["steps"][10]["suggested_effect"] == "updates_local_imports"
    assert f"'{directory}'" in payload["steps"][4]["command"]
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_external_tool_workflow_command_prints_table_without_artifacts(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-workflow",
            "--adapter",
            "rednote_mcp",
            "--directory",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "External tool handoff workflow." in result.output
    assert "Contract version: external-tool-workflow/v1" in result.output
    assert "Commands were not executed." in result.output
    assert "inspect_adapter_registry" in result.output
    assert "check_external_tool_readiness" in result.output
    assert "external-tool-readiness" in result.output
    assert "print_adapter_template_json" in result.output
    assert "community-handoff-manifest" in result.output
    assert "community-candidates-dir" in result.output
    assert "imported-review-workflow" in result.output
    assert "No platform collection" in result.output
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_external_tool_workflow_command_applies_overrides() -> None:
    result = CliRunner().invoke(
        app,
        [
            "external-tool-workflow",
            "--adapter",
            "x_search_export",
            "--input-format",
            "json",
            "--pattern",
            "*.handoff.json",
            "--source-name",
            "Local Desk Export",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "x_search_export"
    assert payload["input_format"] == "json"
    assert payload["pattern"] == "*.handoff.json"
    assert payload["source_name"] == "Local Desk Export"


def test_external_tool_workflow_command_defaults_to_generic_adapter() -> None:
    result = CliRunner().invoke(app, ["external-tool-workflow", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "generic_community_export"


def test_external_tool_workflow_command_rejects_unknown_adapter() -> None:
    result = CliRunner().invoke(app, ["external-tool-workflow", "--adapter", "missing"])

    assert result.exit_code == 1
    assert (
        "Could not build external tool workflow: Unknown external tool adapter: missing"
        in result.output
    )


def test_external_tool_workflow_command_rejects_invalid_as_of_without_builder(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_external_tool_workflow",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("build_external_tool_workflow should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        ["external-tool-workflow", "--as-of", "not-a-date"],
    )

    assert result.exit_code == 1
    assert "Could not build external tool workflow: invalid --as-of" in result.output
    assert "build_external_tool_workflow should not be called" not in result.output
    assert "Traceback" not in result.output


def test_external_tool_workflow_command_rejects_invalid_format_without_builder(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_external_tool_workflow",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("build_external_tool_workflow should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        ["external-tool-workflow", "--format", "xml"],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "build_external_tool_workflow should not be called" not in result.output
    assert "Traceback" not in result.output


def test_external_tool_workflow_command_does_not_read_directory_or_run_side_effects(
    tmp_path: Path,
    monkeypatch,
) -> None:
    directory = tmp_path / "exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    guarded_paths = {directory, config_dir, data_dir}

    def fail_side_effect(*args, **kwargs):
        raise AssertionError("side effect should not run")

    def is_guarded_path(path) -> bool:
        try:
            return Path(path) in guarded_paths
        except TypeError:
            return False

    def guard_path_method(name: str):
        original = getattr(Path, name)

        def guarded(self: Path, *args, **kwargs):
            if self in guarded_paths:
                raise AssertionError(f"{name} should not inspect supplied paths")
            return original(self, *args, **kwargs)

        monkeypatch.setattr(Path, name, guarded)

    def guard_os_function(name: str):
        original = getattr(os, name)

        def guarded(path, *args, **kwargs):
            if is_guarded_path(path):
                raise AssertionError(f"os.{name} should not inspect supplied path: {path}")
            return original(path, *args, **kwargs)

        monkeypatch.setattr(os, name, guarded)

    for path_method in (
        "exists",
        "is_file",
        "is_dir",
        "iterdir",
        "glob",
        "rglob",
        "stat",
        "lstat",
    ):
        guard_path_method(path_method)
    for os_function in ("scandir", "stat", "listdir", "walk"):
        guard_os_function(os_function)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail_side_effect)
    monkeypatch.setattr(cli_module, "initialize_schema", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_directory_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "store_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_directory", fail_side_effect)
    monkeypatch.setattr(cli_module, "check_community_handoff_directory", fail_side_effect)
    monkeypatch.setattr(cli_module, "collect_configured_sources", fail_side_effect)
    monkeypatch.setattr(cli_module, "write_daily_report_files", fail_side_effect)
    monkeypatch.setattr(cli_module, "package_daily_digest", fail_side_effect)

    result = CliRunner().invoke(
        app,
        [
            "external-tool-workflow",
            "--adapter",
            "instaloader",
            "--directory",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "instaloader"


def test_external_tool_readiness_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["external-tool-readiness", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--adapter" in result.output
    assert "--directory" in result.output
    assert "--input-format" in result.output
    assert "--pattern" in result.output
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--format" in result.output
    assert "generic_community_export" in result.output
    assert "Print local external tool readiness guidance" in result.output


def test_external_tool_readiness_command_prints_json_with_stable_keys(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)
    directory = tmp_path / "exports ? # & %"
    config_dir = tmp_path / "config ? # & %"
    data_dir = tmp_path / "data ? # & %"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-readiness",
            "--adapter",
            "instaloader",
            "--directory",
            str(directory),
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
    payload = json.loads(result.output)
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
        "checks",
        "step_count",
        "steps",
        "boundaries",
    ]
    assert payload["contract_version"] == "external-tool-readiness/v1"
    assert payload["execution_mode"] == "local_read_only"
    assert payload["adapter_id"] == "instaloader"
    assert payload["checks"][0]["status"] in {"missing", "found"}
    assert payload["step_count"] == 7
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_external_tool_readiness_command_prints_table_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-readiness",
            "--adapter",
            "rednote_mcp",
            "--directory",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "External tool readiness." in result.output
    assert "Contract version: external-tool-readiness/v1" in result.output
    assert "Commands were not executed." in result.output
    assert "upstream_command" in result.output
    assert "rednote-mcp" in result.output
    assert "install" in result.output.lower()
    assert "npmmirror" in result.output
    assert "No platform collection" in result.output
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_external_tool_readiness_command_defaults_to_generic_adapter(monkeypatch) -> None:
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)

    result = CliRunner().invoke(app, ["external-tool-readiness", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "generic_community_export"
    assert payload["checks"][0]["status"] == "not_applicable"


def test_external_tool_readiness_command_applies_overrides(monkeypatch) -> None:
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)

    result = CliRunner().invoke(
        app,
        [
            "external-tool-readiness",
            "--adapter",
            "x_search_export",
            "--input-format",
            "json",
            "--pattern",
            "*.handoff.json",
            "--source-name",
            "Local Desk Export",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "x_search_export"
    assert payload["input_format"] == "json"
    assert payload["pattern"] == "*.handoff.json"
    assert payload["source_name"] == "Local Desk Export"


def test_external_tool_readiness_command_rejects_unknown_adapter() -> None:
    result = CliRunner().invoke(app, ["external-tool-readiness", "--adapter", "missing"])

    assert result.exit_code == 1
    assert (
        "Could not build external tool readiness: Unknown external tool adapter: missing"
        in result.output
    )


def test_external_tool_readiness_command_rejects_invalid_as_of_without_builder(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_external_tool_readiness",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("build_external_tool_readiness should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        ["external-tool-readiness", "--as-of", "not-a-date"],
    )

    assert result.exit_code == 1
    assert "Could not build external tool readiness: invalid --as-of" in result.output
    assert "build_external_tool_readiness should not be called" not in result.output
    assert "Traceback" not in result.output


def test_external_tool_readiness_command_rejects_invalid_format_without_builder(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_external_tool_readiness",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("build_external_tool_readiness should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        ["external-tool-readiness", "--format", "xml"],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "build_external_tool_readiness should not be called" not in result.output
    assert "Traceback" not in result.output


def test_external_tool_readiness_command_does_not_read_directory_or_run_side_effects(
    tmp_path: Path,
    monkeypatch,
) -> None:
    directory = tmp_path / "exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    guarded_paths = {directory, config_dir, data_dir}
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)

    def fail_side_effect(*args, **kwargs):
        raise AssertionError("side effect should not run")

    def is_guarded_path(path) -> bool:
        try:
            return Path(path) in guarded_paths
        except TypeError:
            return False

    def guard_path_method(name: str):
        original = getattr(Path, name)

        def guarded(self: Path, *args, **kwargs):
            if self in guarded_paths:
                raise AssertionError(f"{name} should not inspect supplied paths")
            return original(self, *args, **kwargs)

        monkeypatch.setattr(Path, name, guarded)

    def guard_os_function(name: str):
        original = getattr(os, name)

        def guarded(path, *args, **kwargs):
            if is_guarded_path(path):
                raise AssertionError(f"os.{name} should not inspect supplied path: {path}")
            return original(path, *args, **kwargs)

        monkeypatch.setattr(os, name, guarded)

    for path_method in (
        "is_dir",
        "is_file",
        "iterdir",
        "open",
        "stat",
        "glob",
        "rglob",
    ):
        guard_path_method(path_method)
    for os_function in ("scandir", "stat", "listdir", "walk"):
        guard_os_function(os_function)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    for name in (
        "create_sqlite_engine",
        "initialize_schema",
        "load_manual_signal_directory_rows",
        "load_manual_signal_rows",
        "store_manual_signal_rows",
        "lint_community_signal_directory",
        "lint_community_signal_file",
        "check_community_handoff_directory",
        "collect_configured_sources",
        "write_daily_report_files",
        "package_daily_digest",
    ):
        if hasattr(cli_module, name):
            monkeypatch.setattr(cli_module, name, fail_side_effect)

    result = CliRunner().invoke(
        app,
        [
            "external-tool-readiness",
            "--adapter",
            "instaloader",
            "--directory",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "instaloader"
    assert "should not" not in result.output


def test_community_signal_profile_json_is_deterministic_across_env_and_cwd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    first_cwd = tmp_path / "first"
    second_cwd = tmp_path / "second"
    first_cwd.mkdir()
    second_cwd.mkdir()

    monkeypatch.chdir(first_cwd)
    first = CliRunner().invoke(
        app,
        ["community-signal-profile", "--format", "json"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(first_cwd / "config"),
            "FASHION_RADAR_DATA_DIR": str(first_cwd / "data"),
            "FASHION_RADAR_REPORTS_DIR": str(first_cwd / "reports"),
        },
    )
    monkeypatch.chdir(second_cwd)
    second = CliRunner().invoke(
        app,
        ["community-signal-profile", "--format", "json"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(second_cwd / "config"),
            "FASHION_RADAR_DATA_DIR": str(second_cwd / "data"),
            "FASHION_RADAR_REPORTS_DIR": str(second_cwd / "reports"),
        },
    )

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert json.loads(first.output) == json.loads(second.output)


def test_community_signal_profile_does_not_create_project_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        ["community-signal-profile", "--format", "json"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_community_signal_profile_does_not_run_side_effect_helpers(
    monkeypatch,
) -> None:
    def fail_side_effect(*args, **kwargs):
        raise AssertionError("side effect should not run")

    for name in ("iterdir", "glob", "rglob"):
        monkeypatch.setattr(Path, name, fail_side_effect)
    monkeypatch.setattr(os, "scandir", fail_side_effect)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail_side_effect)
    monkeypatch.setattr(cli_module, "initialize_schema", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_file", fail_side_effect)
    monkeypatch.setattr(cli_module, "store_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "collect_configured_sources", fail_side_effect)
    monkeypatch.setattr(cli_module, "write_daily_report_files", fail_side_effect)
    monkeypatch.setattr(cli_module, "package_daily_digest", fail_side_effect)

    result = CliRunner().invoke(app, ["community-signal-profile", "--format", "json"])

    assert result.exit_code == 0


def test_community_signal_profile_real_process_does_not_create_artifacts(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "src"),
        "FASHION_RADAR_CONFIG_DIR": str(config_dir),
        "FASHION_RADAR_DATA_DIR": str(data_dir),
        "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
    }

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fashion_radar",
            "community-signal-profile",
            "--format",
            "json",
        ],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["contract_version"] == "community-signals/v1"
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert list(tmp_path.rglob("*.sqlite*")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []


def test_community_signal_profile_invalid_format_exits_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        ["community-signal-profile", "--format", "yaml"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code != 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_community_signal_profile_rejects_unexpected_path_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        ["community-signal-profile", "./exports"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code != 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_community_signal_lint_dir_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["community-signal-lint-dir", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--input-format" in result.output
    assert "--pattern" in result.output
    assert "--format" in result.output
    assert "--source-name" in result.output
    assert "--strict" in result.output
    assert "without importing rows" in result.output


def test_community_signal_lint_dir_prints_table(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,source_name,platform,summary\n"
        "https://example.com/a,Signal,2026-06-12T08:00:00Z,Tool,community,Note\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
    )

    assert result.exit_code == 0
    assert f"Community signal directory: {tmp_path}" in result.output
    assert "Files: 1" in result.output
    assert "Rows: 1 total, 1 import-ready" in result.output


def test_community_signal_lint_dir_prints_json(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/a",
                    "title": "Signal",
                    "published_at": "2026-06-12T08:00:00Z",
                    "source_name": "Tool",
                    "platform": "community",
                    "summary": "Note",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "json",
            "--pattern",
            "*.json",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "file_count",
        "row_count",
        "valid_row_count",
        "error_count",
        "warning_count",
        "info_count",
        "field_counts",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["file_count"] == 1
    assert payload["row_count"] == 1
    assert payload["valid_row_count"] == 1
    assert payload["error_count"] == 0
    assert payload["warning_count"] == 0
    assert payload["info_count"] == 2
    assert payload["files"][0]["row_count"] == 1


def test_community_signal_lint_dir_json_counts_and_file_order(
    tmp_path: Path,
) -> None:
    (tmp_path / "b.csv").write_text(
        "url,title,published_at\nhttps://example.com/b,Warning Only,2026-06-12T09:00:00Z\n",
        encoding="utf-8",
    )
    (tmp_path / "a.csv").write_text(
        "url,title,published_at\n,Broken,not-a-date\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert [Path(file["path"]).name for file in payload["files"]] == [
        "a.csv",
        "b.csv",
    ]
    assert payload["file_count"] == 2
    assert payload["row_count"] == 2
    assert payload["valid_row_count"] == 1
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 3
    assert payload["info_count"] == 2
    assert list(payload["field_counts"]) == sorted(payload["field_counts"])
    assert payload["source_name_counts"] == {"Community Signal Import": 1}
    assert payload["platform_counts"] == {}


def test_community_signal_lint_dir_json_invalid_directory_shape(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(missing),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "file_count",
        "row_count",
        "valid_row_count",
        "error_count",
        "warning_count",
        "info_count",
        "field_counts",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["directory"] == str(missing)
    assert payload["input_format"] == "csv"
    assert payload["pattern"] == "*.csv"
    assert payload["file_count"] == 0
    assert payload["row_count"] == 0
    assert payload["valid_row_count"] == 0
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 0
    assert payload["info_count"] == 0
    assert payload["field_counts"] == {}
    assert payload["source_name_counts"] == {}
    assert payload["platform_counts"] == {}
    assert payload["files"] == []
    assert payload["findings"] == [
        {
            "severity": "error",
            "code": "invalid_directory",
            "message": "Community signal directory does not exist or is not a directory.",
            "row": None,
            "field": None,
        }
    ]
    assert list(payload["findings"][0]) == [
        "severity",
        "code",
        "message",
        "row",
        "field",
    ]


def test_community_signal_lint_dir_json_no_matching_files_shape(
    tmp_path: Path,
) -> None:
    (tmp_path / "ignored.txt").write_text("ignore", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "file_count",
        "row_count",
        "valid_row_count",
        "error_count",
        "warning_count",
        "info_count",
        "field_counts",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["directory"] == str(tmp_path)
    assert payload["input_format"] == "csv"
    assert payload["pattern"] == "*.csv"
    assert payload["file_count"] == 0
    assert payload["row_count"] == 0
    assert payload["valid_row_count"] == 0
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 0
    assert payload["info_count"] == 0
    assert payload["field_counts"] == {}
    assert payload["source_name_counts"] == {}
    assert payload["platform_counts"] == {}
    assert payload["files"] == []
    assert payload["findings"] == [
        {
            "severity": "error",
            "code": "no_matching_files",
            "message": "No regular files matched the pattern in the directory.",
            "row": None,
            "field": None,
        }
    ]
    assert list(payload["findings"][0]) == [
        "severity",
        "code",
        "message",
        "row",
        "field",
    ]


def test_community_signal_lint_dir_invalid_directory_exits_nonzero(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(missing),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output


def test_community_signal_lint_dir_file_path_as_directory_exits_nonzero(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text("url,title,published_at\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output


def test_community_signal_lint_dir_unreadable_directory_exits_nonzero_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    original_iterdir = Path.iterdir

    def fail_iterdir(path: Path):
        if path == tmp_path:
            raise PermissionError("no access")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_iterdir)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output
    monkeypatch.setattr(Path, "iterdir", original_iterdir)
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_community_signal_lint_dir_warning_only_exits_zero_without_strict(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
    )

    assert result.exit_code == 0
    assert "missing_source_name" in result.output


def test_community_signal_lint_dir_warning_only_exits_nonzero_with_strict(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--strict",
        ],
    )

    assert result.exit_code == 1
    assert "missing_source_name" in result.output


def test_community_signal_lint_dir_does_not_create_project_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(tmp_path),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["import-signals-dir", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--pattern" in result.output
    assert "--dry-run" in result.output
    assert "--output-format" in result.output
    assert "--source-name" in result.output
    assert "--data-dir" in result.output
    assert "--imported-at" in result.output
    assert "without importing rows" not in result.output


def test_import_signals_dir_prints_table(tmp_path: Path) -> None:
    (tmp_path / "signals.csv").write_text(
        "url,title,published_at,source_name,platform\n"
        "https://example.com/a,Signal,2026-06-12T08:00:00Z,Tool,community\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert f"Import signals directory dry run: {tmp_path}" in result.output
    assert "Files: 1 total, 1 valid" in result.output
    assert "Rows: 1 import-ready" in result.output


def test_import_signals_dir_prints_json(tmp_path: Path) -> None:
    (tmp_path / "signals.json").write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/a",
                    "title": "Signal",
                    "published_at": "2026-06-12T08:00:00Z",
                    "source_name": "Tool",
                    "platform": "community",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "json",
            "--pattern",
            "*.json",
            "--dry-run",
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "file_count",
        "valid_file_count",
        "row_count",
        "error_count",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["file_count"] == 1
    assert payload["valid_file_count"] == 1
    assert payload["row_count"] == 1
    assert payload["error_count"] == 0
    assert payload["source_name_counts"] == {"Tool": 1}
    assert payload["platform_counts"] == {"community": 1}
    assert payload["files"][0]["findings"] == []


def test_import_signals_dir_imports_csv_directory(tmp_path: Path) -> None:
    exports_dir = tmp_path / "exports"
    data_dir = tmp_path / "data"
    exports_dir.mkdir()
    (exports_dir / "b.csv").write_text(
        "url,title,published_at,source_name,platform,author_handle,raw_comment,account_id\n"
        "https://example.com/b,Second,2026-06-12T09:00:00Z,Tool,x,"
        "@private,do not store,secret\n",
        encoding="utf-8",
    )
    (exports_dir / "a.csv").write_text(
        "url,title,published_at,summary\nhttps://example.com/a,First,2026-06-12T08:00:00Z,Signal\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(exports_dir),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Fallback Source",
            "--imported-at",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Validated 2 manual signal rows across 2 files" in result.output
    assert "Imported 2 manual signal rows" in result.output
    assert "Items added: 2" in result.output
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    repository = ItemRepository(engine)
    first = repository.get_item(1)
    second = repository.get_item(2)
    assert [first["url"], second["url"]] == [
        "https://example.com/a",
        "https://example.com/b",
    ]
    assert first["source_type"] == "manual_import"
    assert first["source_name"] == "Fallback Source"
    assert first["collected_at"] == "2026-06-12T12:00:00+00:00"
    assert second["source_type"] == "manual_import"
    assert second["source_name"] == "Tool"
    assert second["platform"] == "x"
    assert "author_handle" not in second
    assert "raw_comment" not in second
    assert "account_id" not in second


def test_import_signals_dir_imports_json_directory_with_json_output(
    tmp_path: Path,
) -> None:
    exports_dir = tmp_path / "exports"
    data_dir = tmp_path / "data"
    exports_dir.mkdir()
    (exports_dir / "signals.json").write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/json",
                    "title": "JSON signal",
                    "published_at": "2026-06-12T08:00:00Z",
                    "source_name": "JSON Tool",
                    "platform": "instagram",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(exports_dir),
            "--format",
            "json",
            "--pattern",
            "*.json",
            "--data-dir",
            str(data_dir),
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "file_count",
        "row_count",
        "rows_imported",
        "items_added",
        "source_name_counts",
        "platform_counts",
    ]
    assert payload["directory"] == str(exports_dir)
    assert payload["input_format"] == "json"
    assert payload["pattern"] == "*.json"
    assert payload["file_count"] == 1
    assert payload["row_count"] == 1
    assert payload["rows_imported"] == 1
    assert payload["items_added"] == 1
    assert payload["source_name_counts"] == {"JSON Tool": 1}
    assert payload["platform_counts"] == {"instagram": 1}


def test_import_signals_dir_reports_duplicate_url_upserts(tmp_path: Path) -> None:
    exports_dir = tmp_path / "exports"
    data_dir = tmp_path / "data"
    exports_dir.mkdir()
    (exports_dir / "a.csv").write_text(
        "url,title,published_at\nhttps://example.com/shared,First,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    (exports_dir / "b.csv").write_text(
        "url,title,published_at\nhttps://example.com/shared,Second,2026-06-12T09:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(exports_dir),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Imported 2 manual signal rows" in result.output
    assert "Items added: 1" in result.output
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    assert ItemRepository(engine).count_items() == 1


def test_import_signals_dir_json_failure_shape(tmp_path: Path) -> None:
    (tmp_path / "broken.csv").write_text(
        "url,title,published_at\n,Broken,not-a-date\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert payload["file_count"] == 1
    assert payload["valid_file_count"] == 0
    assert payload["row_count"] == 0
    assert payload["error_count"] == 1
    assert payload["findings"] == []
    assert payload["files"][0]["error_count"] == 1
    assert payload["files"][0]["findings"][0]["severity"] == "error"
    assert payload["files"][0]["findings"][0]["code"] == "invalid_file"
    assert "row 2" in payload["files"][0]["findings"][0]["message"]


def test_import_signals_dir_invalid_directory_exits_nonzero(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(missing),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output


def test_import_signals_dir_json_no_matching_files_shape(tmp_path: Path) -> None:
    (tmp_path / "ignored.txt").write_text("ignore", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "file_count",
        "valid_file_count",
        "row_count",
        "error_count",
        "source_name_counts",
        "platform_counts",
        "files",
        "findings",
    ]
    assert payload["directory"] == str(tmp_path)
    assert payload["input_format"] == "csv"
    assert payload["pattern"] == "*.csv"
    assert payload["file_count"] == 0
    assert payload["valid_file_count"] == 0
    assert payload["row_count"] == 0
    assert payload["error_count"] == 1
    assert payload["source_name_counts"] == {}
    assert payload["platform_counts"] == {}
    assert payload["files"] == []
    assert payload["findings"] == [
        {
            "severity": "error",
            "code": "no_matching_files",
            "message": "No regular files matched the pattern in the directory.",
            "path": None,
        }
    ]


def test_import_signals_dir_invalid_directory_import_exits_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing = tmp_path / "missing"
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(missing),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_no_matching_files_import_exits_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "ignored.txt").write_text("ignore", encoding="utf-8")
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "no_matching_files" in result.output
    assert "Traceback" not in result.output
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_invalid_file_import_exits_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "a-clean.csv").write_text(
        "url,title,published_at\nhttps://example.com/clean,Clean,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    (tmp_path / "b-broken.csv").write_text(
        "url,title,published_at\n,Broken,not-a-date\n",
        encoding="utf-8",
    )
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "invalid_file" in result.output
    assert "b-broken.csv" in result.output
    assert "Traceback" not in result.output
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_unreadable_directory_exits_nonzero_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    original_iterdir = Path.iterdir

    def fail_iterdir(path: Path):
        if path == tmp_path:
            raise PermissionError("no access")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_iterdir)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "invalid_directory" in result.output
    assert "Traceback" not in result.output
    monkeypatch.setattr(Path, "iterdir", original_iterdir)
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_does_not_create_project_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "signals.csv").write_text(
        "url,title,published_at\nhttps://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(tmp_path),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
            "--data-dir",
            str(data_dir),
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_rejects_invalid_imported_at_before_reading_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing = tmp_path / "missing"
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(missing),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--imported-at",
            "not-a-date",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "Could not import signals directory: invalid --imported-at" in result.output
    assert "invalid_directory" not in result.output
    assert "Traceback" not in result.output
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_rejects_invalid_dry_run_imported_at_before_reading_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing = tmp_path / "missing"
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(missing),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
            "--imported-at",
            "not-a-date",
            "--data-dir",
            str(data_dir),
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "Could not import signals directory: invalid --imported-at" in result.output
    assert "invalid_directory" not in result.output
    assert "Traceback" not in result.output
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_rejects_invalid_imported_at_with_json_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing = tmp_path / "missing"
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(missing),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--imported-at",
            "not-a-date",
            "--output-format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert payload["directory"] == str(missing)
    assert payload["input_format"] == "csv"
    assert payload["pattern"] == "*.csv"
    assert payload["error_count"] == 1
    assert payload["findings"][0]["code"] == "invalid_imported_at"
    assert "invalid --imported-at" in payload["findings"][0]["message"]
    assert "invalid_directory" not in result.output
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_import_signals_dir_rejects_invalid_dry_run_imported_at_with_json_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing = tmp_path / "missing"
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(missing),
            "--format",
            "csv",
            "--pattern",
            "*.csv",
            "--dry-run",
            "--imported-at",
            "not-a-date",
            "--data-dir",
            str(data_dir),
            "--output-format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 1
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert payload["error_count"] == 1
    assert payload["findings"][0]["code"] == "invalid_imported_at"
    assert "invalid --imported-at" in payload["findings"][0]["message"]
    assert "invalid_directory" not in result.output
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_imported_signals_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-signals", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--lookback-days" in result.output
    assert "--limit" in result.output
    assert "--source-name" in result.output
    assert "--unmatched-only" in result.output
    assert "--format" in result.output
    assert "UTC review timestamp" in result.output


def test_imported_signals_command_requires_as_of(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        ["imported-signals", "--data-dir", str(data_dir)],
    )

    assert result.exit_code != 0
    assert "--as-of" in result.output
    assert not data_dir.exists()


def test_imported_signals_command_invalid_as_of_creates_no_data_dir(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported signals: invalid --as-of" in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_signals_command_invalid_as_of_skips_query_when_database_exists(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "fashion-radar.sqlite").touch()

    def fail_query(*args, **kwargs):
        raise AssertionError("query_imported_signals should not be called")

    monkeypatch.setattr(cli_module, "query_imported_signals", fail_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported signals: invalid --as-of" in result.output
    assert "query_imported_signals should not be called" not in result.output
    assert "Traceback" not in result.output


def _fail_imported_signals_query(*args, **kwargs):
    raise AssertionError("query_imported_signals should not be called")


def test_imported_signals_command_rejects_zero_lookback_days_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(cli_module, "query_imported_signals", _fail_imported_signals_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "0",
        ],
    )

    assert result.exit_code != 0
    assert "--lookback-days" in result.output
    assert "query_imported_signals should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_signals_command_rejects_negative_limit_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(cli_module, "query_imported_signals", _fail_imported_signals_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "--limit" in result.output
    assert "query_imported_signals should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_signals_command_rejects_invalid_format_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(cli_module, "query_imported_signals", _fail_imported_signals_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "query_imported_signals should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_signals_command_missing_database_is_read_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["total_count"] == 0
    assert payload["row_count"] == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_imported_signals_command_prints_table(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual signals from local SQLite." in result.output
    assert (
        "Window: 2026-06-11T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00"
    ) in result.output
    assert "Rows: 2 shown, 2 total" in result.output
    assert "Matched rows: 1 matched, 1 unmatched" in result.output
    assert "Matches: 1 matched, 1 unmatched" not in result.output
    assert "Sources: Community Tool Export=2" in result.output
    assert "Platforms: instagram=1, tiktok=1" in result.output
    assert "Community Tool Export | tiktok | 1.00 | Unmatched local item" in result.output
    assert "Community Tool Export | instagram | 1.40 | Margaux interest" in result.output
    assert "Unmatched local item" in result.output
    assert "Margaux interest" in result.output
    assert "https://example.com/margaux" in result.output
    assert "Old local item" not in result.output
    assert "RSS item" not in result.output


def test_imported_signals_command_prints_json_with_stable_keys(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
            "--source-name",
            "Community Tool Export",
            "--limit",
            "1",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "database",
        "as_of",
        "window_start",
        "lookback_days",
        "source_name",
        "unmatched_only",
        "limit",
        "row_count",
        "total_count",
        "matched_count",
        "unmatched_count",
        "source_name_counts",
        "platform_counts",
        "latest_collected_at",
        "items",
    ]
    assert payload["source_name"] == "Community Tool Export"
    assert payload["limit"] == 1
    assert payload["row_count"] == 1
    assert payload["total_count"] == 2
    assert payload["matched_count"] == 1
    assert payload["unmatched_count"] == 1
    assert payload["source_name_counts"] == {"Community Tool Export": 2}
    assert payload["platform_counts"] == {"instagram": 1, "tiktok": 1}
    assert payload["latest_collected_at"] == "2026-06-12T10:00:00+00:00"
    assert payload["items"][0]["title"] == "Unmatched local item"
    assert payload["items"][0]["platform"] == "tiktok"
    assert list(payload["items"][0]) == [
        "id",
        "source_name",
        "platform",
        "url",
        "title",
        "published_at",
        "collected_at",
        "source_weight",
        "summary",
        "match_status",
        "matches",
    ]
    assert "normalized_url" not in payload["items"][0]
    assert "content_hash" not in payload["items"][0]


def test_imported_signals_command_json_match_keys_exclude_internal_fields(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
            "--limit",
            "2",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    matched_item = next(item for item in payload["items"] if item["match_status"] == "matched")
    assert list(matched_item["matches"][0]) == [
        "entity_name",
        "entity_type",
        "alias",
        "confidence",
    ]
    assert "reason" not in matched_item["matches"][0]
    assert "context_terms" not in matched_item["matches"][0]


def test_imported_signals_command_unmatched_only(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
            "--unmatched-only",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["unmatched_only"] is True
    assert payload["total_count"] == 1
    assert payload["matched_count"] == 0
    assert payload["unmatched_count"] == 1
    assert payload["items"][0]["match_status"] == "unmatched"
    assert payload["items"][0]["matches"] == []


def test_imported_signals_command_handles_special_character_data_dir(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(
        tmp_path,
        data_dir_name="data ? # & %",
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["total_count"] == 2
    assert payload["row_count"] == 2
    assert payload["database"] == str(data_dir / "fashion-radar.sqlite")


def test_imported_signals_command_invalid_schema_no_traceback(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with sqlite3.connect(data_dir / "fashion-radar.sqlite") as connection:
        connection.execute("create table schema_metadata (version integer primary key)")
        connection.execute(f"insert into schema_metadata (version) values ({SCHEMA_VERSION})")

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported signals" in result.output
    assert "Traceback" not in result.output


def test_imported_signals_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-01-15T00:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_imported_signals_command_does_not_mutate_existing_database(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    with sqlite3.connect(db_path) as connection:
        before_items = connection.execute("select count(*) from items").fetchone()[0]
        before_matches = connection.execute("select count(*) from item_entities").fetchone()[0]

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    with sqlite3.connect(db_path) as connection:
        after_items = connection.execute("select count(*) from items").fetchone()[0]
        after_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
    assert after_items == before_items
    assert after_matches == before_matches


def test_imported_candidates_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-candidates", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "imported manual candidate" in result.output.lower()
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--limit" in result.output
    assert "--format" in result.output


def test_imported_candidates_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_imported_candidates_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
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
        "database",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_type",
        "source_name",
        "limit",
        "candidate_count",
        "candidates",
    ]
    assert payload["source_type"] == "manual_import"
    assert payload["source_name"] == "Community Tool Export"
    assert payload["candidate_count"] == 1
    assert list(payload["candidates"][0]) == [
        "phrase",
        "candidate_type",
        "label",
        "score",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "growth_ratio",
        "first_seen_at",
    ]
    forbidden = {
        "representative_items",
        "source_url",
        "title",
        "summary",
        "contexts",
        "normalized_key",
        "item_id",
        "matches",
        "match_status",
    }
    assert forbidden.isdisjoint(payload["candidates"][0])
    assert payload["candidates"][0]["phrase"] == "Le Teckel bag"
    assert payload["candidates"][0]["current_mentions"] == 1


def test_imported_candidates_command_prints_table_without_item_fields(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_imported_candidates_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--source-name",
            "Community Tool Export",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual candidate signals from local SQLite." in result.output
    assert "Le Teckel bag" in result.output
    assert "https://example.com/imported-a" not in result.output
    assert "Le Teckel bag current mention" not in result.output
    assert "private review note" not in result.output


def _fail_imported_candidates_query(*args, **kwargs):
    raise AssertionError("query_imported_candidates should not be called")


def test_imported_candidates_command_rejects_invalid_as_of_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_candidates",
        _fail_imported_candidates_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported candidates: invalid --as-of" in result.output
    assert "query_imported_candidates should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_candidates_command_rejects_invalid_format_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_candidates",
        _fail_imported_candidates_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "query_imported_candidates should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_candidates_command_rejects_negative_limit_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_candidates",
        _fail_imported_candidates_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "--limit" in result.output
    assert "query_imported_candidates should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_candidates_command_missing_database_is_read_only(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "missing-data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
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
    payload = json.loads(result.output)
    assert payload["candidate_count"] == 0
    assert payload["candidates"] == []
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []


def test_imported_candidates_command_invalid_schema_no_traceback(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    with sqlite3.connect(data_dir / "fashion-radar.sqlite") as connection:
        connection.execute("create table schema_metadata (version integer primary key)")
        connection.execute(f"insert into schema_metadata (version) values ({SCHEMA_VERSION})")

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported candidates" in result.output
    assert "Traceback" not in result.output


def test_imported_candidates_command_does_not_mutate_existing_database(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_imported_candidates_cli_fixture(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    with sqlite3.connect(db_path) as connection:
        before_items = connection.execute("select count(*) from items").fetchone()[0]
        before_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        before_schema_version = connection.execute(
            "select version from schema_metadata"
        ).fetchone()[0]
        before_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
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
    with sqlite3.connect(db_path) as connection:
        after_items = connection.execute("select count(*) from items").fetchone()[0]
        after_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        after_schema_version = connection.execute("select version from schema_metadata").fetchone()[
            0
        ]
        after_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert after_items == before_items
    assert after_matches == before_matches
    assert after_schema_version == before_schema_version
    assert after_tables == before_tables


def test_imported_candidate_evidence_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-candidate-evidence", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "candidate phrase" in result.output.lower()
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--phrase" in result.output
    assert "--source-name" in result.output
    assert "--limit" in result.output
    assert "--format" in result.output


def test_imported_candidate_evidence_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_imported_candidate_evidence_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "Le Teckel bag",
            "--source-name",
            "Community Tool Export",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "database",
        "as_of",
        "phrase",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_type",
        "source_name",
        "limit",
        "row_count",
        "total_count",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "evidence",
    ]
    assert payload["phrase"] == "Le Teckel bag"
    assert payload["source_type"] == "manual_import"
    assert payload["source_name"] == "Community Tool Export"
    assert payload["row_count"] == 2
    assert payload["total_count"] == 2
    assert payload["current_mentions"] == 1
    assert payload["baseline_mentions"] == 1
    assert list(payload["evidence"][0]) == [
        "id",
        "window",
        "source_name",
        "title",
        "url",
        "published_at",
        "collected_at",
    ]
    forbidden = {
        "summary",
        "contexts",
        "normalized_phrase",
        "normalized_key",
        "normalized_url",
        "matches",
        "match_status",
        "source_file",
        "source_path",
        "import_path",
        "raw_comment",
        "account_id",
    }
    assert forbidden.isdisjoint(payload)
    assert forbidden.isdisjoint(payload["evidence"][0])


def test_imported_candidate_evidence_command_prints_table(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_imported_candidate_evidence_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "Le Teckel bag",
            "--source-name",
            "Community Tool Export",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual candidate evidence from local SQLite." in result.output
    assert "Le Teckel bag current mention" in result.output
    assert "https://example.com/current" in result.output
    assert "private review note" not in result.output
    assert "raw_comment" not in result.output


def _fail_imported_candidate_evidence_query(*args, **kwargs):
    raise AssertionError("query_imported_candidate_evidence should not be called")


def test_imported_candidate_evidence_command_requires_phrase(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code != 0
    assert "--phrase" in result.output
    assert not data_dir.exists()


def test_imported_candidate_evidence_command_rejects_blank_phrase_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_candidate_evidence",
        _fail_imported_candidate_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "  ",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported candidate evidence: invalid --phrase" in result.output
    assert "query_imported_candidate_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_candidate_evidence_command_rejects_invalid_as_of_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_candidate_evidence",
        _fail_imported_candidate_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
            "--phrase",
            "Le Teckel bag",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported candidate evidence: invalid --as-of" in result.output
    assert "query_imported_candidate_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_candidate_evidence_command_rejects_invalid_format_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_candidate_evidence",
        _fail_imported_candidate_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "Le Teckel bag",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "query_imported_candidate_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_candidate_evidence_command_rejects_negative_limit_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_candidate_evidence",
        _fail_imported_candidate_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "Le Teckel bag",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "--limit" in result.output
    assert "query_imported_candidate_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_candidate_evidence_command_blank_source_name_is_no_filter(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_imported_candidate_evidence_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "Le Teckel bag",
            "--source-name",
            "   ",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["source_name"] is None
    assert payload["total_count"] == 3
    assert payload["current_mentions"] == 2


def test_imported_candidate_evidence_command_missing_database_is_read_only(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "missing-data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "Le Teckel bag",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["row_count"] == 0
    assert payload["total_count"] == 0
    assert payload["evidence"] == []
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []


def test_imported_candidate_evidence_command_invalid_schema_no_traceback(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    with sqlite3.connect(data_dir / "fashion-radar.sqlite") as connection:
        connection.execute("create table schema_metadata (version integer primary key)")
        connection.execute(f"insert into schema_metadata (version) values ({SCHEMA_VERSION})")

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "Le Teckel bag",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported candidate evidence" in result.output
    assert "Traceback" not in result.output


def test_imported_candidate_evidence_command_does_not_mutate_existing_database(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_imported_candidate_evidence_cli_fixture(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    with sqlite3.connect(db_path) as connection:
        before_items = connection.execute("select count(*) from items").fetchone()[0]
        before_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        before_schema_version = connection.execute(
            "select version from schema_metadata"
        ).fetchone()[0]
        before_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }

    result = CliRunner().invoke(
        app,
        [
            "imported-candidate-evidence",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--phrase",
            "Le Teckel bag",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    with sqlite3.connect(db_path) as connection:
        after_items = connection.execute("select count(*) from items").fetchone()[0]
        after_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        after_schema_version = connection.execute("select version from schema_metadata").fetchone()[
            0
        ]
        after_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert after_items == before_items
    assert after_matches == before_matches
    assert after_schema_version == before_schema_version
    assert after_tables == before_tables


def test_imported_signals_summary_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-signals-summary", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--data-dir" in result.output
    assert "--format" in result.output
    assert "Summarize imported manual signal source labels" in result.output


def test_imported_signals_summary_command_missing_database_is_read_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["row_count"] == 0
    assert payload["source_count"] == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_imported_signals_summary_command_prints_table(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual signal source summary from local SQLite." in result.output
    assert "Rows: 3 retained manual rows across 2 sources" in result.output
    assert "Matched rows: 1 matched, 2 unmatched" in result.output
    assert "Platforms: instagram=1, manual=1, tiktok=1" in result.output
    assert "Community Tool Export | instagram=1, tiktok=1 | 2 | 1 | 1" in result.output
    assert "Manual Import | manual=1 | 1 | 0 | 1" in result.output
    assert "Margaux interest" not in result.output
    assert "https://example.com/margaux" not in result.output
    assert "RSS Source" not in result.output


def test_imported_signals_summary_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "database",
        "source_type",
        "platform_counts",
        "source_count",
        "row_count",
        "matched_count",
        "unmatched_count",
        "first_collected_at",
        "latest_collected_at",
        "sources",
    ]
    assert payload["source_type"] == "manual_import"
    assert payload["platform_counts"] == {"instagram": 1, "manual": 1, "tiktok": 1}
    assert payload["source_count"] == 2
    assert payload["row_count"] == 3
    assert payload["matched_count"] == 1
    assert payload["unmatched_count"] == 2
    assert list(payload["sources"][0]) == [
        "source_name",
        "platform_counts",
        "row_count",
        "matched_count",
        "unmatched_count",
        "first_collected_at",
        "latest_collected_at",
    ]
    assert "title" not in payload["sources"][0]
    assert "url" not in payload["sources"][0]


def _fail_imported_signals_summary_query(*args, **kwargs):
    raise AssertionError("query_imported_signals_summary should not be called")


def test_imported_signals_summary_command_rejects_invalid_format_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_signals_summary",
        _fail_imported_signals_summary_query,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "query_imported_signals_summary should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_signals_summary_command_handles_special_character_data_dir(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(
        tmp_path,
        data_dir_name="data ? # & %",
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["row_count"] == 3
    assert payload["database"] == str(data_dir / "fashion-radar.sqlite")


def test_imported_signals_summary_command_invalid_schema_no_traceback(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with sqlite3.connect(data_dir / "fashion-radar.sqlite") as connection:
        connection.execute("create table schema_metadata (version integer primary key)")
        connection.execute(f"insert into schema_metadata (version) values ({SCHEMA_VERSION})")

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Could not summarize imported signals" in result.output
    assert "Traceback" not in result.output


def test_imported_signals_summary_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 1
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_imported_signals_summary_command_does_not_mutate_existing_database(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    with sqlite3.connect(db_path) as connection:
        before_items = connection.execute("select count(*) from items").fetchone()[0]
        before_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        before_schema_version = connection.execute(
            "select version from schema_metadata"
        ).fetchone()[0]
        before_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    with sqlite3.connect(db_path) as connection:
        after_items = connection.execute("select count(*) from items").fetchone()[0]
        after_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        after_schema_version = connection.execute("select version from schema_metadata").fetchone()[
            0
        ]
        after_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert after_items == before_items
    assert after_matches == before_matches
    assert after_schema_version == before_schema_version
    assert after_tables == before_tables


def test_imported_review_workflow_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-review-workflow", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--lookback-days" in result.output
    assert "--current-days" in result.output
    assert "--baseline-days" in result.output
    assert "--format" in result.output
    assert "Print a post-import review command checklist" in result.output


def test_imported_review_workflow_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config dir"
    data_dir = tmp_path / "data dir"

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
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
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "lookback_days",
        "current_days",
        "baseline_days",
        "execution_mode",
        "step_count",
        "steps",
    ]
    assert payload["as_of"] == "2026-06-13T12:00:00+00:00"
    assert payload["config_dir"] == str(config_dir)
    assert payload["data_dir"] == str(data_dir)
    assert payload["source_name"] == "Community Tool Export"
    assert payload["execution_mode"] == "print_only"
    assert payload["step_count"] == 7
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]
    assert payload["steps"][1]["suggested_effect"] == "updates_local_matches"
    assert "--source-name 'Community Tool Export'" in payload["steps"][2]["command"]
    assert payload["steps"][3]["name"] == "review_imported_entity_evidence"
    assert payload["steps"][3]["suggested_effect"] == "read_only"
    assert payload["steps"][3]["command"] == (
        "fashion-radar imported-entity-evidence "
        f"--data-dir {shlex.quote(str(data_dir))} "
        "--as-of 2026-06-13T12:00:00+00:00 --entity-name 'The Row' "
        "--entity-type brand --current-days 7 --baseline-days 7 "
        "--source-name 'Community Tool Export'"
    )
    assert payload["steps"][4]["name"] == "review_imported_candidate_phrases"
    assert payload["steps"][4]["suggested_effect"] == "read_only"
    assert payload["steps"][4]["command"] == (
        "fashion-radar imported-candidates "
        f"--config-dir {shlex.quote(str(config_dir))} "
        f"--data-dir {shlex.quote(str(data_dir))} "
        "--as-of 2026-06-13T12:00:00+00:00 --source-name 'Community Tool Export'"
    )
    assert "--source-name 'Community Tool Export'" in payload["steps"][3]["command"]
    assert "--source-name 'Community Tool Export'" in payload["steps"][4]["command"]
    assert "--source-name 'Community Tool Export'" in payload["steps"][5]["command"]
    assert payload["steps"][-1]["name"] == "review_local_heat_movers"
    assert payload["steps"][-1]["suggested_effect"] == "read_only"
    assert payload["steps"][-1]["command"] == (
        "fashion-radar heat-movers "
        f"--config-dir {shlex.quote(str(config_dir))} "
        f"--data-dir {shlex.quote(str(data_dir))} "
        "--as-of 2026-06-13T12:00:00+00:00"
    )
    assert "--source-name" not in payload["steps"][-1]["command"]


def test_imported_review_workflow_command_prints_table() -> None:
    config_dir = Path("config ? # & %")
    data_dir = Path("data ? # & %")

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--source-name",
            "Community | Tool Export",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual signal review workflow." in result.output
    assert "Execution mode: print_only" in result.output
    assert "Commands were not executed." in result.output
    assert "Order | Step | Suggested Effect | Purpose | Command" in result.output
    assert "refresh_stored_matches | updates_local_matches" in result.output
    assert "review_imported_entity_evidence" in result.output
    assert "fashion-radar imported-entity-evidence" in result.output
    assert "--entity-name 'The Row' --entity-type brand" in result.output
    assert "review_imported_candidate_phrases" in result.output
    assert "fashion-radar imported-candidates" in result.output
    assert "review_local_heat_movers" in result.output
    assert "fashion-radar heat-movers" in result.output
    assert "Source name: Community / Tool Export" in result.output
    assert "--data-dir" in result.output
    assert "'data ? # & %'" in result.output
    assert "--source-name 'Community | Tool Export'" in result.output


def _prepare_community_handoff_check_fixture(
    tmp_path: Path,
) -> tuple[Path, Path, Path, Path]:
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


def test_community_handoff_check_dir_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["community-handoff-check-dir", "--help"],
        env={"COLUMNS": "120"},
    )

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


def test_community_handoff_check_dir_reports_invalid_files_without_traceback(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, _reports_dir, directory = _prepare_community_handoff_check_fixture(
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


def test_community_handoff_check_dir_table_output_is_summary_only(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, _reports_dir, directory = _prepare_community_handoff_check_fixture(
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


def test_community_handoff_check_dir_does_not_write_runtime_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, data_dir, reports_dir, directory = _prepare_community_handoff_check_fixture(
        tmp_path
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("write path should not be called")

    monkeypatch.setattr(cli_module, "create_sqlite_engine", forbidden)
    monkeypatch.setattr(cli_module, "initialize_schema", forbidden)
    monkeypatch.setattr(cli_module, "store_manual_signal_rows", forbidden)
    monkeypatch.setattr(cli_module, "collect_configured_sources", forbidden)
    monkeypatch.setattr(cli_module, "write_daily_report_files", forbidden)
    monkeypatch.setattr(cli_module, "package_daily_digest", forbidden)
    monkeypatch.setattr(cli_module.subprocess, "run", forbidden)

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


def test_community_handoff_workflow_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["community-handoff-workflow", "--help"],
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
    assert "Print a local community handoff command checklist" in result.output


def test_community_handoff_workflow_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "config dir"
    data_dir = tmp_path / "data dir"

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-workflow",
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
    assert payload["directory"] == str(directory)
    assert payload["execution_mode"] == "print_only"
    assert payload["step_count"] == 6
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]
    assert [step["name"] for step in payload["steps"]] == [
        "lint_handoff_directory",
        "preview_candidate_phrases",
        "review_handoff_readiness",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ]
    readiness_command = payload["steps"][2]["command"]
    for expected in (
        "fashion-radar community-handoff-check-dir",
        "--input-format",
        "--pattern",
        "--config-dir",
        "--as-of",
        "--source-name",
        "--strict",
    ):
        assert expected in readiness_command
    assert payload["steps"][4]["suggested_effect"] == "updates_local_imports"
    assert payload["steps"][5]["suggested_effect"] == "print_only"
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_community_handoff_workflow_command_prints_table_without_artifacts(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-workflow",
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
        ],
    )

    assert result.exit_code == 0
    assert "Community signal handoff workflow." in result.output
    assert "Commands were not executed." in result.output
    assert "community-signal-lint-dir" in result.output
    assert "community-candidates-dir" in result.output
    assert "review_handoff_readiness" in result.output
    assert "community-handoff-check-dir" in result.output
    assert "import-signals-dir" in result.output
    assert "imported-review-workflow" in result.output
    assert str(directory) in result.output
    assert str(config_dir) in result.output
    assert str(data_dir) in result.output
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_community_handoff_workflow_invalid_as_of_is_clean_error(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-handoff-workflow",
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
    assert "Could not build community handoff workflow: invalid --as-of" in result.output


def test_community_handoff_workflow_does_not_read_directory_or_run_side_effects(
    tmp_path: Path,
    monkeypatch,
) -> None:
    directory = tmp_path / "exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    guarded_paths = {directory}

    def fail_side_effect(*args, **kwargs):
        raise AssertionError("side effect should not run")

    def is_guarded_path(path) -> bool:
        try:
            return Path(path) in guarded_paths
        except TypeError:
            return False

    def guard_path_method(name: str):
        original = getattr(Path, name)

        def guarded(self: Path, *args, **kwargs):
            if self in guarded_paths:
                raise AssertionError(f"{name} should not inspect supplied paths")
            return original(self, *args, **kwargs)

        monkeypatch.setattr(Path, name, guarded)

    def guard_os_function(name: str):
        original = getattr(os, name)

        def guarded(path, *args, **kwargs):
            if is_guarded_path(path):
                raise AssertionError(f"os.{name} should not inspect supplied path: {path}")
            return original(path, *args, **kwargs)

        monkeypatch.setattr(os, name, guarded)

    for name in ("iterdir", "glob", "rglob", "exists", "is_dir", "stat", "lstat"):
        guard_path_method(name)
    for name in ("scandir", "stat", "listdir", "walk"):
        guard_os_function(name)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail_side_effect)
    monkeypatch.setattr(cli_module, "initialize_schema", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_directory_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_directory", fail_side_effect)
    monkeypatch.setattr(cli_module, "check_community_handoff_directory", fail_side_effect)
    monkeypatch.setattr(cli_module, "store_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "collect_configured_sources", fail_side_effect)
    monkeypatch.setattr(cli_module, "write_daily_report_files", fail_side_effect)
    monkeypatch.setattr(cli_module, "package_daily_digest", fail_side_effect)

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-workflow",
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
    payload = json.loads(result.output)
    assert payload["step_count"] == 6
    assert payload["steps"][2]["name"] == "review_handoff_readiness"
    assert "community-handoff-check-dir" in payload["steps"][2]["command"]


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
    assert payload["contract_version"] == "community-handoff-manifest/v1"
    assert payload["execution_mode"] == "print_only"
    assert payload["directory"] == str(directory)
    assert payload["input_format"] == "csv"
    assert payload["pattern"] == "*.csv"
    assert payload["as_of"] == "2026-06-13T12:00:00+00:00"
    assert payload["config_dir"] == str(config_dir)
    assert payload["data_dir"] == str(data_dir)
    assert payload["source_name"] == "Community Tool Export"
    assert (
        payload["producer_profile_command"]
        == "fashion-radar community-signal-profile --format json"
    )
    assert payload["producer_contract_version"] == "community-signals/v1"
    assert payload["supported_input_formats"] == ["csv", "json"]
    assert payload["suggested_filename"] == "community-signals.csv"
    assert 'using --pattern "*.json"' in payload["manifest_storage_note"]
    assert "author_handle" in payload["prohibited_fields"]
    assert payload["schema_path"] == "schemas/community-signals.schema.json"
    assert payload["example_paths"] == [
        "examples/community-signals.example.csv",
        "examples/community-signals.example.json",
        "examples/community-tool-handoff.example.csv",
        "examples/community-tool-handoff.example.json",
    ]
    assert payload["directory_example_paths"] == DIRECTORY_EXAMPLE_PATHS
    assert payload["csv_header"] == [
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    ]
    assert payload["required_fields"] == ["url", "title", "published_at"]
    assert payload["optional_fields"] == [
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    ]
    assert payload["json_envelopes"] == ["top_level_array", "object_with_items_only"]
    assert payload["field_notes"]["url"] == (
        "Source URL or stable reference URL for the observed item."
    )
    assert payload["field_rules"]["source_weight"] == {
        "exclusive_minimum": 0,
        "maximum": 5,
        "default": 1.0,
    }
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
    assert payload["workflow"]["step_count"] == 6
    assert payload["workflow"]["steps"][0]["name"] == "lint_handoff_directory"
    assert payload["workflow"]["steps"][2]["name"] == "review_handoff_readiness"
    assert "community-handoff-check-dir" in payload["workflow"]["steps"][2]["command"]
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_community_handoff_manifest_blank_source_name_uses_profile_default(
    tmp_path: Path,
) -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-handoff-manifest",
            str(tmp_path / "exports"),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(tmp_path / "configs"),
            "--data-dir",
            str(tmp_path / "data"),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--source-name",
            " ",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["source_name"] == "Community Tool Export"
    assert payload["workflow"]["source_name"] == "Community Tool Export"


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
    assert "Directory example paths:" in result.output
    assert "community-signal-profile --format json" in result.output
    assert "community-signal-lint-dir" in result.output
    assert "community-candidates-dir" in result.output
    assert "review_handoff_readiness" in result.output
    assert "community-handoff-check-dir" in result.output
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

    def is_guarded_path(path) -> bool:
        try:
            return Path(path) in guarded_paths
        except TypeError:
            return False

    def guard_path_method(name: str):
        original = getattr(Path, name)

        def guarded(self: Path, *args, **kwargs):
            if self in guarded_paths:
                raise AssertionError(f"{name} should not inspect supplied paths")
            return original(self, *args, **kwargs)

        monkeypatch.setattr(Path, name, guarded)

    def guard_os_function(name: str):
        original = getattr(os, name)

        def guarded(path, *args, **kwargs):
            if is_guarded_path(path):
                raise AssertionError(f"os.{name} should not inspect supplied path: {path}")
            return original(path, *args, **kwargs)

        monkeypatch.setattr(os, name, guarded)

    for name in ("exists", "is_dir", "is_file", "iterdir", "glob", "rglob", "stat", "lstat"):
        guard_path_method(name)
    for name in ("scandir", "stat", "listdir", "walk"):
        guard_os_function(name)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail_side_effect)
    monkeypatch.setattr(cli_module, "initialize_schema", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_directory_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_file", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_directory", fail_side_effect)
    monkeypatch.setattr(cli_module, "check_community_handoff_directory", fail_side_effect)
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
    payload = json.loads(result.output)
    assert payload["workflow"]["step_count"] == 6
    assert payload["workflow"]["steps"][2]["name"] == "review_handoff_readiness"
    assert "community-handoff-check-dir" in payload["workflow"]["steps"][2]["command"]


def _fail_imported_review_workflow_builder(*args, **kwargs):
    raise AssertionError("build_imported_review_workflow should not be called")


def _fail_imported_review_workflow_call(name: str):
    def fail(*args, **kwargs):
        raise AssertionError(f"{name} should not be called")

    return fail


def _patch_imported_review_workflow_no_data_access(monkeypatch) -> None:
    for name in (
        "query_imported_signals",
        "query_imported_signals_summary",
        "query_imported_entity_deltas",
        "query_imported_entity_evidence",
        "match_stored_items",
        "default_database_path",
        "load_source_config",
        "load_entity_config",
        "load_scoring_config",
        "create_sqlite_engine",
        "initialize_schema",
    ):
        monkeypatch.setattr(cli_module, name, _fail_imported_review_workflow_call(name))
    if hasattr(cli_module, "query_imported_candidates"):
        monkeypatch.setattr(
            cli_module,
            "query_imported_candidates",
            _fail_imported_review_workflow_call("query_imported_candidates"),
        )
    monkeypatch.setattr(
        cli_module.subprocess,
        "run",
        _fail_imported_review_workflow_call("subprocess.run"),
    )


def test_imported_review_workflow_command_rejects_invalid_format_without_builder(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "build_imported_review_workflow",
        _fail_imported_review_workflow_builder,
        raising=False,
    )
    _patch_imported_review_workflow_no_data_access(monkeypatch)

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "build_imported_review_workflow should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_review_workflow_command_rejects_invalid_as_of_without_builder(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "build_imported_review_workflow",
        _fail_imported_review_workflow_builder,
        raising=False,
    )
    _patch_imported_review_workflow_no_data_access(monkeypatch)

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not build imported review workflow: invalid --as-of" in result.output
    assert "build_imported_review_workflow should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_review_workflow_command_rejects_invalid_numbers_without_builder(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "build_imported_review_workflow",
        _fail_imported_review_workflow_builder,
        raising=False,
    )
    _patch_imported_review_workflow_no_data_access(monkeypatch)

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--lookback-days",
            "0",
        ],
    )

    assert result.exit_code != 0
    assert "--lookback-days" in result.output
    assert "build_imported_review_workflow should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_review_workflow_command_creates_no_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)
    _patch_imported_review_workflow_no_data_access(monkeypatch)

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_imported_review_workflow_command_does_not_access_data_or_execute(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _patch_imported_review_workflow_no_data_access(monkeypatch)

    result = CliRunner().invoke(
        app,
        [
            "imported-review-workflow",
            "--config-dir",
            str(tmp_path / "config"),
            "--data-dir",
            str(tmp_path / "data"),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert "should not be called" not in result.output
    assert "Traceback" not in result.output
    assert "fashion-radar imported-entity-evidence" in result.output
    assert "fashion-radar imported-candidates" in result.output
    assert "fashion-radar heat-movers" in result.output


def test_imported_entity_evidence_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-entity-evidence", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--entity-name" in result.output
    assert "--entity-type" in result.output
    assert "--source-name" in result.output
    assert "--current-days" in result.output
    assert "--baseline-days" in result.output
    assert "--limit" in result.output
    assert "--format" in result.output
    assert "Review retained imported rows behind one matched entity." in result.output


def test_imported_entity_evidence_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_evidence_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
            "--source-name",
            "Community Tool Export",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "database",
        "as_of",
        "entity_name",
        "entity_type",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_type",
        "source_name",
        "limit",
        "row_count",
        "total_count",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "evidence",
    ]
    assert payload["entity_name"] == "The Row"
    assert payload["entity_type"] == "brand"
    assert payload["source_type"] == "manual_import"
    assert payload["source_name"] == "Community Tool Export"
    assert payload["row_count"] == 2
    assert payload["total_count"] == 2
    assert payload["current_mentions"] == 1
    assert payload["baseline_mentions"] == 1
    assert list(payload["evidence"][0]) == [
        "id",
        "window",
        "source_name",
        "title",
        "url",
        "published_at",
        "collected_at",
    ]
    forbidden = {
        "summary",
        "matches",
        "match_status",
        "alias",
        "confidence",
        "reason",
        "context_terms",
        "source_file",
        "source_path",
        "import_path",
        "raw_comment",
        "account_id",
        "profile_url",
        "media_url",
    }
    assert forbidden.isdisjoint(payload)
    assert forbidden.isdisjoint(payload["evidence"][0])


def test_imported_entity_evidence_command_prints_table(tmp_path: Path) -> None:
    data_dir = _prepare_imported_entity_evidence_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
            "--source-name",
            "Community Tool Export",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual entity evidence from local SQLite." in result.output
    assert "The Row current mention" in result.output
    assert "https://example.com/current" in result.output
    for forbidden in (
        "private review note",
        "alias",
        "confidence",
        "reason",
        "context_terms",
        "raw_comment",
    ):
        assert forbidden not in result.output


def _fail_imported_entity_evidence_query(*args, **kwargs):
    raise AssertionError("query_imported_entity_evidence should not be called")


def test_imported_entity_evidence_command_requires_entity_name(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-type",
            "brand",
        ],
    )

    assert result.exit_code != 0
    assert "--entity-name" in result.output
    assert not data_dir.exists()


def test_imported_entity_evidence_command_requires_entity_type(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
        ],
    )

    assert result.exit_code != 0
    assert "--entity-type" in result.output
    assert not data_dir.exists()


def test_imported_entity_evidence_command_rejects_blank_entity_name_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_evidence",
        _fail_imported_entity_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "  ",
            "--entity-type",
            "brand",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported entity evidence: invalid --entity-name" in result.output
    assert "query_imported_entity_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_entity_evidence_command_rejects_blank_entity_type_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_evidence",
        _fail_imported_entity_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            " ",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported entity evidence: invalid --entity-type" in result.output
    assert "query_imported_entity_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_entity_evidence_command_rejects_invalid_as_of_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_evidence",
        _fail_imported_entity_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported entity evidence: invalid --as-of" in result.output
    assert "query_imported_entity_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_entity_evidence_command_rejects_invalid_format_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_evidence",
        _fail_imported_entity_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "query_imported_entity_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--current-days", "0"),
        ("--baseline-days", "0"),
        ("--limit", "-1"),
    ],
)
def test_imported_entity_evidence_command_rejects_invalid_numbers_without_query(
    tmp_path: Path,
    monkeypatch,
    option: str,
    value: str,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_evidence",
        _fail_imported_entity_evidence_query,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
            option,
            value,
        ],
    )

    assert result.exit_code != 0
    assert option in result.output
    assert "query_imported_entity_evidence should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_entity_evidence_command_blank_source_name_is_no_filter(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_evidence_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
            "--source-name",
            "   ",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["source_name"] is None
    assert payload["total_count"] == 3
    assert payload["current_mentions"] == 2


def test_imported_entity_evidence_command_missing_database_is_read_only(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "missing-data"
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["row_count"] == 0
    assert payload["total_count"] == 0
    assert payload["evidence"] == []
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []


def test_imported_entity_evidence_command_invalid_schema_no_traceback(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with sqlite3.connect(data_dir / "fashion-radar.sqlite") as connection:
        connection.execute("create table schema_metadata (version integer primary key)")
        connection.execute(f"insert into schema_metadata (version) values ({SCHEMA_VERSION})")

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported entity evidence" in result.output
    assert "Traceback" not in result.output


def test_imported_entity_evidence_command_does_not_mutate_existing_database(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_evidence_cli_fixture(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    with sqlite3.connect(db_path) as connection:
        before_items = connection.execute("select count(*) from items").fetchone()[0]
        before_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        before_schema_version = connection.execute(
            "select version from schema_metadata"
        ).fetchone()[0]
        before_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    with sqlite3.connect(db_path) as connection:
        after_items = connection.execute("select count(*) from items").fetchone()[0]
        after_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        after_schema_version = connection.execute("select version from schema_metadata").fetchone()[
            0
        ]
        after_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert after_items == before_items
    assert after_matches == before_matches
    assert after_schema_version == before_schema_version
    assert after_tables == before_tables


def test_imported_entity_deltas_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-entity-deltas", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--current-days" in result.output
    assert "--baseline-days" in result.output
    assert "--entity-type" in result.output
    assert "--source-name" in result.output
    assert "--format" in result.output
    assert "Compare imported manual entity counts" in result.output


def test_imported_entity_deltas_command_missing_database_is_read_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["row_count"] == 0
    assert payload["total_count"] == 0
    assert payload["current_matched_item_count"] == 0
    assert payload["baseline_matched_item_count"] == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )


def test_imported_entity_deltas_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_deltas_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "database",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "entity_type",
        "source_name",
        "limit",
        "row_count",
        "total_count",
        "current_matched_item_count",
        "baseline_matched_item_count",
        "entities",
    ]
    assert payload["row_count"] == 2
    assert payload["total_count"] == 2
    assert payload["current_matched_item_count"] == 2
    assert payload["baseline_matched_item_count"] == 1
    assert list(payload["entities"][0]) == [
        "entity_name",
        "entity_type",
        "current_count",
        "baseline_count",
        "delta",
        "change_label",
        "current_source_count",
        "baseline_source_count",
        "source_count_delta",
        "first_collected_at",
        "latest_collected_at",
    ]
    forbidden = {
        "id",
        "item_id",
        "title",
        "url",
        "summary",
        "reason",
        "context_terms",
        "confidence",
        "alias",
        "source_file",
        "source_path",
        "import_path",
    }
    assert forbidden.isdisjoint(payload)
    for entity in payload["entities"]:
        assert forbidden.isdisjoint(entity)


def test_imported_entity_deltas_command_prints_table_without_item_fields(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_deltas_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual entity deltas from local SQLite." in result.output
    assert "Alaia | brand | 1 | 0 | 1 | new_in_current" in result.output
    assert "The Row | brand | 1 | 1 | 0 | unchanged" in result.output
    assert "The Row Margaux current" not in result.output
    assert "https://example.com/current" not in result.output
    for forbidden in (
        "alias",
        "confidence",
        "reason",
        "context_terms",
        "hidden_context",
        "margaux",
        "flats",
        "rss",
        "source_file",
        "source_path",
        "import_path",
    ):
        assert forbidden not in result.output


def _fail_imported_entity_deltas_query(*args, **kwargs):
    raise AssertionError("query_imported_entity_deltas should not be called")


def test_imported_entity_deltas_command_rejects_invalid_format_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_deltas",
        _fail_imported_entity_deltas_query,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "query_imported_entity_deltas should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_entity_deltas_command_rejects_invalid_as_of_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_deltas",
        _fail_imported_entity_deltas_query,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not compare imported entity deltas: invalid --as-of" in result.output
    assert "query_imported_entity_deltas should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_entity_deltas_command_rejects_invalid_numbers_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_deltas",
        _fail_imported_entity_deltas_query,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--current-days",
            "0",
        ],
    )

    assert result.exit_code != 0
    assert "--current-days" in result.output
    assert "query_imported_entity_deltas should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()


def test_imported_entity_deltas_command_handles_special_character_data_dir(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_deltas_cli_fixture(
        tmp_path,
        data_dir_name="data ? # & %",
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["row_count"] == 2
    assert payload["database"] == str(data_dir / "fashion-radar.sqlite")


def test_imported_entity_deltas_command_invalid_schema_no_traceback(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with sqlite3.connect(data_dir / "fashion-radar.sqlite") as connection:
        connection.execute("create table schema_metadata (version integer primary key)")
        connection.execute(f"insert into schema_metadata (version) values ({SCHEMA_VERSION})")

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not compare imported entity deltas" in result.output
    assert "Traceback" not in result.output


def test_imported_entity_deltas_command_does_not_mutate_existing_database(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_deltas_cli_fixture(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    with sqlite3.connect(db_path) as connection:
        before_items = connection.execute("select count(*) from items").fetchone()[0]
        before_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        before_schema_version = connection.execute(
            "select version from schema_metadata"
        ).fetchone()[0]
        before_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    with sqlite3.connect(db_path) as connection:
        after_items = connection.execute("select count(*) from items").fetchone()[0]
        after_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        after_schema_version = connection.execute("select version from schema_metadata").fetchone()[
            0
        ]
        after_tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert after_items == before_items
    assert after_matches == before_matches
    assert after_schema_version == before_schema_version
    assert after_tables == before_tables


def _prepare_imported_entity_deltas_cli_fixture(
    tmp_path: Path,
    *,
    data_dir_name: str = "data",
) -> Path:
    data_dir = tmp_path / data_dir_name
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    current_id = _store_imported_entity_delta_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/current",
        title="The Row Margaux current",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    baseline_id = _store_imported_entity_delta_item(
        repository,
        source_name="Manual Export",
        url="https://example.com/baseline",
        title="The Row baseline",
        published_at=datetime(2026, 6, 3, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 3, 9, 0, tzinfo=UTC),
    )
    new_id = _store_imported_entity_delta_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/new",
        title="Alaia flats",
        published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 11, 9, 0, tzinfo=UTC),
    )
    rss_id = _store_imported_entity_delta_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss",
        title="RSS Alaia",
        published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(current_id, [_imported_entity_delta_match("The Row", "brand")])
    repository.replace_item_matches(baseline_id, [_imported_entity_delta_match("The Row", "brand")])
    repository.replace_item_matches(new_id, [_imported_entity_delta_match("Alaia", "brand")])
    repository.replace_item_matches(rss_id, [_imported_entity_delta_match("Alaia", "brand")])
    engine.dispose()
    return data_dir


def _prepare_imported_entity_evidence_cli_fixture(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    as_of = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)
    current_id = _store_imported_entity_delta_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/current",
        title="The Row current mention",
        published_at=as_of - timedelta(hours=1),
        collected_at=as_of - timedelta(hours=1),
    )
    baseline_id = _store_imported_entity_delta_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/baseline",
        title="The Row baseline mention",
        published_at=as_of - timedelta(days=10),
        collected_at=as_of - timedelta(days=10),
    )
    manual_id = _store_imported_entity_delta_item(
        repository,
        source_name="Manual Export",
        url="https://example.com/manual",
        title="The Row manual mention",
        published_at=as_of - timedelta(hours=2),
        collected_at=as_of - timedelta(hours=2),
    )
    other_entity_id = _store_imported_entity_delta_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/other-entity",
        title="Alaia current mention",
        published_at=as_of - timedelta(hours=3),
        collected_at=as_of - timedelta(hours=3),
    )
    rss_id = _store_imported_entity_delta_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss",
        title="The Row RSS mention",
        published_at=as_of - timedelta(hours=4),
        collected_at=as_of - timedelta(hours=4),
    )
    future_id = _store_imported_entity_delta_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/future",
        title="The Row future mention",
        published_at=as_of + timedelta(hours=1),
        collected_at=as_of + timedelta(hours=1),
    )
    old_id = _store_imported_entity_delta_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/old",
        title="The Row old mention",
        published_at=as_of - timedelta(days=60),
        collected_at=as_of - timedelta(days=60),
    )
    repository.replace_item_matches(
        current_id,
        [
            _imported_entity_delta_match("The Row", "brand"),
            _imported_entity_delta_match("The Row", "brand"),
        ],
    )
    repository.replace_item_matches(baseline_id, [_imported_entity_delta_match("The Row", "brand")])
    repository.replace_item_matches(manual_id, [_imported_entity_delta_match("The Row", "brand")])
    repository.replace_item_matches(
        other_entity_id,
        [_imported_entity_delta_match("Alaia", "brand")],
    )
    repository.replace_item_matches(rss_id, [_imported_entity_delta_match("The Row", "brand")])
    repository.replace_item_matches(future_id, [_imported_entity_delta_match("The Row", "brand")])
    repository.replace_item_matches(old_id, [_imported_entity_delta_match("The Row", "brand")])
    engine.dispose()
    return data_dir


def _prepare_imported_candidates_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        """
version: 1
scoring:
  current_window_days: 7
  baseline_window_days: 30
candidate_discovery:
  min_current_mentions: 1
  review_min_current_mentions: 1
  min_single_token_mentions: 99
  min_single_token_distinct_sources: 99
  max_candidates: 10
""".lstrip(),
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    as_of = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)
    for source_name, url in (
        ("Community Tool Export", "https://example.com/imported-a"),
        ("Manual Export", "https://example.com/imported-b"),
    ):
        repository.upsert_item(
            CollectedItem(
                source_name=source_name,
                source_type=SourceType.MANUAL_IMPORT,
                url=url,
                title="Le Teckel bag current mention",
                published_at=as_of - timedelta(hours=1),
                summary="private review note",
            ),
            collected_at=as_of - timedelta(hours=1),
        )
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/rss",
            title="Le Teckel bag RSS mention",
            published_at=as_of - timedelta(hours=2),
            summary="Le Teckel bag appears outside manual imports.",
        ),
        collected_at=as_of - timedelta(hours=2),
    )
    engine.dispose()
    return config_dir, data_dir


def _prepare_imported_candidate_evidence_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        """
version: 1
scoring:
  current_window_days: 7
  baseline_window_days: 30
candidate_discovery:
  min_current_mentions: 1
  review_min_current_mentions: 1
  min_single_token_mentions: 99
  min_single_token_distinct_sources: 99
  max_candidates: 10
""".lstrip(),
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    as_of = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)
    for source_name, url, collected_at in (
        (
            "Community Tool Export",
            "https://example.com/current",
            as_of - timedelta(hours=1),
        ),
        (
            "Community Tool Export",
            "https://example.com/baseline",
            as_of - timedelta(days=10),
        ),
        (
            "Manual Export",
            "https://example.com/manual",
            as_of - timedelta(hours=2),
        ),
    ):
        repository.upsert_item(
            CollectedItem(
                source_name=source_name,
                source_type=SourceType.MANUAL_IMPORT,
                url=url,
                title=(
                    "Le Teckel bag current mention"
                    if "current" in url or "manual" in url
                    else "Le Teckel bag baseline mention"
                ),
                published_at=collected_at,
                summary="private review note",
            ),
            collected_at=collected_at,
        )
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/rss",
            title="Le Teckel bag RSS mention",
            published_at=as_of - timedelta(hours=3),
            summary="Le Teckel bag appears outside manual imports.",
        ),
        collected_at=as_of - timedelta(hours=3),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="Community Tool Export",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/future",
            title="Le Teckel bag future mention",
            published_at=as_of + timedelta(hours=1),
            summary="future local note",
        ),
        collected_at=as_of + timedelta(hours=1),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="Community Tool Export",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/old",
            title="Le Teckel bag old mention",
            published_at=as_of - timedelta(days=60),
            summary="old local note",
        ),
        collected_at=as_of - timedelta(days=60),
    )
    engine.dispose()
    return config_dir, data_dir


def _store_imported_entity_delta_item(
    repository: ItemRepository,
    *,
    source_name: str,
    url: str,
    title: str,
    published_at: datetime,
    collected_at: datetime,
    source_type: SourceType = SourceType.MANUAL_IMPORT,
) -> int:
    return repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=published_at,
        ),
        source_weight=1.0,
        collected_at=collected_at,
    )


def _imported_entity_delta_match(entity_name: str, entity_type: str) -> dict[str, object]:
    return {
        "entity_name": entity_name,
        "entity_type": entity_type,
        "alias": entity_name,
        "confidence": 1.0,
        "reason": "context",
        "context_terms": ["hidden_context"],
    }


def _prepare_imported_signals_cli_fixture(
    tmp_path: Path,
    *,
    data_dir_name: str = "data",
) -> Path:
    data_dir = tmp_path / data_dir_name
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    matched_id = repository.upsert_item(
        CollectedItem(
            source_name="Community Tool Export",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/margaux",
            title="Margaux interest",
            published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
            summary="Margaux appears in local notes.",
        ),
        source_weight=1.4,
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
        platform="instagram",
    )
    repository.upsert_item(
        CollectedItem(
            source_name="Community Tool Export",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/unmatched",
            title="Unmatched local item",
            published_at=datetime(2026, 6, 12, 8, 30, tzinfo=UTC),
        ),
        collected_at=datetime(2026, 6, 12, 10, 0, tzinfo=UTC),
        platform="tiktok",
    )
    repository.upsert_item(
        CollectedItem(
            source_name="Manual Import",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/old",
            title="Old local item",
            published_at=datetime(2026, 6, 10, 8, 0, tzinfo=UTC),
        ),
        collected_at=datetime(2026, 6, 10, 9, 0, tzinfo=UTC),
        platform="manual",
    )
    repository.upsert_item(
        CollectedItem(
            source_name="RSS Source",
            source_type=SourceType.RSS,
            url="https://example.com/rss",
            title="RSS item",
            published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        ),
        collected_at=datetime(2026, 6, 12, 11, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        matched_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "context",
                "context_terms": ["margaux"],
            }
        ],
    )
    engine.dispose()
    return data_dir


def _create_v4_database(path: Path) -> None:
    engine = create_sqlite_engine(path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (4)")
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name varchar(255) not null,
                source_type varchar(64) not null,
                url text not null,
                normalized_url text not null,
                title text not null,
                published_at varchar(64) not null,
                source_weight float not null default 1.0,
                collected_at varchar(64) not null,
                summary text,
                content_hash varchar(64) not null,
                constraint uq_items_normalized_url unique (normalized_url)
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table item_entities (
                id integer primary key,
                item_id integer not null,
                entity_name varchar(255) not null,
                entity_type varchar(64) not null,
                alias varchar(255) not null,
                confidence float not null,
                reason varchar(64) not null,
                context_terms text not null default '[]'
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table entity_first_seen (
                id integer primary key,
                entity_name varchar(255) not null,
                entity_type varchar(64) not null,
                first_seen_at varchar(64) not null,
                last_seen_at varchar(64) not null,
                constraint uq_entity_first_seen_entity unique (entity_name, entity_type)
            )
            """
        )
    engine.dispose()


def _create_future_metadata_only_database(path: Path) -> None:
    engine = create_sqlite_engine(path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (999)")
    engine.dispose()


def _init_cli_dirs(tmp_path: Path) -> tuple[Path, Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    result = CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    assert result.exit_code == 0
    return config_dir, data_dir, reports_dir


def test_init_writes_example_configs(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0
    assert (config_dir / "sources.yaml").exists()
    assert (config_dir / "entities.yaml").exists()
    assert (config_dir / "scoring.yaml").exists()
    assert data_dir.exists()
    assert reports_dir.exists()


def test_init_reads_default_directories_from_environment(tmp_path: Path) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"

    result = CliRunner().invoke(
        app,
        ["init"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert (config_dir / "sources.yaml").exists()
    assert data_dir.exists()
    assert reports_dir.exists()


def test_migrate_db_command_initializes_missing_database(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "migrate-db",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Database path:" in result.output
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output
    assert (data_dir / "fashion-radar.sqlite").exists()


def test_migrate_db_command_upgrades_v4_database(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    db_path = data_dir / "fashion-radar.sqlite"
    _create_v4_database(db_path)

    result = CliRunner().invoke(app, ["migrate-db", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output
    with create_sqlite_engine(db_path).connect() as connection:
        version = connection.execute(select(schema_metadata.c.version)).scalar_one()
    assert version == SCHEMA_VERSION


def test_migrate_db_rejects_future_schema_without_traceback(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("update schema_metadata set version = 999")
    engine.dispose()

    result = CliRunner().invoke(app, ["migrate-db", "--data-dir", str(data_dir)])

    assert result.exit_code == 1
    assert "Could not migrate database schema" in result.output
    assert "Unsupported database schema version 999" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "migrate-db --data-dir" not in result.output
    assert "Traceback" not in result.output


def test_migrate_db_does_not_run_collection_or_review_workflows(
    tmp_path: Path,
    monkeypatch,
) -> None:
    forbidden = [
        "_package_digest_or_exit",
        "collect_configured_sources",
        "dashboard",
        "discover_candidates",
        "match_stored_items",
        "package_daily_digest",
        "write_daily_report_files",
        "load_source_config",
        "load_entity_config",
        "load_scoring_config",
        "load_manual_signal_rows",
        "load_manual_signal_directory_rows",
        "store_manual_signal_rows",
        "build_trend_comparison",
        "query_imported_candidate_evidence",
        "query_imported_candidates",
        "query_imported_entity_deltas",
        "query_imported_signals",
        "query_imported_signals_summary",
    ]

    def fail(name: str):
        def inner(*_args, **_kwargs):
            raise AssertionError(f"{name} should not be called")

        return inner

    for name in forbidden:
        monkeypatch.setattr(cli_module, name, fail(name))

    result = CliRunner().invoke(
        app,
        [
            "migrate-db",
            "--data-dir",
            str(tmp_path / "data"),
        ],
    )

    assert result.exit_code == 0
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output


def test_doctor_requires_initialized_config(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    data_dir.mkdir()
    reports_dir.mkdir()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Configuration directory" in result.output
    assert "Missing required config" in result.output


def test_doctor_reports_current_database_schema(tmp_path: Path) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output


def test_doctor_accepts_signed_current_database_schema_string(tmp_path: Path) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "delete from schema_metadata",
        )
        connection.exec_driver_sql(
            "insert into schema_metadata (version) values (?)",
            (f"+{SCHEMA_VERSION}",),
        )
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output


def test_doctor_reports_missing_database_without_creating_it(tmp_path: Path) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Database schema: not initialized" in result.output
    assert not db_path.exists()


def test_doctor_reports_old_database_schema_with_migration_hint(tmp_path: Path) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    _create_v4_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: v4 (upgrade available" in result.output
    assert "fashion-radar migrate-db --data-dir" in result.output


def test_doctor_reports_future_database_schema_without_migrate_hint(tmp_path: Path) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("update schema_metadata set version = 999")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert f"Database schema: v999 (unsupported; expected v{SCHEMA_VERSION})" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_doctor_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert f"Database schema: v999 (unsupported; expected v{SCHEMA_VERSION})" in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_doctor_rejects_current_version_database_missing_required_tables(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "missing tables" in result.output
    assert "Traceback" not in result.output


def test_doctor_rejects_current_version_database_missing_required_columns(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    _create_v4_database(db_path)
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            create table collector_runs (
                id integer primary key,
                source_name varchar(255) not null,
                source_type varchar(64) not null,
                status varchar(32) not null,
                started_at varchar(64) not null,
                finished_at varchar(64),
                items_seen integer not null default 0,
                items_stored integer not null default 0,
                error_message text,
                error_type varchar(128)
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table source_health (
                id integer primary key,
                source_name varchar(255) not null,
                source_type varchar(64) not null,
                consecutive_failures integer not null default 0,
                last_success_at varchar(64),
                last_failure_at varchar(64),
                unhealthy_until varchar(64),
                last_error_message text,
                constraint uq_source_health_source unique (source_name, source_type)
            )
            """
        )
        connection.exec_driver_sql(f"update schema_metadata set version = {SCHEMA_VERSION}")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "missing columns" in result.output
    assert "platform" in result.output
    assert "Traceback" not in result.output


def test_doctor_reports_existing_sqlite_without_schema_metadata_with_migrate_hint(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table unrelated (id integer primary key)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "missing schema_metadata table" in result.output
    assert "fashion-radar migrate-db --data-dir" in result.output
    assert "Traceback" not in result.output


def test_doctor_reports_schema_metadata_without_version_without_migrate_hint(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (id integer primary key)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version is missing" in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_doctor_reports_empty_schema_metadata_version_with_migrate_hint(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version is empty" in result.output
    assert "fashion-radar migrate-db --data-dir" in result.output
    assert "Traceback" not in result.output


def test_doctor_rejects_unreadable_database_without_traceback(tmp_path: Path) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    (data_dir / "fashion-radar.sqlite").write_text("not sqlite", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "Traceback" not in result.output


def test_doctor_rejects_non_integer_database_schema_version(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version text)")
        connection.exec_driver_sql("insert into schema_metadata (version) values ('latest')")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version is not an integer" in result.output
    assert "Traceback" not in result.output


def test_doctor_rejects_duplicate_database_schema_versions(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version has multiple rows" in result.output
    assert "Traceback" not in result.output


def test_doctor_rejects_decimal_database_schema_version(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = _init_cli_dirs(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version real)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5.7)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version is not an integer" in result.output
    assert "Traceback" not in result.output


def test_schedule_example_prints_cron_snippet(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "schedule-example",
            "--mode",
            "cron",
            "--project-dir",
            str(tmp_path),
            "--config-dir",
            str(tmp_path / "configs"),
            "--data-dir",
            str(tmp_path / "data"),
            "--reports-dir",
            str(tmp_path / "reports"),
            "--time",
            "08:30",
        ],
    )

    assert result.exit_code == 0
    assert "crontab -e" in result.output
    assert "PATH=/usr/local/bin:/usr/bin:/bin" in result.output
    crontab_path_line = next(
        line for line in result.output.splitlines() if line.startswith("PATH=")
    )
    assert crontab_path_line == "PATH=/usr/local/bin:/usr/bin:/bin"
    assert 'PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" uv run' in result.output
    assert "uv run fashion-radar run" in result.output
    assert "30 8 * * *" in result.output
    assert r"$(date -u +\%Y-\%m-\%dT\%H:\%M:\%SZ)" in result.output


def test_schedule_example_prints_github_actions_snippet() -> None:
    result = CliRunner().invoke(
        app,
        [
            "schedule-example",
            "--mode",
            "github-actions",
            "--time",
            "08:30",
        ],
    )

    assert result.exit_code == 0
    assert "GitHub Actions schedule times are UTC" in result.output
    assert "cron: '30 8 * * *'" in result.output
    assert "uv run fashion-radar run" in result.output


def test_schedule_example_prints_systemd_snippet(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "schedule-example",
            "--mode",
            "systemd",
            "--project-dir",
            str(tmp_path),
            "--time",
            "08:30",
        ],
    )

    assert result.exit_code == 0
    assert "fashion-radar.service" in result.output
    assert "fashion-radar.timer" in result.output
    assert f"WorkingDirectory={tmp_path}" in result.output
    assert "OnCalendar=*-*-* 08:30:00" in result.output
    assert "$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)" in result.output


def test_schedule_example_rejects_invalid_time(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "schedule-example",
            "--mode",
            "cron",
            "--project-dir",
            str(tmp_path),
            "--time",
            "25:00",
        ],
    )

    assert result.exit_code == 1
    assert "HH:MM" in result.output


def test_dashboard_command_requires_dashboard_extra(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli_module.importlib.util, "find_spec", lambda name: None)

    result = CliRunner().invoke(
        app,
        [
            "dashboard",
            "--data-dir",
            str(tmp_path / "data"),
        ],
    )

    assert result.exit_code == 1
    assert "dashboard extra" in result.output
    assert "uv sync --extra dashboard" in result.output


def test_dashboard_command_launches_streamlit_on_localhost(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(cli_module.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(cli_module.subprocess, "run", lambda command, check: calls.append(command))

    result = CliRunner().invoke(
        app,
        [
            "dashboard",
            "--data-dir",
            str(tmp_path / "data"),
            "--reports-dir",
            str(tmp_path / "reports"),
            "--config-dir",
            str(tmp_path / "config"),
        ],
    )

    assert result.exit_code == 0
    command = calls[0]
    assert command[:3] == [cli_module.sys.executable, "-m", "streamlit"]
    assert "--server.address" in command
    assert command[command.index("--server.address") + 1] == "127.0.0.1"
    assert "--server.port" in command
    assert command[command.index("--server.port") + 1] == "8501"
    assert "--" in command
    separator_index = command.index("--")
    app_args = command[separator_index + 1 :]
    assert app_args[app_args.index("--data-dir") + 1] == str(tmp_path / "data")
    assert app_args[app_args.index("--reports-dir") + 1] == str(tmp_path / "reports")
    assert app_args[app_args.index("--config-dir") + 1] == str(tmp_path / "config")


def test_report_command_writes_markdown_and_json(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    data_dir.mkdir()
    reports_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        """
version: 1
scoring:
  current_window_days: 7
  baseline_window_days: 30
""".lstrip(),
        encoding="utf-8",
    )
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = repository.upsert_item(
        CollectedItem(
            source_name="Vogue Business",
            source_type=SourceType.RSS,
            url="https://example.com/the-row",
            title="The Row Margaux handbag gains momentum",
            published_at="2026-06-11T10:00:00Z",
            summary="Short attributed summary.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    result = CliRunner().invoke(
        app,
        [
            "report",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    markdown_path = reports_dir / "fashion-radar-2026-06-11.md"
    json_path = reports_dir / "fashion-radar-2026-06-11.json"
    assert markdown_path.exists()
    assert json_path.exists()
    assert "The Row" in markdown_path.read_text(encoding="utf-8")
    assert '"entity_name": "The Row"' in json_path.read_text(encoding="utf-8")


def _write_report_cli_config(config_dir: Path) -> None:
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")


def _write_daily_report_pair(reports_dir: Path, report_date: str) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = reports_dir / f"fashion-radar-{report_date}.md"
    json_path = reports_dir / f"fashion-radar-{report_date}.json"
    markdown_path.write_text(f"# Fashion Radar {report_date}\n", encoding="utf-8")
    json_path.write_text(
        json.dumps({"metadata": {"report_date": f"{report_date}T00:00:00+00:00"}}),
        encoding="utf-8",
    )
    return markdown_path, json_path


def test_report_command_packages_digest_artifacts(monkeypatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    _write_report_cli_config(config_dir)

    monkeypatch.setattr(
        cli_module,
        "write_daily_report_files",
        lambda **kwargs: _write_daily_report_pair(kwargs["reports_dir"], "2026-06-11"),
    )

    result = CliRunner().invoke(
        app,
        [
            "report",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--digest-latest",
            "copy",
            "--digest-index",
            "--digest-eml",
            "--digest-summary",
        ],
    )

    assert result.exit_code == 0
    assert (reports_dir / "latest.md").exists()
    assert (reports_dir / "latest.json").exists()
    assert (reports_dir / "report-index.json").exists()
    assert (reports_dir / "fashion-radar-2026-06-11.eml").exists()
    assert "Wrote latest Markdown: " in result.output
    assert "Wrote latest JSON: " in result.output
    assert "Wrote report index: " in result.output
    assert "Wrote local EML digest: " in result.output
    assert "Local observed fashion report is ready for review." in result.output


def test_report_command_digest_packaging_error_exits_nonzero(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    _write_report_cli_config(config_dir)

    monkeypatch.setattr(
        cli_module,
        "write_daily_report_files",
        lambda **kwargs: _write_daily_report_pair(kwargs["reports_dir"], "2026-06-11"),
    )

    def fail_package_daily_digest(**_kwargs: object) -> DigestResult:
        raise RuntimeError("bad digest")

    monkeypatch.setattr(
        cli_module,
        "package_daily_digest",
        fail_package_daily_digest,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "report",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--digest-index",
        ],
    )

    assert result.exit_code == 1
    assert "Could not package digest: bad digest" in result.output


def test_report_command_help_lists_digest_options() -> None:
    result = CliRunner().invoke(app, ["report", "--help"], env={"COLUMNS": "140"})

    assert result.exit_code == 0
    assert "--digest-latest" in result.output
    assert "--digest-index" in result.output
    assert "--digest-eml" in result.output
    assert "--digest-summary" in result.output


def test_report_command_default_output_creates_no_digest_artifacts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    _write_report_cli_config(config_dir)

    monkeypatch.setattr(
        cli_module,
        "write_daily_report_files",
        lambda **kwargs: _write_daily_report_pair(kwargs["reports_dir"], "2026-06-11"),
    )
    markdown_path = reports_dir / "fashion-radar-2026-06-11.md"
    json_path = reports_dir / "fashion-radar-2026-06-11.json"

    result = CliRunner().invoke(
        app,
        [
            "report",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert result.output == (
        f"Wrote Markdown report: {markdown_path}\nWrote JSON report: {json_path}\n"
    )
    assert not (reports_dir / "latest.md").exists()
    assert not (reports_dir / "latest.json").exists()
    assert not (reports_dir / "report-index.json").exists()
    assert not (reports_dir / "fashion-radar-2026-06-11.eml").exists()


def _prepare_candidate_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel",
            title="Le Teckel bag rises",
            published_at="2026-06-11T10:00:00Z",
            summary="Le Teckel bag appears again.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="WWD",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel-2",
            title="Le Teckel bag appears again",
            published_at="2026-06-11T10:30:00Z",
            summary="Another configured source mentions Le Teckel bag.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 30, tzinfo=UTC),
    )
    return config_dir, data_dir


def test_candidates_command_prints_json(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_candidate_cli_fixture(tmp_path)
    scoring_before = (config_dir / "scoring.yaml").read_bytes()
    entities_before = (config_dir / "entities.yaml").read_bytes()

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload[0]["phrase"] == "Le Teckel bag"
    assert (config_dir / "scoring.yaml").read_bytes() == scoring_before
    assert (config_dir / "entities.yaml").read_bytes() == entities_before


def test_candidates_command_accepts_signed_current_database_schema_string(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_candidate_cli_fixture(tmp_path)
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    with engine.begin() as connection:
        connection.exec_driver_sql("delete from schema_metadata")
        connection.exec_driver_sql(
            "insert into schema_metadata (version) values (?)",
            (f"+{SCHEMA_VERSION}",),
        )
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload[0]["phrase"] == "Le Teckel bag"


def test_candidates_command_prints_table(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_candidate_cli_fixture(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Phrase" in result.output
    assert "candidate signal" in result.output.lower()
    assert "configured sources and imported local signals" in result.output
    assert "Le Teckel bag" in result.output


def test_candidates_command_is_read_only_when_database_is_missing(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == []
    assert not (data_dir / "fashion-radar.sqlite").exists()


def _prepare_trend_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        """
version: 1
scoring:
  current_window_days: 7
  baseline_window_days: 30
  min_match_confidence: 0.5
candidate_discovery:
  min_current_mentions: 1
  review_min_current_mentions: 1
  min_single_token_mentions: 1
  min_single_token_distinct_sources: 1
  max_candidates: 10
""".lstrip(),
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")

    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)

    def store(
        *,
        url: str,
        title: str,
        source_name: str,
        collected_at: datetime,
        entity_name: str,
        entity_type: str = "brand",
    ) -> None:
        item_id = repository.upsert_item(
            CollectedItem(
                source_name=source_name,
                source_type=SourceType.RSS,
                url=url,
                title=title,
                published_at=collected_at,
                summary=title,
            ),
            collected_at=collected_at,
        )
        repository.replace_item_matches(
            item_id,
            [
                {
                    "entity_name": entity_name,
                    "entity_type": entity_type,
                    "alias": entity_name,
                    "confidence": 1.0,
                    "reason": "accepted",
                    "context_terms": [],
                }
            ],
        )

    as_of = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)
    store(
        url="https://example.com/current-row",
        title="The Row Margaux bag gains momentum",
        source_name="Fashionista",
        collected_at=as_of - timedelta(days=1),
        entity_name="The Row",
    )
    store(
        url="https://example.com/current-row-2",
        title="The Row Margaux bag appears again",
        source_name="WWD",
        collected_at=as_of - timedelta(days=2),
        entity_name="The Row",
    )
    store(
        url="https://example.com/baseline-row",
        title="The Row Margaux bag baseline mention",
        source_name="Vogue Business",
        collected_at=as_of - timedelta(days=8),
        entity_name="The Row",
    )
    store(
        url="https://example.com/dropped",
        title="Old Brand mention cools",
        source_name="Vogue Business",
        collected_at=as_of - timedelta(days=8),
        entity_name="Old Brand",
    )
    return config_dir, data_dir


def _prepare_candidate_trend_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        """
version: 1
scoring:
  current_window_days: 7
  baseline_window_days: 30
candidate_discovery:
  min_current_mentions: 1
  review_min_current_mentions: 1
  min_single_token_mentions: 99
  min_single_token_distinct_sources: 99
  max_candidates: 1
""".lstrip(),
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")

    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    as_of = datetime(2026, 6, 12, tzinfo=UTC)
    baseline_as_of = datetime(2026, 6, 5, tzinfo=UTC)

    def store(*, title: str, url: str, source_name: str, collected_at: datetime) -> None:
        repository.upsert_item(
            CollectedItem(
                source_name=source_name,
                source_type=SourceType.RSS,
                url=url,
                title=title,
                published_at=collected_at,
                summary=title,
            ),
            collected_at=collected_at,
        )

    for index, source_name in enumerate(("Source A", "Source B", "Source C"), start=1):
        store(
            title="Fading bag baseline mention",
            url=f"https://example.com/fading-baseline-{index}",
            source_name=source_name,
            collected_at=baseline_as_of - timedelta(hours=index),
        )
        store(
            title="Bright bag current mention",
            url=f"https://example.com/bright-current-{index}",
            source_name=source_name,
            collected_at=as_of - timedelta(hours=index),
        )
    store(
        title="Fading bag current mention",
        url="https://example.com/fading-current",
        source_name="Source A",
        collected_at=as_of - timedelta(hours=6),
    )
    return config_dir, data_dir


def _prepare_heat_mover_group_limit_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        """
version: 1
scoring:
  current_window_days: 7
  baseline_window_days: 30
  min_match_confidence: 0.5
  rising_min_mentions: 1
  hot_score_threshold: 999
candidate_discovery:
  enabled: false
""".lstrip(),
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")

    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    as_of = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)
    baseline_as_of = as_of - timedelta(days=7)

    def store(
        *,
        entity_name: str,
        url: str,
        title: str,
        source_name: str,
        collected_at: datetime,
    ) -> None:
        item_id = repository.upsert_item(
            CollectedItem(
                source_name=source_name,
                source_type=SourceType.RSS,
                url=url,
                title=title,
                published_at=collected_at,
                summary=title,
            ),
            collected_at=collected_at,
        )
        repository.replace_item_matches(
            item_id,
            [
                {
                    "entity_name": entity_name,
                    "entity_type": "brand",
                    "alias": entity_name,
                    "confidence": 1.0,
                    "reason": "accepted",
                    "context_terms": [],
                }
            ],
        )

    for entity_name, slug in (("Alaia", "alaia"), ("Khaite", "khaite")):
        store(
            entity_name=entity_name,
            url=f"https://example.com/{slug}-current",
            title=f"{entity_name} current heat",
            source_name="Fashionista",
            collected_at=as_of - timedelta(days=1),
        )

    for entity_name, slug in (("The Row", "the-row"), ("Miu Miu", "miu-miu")):
        store(
            entity_name=entity_name,
            url=f"https://example.com/{slug}-baseline",
            title=f"{entity_name} baseline heat",
            source_name="Vogue Business",
            collected_at=baseline_as_of - timedelta(hours=1),
        )
        store(
            entity_name=entity_name,
            url=f"https://example.com/{slug}-current-a",
            title=f"{entity_name} current heat one",
            source_name="Fashionista",
            collected_at=as_of - timedelta(days=1),
        )
        store(
            entity_name=entity_name,
            url=f"https://example.com/{slug}-current-b",
            title=f"{entity_name} current heat two",
            source_name="WWD",
            collected_at=as_of - timedelta(days=2),
        )

    return config_dir, data_dir


def _heat_mover_group_rows(report: HeatMoversReport, group_name: str):
    groups_by_name = {group.name: group for group in report.groups}
    return groups_by_name[group_name].rows


def _heat_mover_group_names(report: HeatMoversReport) -> list[str]:
    return [group.name for group in report.groups]


def test_trends_command_missing_database_writes_nothing(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    comparison = TrendComparison.model_validate_json(result.output)
    assert comparison.deltas == []
    assert comparison.baseline_as_of == datetime(2026, 6, 5, 12, 0, tzinfo=UTC)
    assert not data_dir.exists()
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_trends_command_rejects_invalid_dates_before_data_dir_creation(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not compare trends: invalid --as-of" in result.output
    assert not data_dir.exists()


def test_trends_command_rejects_invalid_baseline_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--baseline-as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not compare trends: invalid --baseline-as-of" in result.output
    assert not data_dir.exists()


def test_trends_command_rejects_baseline_at_or_after_as_of(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--baseline-as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "baseline-as-of must be before as-of" in result.output
    assert not data_dir.exists()


def test_trends_command_rejects_invalid_scoring_config_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        "version: 1\nscoring:\n  current_window_days: 0\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid trend config" in result.output
    assert not data_dir.exists()


def test_trends_command_rejects_incompatible_database_without_schema_mutation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    db_path = data_dir / "fashion-radar.sqlite"
    db_path.touch()

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "schema" in result.output.lower()
    assert "fashion-radar migrate-db --data-dir" in result.output
    with sqlite3.connect(db_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert table_names == set()


def test_trends_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-01-15T00:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_trends_command_prints_json(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    comparison = TrendComparison.model_validate_json(result.output)
    assert comparison.deltas
    assert "The Row" in {delta.name for delta in comparison.deltas}


def test_trends_command_prints_table(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Local observed trend deltas need review." in result.output
    assert "Status | Kind | Type | Name" in result.output
    assert "The Row" in result.output


def test_trends_command_include_dropped_surfaces_baseline_only_signals(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--include-dropped",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    comparison = TrendComparison.model_validate_json(result.output)
    assert "Old Brand" in {delta.name for delta in comparison.deltas}


def test_trends_command_limit_caps_ordered_deltas(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--limit",
            "1",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    comparison = TrendComparison.model_validate_json(result.output)
    assert len(comparison.deltas) == 1


def test_trends_command_existing_database_remains_read_only(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    with engine.connect() as connection:
        item_count = connection.execute(select(items.c.id)).all()
        match_count = connection.execute(select(item_entities.c.id)).all()

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    with engine.connect() as connection:
        assert connection.execute(select(items.c.id)).all() == item_count
        assert connection.execute(select(item_entities.c.id)).all() == match_count


def test_trends_command_help_lists_public_flags() -> None:
    result = CliRunner().invoke(app, ["trends", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "local observed signal deltas" in result.output
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "UTC baseline" in result.output
    assert "--baseline-as-of" in result.output
    assert "Include signals" in result.output
    assert "--no-include" in result.output
    assert "--limit" in result.output
    assert "--format" in result.output


def test_heat_movers_command_help_lists_public_flags() -> None:
    result = CliRunner().invoke(app, ["heat-movers", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "local observed new and rising heat movers" in result.output
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--baseline-as-of" in result.output
    assert "--limit" in result.output
    assert "--format" in result.output
    assert "--include-cooling" in result.output


def test_heat_movers_command_missing_database_writes_nothing_and_prints_empty_outputs(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    json_data_dir = tmp_path / "json-data"
    table_data_dir = tmp_path / "table-data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    json_result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(json_data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert json_result.exit_code == 0
    report = HeatMoversReport.model_validate_json(json_result.output)
    assert report.row_count == 0
    assert report.group_count == 4
    assert report.baseline_as_of == datetime(2026, 6, 5, 12, 0, tzinfo=UTC)
    assert _heat_mover_group_names(report) == [
        "new_tracked_entities",
        "rising_tracked_entities",
        "new_candidate_phrases",
        "rising_candidate_phrases",
    ]
    assert all(group.rows == [] for group in report.groups)
    assert not json_data_dir.exists()
    assert not (json_data_dir / "fashion-radar.sqlite").exists()

    table_result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(table_data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert table_result.exit_code == 0
    assert "# Heat Movers" in table_result.output
    assert "Local observed heat movement" in table_result.output
    assert "_No rows._" in table_result.output
    assert not table_data_dir.exists()
    assert not (table_data_dir / "fashion-radar.sqlite").exists()


def test_heat_movers_command_rejects_invalid_as_of_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review heat movers: invalid --as-of" in result.output
    assert not data_dir.exists()


def test_heat_movers_command_rejects_invalid_baseline_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--baseline-as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review heat movers: invalid --baseline-as-of" in result.output
    assert not data_dir.exists()


def test_heat_movers_command_rejects_baseline_at_or_after_as_of(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--baseline-as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review heat movers: baseline-as-of must be before as-of" in result.output
    assert not data_dir.exists()


def test_heat_movers_command_rejects_invalid_config_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        "version: 1\nscoring:\n  current_window_days: 0\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid heat movers config" in result.output
    assert not data_dir.exists()


def test_heat_movers_command_rejects_negative_limit_at_parse_time(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output
    assert not data_dir.exists()


def test_heat_movers_command_rejects_incompatible_database_without_schema_mutation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    db_path = data_dir / "fashion-radar.sqlite"
    db_path.touch()

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review heat movers" in result.output
    assert "schema" in result.output.lower()
    assert "fashion-radar migrate-db --data-dir" in result.output
    with sqlite3.connect(db_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert table_names == set()


def test_heat_movers_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-01-15T00:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review heat movers" in result.output
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_heat_movers_command_prints_grouped_json(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    report = HeatMoversReport.model_validate_json(result.output)
    assert _heat_mover_group_names(report) == [
        "new_tracked_entities",
        "rising_tracked_entities",
        "new_candidate_phrases",
        "rising_candidate_phrases",
    ]
    assert "The Row" in {
        row.name for row in _heat_mover_group_rows(report, "rising_tracked_entities")
    }


def test_heat_movers_command_groups_candidate_new_and_cooling_rows(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_candidate_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T00:00:00Z",
            "--baseline-as-of",
            "2026-06-05T00:00:00Z",
            "--include-cooling",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    report = HeatMoversReport.model_validate_json(result.output)
    assert "Bright bag" in {
        row.name for row in _heat_mover_group_rows(report, "new_candidate_phrases")
    }
    assert "Fading bag" in {row.name for row in _heat_mover_group_rows(report, "cooling_watchlist")}
    assert report.include_cooling is True


def test_heat_movers_command_limit_caps_each_group_not_raw_trend_deltas(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_heat_mover_group_limit_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--limit",
            "1",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    report = HeatMoversReport.model_validate_json(result.output)
    assert report.limit_per_group == 1
    assert len(_heat_mover_group_rows(report, "new_tracked_entities")) == 1
    assert len(_heat_mover_group_rows(report, "rising_tracked_entities")) == 1
    assert report.row_count == 2


def test_heat_movers_command_table_output_includes_local_observed_review_wording(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_candidate_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T00:00:00Z",
            "--baseline-as-of",
            "2026-06-05T00:00:00Z",
            "--include-cooling",
        ],
    )

    assert result.exit_code == 0
    assert "Local observed heat movers need review." in result.output
    assert "Local observed heat movement" in result.output
    assert "review" in result.output


def test_heat_movers_command_existing_database_remains_read_only(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    with engine.connect() as connection:
        item_count = connection.execute(select(items.c.id)).all()
        match_count = connection.execute(select(item_entities.c.id)).all()

    result = CliRunner().invoke(
        app,
        [
            "heat-movers",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    with engine.connect() as connection:
        assert connection.execute(select(items.c.id)).all() == item_count
        assert connection.execute(select(item_entities.c.id)).all() == match_count


def test_source_pack_lint_help_lists_format_and_strict() -> None:
    result = CliRunner().invoke(app, ["source-pack-lint", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--strict" in result.output
    assert "without collecting sources" in result.output


def test_source_pack_lint_prints_table_for_public_pack() -> None:
    result = CliRunner().invoke(
        app,
        ["source-pack-lint", "configs/source-packs/fashion-public.example.yaml"],
    )

    assert result.exit_code == 0
    assert "Source pack: configs/source-packs/fashion-public.example.yaml" in result.output
    assert "Sources:" in result.output
    assert "Findings:" in result.output
    assert "errors" in result.output


def test_source_pack_lint_prints_json_for_public_pack() -> None:
    result = CliRunner().invoke(
        app,
        [
            "source-pack-lint",
            "configs/source-packs/fashion-public.example.yaml",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["path"] == "configs/source-packs/fashion-public.example.yaml"
    assert payload["source_count"] == 16
    assert payload["type_counts"] == {"gdelt": 10, "rss": 6}
    assert isinstance(payload["findings"], list)


def test_source_pack_lint_strict_exits_nonzero_on_warnings(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        """
version: 1
sources:
  - name: Untagged GDELT
    type: gdelt
    query: fashion
    weight: 0.8
""".lstrip(),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["source-pack-lint", str(path), "--strict"])

    assert result.exit_code == 1
    assert "missing_tags" in result.output


def test_source_pack_lint_invalid_config_exits_nonzero_without_traceback(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        """
version: 1
sources:
  - name: Broken Feed
    type: rss
""".lstrip(),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["source-pack-lint", str(path)])

    assert result.exit_code == 1
    assert "invalid_config" in result.output
    assert "requires url" in result.output
    assert "Traceback" not in result.output


def test_source_pack_lint_does_not_create_default_or_explicit_config_data_report_dirs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        """
version: 1
sources:
  - name: GDELT Local
    type: gdelt
    query: fashion
    weight: 0.8
    tags: [gdelt]
""".lstrip(),
        encoding="utf-8",
    )
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    explicit_config = tmp_path / "explicit-config"
    explicit_data = tmp_path / "explicit-data"
    explicit_reports = tmp_path / "explicit-reports"
    monkeypatch.chdir(workdir)

    result = CliRunner().invoke(
        app,
        ["source-pack-lint", str(path)],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(explicit_config),
            "FASHION_RADAR_DATA_DIR": str(explicit_data),
            "FASHION_RADAR_REPORTS_DIR": str(explicit_reports),
        },
    )

    assert result.exit_code == 0
    assert not (workdir / "config").exists()
    assert not (workdir / "data").exists()
    assert not (workdir / "reports").exists()
    assert not explicit_config.exists()
    assert not explicit_data.exists()
    assert not explicit_reports.exists()


def test_source_pack_lint_does_not_create_sqlite_or_workflow_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        """
version: 1
sources:
  - name: GDELT Local
    type: gdelt
    query: fashion
    weight: 0.8
    tags: [gdelt]
""".lstrip(),
        encoding="utf-8",
    )
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    monkeypatch.chdir(workdir)

    result = CliRunner().invoke(app, ["source-pack-lint", str(path)])

    assert result.exit_code == 0
    artifact_names = {artifact.name for artifact in workdir.rglob("*")}
    assert "fashion-radar.sqlite" not in artifact_names
    assert not any(artifact.match("*.sqlite*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("collector-*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("collector_runs*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("fashion-radar-*.md") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("fashion-radar-*.json") for artifact in workdir.rglob("*"))
    assert not (workdir / "latest.md").exists()
    assert not (workdir / "latest.json").exists()
    assert not (workdir / "report-index.json").exists()


def test_entity_pack_lint_help_lists_format_and_strict() -> None:
    result = CliRunner().invoke(app, ["entity-pack-lint", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--strict" in result.output
    assert "without matching, scoring, or collecting sources" in result.output


def test_entity_pack_lint_prints_table_for_public_pack() -> None:
    result = CliRunner().invoke(
        app,
        ["entity-pack-lint", "configs/entity-packs/fashion-watchlist.example.yaml"],
    )

    assert result.exit_code == 0
    assert "Entity pack: configs/entity-packs/fashion-watchlist.example.yaml" in result.output
    assert "Entities:" in result.output
    assert "Aliases:" in result.output
    assert "Findings:" in result.output


def test_entity_pack_lint_prints_json_for_public_pack() -> None:
    result = CliRunner().invoke(
        app,
        [
            "entity-pack-lint",
            "configs/entity-packs/fashion-watchlist.example.yaml",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["path"] == "configs/entity-packs/fashion-watchlist.example.yaml"
    assert payload["entity_count"] >= 24
    assert payload["alias_count"] >= payload["entity_count"]
    assert "findings" in payload


def test_entity_pack_lint_strict_exits_nonzero_on_warnings(tmp_path: Path) -> None:
    path = tmp_path / "entities.yaml"
    path.write_text(
        """
version: 1
entities:
  - name: Untagged Trend
    type: trend
    aliases:
      - value: quiet trend
    initial_weight: 1.0
    match_confidence: 1.0
""".lstrip(),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["entity-pack-lint", str(path), "--strict"])

    assert result.exit_code == 1
    assert "missing_tags" in result.output


def test_entity_pack_lint_invalid_config_exits_nonzero_without_traceback(
    tmp_path: Path,
) -> None:
    path = tmp_path / "entities.yaml"
    path.write_text(
        """
version: 1
entities:
  - name: Broken
    type: brand
""".lstrip(),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["entity-pack-lint", str(path)])

    assert result.exit_code == 1
    assert "invalid_config" in result.output
    assert "Invalid entity config" in result.output
    assert "Traceback" not in result.output


def test_entity_pack_lint_does_not_create_default_or_explicit_config_data_report_dirs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "entities.yaml"
    path.write_text(
        """
version: 1
entities:
  - name: Local Brand
    type: brand
    aliases:
      - value: Local Brand
    tags: [brand]
    initial_weight: 1.0
    match_confidence: 1.0
""".lstrip(),
        encoding="utf-8",
    )
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    explicit_config = tmp_path / "explicit-config"
    explicit_data = tmp_path / "explicit-data"
    explicit_reports = tmp_path / "explicit-reports"
    monkeypatch.chdir(workdir)

    result = CliRunner().invoke(
        app,
        ["entity-pack-lint", str(path)],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(explicit_config),
            "FASHION_RADAR_DATA_DIR": str(explicit_data),
            "FASHION_RADAR_REPORTS_DIR": str(explicit_reports),
        },
    )

    assert result.exit_code == 0
    assert not (workdir / "config").exists()
    assert not (workdir / "data").exists()
    assert not (workdir / "reports").exists()
    assert not explicit_config.exists()
    assert not explicit_data.exists()
    assert not explicit_reports.exists()


def test_entity_pack_lint_does_not_create_sqlite_or_workflow_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "entities.yaml"
    path.write_text(
        """
version: 1
entities:
  - name: Local Brand
    type: brand
    aliases:
      - value: Local Brand
    tags: [brand]
    initial_weight: 1.0
    match_confidence: 1.0
""".lstrip(),
        encoding="utf-8",
    )
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    monkeypatch.chdir(workdir)

    result = CliRunner().invoke(app, ["entity-pack-lint", str(path)])

    assert result.exit_code == 0
    artifact_names = {artifact.name for artifact in workdir.rglob("*")}
    assert "fashion-radar.sqlite" not in artifact_names
    assert not any(artifact.match("*.sqlite*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("collector-*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("collector_runs*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("fashion-radar-*.md") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("fashion-radar-*.json") for artifact in workdir.rglob("*"))
    assert not (workdir / "latest.md").exists()
    assert not (workdir / "latest.json").exists()
    assert not (workdir / "report-index.json").exists()
    assert not any(artifact.match("*.eml") for artifact in workdir.rglob("*"))


def test_candidates_command_does_not_create_missing_data_directory(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "missing-data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == []
    assert not data_dir.exists()


def test_candidates_command_rejects_incompatible_database_without_schema_mutation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    db_path = data_dir / "fashion-radar.sqlite"
    db_path.touch()

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    assert "schema" in result.output.lower()
    assert "fashion-radar migrate-db --data-dir" in result.output
    with sqlite3.connect(db_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert table_names == set()


def test_candidates_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-01-15T00:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_match_command_stores_entity_matches(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "entities.yaml").write_text(
        """
version: 1
entities:
  - name: The Row
    type: brand
    aliases: [The Row]
    context_terms: [handbag]
""".lstrip(),
        encoding="utf-8",
    )
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    item_id = ItemRepository(engine).upsert_item(
        CollectedItem(
            source_name="Vogue Business",
            source_type=SourceType.RSS,
            url="https://example.com/the-row",
            title="The Row Margaux handbag gains momentum",
            published_at="2026-06-11T10:00:00Z",
            summary="The Row handbag coverage.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
    )

    result = CliRunner().invoke(
        app,
        [
            "match",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Stored 1 matches" in result.output
    assert ItemRepository(engine).list_item_matches(item_id)[0]["entity_name"] == "The Row"


def test_clean_old_data_command_prunes_old_items(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    repository.upsert_item(
        CollectedItem(
            source_name="Old Source",
            source_type=SourceType.RSS,
            url="https://example.com/old",
            title="Old signal",
            published_at="2026-05-01T10:00:00Z",
            summary="old",
        ),
        collected_at=datetime(2026, 5, 1, tzinfo=UTC),
    )

    result = CliRunner().invoke(
        app,
        [
            "clean-old-data",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T00:00:00Z",
            "--retention-days",
            "14",
        ],
    )

    assert result.exit_code == 0
    assert "Pruned 1 items" in result.output
    assert repository.count_items() == 0


def test_collect_command_uses_workflow(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "sources.yaml").write_text(
        """
version: 1
sources:
  - name: Fixture Feed
    type: rss
    url: https://example.com/feed.xml
""".lstrip(),
        encoding="utf-8",
    )

    def fake_collect_configured_sources(**kwargs):
        calls.append(kwargs)
        return []

    monkeypatch.setattr(
        cli_module,
        "collect_configured_sources",
        fake_collect_configured_sources,
    )

    result = CliRunner().invoke(
        app,
        [
            "collect",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--now",
            "2026-06-11T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Collection finished" in result.output
    assert len(calls[0]["sources"]) == 1


def test_run_command_executes_collect_match_and_report(monkeypatch, tmp_path: Path) -> None:
    calls: list[str] = []
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    (config_dir / "sources.yaml").write_text("version: 1\nsources: []\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    monkeypatch.setattr(
        cli_module,
        "collect_configured_sources",
        lambda **_kwargs: calls.append("collect") or [],
    )
    monkeypatch.setattr(
        cli_module,
        "match_stored_items",
        lambda **_kwargs: (
            calls.append("match") or cli_module.MatchSummary(items_processed=0, matches_stored=0)
        ),
    )
    monkeypatch.setattr(
        cli_module,
        "write_daily_report_files",
        lambda **_kwargs: (
            calls.append("report") or (reports_dir / "report.md", reports_dir / "report.json")
        ),
    )

    result = CliRunner().invoke(
        app,
        [
            "run",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert calls == ["collect", "match", "report"]


def test_run_command_packages_digest_after_report(monkeypatch, tmp_path: Path) -> None:
    calls: list[str] = []
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    (config_dir / "sources.yaml").write_text("version: 1\nsources: []\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    monkeypatch.setattr(
        cli_module,
        "collect_configured_sources",
        lambda **_kwargs: calls.append("collect") or [],
    )
    monkeypatch.setattr(
        cli_module,
        "match_stored_items",
        lambda **_kwargs: (
            calls.append("match") or cli_module.MatchSummary(items_processed=0, matches_stored=0)
        ),
    )
    monkeypatch.setattr(
        cli_module,
        "write_daily_report_files",
        lambda **kwargs: (
            calls.append("report") or _write_daily_report_pair(kwargs["reports_dir"], "2026-06-11")
        ),
    )

    def fake_package_daily_digest(
        *,
        markdown_path: Path,
        json_path: Path,
        reports_dir: Path,
        options: DigestOptions,
    ) -> DigestResult:
        calls.append("digest")
        assert markdown_path == reports_dir / "fashion-radar-2026-06-11.md"
        assert json_path == reports_dir / "fashion-radar-2026-06-11.json"
        assert options.write_index is True
        assert options.print_summary is True
        return DigestResult(
            index_path=reports_dir / "report-index.json",
            summary_text="Local observed fashion report is ready for review.",
        )

    monkeypatch.setattr(
        cli_module,
        "package_daily_digest",
        fake_package_daily_digest,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "run",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--digest-index",
            "--digest-summary",
        ],
    )

    assert result.exit_code == 0
    assert calls == ["collect", "match", "report", "digest"]
    assert "Wrote report index: " in result.output
    assert "Local observed fashion report is ready for review." in result.output


def test_run_command_default_output_creates_no_digest_artifacts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls: list[str] = []
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    (config_dir / "sources.yaml").write_text("version: 1\nsources: []\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    markdown_path = reports_dir / "fashion-radar-2026-06-11.md"
    json_path = reports_dir / "fashion-radar-2026-06-11.json"

    monkeypatch.setattr(
        cli_module,
        "collect_configured_sources",
        lambda **_kwargs: calls.append("collect") or [],
    )
    monkeypatch.setattr(
        cli_module,
        "match_stored_items",
        lambda **_kwargs: (
            calls.append("match") or cli_module.MatchSummary(items_processed=0, matches_stored=0)
        ),
    )
    monkeypatch.setattr(
        cli_module,
        "write_daily_report_files",
        lambda **kwargs: (
            calls.append("report") or _write_daily_report_pair(kwargs["reports_dir"], "2026-06-11")
        ),
    )

    result = CliRunner().invoke(
        app,
        [
            "run",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert result.output == (
        "Stored 0 matches\n"
        f"Wrote Markdown report: {markdown_path}\n"
        f"Wrote JSON report: {json_path}\n"
    )
    assert calls == ["collect", "match", "report"]
    assert not (reports_dir / "latest.md").exists()
    assert not (reports_dir / "latest.json").exists()
    assert not (reports_dir / "report-index.json").exists()
    assert not (reports_dir / "fashion-radar-2026-06-11.eml").exists()


def test_run_command_writes_candidate_report_filtered_by_loaded_entities(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    data_dir.mkdir()
    reports_dir.mkdir()
    (config_dir / "sources.yaml").write_text("version: 1\nsources: []\n", encoding="utf-8")
    (config_dir / "scoring.yaml").write_text(
        """
version: 1
scoring: {}
candidate_discovery:
  min_current_mentions: 1
  review_min_current_mentions: 1
""".lstrip(),
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text(
        """
version: 1
entities:
  - name: The Row
    type: brand
    aliases: [The Row]
    context_terms: [bag]
  - name: Margaux
    type: product
    aliases: [Margaux]
    context_terms: [bag]
""".lstrip(),
        encoding="utf-8",
    )
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/the-row-margaux",
            title="The Row Margaux bag gains attention",
            published_at="2026-06-11T10:00:00Z",
            summary="The Row Margaux bag appears in coverage.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="WWD",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel",
            title="Le Teckel bag gains attention",
            published_at="2026-06-11T10:30:00Z",
            summary="Le Teckel bag appears in coverage.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 30, tzinfo=UTC),
    )

    monkeypatch.setattr(cli_module, "collect_configured_sources", lambda **_kwargs: [])
    monkeypatch.setattr(
        cli_module,
        "match_stored_items",
        lambda **_kwargs: cli_module.MatchSummary(items_processed=1, matches_stored=0),
    )

    result = CliRunner().invoke(
        app,
        [
            "run",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(
        (reports_dir / "fashion-radar-2026-06-11.json").read_text(encoding="utf-8")
    )
    candidate_keys = {candidate["phrase"].lower() for candidate in payload["candidates"]}
    serialized_candidates = json.dumps(payload["candidates"]).lower()
    assert "le teckel bag" in candidate_keys
    assert "margaux" not in serialized_candidates
    assert "the row" not in serialized_candidates


def _prepare_community_candidates_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
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
    data_dir = tmp_path / "data"
    path = tmp_path / "private-community.csv"
    path.write_text(
        "url,title,published_at,summary,source_name,collected_at\n"
        "https://private.example.com/a,Le Teckel bag mention,"
        "2026-06-13T09:00:00Z,private summary,Community,2026-06-13T10:00:00Z\n",
        encoding="utf-8",
    )
    return config_dir, data_dir, path


def test_community_candidates_help_lists_command() -> None:
    result = CliRunner().invoke(app, ["community-candidates", "--help"])

    assert result.exit_code == 0
    assert "--as-of" in result.output
    assert "--input-format" in result.output
    assert "--format" in result.output


def test_community_candidates_command_prints_json_without_paths_or_raw_values(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--input-format",
            "csv",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "input_format",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_name",
        "row_count",
        "candidate_count",
        "limit",
        "candidates",
    ]
    assert payload["row_count"] == 1
    assert payload["candidate_count"] >= 1
    assert any(candidate["phrase"] == "Le Teckel bag" for candidate in payload["candidates"])
    serialized = json.dumps(payload, sort_keys=True)
    forbidden_fragments = {
        str(path),
        path.name,
        "https://private.example.com/a",
        "Le Teckel bag mention",
        "private summary",
        "normalized_key",
        "normalized_phrase",
        "contexts",
        "representative_items",
        "source_file",
        "source_path",
        "import_path",
        "account_id",
    }
    for fragment in forbidden_fragments:
        assert fragment not in serialized
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_community_candidates_command_prints_table_without_path(tmp_path: Path) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Community candidate preview from one local handoff file." in result.output
    assert "Le Teckel bag" in result.output
    assert str(path) not in result.output
    assert path.name not in result.output


def test_community_candidates_invalid_as_of_does_not_load_config_or_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    def fail_load_config(*args, **kwargs):
        raise AssertionError("config should not be loaded")

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr(cli_module, "load_scoring_config", fail_load_config)
    monkeypatch.setattr(cli_module, "preview_community_candidates", fail_preview, raising=False)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "invalid --as-of" in result.output


def test_community_candidates_invalid_input_format_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr(cli_module, "preview_community_candidates", fail_preview, raising=False)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--input-format",
            "xml",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_community_candidates_invalid_output_format_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr(cli_module, "preview_community_candidates", fail_preview, raising=False)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_community_candidates_negative_limit_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr(cli_module, "preview_community_candidates", fail_preview, raising=False)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_community_candidates_invalid_config_does_not_read_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: bad\n", encoding="utf-8")

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr(cli_module, "preview_community_candidates", fail_preview, raising=False)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid community candidate config" in result.output


def test_community_candidates_invalid_file_has_clean_error_without_path_echo(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)
    missing = path.parent / "missing-private-file.csv"

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(missing),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not preview community candidates" in result.output
    assert "Traceback" not in result.output
    assert str(missing) not in result.output
    assert missing.name not in result.output


def test_community_candidates_validation_error_has_clean_error_without_row_values(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)
    private_row = ",".join(
        [
            "https://private.example/secret",
            "Private Runway Note",
            "not-a-date",
            "Private summary text",
            "private-weight",
        ]
    )
    path.write_text(
        "\n".join(
            [
                "url,title,published_at,summary,source_weight",
                private_row,
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not preview community candidates" in result.output
    assert "input file could not be read or validated" in result.output
    assert "Traceback" not in result.output
    assert str(path) not in result.output
    assert path.name not in result.output
    assert "https://private.example/secret" not in result.output
    assert "Private Runway Note" not in result.output
    assert "Private summary text" not in result.output
    assert "not-a-date" not in result.output
    assert "private-weight" not in result.output


def test_community_candidates_unexpected_error_has_clean_error_without_raw_message(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    def fail_preview(*args, **kwargs):
        raise RuntimeError(
            f"private failure in {path} with https://private.example/raw and Private Runway Note"
        )

    monkeypatch.setattr(cli_module, "preview_community_candidates", fail_preview)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not preview community candidates" in result.output
    assert "input file could not be read or validated" in result.output
    assert "Traceback" not in result.output
    assert str(path) not in result.output
    assert path.name not in result.output
    assert "https://private.example/raw" not in result.output
    assert "Private Runway Note" not in result.output


def test_community_candidates_command_does_not_create_artifacts(tmp_path: Path) -> None:
    config_dir, data_dir, path = _prepare_community_candidates_fixture(tmp_path)
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not (tmp_path / "dashboard").exists()


def _write_community_candidate_dir_csv(path: Path, rows: list[dict[str, str]]) -> None:
    headers = [
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "collected_at",
        "source_weight",
    ]
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(json.dumps(row.get(header, ""))[1:-1] for header in headers))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _prepare_community_candidates_dir_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
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
    directory = tmp_path / "private-community-dir"
    directory.mkdir()
    nested = directory / "nested-private"
    nested.mkdir()
    _write_community_candidate_dir_csv(
        directory / "first.csv",
        [
            {
                "url": "https://example.com/private-current",
                "title": "Le Teckel bag mention PRIVATE_ROW_TITLE",
                "published_at": "2026-06-13T09:00:00Z",
                "summary": "Private raw summary",
                "source_name": "Community A",
                "collected_at": "2026-06-13T10:00:00Z",
            },
            {
                "url": "https://example.com/private-baseline",
                "title": "Le Teckel bag baseline PRIVATE_BASELINE_TITLE",
                "published_at": "2026-06-01T09:00:00Z",
                "summary": "Private baseline summary",
                "source_name": "Community A",
                "collected_at": "2026-06-01T10:00:00Z",
            },
        ],
    )
    _write_community_candidate_dir_csv(
        directory / "second.csv",
        [
            {
                "url": "https://example.com/private-second",
                "title": "Le Teckel bag second PRIVATE_SECOND_TITLE",
                "published_at": "2026-06-12T09:00:00Z",
                "summary": "Private second summary",
                "source_name": "Community B",
                "collected_at": "2026-06-12T10:00:00Z",
            }
        ],
    )
    _write_community_candidate_dir_csv(
        nested / "nested.csv",
        [
            {
                "url": "https://example.com/private-nested",
                "title": "Nested private title",
                "published_at": "2026-06-13T09:00:00Z",
                "summary": "Nested private summary",
                "source_name": "Nested Source",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )
    return config_dir, data_dir, directory


def _community_candidates_dir_forbidden_fragments(directory: Path) -> set[str]:
    return {
        str(directory),
        directory.name,
        "first.csv",
        "second.csv",
        "nested.csv",
        "https://example.com/private-current",
        "https://example.com/private-baseline",
        "https://example.com/private-second",
        "https://example.com/private-nested",
        "PRIVATE_ROW_TITLE",
        "PRIVATE_BASELINE_TITLE",
        "PRIVATE_SECOND_TITLE",
        "Nested private title",
        "Private raw summary",
        "Private baseline summary",
        "Private second summary",
        "Nested private summary",
        "le teckel bag",
        "normalized_key",
        "normalized_phrase",
        "contexts",
        "candidate_contexts",
        "representative_items",
        "source_file",
        "source_path",
        "import_path",
        "account_id",
        "findings",
    }


def test_community_candidates_dir_help_lists_command() -> None:
    result = CliRunner().invoke(app, ["community-candidates-dir", "--help"])

    assert result.exit_code == 0
    assert "--as-of" in result.output
    assert "--input-format" in result.output
    assert "--pattern" in result.output
    assert "--format" in result.output


def test_community_candidates_dir_command_prints_json_without_paths_or_raw_values(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "input_format",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_name",
        "file_count",
        "row_count",
        "candidate_count",
        "limit",
        "candidates",
    ]
    assert payload["file_count"] == 2
    assert payload["row_count"] == 3
    assert payload["candidate_count"] >= 1
    assert "directory" not in payload
    assert "files" not in payload
    assert "pattern" not in payload
    assert any(candidate["phrase"] == "Le Teckel bag" for candidate in payload["candidates"])
    assert list(payload["candidates"][0]) == [
        "phrase",
        "candidate_type",
        "label",
        "score",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "growth_ratio",
        "first_seen_at",
    ]
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for fragment in _community_candidates_dir_forbidden_fragments(directory):
        assert fragment not in serialized
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_community_candidates_dir_command_prints_table_without_paths_or_raw_values(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Community candidate preview from local handoff files." in result.output
    assert "Files: 2" in result.output
    assert "Rows: 3" in result.output
    assert "Phrase | Type | Label | Score | Current Mentions" in result.output
    assert "Le Teckel bag" in result.output
    for fragment in _community_candidates_dir_forbidden_fragments(directory):
        assert fragment not in result.output


def test_community_candidates_dir_invalid_as_of_does_not_load_config_or_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    def fail_load_config(*args, **kwargs):
        raise AssertionError("config should not be loaded")

    def fail_preview(*args, **kwargs):
        raise AssertionError("directory should not be loaded")

    monkeypatch.setattr(cli_module, "load_scoring_config", fail_load_config)
    monkeypatch.setattr(cli_module, "load_entity_config", fail_load_config)
    monkeypatch.setattr(
        cli_module,
        "preview_community_candidate_directory",
        fail_preview,
        raising=False,
    )
    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "invalid --as-of" in result.output


def test_community_candidates_dir_invalid_input_format_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    def fail_load_config(*args, **kwargs):
        raise AssertionError("config should not be loaded")

    def fail_preview(*args, **kwargs):
        raise AssertionError("directory should not be loaded")

    monkeypatch.setattr(cli_module, "load_scoring_config", fail_load_config)
    monkeypatch.setattr(cli_module, "load_entity_config", fail_load_config)
    monkeypatch.setattr(
        cli_module,
        "preview_community_candidate_directory",
        fail_preview,
        raising=False,
    )
    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--input-format",
            "xml",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_community_candidates_dir_invalid_output_format_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    def fail_load_config(*args, **kwargs):
        raise AssertionError("config should not be loaded")

    def fail_preview(*args, **kwargs):
        raise AssertionError("directory should not be loaded")

    monkeypatch.setattr(cli_module, "load_scoring_config", fail_load_config)
    monkeypatch.setattr(cli_module, "load_entity_config", fail_load_config)
    monkeypatch.setattr(
        cli_module,
        "preview_community_candidate_directory",
        fail_preview,
        raising=False,
    )
    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_community_candidates_dir_negative_limit_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    def fail_load_config(*args, **kwargs):
        raise AssertionError("config should not be loaded")

    def fail_preview(*args, **kwargs):
        raise AssertionError("directory should not be loaded")

    monkeypatch.setattr(cli_module, "load_scoring_config", fail_load_config)
    monkeypatch.setattr(cli_module, "load_entity_config", fail_load_config)
    monkeypatch.setattr(
        cli_module,
        "preview_community_candidate_directory",
        fail_preview,
        raising=False,
    )
    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_community_candidates_dir_invalid_config_does_not_read_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: bad\n", encoding="utf-8")

    def fail_preview(*args, **kwargs):
        raise AssertionError("directory should not be loaded")

    monkeypatch.setattr(
        cli_module,
        "preview_community_candidate_directory",
        fail_preview,
        raising=False,
    )
    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid community candidate directory config" in result.output


def test_community_candidates_dir_invalid_directory_has_clean_error_without_path_echo(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)
    missing = directory.parent / "missing-private-directory"

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(missing),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not preview community candidates directory" in result.output
    assert "input directory could not be read or validated" in result.output
    assert "Traceback" not in result.output
    assert str(missing) not in result.output
    assert missing.name not in result.output


def test_community_candidates_dir_no_matching_files_has_clean_error_without_path_echo(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--pattern",
            "*.missing.csv",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not preview community candidates directory" in result.output
    assert "input directory could not be read or validated" in result.output
    assert "No regular files matched" not in result.output
    assert str(directory) not in result.output
    assert directory.name not in result.output
    assert "first.csv" not in result.output
    assert "second.csv" not in result.output


def test_community_candidates_dir_validation_error_has_clean_error_without_row_values(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)
    for child in directory.iterdir():
        if child.is_file():
            child.unlink()
    _write_community_candidate_dir_csv(
        directory / "secret.csv",
        [
            {
                "url": "https://private.example/secret",
                "title": "Private Runway Note",
                "published_at": "bad-date",
                "summary": "Private summary text",
                "source_weight": "not-a-number",
            }
        ],
    )

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not preview community candidates directory" in result.output
    assert "input directory could not be read or validated" in result.output
    assert "Traceback" not in result.output
    assert str(directory) not in result.output
    assert directory.name not in result.output
    assert "secret.csv" not in result.output
    assert "https://private.example/secret" not in result.output
    assert "Private Runway Note" not in result.output
    assert "Private summary text" not in result.output
    assert "bad-date" not in result.output
    assert "not-a-number" not in result.output


def test_community_candidates_dir_unexpected_error_has_clean_error_without_raw_message(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    def fail_preview(*args, **kwargs):
        raise RuntimeError(
            f"private failure in {directory / 'secret.csv'} with https://private.example/raw"
        )

    monkeypatch.setattr(cli_module, "preview_community_candidate_directory", fail_preview)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not preview community candidates directory" in result.output
    assert "input directory could not be read or validated" in result.output
    assert "Traceback" not in result.output
    assert str(directory) not in result.output
    assert directory.name not in result.output
    assert "secret.csv" not in result.output
    assert "https://private.example/raw" not in result.output


def test_community_candidates_dir_command_does_not_create_artifacts(tmp_path: Path) -> None:
    config_dir, data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not (tmp_path / "dashboard").exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite-*")) == []
    assert list(tmp_path.rglob("*.sqlite3")) == []
    assert list(tmp_path.rglob("*.db")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("*.eml")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []
