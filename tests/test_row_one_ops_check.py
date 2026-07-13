from __future__ import annotations

import json
import socket
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError

import pytest

from fashion_radar.row_one.ops_check import (
    ROW_ONE_SERVER_TIMEOUT_SECONDS,
    ROW_ONE_SYSTEMD_UNITS,
    RowOneServerProbeResult,
    _systemd_payload,
    build_row_one_ops_check_payload,
    probe_row_one_server,
)


def _write_site(site_dir: Path, *, edition_date: str) -> None:
    (site_dir / "data").mkdir(parents=True)
    (site_dir / ".row-one-site").write_text("", encoding="utf-8")
    (site_dir / "index.html").write_text("<h1>ROW ONE</h1>", encoding="utf-8")
    runtime = {
        "contract_version": "row-one-runtime/v1",
        "generated_at": edition_date,
        "edition_date": edition_date,
        "refresh": {"recommended_time": "04:00"},
        "serve": {
            "default_host": "127.0.0.1",
            "default_port": 8787,
            "local_url": "http://127.0.0.1:8787",
            "lan_url_hint": "http://<LAN-IP>:8787",
        },
    }
    (site_dir / "data" / "runtime.json").write_text(
        json.dumps(runtime),
        encoding="utf-8",
    )
    (site_dir / "data" / "edition.json").write_text("{}", encoding="utf-8")
    (site_dir / "data" / "manifest.json").write_text("{}", encoding="utf-8")


def _write_saved_article_route_fixture(site_dir: Path, *, complete: bool = True) -> None:
    _write_site(site_dir, edition_date="2026-07-07T04:00:00Z")
    story_id = "the-row-route-1234567890"
    articles_data = site_dir / "data" / "articles"
    articles_data.mkdir(parents=True, exist_ok=True)
    (articles_data / f"{story_id}.json").write_text("{}", encoding="utf-8")
    if complete:
        (site_dir / "index.html").write_text(
            '<h1>ROW ONE</h1><a href="articles/index.html">Saved article library</a>',
            encoding="utf-8",
        )
        articles_dir = site_dir / "articles"
        articles_dir.mkdir(parents=True, exist_ok=True)
        (articles_dir / "index.html").write_text(
            f'<a href="{story_id}.html">Read local article</a>',
            encoding="utf-8",
        )
        (articles_dir / f"{story_id}.html").write_text(
            "<!doctype html><title>ROW ONE local article</title>",
            encoding="utf-8",
        )


def _write_saved_article_content_fixture(site_dir: Path, *, complete: bool = True) -> None:
    _write_site(site_dir, edition_date="2026-07-07T04:00:00Z")
    story_id = "the-row-content-1234567890"
    (site_dir / "index.html").write_text(
        '<h1>ROW ONE</h1><a href="articles/index.html">Saved article library</a>',
        encoding="utf-8",
    )
    articles_data = site_dir / "data" / "articles"
    articles_data.mkdir(parents=True, exist_ok=True)
    (articles_data / f"{story_id}.json").write_text(
        json.dumps(
            {
                "story_id": story_id,
                "url": "https://example.com/content",
                "title": "The Row content",
                "source_name": "Example",
                "extracted_at": "2026-07-07T04:00:00Z",
                "paragraphs": ["First paragraph.", "Second paragraph."],
                "paragraphs_zh": ["第一段。", "第二段。"],
                "brief_sections": [],
                "content_sections": [
                    {
                        "key": "brand_signals",
                        "title": {"en": "Brand Signals", "zh": "品牌信号"},
                        "items": [
                            {
                                "label": {"en": "The Row", "zh": "The Row"},
                                "paragraph_indices": [0],
                            }
                        ],
                    }
                ],
                "body_source": "extracted",
                "skipped": False,
            }
        ),
        encoding="utf-8",
    )
    articles_dir = site_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / "index.html").write_text(
        f'<a href="{story_id}.html">Read local article</a>',
        encoding="utf-8",
    )
    article_html = (
        '<section id="local-article">'
        '<div id="local-article-body">'
        '<p id="local-article-paragraph-1">First paragraph.</p>'
        '<p id="local-article-paragraph-2">Second paragraph.</p>'
        "</div>"
        '<article id="local-article-content-section-1">Brand Signals</article>'
        "</section>"
    )
    if not complete:
        article_html = article_html.replace(
            'id="local-article-paragraph-2"',
            'data-id="local-article-paragraph-2"',
        )
    (articles_dir / f"{story_id}.html").write_text(article_html, encoding="utf-8")


def _probe(status: str) -> RowOneServerProbeResult:
    return RowOneServerProbeResult(
        status=status,
        probe_url="http://127.0.0.1:8787",
        detail="test probe",
    )


def _unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_ops_check_reexports_canonical_systemd_unit_names() -> None:
    assert ROW_ONE_SYSTEMD_UNITS == (
        "row-one-refresh.service",
        "row-one-refresh.timer",
        "row-one-serve.service",
    )


def test_ops_check_reports_filename_evidence_when_site_and_local_articles_are_ready(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_content_fixture(site_dir, complete=True)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    probe_calls: list[tuple[str, int, float]] = []

    def probe(host: str, port: int, timeout: float) -> RowOneServerProbeResult:
        probe_calls.append((host, port, timeout))
        return _probe("serving_row_one")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="0.0.0.0",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=probe,
    )

    assert payload["ok"] is True
    assert payload["status"] == "site_ready_scheduler_unverified"
    assert payload["freshness"]["status"] == "fresh"
    assert payload["server"]["status"] == "serving_row_one"
    assert payload["systemd"]["status"] == "unit_files_present"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["systemd"]["units"] == {
        "row-one-refresh.service": True,
        "row-one-refresh.timer": True,
        "row-one-serve.service": True,
    }
    assert payload["local_article_routes"]["status"] == "ready"
    assert payload["local_article_content"]["status"] == "ready"
    assert payload["access"]["local_url"] == "http://127.0.0.1:8787"
    assert payload["access"]["lan_url_hint"] == "http://<LAN-IP>:8787"
    assert payload["actions"] == []
    assert probe_calls == [("0.0.0.0", 8787, ROW_ONE_SERVER_TIMEOUT_SECONDS)]


def test_ops_check_reports_filename_evidence_for_malformed_canonical_unit_files(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_content_fixture(site_dir, complete=True)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Malformed\nnot-systemd=true\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "site_ready_scheduler_unverified"
    assert payload["systemd"]["status"] == "unit_files_present"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["systemd"]["units"] == {
        "row-one-refresh.service": True,
        "row-one-refresh.timer": True,
        "row-one-serve.service": True,
    }
    assert payload["actions"] == []


def test_ops_check_reports_filename_evidence_for_empty_canonical_unit_files(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_content_fixture(site_dir, complete=True)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_bytes(b"")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "site_ready_scheduler_unverified"
    assert payload["systemd"]["status"] == "unit_files_present"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["systemd"]["units"] == {
        "row-one-refresh.service": True,
        "row-one-refresh.timer": True,
        "row-one-serve.service": True,
    }
    assert payload["actions"] == []


def test_systemd_payload_does_not_read_canonical_unit_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unit_dir = tmp_path / "units"
    unit_dir.mkdir()
    unit_paths = {unit_dir / unit for unit in ROW_ONE_SYSTEMD_UNITS}
    for unit_path in unit_paths:
        unit_path.write_text("[Unit]\n", encoding="utf-8")

    original_read_text = Path.read_text
    original_read_bytes = Path.read_bytes
    original_open = Path.open

    def forbid_unit_read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path in unit_paths:
            raise AssertionError(f"must not read unit file: {path}")
        return original_read_text(path, *args, **kwargs)

    def forbid_unit_read_bytes(path: Path, *args: object, **kwargs: object) -> bytes:
        if path in unit_paths:
            raise AssertionError(f"must not read unit file: {path}")
        return original_read_bytes(path, *args, **kwargs)

    def forbid_unit_open(path: Path, *args: object, **kwargs: object) -> object:
        if path in unit_paths:
            raise AssertionError(f"must not read unit file: {path}")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", forbid_unit_read_text)
    monkeypatch.setattr(Path, "read_bytes", forbid_unit_read_bytes)
    monkeypatch.setattr(Path, "open", forbid_unit_open)

    payload = _systemd_payload(unit_dir)

    assert payload["status"] == "unit_files_present"
    assert payload["verification"] == "filenames_only"
    assert payload["units"] == {
        "row-one-refresh.service": True,
        "row-one-refresh.timer": True,
        "row-one-serve.service": True,
    }


@pytest.mark.parametrize(
    ("missing_units", "expected_units"),
    [
        (
            ("row-one-refresh.service",),
            {
                "row-one-refresh.service": False,
                "row-one-refresh.timer": True,
                "row-one-serve.service": True,
            },
        ),
        (
            ("row-one-refresh.timer",),
            {
                "row-one-refresh.service": True,
                "row-one-refresh.timer": False,
                "row-one-serve.service": True,
            },
        ),
        (
            ("row-one-serve.service",),
            {
                "row-one-refresh.service": True,
                "row-one-refresh.timer": True,
                "row-one-serve.service": False,
            },
        ),
        (
            ROW_ONE_SYSTEMD_UNITS,
            {
                "row-one-refresh.service": False,
                "row-one-refresh.timer": False,
                "row-one-serve.service": False,
            },
        ),
    ],
    ids=("refresh-service", "refresh-timer", "serve-service", "all-units"),
)
def test_ops_check_reports_missing_filename_evidence_and_install_action(
    tmp_path: Path,
    missing_units: tuple[str, ...],
    expected_units: dict[str, bool],
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_content_fixture(site_dir, complete=True)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        if unit not in missing_units:
            (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "attention"
    assert payload["systemd"]["status"] == "missing"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["systemd"]["units"] == expected_units
    assert payload["actions"] == [
        "Run `fashion-radar row-one install-local --dry-run` to inspect user systemd units.",
    ]


def test_ops_check_reports_attention_for_stale_site_other_server_and_missing_units(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_site(site_dir, edition_date="2026-07-06T04:00:00Z")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="0.0.0.0",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_other"),
    )

    assert payload["status"] == "attention"
    assert payload["freshness"]["status"] == "stale"
    assert payload["freshness"]["expected_date"] == "2026-07-07"
    assert payload["server"]["status"] == "serving_other"
    assert payload["systemd"]["status"] == "missing"
    assert payload["systemd"]["unit_dir_exists"] is False
    assert payload["systemd"]["units"] == {
        "row-one-refresh.service": False,
        "row-one-refresh.timer": False,
        "row-one-serve.service": False,
    }
    assert any("refresh" in action for action in payload["actions"])
    assert any("non-ROW ONE" in action for action in payload["actions"])
    assert any("install-local --dry-run" in action for action in payload["actions"])


def test_ops_check_reports_attention_when_units_missing_but_site_and_server_ready(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_site(site_dir, edition_date="2026-07-07T04:00:00Z")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "attention"
    assert payload["freshness"]["status"] == "fresh"
    assert payload["server"]["status"] == "serving_row_one"
    assert payload["systemd"]["status"] == "missing"
    assert any("install-local --dry-run" in action for action in payload["actions"])


def test_ops_check_reports_attention_when_freshness_is_stale_only(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_site(site_dir, edition_date="2026-07-06T04:00:00Z")
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "attention"
    assert payload["freshness"]["status"] == "stale"
    assert payload["server"]["status"] == "serving_row_one"
    assert payload["systemd"]["status"] == "unit_files_present"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["actions"] == [f"Run `fashion-radar row-one refresh --output-dir {site_dir}`."]


def test_ops_check_reports_local_article_route_health_ready(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_route_fixture(site_dir, complete=True)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "site_ready_scheduler_unverified"
    assert payload["local_article_routes"]["status"] == "ready"
    assert payload["local_article_routes"]["article_count"] == 1
    assert payload["actions"] == []


def test_ops_check_reports_attention_for_missing_local_article_routes(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_route_fixture(site_dir, complete=False)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "attention"
    assert payload["systemd"]["status"] == "unit_files_present"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["local_article_routes"]["status"] == "missing"
    assert any("row-one refresh" in action for action in payload["actions"])


def test_ops_check_reports_local_article_content_health_ready(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_content_fixture(site_dir, complete=True)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "site_ready_scheduler_unverified"
    assert payload["local_article_content"]["status"] == "ready"
    assert payload["local_article_content"]["article_count"] == 1
    assert payload["local_article_content"]["paragraph_anchor_count"] == 2
    assert payload["local_article_content"]["content_section_anchor_count"] == 1
    assert payload["actions"] == []


def test_ops_check_reports_attention_for_missing_local_article_content(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_saved_article_content_fixture(site_dir, complete=False)
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "attention"
    assert payload["systemd"]["status"] == "unit_files_present"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["local_article_content"]["status"] == "missing"
    assert payload["local_article_content"]["missing_paragraph_anchors"] == [
        "articles/the-row-content-1234567890.html#local-article-paragraph-2"
    ]
    assert any("row-one refresh" in action for action in payload["actions"])


def test_ops_check_text_includes_local_article_content_health() -> None:
    from fashion_radar.cli import _render_row_one_ops_check_text

    text = _render_row_one_ops_check_text(
        {
            "status": "attention",
            "freshness": {"status": "fresh"},
            "server": {"status": "serving_row_one"},
            "systemd": {
                "status": "unit_files_present",
                "verification": "filenames_only",
            },
            "local_article_routes": {"status": "ready"},
            "local_article_content": {"status": "missing"},
            "access": {},
            "actions": [],
        }
    )

    assert "Local article content: missing" in text
    assert "Systemd verification: filenames_only" in text
    assert "scheduler state is not verified" in text


def test_ops_check_text_preserves_scheduler_disclaimer_for_missing_units() -> None:
    from fashion_radar.cli import _render_row_one_ops_check_text

    action = "Run `fashion-radar row-one install-local --dry-run` to inspect user systemd units."
    text = _render_row_one_ops_check_text(
        {
            "status": "attention",
            "freshness": {"status": "fresh"},
            "server": {"status": "serving_row_one"},
            "systemd": {
                "status": "missing",
                "verification": "filenames_only",
                "unit_dir_exists": True,
                "units": {
                    "row-one-refresh.service": False,
                    "row-one-refresh.timer": False,
                    "row-one-serve.service": False,
                },
            },
            "local_article_routes": {"status": "ready"},
            "local_article_content": {"status": "ready"},
            "access": {},
            "actions": [action],
        }
    )

    assert "Systemd units: missing" in text
    assert "Systemd verification: filenames_only" in text
    assert "Systemd scheduler state is not verified." in text
    assert action in text


def test_ops_check_reports_missing_site_without_writing_files(tmp_path: Path) -> None:
    site_dir = tmp_path / "missing-site"
    unit_dir = tmp_path / "units"

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("not_running"),
    )

    assert payload["status"] == "unknown"
    assert payload["site"]["status"] == "missing"
    assert payload["freshness"]["status"] == "unknown"
    assert payload["server"]["status"] == "not_running"
    assert f"Generate the ROW ONE site at {site_dir}." in payload["actions"]
    assert not any("runtime metadata" in action for action in payload["actions"])
    assert not site_dir.exists()
    assert not unit_dir.exists()


def test_ops_check_reports_unknown_for_invalid_runtime_timestamp_and_partial_units(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_site(site_dir, edition_date="not-a-date")
    unit_dir.mkdir()
    (unit_dir / "row-one-refresh.service").write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "unknown"
    assert payload["freshness"] == {
        "status": "unknown",
        "generated_at": None,
        "edition_date": None,
        "expected_date": "2026-07-07",
    }
    assert payload["systemd"]["status"] == "missing"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["systemd"]["unit_dir_exists"] is True
    assert payload["systemd"]["units"] == {
        "row-one-refresh.service": True,
        "row-one-refresh.timer": False,
        "row-one-serve.service": False,
    }
    assert any(
        f"row-one refresh --output-dir {site_dir}" in action for action in payload["actions"]
    )


def test_ops_check_reports_unknown_for_invalid_runtime_timestamp_and_all_unit_files(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_site(site_dir, edition_date="not-a-date")
    unit_dir.mkdir()
    for unit in ROW_ONE_SYSTEMD_UNITS:
        (unit_dir / unit).write_text("[Unit]\n", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["status"] == "unknown"
    assert payload["status"] != "site_ready_scheduler_unverified"
    assert payload["systemd"]["status"] == "unit_files_present"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["systemd"]["units"] == {
        "row-one-refresh.service": True,
        "row-one-refresh.timer": True,
        "row-one-serve.service": True,
    }


def test_ops_check_reports_unknown_for_unparseable_runtime_json(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    (site_dir / "data").mkdir(parents=True)
    (site_dir / ".row-one-site").write_text("", encoding="utf-8")
    (site_dir / "index.html").write_text("<h1>ROW ONE</h1>", encoding="utf-8")
    (site_dir / "data" / "runtime.json").write_text("{", encoding="utf-8")
    (site_dir / "data" / "edition.json").write_text("{}", encoding="utf-8")
    (site_dir / "data" / "manifest.json").write_text("{}", encoding="utf-8")

    payload = build_row_one_ops_check_payload(
        site_dir=site_dir,
        host="127.0.0.1",
        port=8787,
        unit_dir=unit_dir,
        as_of=datetime(2026, 7, 7, 8, 0, tzinfo=UTC),
        server_probe=lambda host, port, timeout: _probe("serving_row_one"),
    )

    assert payload["site"]["status"] == "present"
    assert payload["freshness"]["status"] == "unknown"
    assert payload["freshness"]["generated_at"] is None
    assert payload["freshness"]["edition_date"] is None
    assert payload["status"] == "unknown"
    assert any(
        f"row-one refresh --output-dir {site_dir}" in action for action in payload["actions"]
    )


def test_probe_row_one_server_classifies_row_one_content(monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        status = 200

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self, limit: int) -> bytes:
            assert limit == 64_000
            return b"<h1>ROW ONE</h1>"

    import fashion_radar.row_one.ops_check as ops_check

    monkeypatch.setattr(ops_check, "urlopen", lambda url, timeout: Response())

    result = probe_row_one_server("0.0.0.0", 8787, 0.25)

    assert result == RowOneServerProbeResult(
        status="serving_row_one",
        probe_url="http://127.0.0.1:8787",
        detail="root contains ROW ONE",
    )


def test_probe_row_one_server_bind_probe_does_not_hold_available_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import fashion_radar.row_one.ops_check as ops_check

    port = _unused_port()

    def raise_url_error(url: str, timeout: float) -> None:
        raise URLError("connection refused")

    monkeypatch.setattr(ops_check, "urlopen", raise_url_error)

    result = probe_row_one_server("127.0.0.1", port, 0.25)

    assert result.status == "not_running"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", port))


def test_probe_row_one_server_bind_probe_does_not_use_reuseaddr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import fashion_radar.row_one.ops_check as ops_check

    class FakeSocket:
        def __enter__(self) -> FakeSocket:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def bind(self, address: tuple[str, int]) -> None:
            assert address == ("127.0.0.1", 8787)

        def setsockopt(self, *args: object) -> None:
            raise AssertionError("bind probe must not set SO_REUSEADDR")

    monkeypatch.setattr(
        ops_check,
        "urlopen",
        lambda url, timeout: (_ for _ in ()).throw(URLError("connection refused")),
    )
    monkeypatch.setattr(ops_check.socket, "socket", lambda family, kind: FakeSocket())

    result = probe_row_one_server("127.0.0.1", 8787, 0.25)

    assert result.status == "not_running"


def test_probe_row_one_server_catches_bind_socket_exceptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import fashion_radar.row_one.ops_check as ops_check

    monkeypatch.setattr(
        ops_check,
        "urlopen",
        lambda url, timeout: (_ for _ in ()).throw(URLError("connection refused")),
    )
    monkeypatch.setattr(
        ops_check.socket,
        "socket",
        lambda family, kind: (_ for _ in ()).throw(OSError("bind probe failed")),
    )

    result = probe_row_one_server("127.0.0.1", 8787, 0.25)

    assert result.status == "port_in_use"
    assert result.probe_url == "http://127.0.0.1:8787"
