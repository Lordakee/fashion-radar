# Stage 329 ROW ONE Local Ops Check Design

## Goal

Add a read-only ROW ONE local ops diagnostic so a user can tell whether the
daily local website is fresh, reachable on the expected host/port, and prepared
for the existing user-level systemd refresh/serve units.

## Product Gap Closed

ROW ONE already has `row-one refresh`, `row-one serve`, `row-one schedule`,
`row-one local-ops`, `row-one install-local`, and `row-one status`. The missing
layer is a single machine-readable readiness view for local operations:

- Is the generated site present?
- Is the current site edition fresh for the expected date?
- Is the configured port available, unreachable, serving ROW ONE, or occupied
  by a non-ROW ONE service?
- Which local URL and LAN hint should be used?
- Are the expected user systemd unit files present?

This closes an ops/reporting gap toward the user's fixed local ROW ONE website
requirement without mutating the machine.

## Scope

- Add a read-only diagnostic module under `fashion_radar.row_one`.
- Add a `fashion-radar row-one ops-check` CLI command.
- Default paths and host/port should match existing ROW ONE CLI defaults.
- Support `--json` machine-readable output.
- Support `--as-of` for deterministic freshness checks in tests and scripts.
- Support `--unit-dir` to inspect a user-level systemd unit directory.
- Reuse existing URL formatting and site marker conventions.
- Add tests and documentation.

## Non-Goals

- Do not start the ROW ONE server.
- Do not install, enable, reload, start, stop, restart, or kill systemd units.
- Do not call `systemctl`.
- Do not kill or alter any process occupying a port.
- Do not rebuild or refresh the ROW ONE site.
- Do not write files, JSON artifacts, reports, generated pages, service files,
  unit files, caches, lockfiles, or SQLite data.
- Do not change `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`,
  schemas, generated site routes, source collection, fetching, extraction,
  scoring, ranking, LLM, connectors, deployment automation, market grouping,
  domestic/international classification, or compliance-review behavior.
- Do not add dependencies.

## Behavior

`row-one ops-check` should validate local readiness from observable local state.

Inputs:

- `--site-dir`, defaulting to the existing ROW ONE site directory option.
- `--host`, defaulting to the existing ROW ONE host option.
- `--port`, defaulting to the existing ROW ONE port option.
- `--unit-dir`, defaulting to the existing ROW ONE user systemd unit directory
  option.
- `--as-of`, optional ISO datetime. When omitted, use current UTC time.
- `--json`, optional JSON output.

Checks:

1. Site files:
   - `.row-one-site`
   - `index.html`
   - `data/runtime.json`
   - `data/edition.json`
   - `data/manifest.json`

2. Runtime freshness:
   - Parse `runtime.generated_at` and `runtime.edition_date` when possible.
   - Compare the `edition_date` date to the reference `--as-of` date in UTC.
   - Emit `fresh` or `stale`; emit `unknown` when runtime is missing or invalid.

3. HTTP/port readiness:
   - Probe `http://<browser-host>:<port>/` using stdlib only and a short timeout.
   - If root returns HTML containing `ROW ONE`, classify `server.status` as
     `serving_row_one`.
   - If the connection succeeds but content/status does not identify ROW ONE,
     classify as `serving_other`.
   - If the connection is refused or times out, probe bind availability:
     - bind available: `not_running`
     - bind unavailable: `port_in_use`
   - Never hold the port after probing.
   - Treat bind availability as a best-effort local heuristic, avoid
     `SO_REUSEADDR`, and catch socket errors so the diagnostic never crashes on
     probe-only failures.

4. Access links:
   - Include the same access message as `row-one serve`.
   - Include local URL and LAN URL hint.

5. Systemd unit files:
   - Inspect only file existence under `unit_dir`.
   - If `unit_dir` does not exist, treat all expected units as missing and
     include `unit_dir_exists: false`.
   - Required files:
     - `row-one-refresh.service`
     - `row-one-refresh.timer`
     - `row-one-serve.service`
   - Emit per-unit `present` booleans and a summary status `present` or
     `missing`.

Overall status:

- `ready`: site files are present, runtime is fresh, server is
  `serving_row_one`, and expected user systemd unit files are present.
- `attention`: any required check is missing, stale, not running, or occupied by
  another service.
- `unknown`: only when enough local state is missing to prevent a meaningful
  readiness judgment.

The command should exit `0` for diagnostic output even when the result is
`attention`. It should exit non-zero only for invalid input such as malformed
`--as-of`, malformed `--time` if added later, or an unexpected unhandled error.

## Output

JSON output should be a top-level object with stable keys:

```json
{
  "ok": true,
  "status": "attention",
  "site_dir": "reports/row-one/site",
  "as_of": "2026-07-07T04:00:00Z",
  "access": {
    "message": "Open locally: http://127.0.0.1:8787\nOpen from LAN: http://<LAN-IP>:8787\n...",
    "local_url": "http://127.0.0.1:8787",
    "lan_url_hint": "http://<LAN-IP>:8787"
  },
  "site": {
    "status": "present",
    "files": {
      "marker": true,
      "index": true,
      "runtime": true,
      "edition": true,
      "manifest": true
    }
  },
  "freshness": {
    "status": "stale",
    "generated_at": "2026-07-06T04:00:00Z",
    "edition_date": "2026-07-06T04:00:00Z",
    "expected_date": "2026-07-07"
  },
  "server": {
    "status": "serving_other",
    "host": "0.0.0.0",
    "probe_url": "http://127.0.0.1:8787",
    "port": 8787
  },
  "systemd": {
    "status": "missing",
    "unit_dir": "~/.config/systemd/user",
    "units": {
      "row-one-refresh.service": false,
      "row-one-refresh.timer": false,
      "row-one-serve.service": false
    }
  },
  "actions": [
    "Run `fashion-radar row-one refresh --output-dir reports/row-one/site`.",
    "Run `fashion-radar row-one install-local --dry-run` to inspect user systemd units.",
    "Stop or move the non-ROW ONE process before serving on this port."
  ]
}
```

Human output should be compact and script-safe:

- `ROW ONE ops check`
- `Status: ready|attention|unknown`
- `Freshness: fresh|stale|unknown`
- `Server: serving_row_one|serving_other|not_running|port_in_use`
- `Systemd units: present|missing`
- access message
- action lines when any check needs attention

## Testing

Use TDD:

- Unit-test pure payload construction with temporary site directories.
- Mock or inject server probe results so tests do not require real port
  conflicts.
- Assert injected probe functions receive the expected host, port, and timeout.
- Test stale and fresh runtime payloads.
- Test missing unit files and present unit files.
- Test missing unit directories are reported as missing without creating them.
- Test CLI JSON output and human output.
- Test malformed `--as-of` fails without running the diagnostic.
- Test that the command does not create files under the site, report, data, or
  unit directories.
- Test docs list the new command and preserve non-mutating boundaries.
