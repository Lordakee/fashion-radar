from __future__ import annotations

import http.client
import json
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

import fashion_radar.cli as cli_module
from fashion_radar.cli import app
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.report import DailyReport, ReportMetadata, empty_daily_brief
from fashion_radar.models.source import SourceType
from fashion_radar.row_one.edition import build_row_one_edition
from fashion_radar.row_one.render import render_row_one_site
from fashion_radar.row_one.server import (
    create_row_one_http_server,
    format_row_one_site_access_message,
    format_row_one_site_url,
)
from fashion_radar.utils.dates import parse_datetime_utc
from fashion_radar.workflows import default_database_path

AS_OF = "2026-07-02T04:00:00Z"


def _write_minimal_config(config_dir: Path) -> None:
    config_dir.mkdir(parents=True)
    (config_dir / "sources.yaml").write_text("version: 1\nsources: []\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    (config_dir / "scoring.yaml").write_text(
        "version: 1\n"
        "scoring:\n"
        "  current_window_days: 7\n"
        "  baseline_window_days: 30\n"
        "candidate_discovery:\n"
        "  enabled: true\n"
        "  max_candidates: 20\n",
        encoding="utf-8",
    )


def _empty_report() -> DailyReport:
    return DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=1),
        brief=empty_daily_brief(),
        entities=[],
        candidates=[],
    )


def _seed_collected_item(data_dir: Path, *, title: str, url: str) -> None:
    engine = create_sqlite_engine(default_database_path(data_dir))
    try:
        initialize_schema(engine)
        ItemRepository(engine).upsert_item(
            CollectedItem(
                source_name="Local Desk",
                source_type=SourceType.RSS,
                url=url,
                title=title,
                published_at=AS_OF,
                summary="国内设计师品牌热度上升。",
            ),
            collected_at=parse_datetime_utc(AS_OF),
        )
    finally:
        engine.dispose()


def test_row_one_build_command_writes_empty_state_site(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "site"
    _write_minimal_config(config_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "build",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            AS_OF,
            "--output-dir",
            str(output_dir),
            "--latest-only",
        ],
    )

    assert result.exit_code == 0
    assert "Wrote ROW ONE site" in result.output
    assert "0 stories" in result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "data" / "edition.json").exists()
    assert "No ROW ONE stories" in (output_dir / "index.html").read_text(encoding="utf-8")


def test_row_one_preview_builds_site_and_prints_readiness(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "preview",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
            "--latest-only",
            "--dry-run-serve-url",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "data" / "edition.json").exists()
    assert "ROW ONE preview" in result.output
    assert f"Site: {output_dir / 'index.html'}" in result.output
    assert f"JSON: {output_dir / 'data' / 'edition.json'}" in result.output
    assert f"Manifest: {output_dir / 'data' / 'manifest.json'}" in result.output
    assert "Stories:" in result.output
    assert "Sections:" in result.output
    assert "Evidence links:" in result.output
    assert "Empty sections:" in result.output
    assert "Generated at:" in result.output
    assert "Readiness:" in result.output
    assert "Open:" in result.output


def test_row_one_preview_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "preview", "--help"])

    assert result.exit_code == 0
    assert "Build a ROW ONE preview" in result.output
    assert "dry-run" in result.output
    assert "Print the local" in result.output


def test_row_one_refresh_runs_pipeline_and_writes_site(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    calls: list[str] = []

    class StoredMatches:
        matches_stored = 4

    def collect_configured_sources(**kwargs: object) -> None:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["sources"] == []
        assert kwargs["now"] == AS_OF
        calls.append("collect_configured_sources")

    def match_stored_items(**kwargs: object) -> StoredMatches:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["entities"] == []
        calls.append("match_stored_items")
        return StoredMatches()

    def write_daily_report_files(**kwargs: object) -> tuple[Path, Path]:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["reports_dir"] == reports_dir
        assert kwargs["as_of"] == AS_OF
        assert kwargs["scoring"] is not None
        assert kwargs["candidate_discovery"] is not None
        assert kwargs["entity_config"] is not None
        calls.append("write_daily_report_files")
        return reports_dir / "daily.md", reports_dir / "daily.json"

    def prune_stale_daily_report_files(**kwargs: object) -> SimpleNamespace:
        assert kwargs["reports_dir"] == reports_dir
        assert kwargs["as_of"] == AS_OF
        calls.append("prune_stale_daily_report_files")
        return SimpleNamespace(
            current_date="2026-07-02",
            removed_count=3,
            kept_current_count=3,
        )

    def write_row_one_site_from_cli_options(**kwargs: object) -> SimpleNamespace:
        assert kwargs == {
            "config_dir": config_dir,
            "data_dir": data_dir,
            "reports_dir": reports_dir,
            "output_dir": output_dir,
            "as_of": AS_OF,
            "latest_only": True,
        }
        calls.append("_write_row_one_site_from_cli_options")
        return SimpleNamespace(
            index_path=output_dir / "index.html",
            output_dir=output_dir,
            story_count=0,
            edition=build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        )

    monkeypatch.setattr(cli_module, "collect_configured_sources", collect_configured_sources)
    monkeypatch.setattr(cli_module, "match_stored_items", match_stored_items)
    monkeypatch.setattr(cli_module, "write_daily_report_files", write_daily_report_files)
    monkeypatch.setattr(
        cli_module,
        "prune_stale_daily_report_files",
        prune_stale_daily_report_files,
    )
    monkeypatch.setattr(
        cli_module,
        "_write_row_one_site_from_cli_options",
        write_row_one_site_from_cli_options,
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "refresh",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls == [
        "collect_configured_sources",
        "match_stored_items",
        "write_daily_report_files",
        "_write_row_one_site_from_cli_options",
        "prune_stale_daily_report_files",
    ]
    assert "ROW ONE refresh" in result.output
    assert "Stored matches: 4" in result.output
    assert f"Markdown report: {reports_dir / 'daily.md'}" in result.output
    assert f"JSON report: {reports_dir / 'daily.json'}" in result.output
    assert f"HTML report: {reports_dir / 'daily.html'}" in result.output
    assert "Latest-only reports: removed 3 stale files for 2026-07-02; kept 3 current files" in (
        result.output
    )
    assert f"Site: {output_dir / 'index.html'}" in result.output
    assert f"JSON: {output_dir / 'data' / 'edition.json'}" in result.output
    assert f"Manifest: {output_dir / 'data' / 'manifest.json'}" in result.output
    assert "Stories:" in result.output
    assert "Evidence links:" in result.output
    assert "Readiness:" in result.output
    assert "Open: http://127.0.0.1:8787" in result.output


def test_row_one_refresh_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "refresh", "--help"])

    assert result.exit_code == 0
    assert "Refresh ROW ONE" in result.output
    assert "--output-dir" in result.output
    assert "--host" in result.output
    assert "--port" in result.output


def test_row_one_local_ops_command_prints_runbook(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "reports" / "row-one" / "site"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "local-ops",
            "--project-dir",
            str(tmp_path),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--time",
            "04:00",
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE local daily ops" in result.output
    assert "fashion-radar row-one refresh" in result.output
    assert "Source checkout commands:" in result.output
    assert f"cd {tmp_path}" in result.output
    assert "uv run fashion-radar row-one refresh" in result.output
    assert "uv run fashion-radar row-one preview" in result.output
    assert "uv run fashion-radar row-one status" in result.output
    assert "uv run fashion-radar row-one serve" in result.output
    assert "fashion-radar row-one preview" in result.output
    assert "fashion-radar row-one status" in result.output
    assert "fashion-radar row-one serve" in result.output
    assert "fashion-radar run" not in result.output
    assert "fashion-radar row-one build" not in result.output
    assert not re.search(r"fashion-radar row-one refresh\b[^\n]*--latest-only", result.output)
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
    assert "0 4 * * *" in result.output
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not output_dir.exists()


def test_row_one_local_ops_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "local-ops", "--help"])

    assert result.exit_code == 0
    assert "Print ROW ONE local daily ops runbook" in result.output
    assert "--time" in result.output
    assert "--host" in result.output
    assert "--port" in result.output


def test_row_one_install_local_dry_run_prints_systemd_files(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "reports" / "row-one" / "site"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "install-local",
            "--dry-run",
            "--project-dir",
            str(tmp_path),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--time",
            "04:00",
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE local install dry run" in result.output
    assert f"Target unit directory: {Path.home() / '.config' / 'systemd' / 'user'}" in result.output
    assert "# ~/.config/systemd/user/row-one-refresh.service" in result.output
    assert "# ~/.config/systemd/user/row-one-refresh.timer" in result.output
    assert "# ~/.config/systemd/user/row-one-serve.service" in result.output
    assert "Description=ROW ONE daily site refresh" in result.output
    assert "Description=ROW ONE fixed local web server" in result.output
    assert "OnCalendar=*-*-* 04:00:00" in result.output
    assert "uv run fashion-radar row-one refresh" in result.output
    assert "uv run fashion-radar row-one serve" in result.output
    assert '--host "$ROW_ONE_HOST"' in result.output
    assert "systemctl --user daemon-reload" in result.output
    assert "systemctl --user enable --now row-one-refresh.timer" in result.output
    assert "systemctl --user enable --now row-one-serve.service" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
    assert not (tmp_path / ".config" / "systemd" / "user").exists()


def test_row_one_install_local_dry_run_prints_custom_unit_dir(tmp_path: Path) -> None:
    unit_dir = tmp_path / "custom-systemd-user"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "install-local",
            "--dry-run",
            "--project-dir",
            str(tmp_path),
            "--unit-dir",
            str(unit_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert f"Target unit directory: {unit_dir}" in result.output
    assert f"# {unit_dir / 'row-one-refresh.service'}" in result.output
    assert f"# {unit_dir / 'row-one-refresh.timer'}" in result.output
    assert f"# {unit_dir / 'row-one-serve.service'}" in result.output
    assert not unit_dir.exists()


def test_row_one_install_local_writes_user_systemd_units(tmp_path: Path) -> None:
    unit_dir = tmp_path / "systemd-user"
    output_dir = tmp_path / "reports" / "row-one" / "site"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "install-local",
            "--project-dir",
            str(tmp_path),
            "--config-dir",
            str(tmp_path / "configs"),
            "--data-dir",
            str(tmp_path / "data"),
            "--reports-dir",
            str(tmp_path / "reports"),
            "--output-dir",
            str(output_dir),
            "--time",
            "04:00",
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
            "--unit-dir",
            str(unit_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE local install" in result.output
    assert f"Wrote units to: {unit_dir}" in result.output
    assert "Before enabling on a fresh install, generate the site once:" in result.output
    refresh_service = (unit_dir / "row-one-refresh.service").read_text(encoding="utf-8")
    refresh_timer = (unit_dir / "row-one-refresh.timer").read_text(encoding="utf-8")
    serve_service = (unit_dir / "row-one-serve.service").read_text(encoding="utf-8")
    assert "uv run fashion-radar row-one refresh" in refresh_service
    assert f'Environment="ROW_ONE_OUTPUT_DIR={output_dir}"' in refresh_service
    assert "OnCalendar=*-*-* 04:00:00" in refresh_timer
    assert "uv run fashion-radar row-one serve" in serve_service
    assert f'Environment="ROW_ONE_SITE_DIR={output_dir}"' in serve_service
    assert 'Environment="ROW_ONE_HOST=0.0.0.0"' in serve_service
    assert 'Environment="ROW_ONE_PORT=8787"' in serve_service
    assert (
        'Environment="PATH=%h/.local/bin:%h/.cargo/bin:/usr/local/bin:/usr/bin:/bin"'
        in serve_service
    )


def test_row_one_install_local_refuses_existing_unit_without_force(tmp_path: Path) -> None:
    unit_dir = tmp_path / "systemd-user"
    unit_dir.mkdir()
    (unit_dir / "row-one-serve.service").write_text("custom user service\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "install-local",
            "--project-dir",
            str(tmp_path),
            "--unit-dir",
            str(unit_dir),
        ],
    )

    assert result.exit_code == 1
    assert "already exists" in result.output
    assert "Use --force" in result.output
    assert (unit_dir / "row-one-serve.service").read_text(
        encoding="utf-8"
    ) == "custom user service\n"


def test_row_one_install_local_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "install-local", "--help"])

    assert result.exit_code == 0
    assert "Render or install ROW ONE user systemd units" in result.output
    assert "--dry-run" in result.output
    assert "--time" in result.output
    assert "--host" in result.output
    assert "--port" in result.output


def test_row_one_build_command_writes_non_ascii_story_detail_path(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "site"
    _write_minimal_config(config_dir)
    _seed_collected_item(
        data_dir,
        title="上海新锐设计师品牌升温",
        url="https://example.com/row-one-cli-cn",
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "build",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            AS_OF,
            "--output-dir",
            str(output_dir),
            "--latest-only",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads((output_dir / "data" / "edition.json").read_text(encoding="utf-8"))
    assert payload["contract_version"] == "row-one-app/v6"
    assert payload["signal_synthesis"]["boundaries"] == {
        "zh": "本地观察，需人工复核。",
        "en": "Local observed signals; review required.",
    }
    story = next(
        story for story in payload["stories"] if story["headline"] == "上海新锐设计师品牌升温"
    )
    detail_path = story["detail_path"]
    assert story["detail_href"] == detail_path
    assert story["href"] == detail_path
    assert detail_path.startswith("details/story-")
    assert detail_path.endswith(".html")
    assert detail_path.isascii()
    assert "%" not in detail_path
    assert payload["story_directory"]["story_count"] == payload["story_count"]
    assert story["id"] in payload["story_directory"]["story_ids"]
    route = next(
        route for route in payload["story_directory"]["routes"] if route["story_id"] == story["id"]
    )
    assert route == {
        "story_id": story["id"],
        "detail_href": detail_path,
        "section_key": story["section_key"],
        "section_href": story["section"]["href"],
        "published_date": story["published_date"],
    }
    assert (output_dir / detail_path).exists()
    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert 'class="edition-nav"' in index_html
    assert 'class="edition-rail"' in index_html
    assert 'class="edition-nav-item edition-rail-item"' in index_html
    assert 'href="#top_stories"' in index_html
    assert "上海新锐设计师品牌升温" in index_html


def test_row_one_serve_dry_run_prints_url(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html>ROW ONE</html>", encoding="utf-8")
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "http://127.0.0.1:8787" in result.output


def test_row_one_serve_dry_run_guides_wildcard_host(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html>ROW ONE</html>", encoding="utf-8")
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Open locally: http://127.0.0.1:8787" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
    assert "Bound to 0.0.0.0:8787" in result.output
    assert "no authentication" in result.output
    assert "http://0.0.0.0:8787" not in result.output


def test_row_one_serve_dry_run_rejects_unmarked_directory(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html>ROW ONE</html>", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "site marker" in result.output


def test_row_one_serve_dry_run_does_not_bind_requested_port(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html>ROW ONE</html>", encoding="utf-8")
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        occupied_port = int(listener.getsockname()[1])

        result = CliRunner().invoke(
            app,
            [
                "row-one",
                "serve",
                "--site-dir",
                str(site_dir),
                "--host",
                "127.0.0.1",
                "--port",
                str(occupied_port),
                "--dry-run",
            ],
        )

    assert result.exit_code == 0
    assert f"http://127.0.0.1:{occupied_port}" in result.output


def test_row_one_serve_dry_run_rejects_marked_directory_without_index(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "index.html" in result.output


def test_row_one_status_prints_generated_site_readiness(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "status",
            "--site-dir",
            str(tmp_path),
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE status" in result.output
    assert f"Site: {tmp_path}" in result.output
    assert f"Runtime: {tmp_path / 'data' / 'runtime.json'}" in result.output
    assert f"JSON: {tmp_path / 'data' / 'edition.json'}" in result.output
    assert f"Manifest: {tmp_path / 'data' / 'manifest.json'}" in result.output
    assert "Stories: 0" in result.output
    assert "Sections: 5" in result.output
    assert "Evidence links: 0" in result.output
    assert "Refresh time: 04:00" in result.output
    assert "Generated at: 2026-07-02T04:00:00Z" in result.output
    assert "Readiness: empty" in result.output
    assert "Open locally: http://127.0.0.1:8787" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output


def test_row_one_status_json_outputs_machine_readable_payload(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["site_dir"] == str(tmp_path)
    assert payload["paths"] == {
        "manifest": "data/manifest.json",
        "edition": "data/edition.json",
        "runtime": "data/runtime.json",
    }
    assert payload["runtime"]["contract_version"] == "row-one-runtime/v1"
    assert payload["manifest"]["contract_version"] == "row-one-manifest/v1"
    assert payload["contracts"] == {
        "app": "row-one-app/v6",
        "manifest": "row-one-manifest/v1",
        "runtime": "row-one-runtime/v1",
    }
    assert payload["story_count"] == 0
    assert payload["site"] == {
        "index_path": "index.html",
        "manifest_path": "data/manifest.json",
        "edition_path": "data/edition.json",
        "runtime_path": "data/runtime.json",
    }
    assert payload["serve"] == {
        "default_host": "127.0.0.1",
        "default_port": 8787,
        "local_url": "http://127.0.0.1:8787",
        "lan_url_hint": "http://<LAN-IP>:8787",
    }
    assert payload["refresh"]["recommended_time"] == "04:00"
    assert payload["refresh"]["latest_only_cleanup"] is True
    assert payload["counts"] == {
        "story_count": 0,
        "section_count": 5,
        "evidence_count": 0,
    }
    assert payload["readiness"] == {
        "status": "empty",
        "en": "empty",
        "zh": "暂无故事",
    }
    assert payload["refresh_time"] == "04:00"
    assert payload["local_url"] == "http://127.0.0.1:8787"
    assert payload["lan_url_hint"] == "http://<LAN-IP>:8787"
    assert payload["edition_path"] == "data/edition.json"
    assert payload["manifest_path"] == "data/manifest.json"
    assert payload["runtime_path"] == "data/runtime.json"
    assert payload["story_count"] == payload["runtime"]["counts"]["story_count"]
    assert payload["section_count"] == payload["runtime"]["counts"]["section_count"]
    assert payload["evidence_count"] == payload["runtime"]["counts"]["evidence_count"]
    assert payload["readiness_status"] == payload["runtime"]["readiness"]["status"]
    assert payload["generated_at"] == payload["runtime"]["generated_at"]
    assert payload["edition_date"] == payload["runtime"]["edition_date"]
    assert payload["site"] == payload["runtime"]["site"]
    assert payload["serve"] == payload["runtime"]["serve"]
    assert payload["refresh"] == payload["runtime"]["refresh"]


def test_row_one_status_json_keeps_fixed_runtime_urls_for_wildcard_host(
    tmp_path: Path,
) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "status",
            "--site-dir",
            str(tmp_path),
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "Open locally: http://127.0.0.1:8787" in payload["access"]
    assert "Open from LAN: http://<LAN-IP>:8787" in payload["access"]
    assert payload["local_url"] == "http://127.0.0.1:8787"
    assert payload["lan_url_hint"] == "http://<LAN-IP>:8787"
    assert "http://0.0.0.0:8787" not in json.dumps(payload)


def test_row_one_status_json_reports_ready_counts_for_populated_site(
    tmp_path: Path,
) -> None:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/status-ready",
                "title": "The Row showroom appointment demand rises",
                "summary": "Local desk notes rising interest in quiet luxury appointments.",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    render_row_one_site(edition, tmp_path)

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["story_count"] == 1
    assert payload["counts"]["story_count"] == 1
    assert payload["readiness_status"] == "ready"
    assert payload["readiness"]["status"] == "ready"
    assert payload["readiness"]["en"] == "ready"
    assert payload["counts"] == payload["runtime"]["counts"]
    assert payload["readiness"] == payload["runtime"]["readiness"]


def test_row_one_status_rejects_missing_runtime_payload(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )
    (tmp_path / "data" / "runtime.json").unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "data/runtime.json" in result.output


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (
            lambda runtime, _manifest, _edition: runtime.update(
                {"contract_version": "row-one-runtime/v2"}
            ),
            "runtime contract_version",
        ),
        (
            lambda _runtime, _manifest, edition: edition.update(
                {"contract_version": "row-one-app/v3"}
            ),
            "edition contract_version",
        ),
        (
            lambda _runtime, _manifest, edition: edition.pop("edition_brief"),
            "edition.edition_brief",
        ),
        (
            lambda _runtime, _manifest, edition: edition.pop("signal_synthesis"),
            "edition.signal_synthesis",
        ),
        (
            lambda _runtime, _manifest, edition: edition["signal_synthesis"]["boundaries"].update(
                {"en": "Verified platform heat."}
            ),
            "edition.signal_synthesis.boundaries.en",
        ),
        (
            lambda _runtime, _manifest, edition: edition["signal_synthesis"].update(
                {"signal_count": 99}
            ),
            "edition.signal_synthesis.signal_count",
        ),
        (
            lambda _runtime, _manifest, edition: edition["edition_brief"].update(
                {"story_directory_story_count": 99}
            ),
            "edition.edition_brief.story_directory_story_count",
        ),
        (
            lambda runtime, _manifest, _edition: runtime["site"].update(
                {"runtime_path": "runtime.json"}
            ),
            "runtime.site.runtime_path",
        ),
        (
            lambda runtime, _manifest, _edition: runtime["serve"].update({"default_port": 9999}),
            "runtime.serve.default_port",
        ),
        (
            lambda runtime, _manifest, _edition: runtime.update(
                {"generated_at": "2026-07-03T04:00:00Z"}
            ),
            "runtime generated_at",
        ),
        (
            lambda runtime, _manifest, _edition: runtime["counts"].update({"story_count": 7}),
            "runtime counts",
        ),
        (
            lambda runtime, _manifest, _edition: runtime["readiness"].update({"en": "ready"}),
            "runtime.readiness.en",
        ),
    ],
)
def test_row_one_status_rejects_runtime_contract_drift(
    tmp_path: Path,
    mutation: object,
    expected_error: str,
) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )
    manifest_path = tmp_path / "data" / "manifest.json"
    edition_path = tmp_path / "data" / "edition.json"
    runtime_path = tmp_path / "data" / "runtime.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    edition = json.loads(edition_path.read_text(encoding="utf-8"))
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    mutation(runtime, manifest, edition)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    edition_path.write_text(json.dumps(edition), encoding="utf-8")
    runtime_path.write_text(json.dumps(runtime), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert expected_error in result.output


def test_row_one_status_rejects_story_directory_route_drift(tmp_path: Path) -> None:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/story-directory",
                "title": "The Row route index demand rises",
                "summary": "Local desk notes route index drift should be rejected.",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    render_row_one_site(edition, tmp_path)
    edition_path = tmp_path / "data" / "edition.json"
    payload = json.loads(edition_path.read_text(encoding="utf-8"))
    payload["story_directory"]["routes"][0]["detail_href"] = "details/drifted-route.html"
    edition_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "edition.story_directory.routes[0].detail_href" in result.output


def test_row_one_schedule_prints_refresh_command() -> None:
    result = CliRunner().invoke(app, ["row-one", "schedule", "--time", "04:00"])

    assert result.exit_code == 0
    assert "04:00" in result.output
    assert "fashion-radar row-one refresh" in result.output
    assert "fashion-radar run" not in result.output
    assert "fashion-radar row-one build" not in result.output
    assert "--latest-only" not in result.output


def test_row_one_server_serves_index_on_ephemeral_port(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html><body>ROW ONE</body></html>", encoding="utf-8")
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    server = create_row_one_http_server(site_dir=site_dir, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)

    try:
        thread.start()
        port = int(server.server_address[1])
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        connection.request("GET", "/")
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 200
    assert "ROW ONE" in body


def test_row_one_server_rejects_unmarked_directory(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html><body>ROW ONE</body></html>", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="site marker"):
        create_row_one_http_server(site_dir=site_dir, host="127.0.0.1", port=0)


def test_row_one_server_serves_generated_chinese_detail_link(tmp_path: Path) -> None:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/cn",
                "title": "上海新锐设计师品牌升温",
                "summary": "国内设计师品牌热度上升。",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    render_row_one_site(edition, tmp_path)
    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_href_match = re.search(r'href="(?P<href>details/[^"]+\.html)"', index_html)
    assert detail_href_match is not None
    detail_href = detail_href_match.group("href")

    server = create_row_one_http_server(site_dir=tmp_path, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)

    try:
        thread.start()
        port = int(server.server_address[1])
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        connection.request("GET", f"/{detail_href}")
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 200
    assert "上海新锐设计师品牌升温" in body


def test_row_one_serve_cli_process_serves_generated_site(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = int(sock.getsockname()[1])

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "fashion_radar",
            "row-one",
            "serve",
            "--site-dir",
            str(tmp_path),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        fetched: dict[str, str] = {}
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and len(fetched) < 6:
            try:
                fetched = {
                    path: _fetch_row_one_cli_process_path(port, path)
                    for path in (
                        "/",
                        "/data/manifest.json",
                        "/data/edition.json",
                        "/data/runtime.json",
                        "/assets/row-one.css",
                        "/assets/row-one.js",
                    )
                }
            except OSError:
                time.sleep(0.1)

        assert len(fetched) == 6
        assert "ROW ONE" in fetched["/"]
        assert '"contract_version": "row-one-manifest/v1"' in fetched["/data/manifest.json"]
        assert '"contract_version": "row-one-app/v6"' in fetched["/data/edition.json"]
        assert '"contract_version": "row-one-runtime/v1"' in fetched["/data/runtime.json"]
        assert "RowOneSerif" in fetched["/assets/row-one.css"]
        assert "row-one:language" in fetched["/assets/row-one.js"]
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _fetch_row_one_cli_process_path(port: int, path: str) -> str:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.5)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        connection.close()
    if response.status != 200:
        raise OSError(f"{path} returned HTTP {response.status}")
    return body


def test_format_row_one_site_url() -> None:
    assert format_row_one_site_url("127.0.0.1", 8787) == "http://127.0.0.1:8787"
    assert format_row_one_site_url("localhost", 8787) == "http://localhost:8787"
    assert format_row_one_site_url("192.168.1.20", 8787) == "http://192.168.1.20:8787"
    assert format_row_one_site_url("0.0.0.0", 8787) == "http://127.0.0.1:8787"
    assert format_row_one_site_url("::1", 8787) == "http://[::1]:8787"
    assert format_row_one_site_url("::", 8787) == "http://[::1]:8787"
    assert format_row_one_site_url("2001:db8::1", 8787) == "http://[2001:db8::1]:8787"


def test_format_row_one_site_access_message_for_wildcard_host() -> None:
    message = format_row_one_site_access_message("0.0.0.0", 8787)

    assert "Open locally: http://127.0.0.1:8787" in message
    assert "Open from LAN: http://<LAN-IP>:8787" in message
    assert "Bound to 0.0.0.0:8787" in message
    assert "no authentication" in message
