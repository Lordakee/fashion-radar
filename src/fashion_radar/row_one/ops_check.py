from __future__ import annotations

import json
import socket
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fashion_radar.row_one.local_article_route_health import (
    build_row_one_local_article_route_health,
    row_one_local_article_route_health_payload,
)
from fashion_radar.row_one.server import (
    format_row_one_site_access_message,
    format_row_one_site_url,
)
from fashion_radar.utils.dates import parse_datetime_utc

ROW_ONE_SYSTEMD_UNITS = (
    "row-one-refresh.service",
    "row-one-refresh.timer",
    "row-one-serve.service",
)
ROW_ONE_SERVER_TIMEOUT_SECONDS = 1.0


@dataclass(frozen=True)
class RowOneServerProbeResult:
    status: str
    probe_url: str
    detail: str


ServerProbe = Callable[[str, int, float], RowOneServerProbeResult]


def build_row_one_ops_check_payload(
    *,
    site_dir: Path,
    host: str,
    port: int,
    unit_dir: Path,
    as_of: datetime | None = None,
    server_probe: ServerProbe | None = None,
) -> dict[str, object]:
    reference = _as_utc(as_of or datetime.now(UTC))
    runtime = _load_runtime(site_dir)
    site = _site_payload(site_dir)
    freshness = _freshness_payload(runtime, reference)
    probe = (server_probe or probe_row_one_server)(
        host,
        port,
        ROW_ONE_SERVER_TIMEOUT_SECONDS,
    )
    systemd = _systemd_payload(unit_dir)
    access = _access_payload(host, port)
    local_article_routes = row_one_local_article_route_health_payload(
        build_row_one_local_article_route_health(site_dir),
    )
    actions = _actions(site, freshness, probe, systemd, local_article_routes, site_dir)
    status = _overall_status(site, freshness, probe, systemd, local_article_routes)
    return {
        "ok": True,
        "status": status,
        "site_dir": str(site_dir),
        "as_of": _iso(reference),
        "access": access,
        "site": site,
        "freshness": freshness,
        "server": {
            "status": probe.status,
            "host": host,
            "port": port,
            "probe_url": probe.probe_url,
            "detail": probe.detail,
        },
        "systemd": systemd,
        "local_article_routes": local_article_routes,
        "actions": actions,
    }


def probe_row_one_server(host: str, port: int, timeout: float) -> RowOneServerProbeResult:
    probe_url = format_row_one_site_url(host, port)
    try:
        with urlopen(probe_url, timeout=timeout) as response:
            body = response.read(64_000).decode("utf-8", errors="replace")
            if "ROW ONE" in body:
                return RowOneServerProbeResult(
                    status="serving_row_one",
                    probe_url=probe_url,
                    detail="root contains ROW ONE",
                )
            return RowOneServerProbeResult(
                status="serving_other",
                probe_url=probe_url,
                detail=f"HTTP {response.status}",
            )
    except HTTPError as exc:
        return RowOneServerProbeResult(
            status="serving_other",
            probe_url=probe_url,
            detail=f"HTTP {exc.code}",
        )
    except (OSError, URLError) as exc:
        if _can_bind(host, port):
            return RowOneServerProbeResult(
                status="not_running",
                probe_url=probe_url,
                detail=str(exc),
            )
        return RowOneServerProbeResult(
            status="port_in_use",
            probe_url=probe_url,
            detail=str(exc),
        )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _load_runtime(site_dir: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(
            (site_dir / "data" / "runtime.json").read_text(encoding="utf-8"),
        )
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _site_payload(site_dir: Path) -> dict[str, object]:
    files = {
        "marker": (site_dir / ".row-one-site").is_file(),
        "index": (site_dir / "index.html").is_file(),
        "runtime": (site_dir / "data" / "runtime.json").is_file(),
        "edition": (site_dir / "data" / "edition.json").is_file(),
        "manifest": (site_dir / "data" / "manifest.json").is_file(),
    }
    return {
        "status": "present" if all(files.values()) else "missing",
        "files": files,
    }


def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str | datetime):
        return None
    try:
        return parse_datetime_utc(value)
    except (TypeError, ValueError):
        return None


def _freshness_payload(
    runtime: dict[str, object] | None,
    as_of: datetime,
) -> dict[str, object]:
    generated_at = _parse_datetime(runtime.get("generated_at")) if runtime else None
    edition_date = _parse_datetime(runtime.get("edition_date")) if runtime else None
    expected_date = as_of.date().isoformat()
    if edition_date is None:
        status = "unknown"
    elif edition_date.date().isoformat() == expected_date:
        status = "fresh"
    else:
        status = "stale"
    return {
        "status": status,
        "generated_at": _iso_or_none(generated_at),
        "edition_date": _iso_or_none(edition_date),
        "expected_date": expected_date,
    }


def _iso_or_none(value: datetime | None) -> str | None:
    return _iso(value) if value is not None else None


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _can_bind(host: str, port: int) -> bool:
    try:
        family = socket.AF_INET6 if ":" in host else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
    except Exception:
        return False
    return True


def _systemd_payload(unit_dir: Path) -> dict[str, object]:
    unit_dir_exists = unit_dir.is_dir()
    units = {unit: (unit_dir / unit).is_file() for unit in ROW_ONE_SYSTEMD_UNITS}
    return {
        "status": "present" if all(units.values()) else "missing",
        "unit_dir": str(unit_dir),
        "unit_dir_exists": unit_dir_exists,
        "units": units,
    }


def _access_payload(host: str, port: int) -> dict[str, str]:
    return {
        "message": format_row_one_site_access_message(host, port),
        "local_url": format_row_one_site_url(host, port),
        "lan_url_hint": f"http://<LAN-IP>:{port}",
    }


def _actions(
    site: dict[str, object],
    freshness: dict[str, object],
    server: RowOneServerProbeResult,
    systemd: dict[str, object],
    local_article_routes: dict[str, object],
    site_dir: Path,
) -> list[str]:
    actions: list[str] = []
    if site.get("status") != "present":
        actions.append(f"Generate the ROW ONE site at {site_dir}.")
    if freshness.get("status") == "stale":
        actions.append(f"Run `fashion-radar row-one refresh --output-dir {site_dir}`.")
    if site.get("status") == "present" and freshness.get("status") == "unknown":
        actions.append(
            "Regenerate ROW ONE runtime metadata with "
            f"`fashion-radar row-one refresh --output-dir {site_dir}`.",
        )
    if server.status == "not_running":
        actions.append("Run `fashion-radar row-one serve` or enable `row-one-serve.service`.")
    if server.status == "port_in_use":
        actions.append("Stop or move the process occupying the ROW ONE port before serving.")
    if server.status == "serving_other":
        actions.append("Stop or move the non-ROW ONE process before serving on this port.")
    if systemd.get("status") != "present":
        actions.append(
            "Run `fashion-radar row-one install-local --dry-run` to inspect user systemd units.",
        )
    if local_article_routes.get("status") == "missing":
        action = f"Run `fashion-radar row-one refresh --output-dir {site_dir}`."
        if action not in actions:
            actions.append(action)
    return actions


def _overall_status(
    site: dict[str, object],
    freshness: dict[str, object],
    server: RowOneServerProbeResult,
    systemd: dict[str, object],
    local_article_routes: dict[str, object],
) -> str:
    if site.get("status") != "present" or freshness.get("status") == "unknown":
        return "unknown"
    if (
        freshness.get("status") == "fresh"
        and server.status == "serving_row_one"
        and systemd.get("status") == "present"
        and local_article_routes.get("status") != "missing"
    ):
        return "ready"
    return "attention"
