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


def test_ops_check_reports_ready_when_site_fresh_server_row_one_and_units_present(
    tmp_path: Path,
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_site(site_dir, edition_date="2026-07-07T04:00:00Z")
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
    assert payload["status"] == "ready"
    assert payload["freshness"]["status"] == "fresh"
    assert payload["server"]["status"] == "serving_row_one"
    assert payload["systemd"]["status"] == "present"
    assert payload["access"]["local_url"] == "http://127.0.0.1:8787"
    assert payload["access"]["lan_url_hint"] == "http://<LAN-IP>:8787"
    assert payload["actions"] == []
    assert probe_calls == [("0.0.0.0", 8787, ROW_ONE_SERVER_TIMEOUT_SECONDS)]


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
    assert payload["systemd"]["status"] == "present"
    assert payload["actions"] == [f"Run `fashion-radar row-one refresh --output-dir {site_dir}`."]


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
    assert payload["systemd"]["unit_dir_exists"] is True
    assert payload["systemd"]["units"] == {
        "row-one-refresh.service": True,
        "row-one-refresh.timer": False,
        "row-one-serve.service": False,
    }
    assert any(
        f"row-one refresh --output-dir {site_dir}" in action for action in payload["actions"]
    )


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
