# Stage 329 ROW ONE Local Ops Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only `row-one ops-check` command that reports local ROW ONE website freshness, server/port readiness, access URLs, and user systemd unit-file presence.

**Architecture:** Create a small pure diagnostic module, `row_one/ops_check.py`, that reads local site files, parses runtime timestamps with the existing UTC date utility, performs injectable stdlib HTTP/bind probes, inspects unit-file existence, and returns a stable payload. Wire that module into the Typer `row-one` CLI with JSON and compact human output; keep existing `status`, `local-ops`, `install-local`, `serve`, app/runtime/manifest schemas, and generated site files unchanged.

**Tech Stack:** Python dataclasses, pathlib, json, datetime, existing `parse_datetime_utc`, urllib/socket stdlib probes, existing Typer CLI, pytest, Ruff, `UV_NO_CONFIG=1 uv --no-config run --frozen`, Claude Code/opencode review gates.

---

## Files

- Create: `src/fashion_radar/row_one/ops_check.py`
  - Own pure diagnostic dataclasses/functions.
  - No Typer imports.
  - No writes.
  - Inject probe functions for deterministic tests.
- Modify: `src/fashion_radar/cli.py`
  - Import `build_row_one_ops_check_payload()`.
  - Add `row-one ops-check`.
  - Print JSON or compact human output.
- Create: `tests/test_row_one_ops_check.py`
  - Unit tests for pure diagnostics.
- Modify: `tests/test_row_one_cli.py`
  - CLI tests for JSON/human output and non-mutating behavior.
- Modify: `tests/test_row_one_docs.py`
  - Docs command listing and boundary tests.
- Modify: `tests/test_workflows.py`
  - Workflow sentinel that `ops-check` does not add app/runtime/manifest fields
    or generated artifacts.
- Modify: `README.md`, `docs/row-one.md`, `docs/cli-reference.md`
  - Document the read-only command.
- Create review artifacts:
  - `docs/reviews/claude-code-stage-329-plan-review-prompt.md`
  - `docs/reviews/claude-code-stage-329-plan-review.md`
  - `docs/reviews/opencode-stage-329-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-329-plan-review.md` when used
  - `docs/reviews/claude-code-stage-329-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-329-code-review.md`
  - opencode fallback/rereview artifacts if needed

## Task 1: Pure Ops Check Payload

**Files:**
- Create: `tests/test_row_one_ops_check.py`
- Create: `src/fashion_radar/row_one/ops_check.py`

- [ ] **Step 1: Write failing pure diagnostics tests**

Create `tests/test_row_one_ops_check.py` with helpers:

```python
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.row_one.ops_check import (
    ROW_ONE_SYSTEMD_UNITS,
    RowOneServerProbeResult,
    build_row_one_ops_check_payload,
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
    (site_dir / "data" / "runtime.json").write_text(json.dumps(runtime), encoding="utf-8")
    (site_dir / "data" / "edition.json").write_text("{}", encoding="utf-8")
    (site_dir / "data" / "manifest.json").write_text("{}", encoding="utf-8")


def _probe(status: str) -> RowOneServerProbeResult:
    return RowOneServerProbeResult(
        status=status,
        probe_url="http://127.0.0.1:8787",
        detail="test probe",
    )
```

Add:

```python
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
    assert probe_calls == [("0.0.0.0", 8787, 1.0)]
```

Add:

```python
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
```

Add:

```python
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
    assert not site_dir.exists()
    assert not unit_dir.exists()
```

- [ ] **Step 2: Run pure tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py -q
```

Expected: fail because `fashion_radar.row_one.ops_check` does not exist.

- [ ] **Step 3: Implement `ops_check.py` minimally**

Create `src/fashion_radar/row_one/ops_check.py`:

```python
from __future__ import annotations

import json
import socket
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fashion_radar.row_one.server import format_row_one_site_access_message, format_row_one_site_url
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
```

Implement:

```python
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
    probe = (server_probe or probe_row_one_server)(host, port, ROW_ONE_SERVER_TIMEOUT_SECONDS)
    systemd = _systemd_payload(unit_dir)
    access = _access_payload(host, port)
    actions = _actions(site, freshness, probe, systemd, site_dir)
    status = _overall_status(site, freshness, probe, systemd)
    return {
        "ok": True,
        "status": status,
        "site_dir": str(site_dir),
        "as_of": reference.isoformat().replace("+00:00", "Z"),
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
        "actions": actions,
    }
```

Add helpers:

```python
def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _load_runtime(site_dir: Path) -> dict[str, object] | None:
    try:
        payload = json.loads((site_dir / "data" / "runtime.json").read_text(encoding="utf-8"))
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
    return {"status": "present" if all(files.values()) else "missing", "files": files}
```

Implement timestamp and probe helpers. Reuse the project UTC date utility so
runtime and CLI parsing normalize timestamps the same way:

```python
def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str | datetime):
        return None
    try:
        return parse_datetime_utc(value)
    except (TypeError, ValueError):
        return None


def _freshness_payload(runtime: dict[str, object] | None, as_of: datetime) -> dict[str, object]:
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
    return value.isoformat().replace("+00:00", "Z") if value is not None else None
```

```python
def probe_row_one_server(host: str, port: int, timeout: float) -> RowOneServerProbeResult:
    probe_url = format_row_one_site_url(host, port)
    try:
        with urlopen(probe_url, timeout=timeout) as response:
            body = response.read(64_000).decode("utf-8", errors="replace")
            if "ROW ONE" in body:
                return RowOneServerProbeResult("serving_row_one", probe_url, "root contains ROW ONE")
            return RowOneServerProbeResult("serving_other", probe_url, f"HTTP {response.status}")
    except HTTPError as exc:
        return RowOneServerProbeResult("serving_other", probe_url, f"HTTP {exc.code}")
    except (OSError, URLError) as exc:
        if _can_bind(host, port):
            return RowOneServerProbeResult("not_running", probe_url, str(exc))
        return RowOneServerProbeResult("port_in_use", probe_url, str(exc))


def _can_bind(host: str, port: int) -> bool:
    try:
        family = socket.AF_INET6 if ":" in host else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
    except Exception:
        return False
    return True
```

```python
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
    local_url = format_row_one_site_url(host, port)
    return {
        "message": format_row_one_site_access_message(host, port),
        "local_url": local_url,
        "lan_url_hint": f"http://<LAN-IP>:{port}",
    }
```

```python
def _actions(
    site: dict[str, object],
    freshness: dict[str, object],
    server: RowOneServerProbeResult,
    systemd: dict[str, object],
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
            f"`fashion-radar row-one refresh --output-dir {site_dir}`."
        )
    if server.status == "not_running":
        actions.append("Run `fashion-radar row-one serve` or enable `row-one-serve.service`.")
    if server.status == "port_in_use":
        actions.append("Stop or move the process occupying the ROW ONE port before serving.")
    if server.status == "serving_other":
        actions.append("Stop or move the non-ROW ONE process before serving on this port.")
    if systemd.get("status") != "present":
        actions.append("Run `fashion-radar row-one install-local --dry-run` to inspect user systemd units.")
    return actions


def _overall_status(
    site: dict[str, object],
    freshness: dict[str, object],
    server: RowOneServerProbeResult,
    systemd: dict[str, object],
) -> str:
    if site.get("status") != "present" or freshness.get("status") == "unknown":
        return "unknown"
    if (
        freshness.get("status") == "fresh"
        and server.status == "serving_row_one"
        and systemd.get("status") == "present"
    ):
        return "ready"
    return "attention"
```

- [ ] **Step 4: Run pure tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py -q
```

Expected: all pure ops-check tests pass.

## Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add tests near existing ROW ONE CLI status/local-ops tests:

```python
def test_row_one_ops_check_json_reports_stale_site_port_and_units(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_minimal_row_one_site(site_dir, generated_at="2026-07-06T04:00:00Z")

    result = runner.invoke(
        app,
        [
            "row-one",
            "ops-check",
            "--site-dir",
            str(site_dir),
            "--unit-dir",
            str(unit_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
            "--as-of",
            "2026-07-07T08:00:00Z",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] in {"attention", "unknown"}
    assert payload["freshness"]["status"] == "stale"
    assert payload["systemd"]["status"] == "missing"
    assert payload["access"]["local_url"] == "http://127.0.0.1:8787"
```

Add:

```python
def test_row_one_ops_check_human_output_is_read_only(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    _write_minimal_row_one_site(site_dir, generated_at="2026-07-07T04:00:00Z")
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    result = runner.invoke(
        app,
        [
            "row-one",
            "ops-check",
            "--site-dir",
            str(site_dir),
            "--unit-dir",
            str(unit_dir),
            "--as-of",
            "2026-07-07T08:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "ROW ONE ops check" in result.stdout
    assert "Status:" in result.stdout
    assert "Freshness:" in result.stdout
    assert "Server:" in result.stdout
    assert "Systemd units:" in result.stdout
    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert after == before
```

If existing helper `_write_minimal_row_one_site` does not exist, create a local
test helper with the minimum files needed by `ops-check`; do not reuse builders
that write unrelated reports.

Add malformed input coverage:

```python
def test_row_one_ops_check_rejects_malformed_as_of(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "row-one",
            "ops-check",
            "--site-dir",
            str(tmp_path / "site"),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code != 0
    assert "must be an ISO datetime" in result.output
```

- [ ] **Step 2: Run CLI tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "ops_check"
```

Expected: fail because `row-one ops-check` does not exist.

- [ ] **Step 3: Wire CLI**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.row_one.ops_check import build_row_one_ops_check_payload
from fashion_radar.utils.dates import parse_datetime_utc
```

Add a helper that delegates to the existing UTC date parser:

```python
def _parse_row_one_ops_check_as_of(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = parse_datetime_utc(value)
    except (TypeError, ValueError) as exc:
        raise typer.BadParameter("must be an ISO datetime") from exc
    return parsed
```

Add command:

```python
@row_one_app.command(name="ops-check")
def row_one_ops_check(
    site_dir: Path = ROW_ONE_SITE_DIR_OPTION,
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
    unit_dir: Path = ROW_ONE_UNIT_DIR_OPTION,
    as_of: str | None = typer.Option(None, help="Reference ISO datetime for freshness checks."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    """Read-only local ROW ONE operations readiness check."""
    try:
        payload = build_row_one_ops_check_payload(
            site_dir=site_dir,
            host=host,
            port=port,
            unit_dir=unit_dir,
            as_of=_parse_row_one_ops_check_as_of(as_of),
        )
    except Exception as exc:
        typer.echo(f"ROW ONE ops check failed: {exc}", err=True)
        raise typer.Exit(1) from exc
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(_render_row_one_ops_check_text(payload))
```

Add:

```python
def _render_row_one_ops_check_text(payload: dict[str, object]) -> str:
    freshness = payload.get("freshness") if isinstance(payload.get("freshness"), dict) else {}
    server = payload.get("server") if isinstance(payload.get("server"), dict) else {}
    systemd = payload.get("systemd") if isinstance(payload.get("systemd"), dict) else {}
    access = payload.get("access") if isinstance(payload.get("access"), dict) else {}
    actions = payload.get("actions") if isinstance(payload.get("actions"), list) else []
    lines = [
        "ROW ONE ops check",
        f"Status: {payload.get('status', 'unknown')}",
        f"Freshness: {freshness.get('status', 'unknown')}",
        f"Server: {server.get('status', 'unknown')}",
        f"Systemd units: {systemd.get('status', 'unknown')}",
    ]
    message = access.get("message")
    if isinstance(message, str) and message:
        lines.extend(["Access:", message])
    if actions:
        lines.append("Actions:")
        lines.extend(f"- {action}" for action in actions if isinstance(action, str))
    return "\n".join(lines)
```

- [ ] **Step 4: Run CLI tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "ops_check"
```

Expected: CLI ops-check tests pass.

## Task 3: Docs And Workflow Sentinels

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Write failing docs/workflow tests**

Extend `test_row_one_cli_docs_list_build_preview_serve_and_schedule_commands()`:

```python
"`row-one ops-check`",
```

Add docs boundary test:

```python
def test_row_one_docs_describe_ops_check_boundary() -> None:
    expected = _normalized(
        "Stage 329 adds `row-one ops-check` as a read-only local ROW ONE ops "
        "diagnostic for site freshness, server/port readiness, access URLs, "
        "and user systemd unit-file presence; it does not start servers, install "
        "or enable systemd units, kill processes, refresh or rebuild the site, "
        "write files, change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, "
        "fetching, extraction, scoring, ranking, LLM, connector, deployment "
        "automation, market grouping, domestic/international classification, "
        "or compliance-review behavior."
    )
    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage_329 = normalized[
            normalized.index("stage 329 adds `row-one ops-check`") :
            normalized.index("stage 328 adds generated-site only evidence excerpts")
        ]
        for phrase in (
            "starts servers",
            "installs systemd",
            "enables systemd",
            "kills processes",
            "refreshes the site",
            "rebuilds the site",
            "writes files",
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "adds deployment automation",
            "adds compliance review",
        ):
            assert phrase not in stage_329
```

Extend workflow generated-contract sentinel:

```python
assert '"ops_check"' not in generated_contract_payload
assert '"deploy_status"' not in generated_contract_payload
assert '"port_status"' not in generated_contract_payload
assert "ROW ONE ops check" not in generated_contract_payload
assert not (output_dir / "data" / "ops-check.json").exists()
assert not (output_dir / "ops-check.html").exists()
```

- [ ] **Step 2: Run docs/workflow tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: fail because docs and workflow sentinels have not been updated.

- [ ] **Step 3: Update docs**

Add this exact sentence before the Stage 328 note in `README.md` and
`docs/row-one.md`:

```markdown
Stage 329 adds `row-one ops-check` as a read-only local ROW ONE ops diagnostic for site freshness, server/port readiness, access URLs, and user systemd unit-file presence; it does not start servers, install or enable systemd units, kill processes, refresh or rebuild the site, write files, change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, extraction, scoring, ranking, LLM, connector, deployment automation, market grouping, domestic/international classification, or compliance-review behavior.
```

In `docs/cli-reference.md`, add `row-one ops-check` near the existing ROW ONE
ops commands:

```markdown
### `row-one ops-check`

Read-only local ROW ONE operations readiness check. It inspects the generated
site files, runtime freshness, local HTTP/port status, access URLs, and expected
user systemd unit files. It does not start servers, install units, refresh the
site, or write files.
```

- [ ] **Step 4: Run docs/workflow tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: docs/workflow tests pass.

## Task 4: Review, Verification, Commit, Push

**Files:**
- Create/modify Stage 329 review artifacts.
- Commit all Stage 329 changes.

- [ ] **Step 1: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_workflows.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/ops_check.py src/fashion_radar/cli.py tests/test_row_one_ops_check.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_workflows.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/ops_check.py src/fashion_radar/cli.py tests/test_row_one_ops_check.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_workflows.py
git diff --check
```

- [ ] **Step 2: Code review**

Create `docs/reviews/claude-code-stage-329-code-review-prompt.md` and request
Claude Code review. If Claude Code is unavailable or returns incomplete output,
use opencode GLM 5.2 max fallback. Fix all Critical/Important findings.

- [ ] **Step 3: Full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
if git grep -n -E 'ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' -- . ':!docs/reviews/*'; then exit 1; else exit 0; fi
```

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add README.md docs/row-one.md docs/cli-reference.md docs/superpowers/specs/2026-07-07-stage-329-row-one-local-ops-check-design.md docs/superpowers/plans/2026-07-07-stage-329-row-one-local-ops-check-plan.md docs/reviews src/fashion_radar/row_one/ops_check.py src/fashion_radar/cli.py tests/test_row_one_ops_check.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_workflows.py
git commit -m "Stage 329: add row one local ops check"
git push origin main
```
