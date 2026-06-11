from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

import fashion_radar.cli as cli_module
from fashion_radar.cli import app
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType


def test_cli_help() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Fashion Radar" in result.output


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
        ],
    )

    assert result.exit_code == 0
    command = calls[0]
    assert command[:3] == [cli_module.sys.executable, "-m", "streamlit"]
    assert "--server.address" in command
    assert command[command.index("--server.address") + 1] == "127.0.0.1"
    assert "--server.port" in command
    assert command[command.index("--server.port") + 1] == "8501"


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
