from __future__ import annotations

import http.client
import json
import re
import socket
import threading
from pathlib import Path

import pytest
from typer.testing import CliRunner

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
    assert "fashion-radar run" in result.output
    assert "fashion-radar row-one build" in result.output
    assert "fashion-radar row-one preview" in result.output
    assert "fashion-radar row-one serve" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
    assert "0 4 * * *" in result.output


def test_row_one_local_ops_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "local-ops", "--help"])

    assert result.exit_code == 0
    assert "Print ROW ONE local daily ops runbook" in result.output
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
    assert payload["contract_version"] == "row-one-app/v1"
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
    assert (output_dir / detail_path).exists()
    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert 'class="edition-nav"' in index_html
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


def test_row_one_schedule_prints_refresh_then_build() -> None:
    result = CliRunner().invoke(app, ["row-one", "schedule", "--time", "04:00"])

    assert result.exit_code == 0
    assert "04:00" in result.output
    assert "fashion-radar run" in result.output
    assert "fashion-radar row-one build" in result.output
    assert "--latest-only" in result.output
    assert result.output.index("fashion-radar run") < result.output.index(
        "fashion-radar row-one build"
    )


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
