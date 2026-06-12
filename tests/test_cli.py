import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from typer.testing import CliRunner

import fashion_radar.cli as cli_module
from fashion_radar.cli import app
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema, item_entities, items
from fashion_radar.digests import DigestOptions, DigestResult
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.models.trend import TrendComparison


def test_cli_help() -> None:
    result = CliRunner().invoke(app, ["--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "Fashion Radar" in result.output
    assert "trends" in result.output


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
    assert "platform" not in item
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
    with sqlite3.connect(db_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert table_names == set()


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
    with sqlite3.connect(db_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
    assert table_names == set()


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
