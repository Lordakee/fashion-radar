# Stage 270 ROW ONE Runtime Readiness Design

## Objective

Make ROW ONE easier to run as a daily local website: one fixed IP:port serve
surface, one documented 04:00 refresh path, explicit runtime status metadata,
and stronger smoke coverage that proves the generated site can be served and
read by a browser or app client.

This stage builds on existing ROW ONE primitives instead of replacing them.
`row-one refresh`, `row-one schedule`, `row-one local-ops`, `row-one preview`,
and `row-one serve` already exist. Stage 270 should close the remaining runtime
readiness gaps around status visibility, local retention wording, and real
server smoke coverage.

## Current State

- `row-one refresh` collects configured sources, refreshes matches, writes the
  dated Markdown/JSON/HTML report, rebuilds the ROW ONE static site with
  `latest_only=True`, and prints the serve URL.
- `row-one schedule --time 04:00` prints cron/systemd snippets and does not
  install timers.
- `row-one local-ops --time 04:00 --host 0.0.0.0 --port 8787` prints a local
  operator runbook for manual refresh, preview, serve, and cron.
- `row-one serve` validates a generated site marker and serves static files
  through the Python standard library.
- `render_row_one_site(..., latest_only=True)` removes known generated site
  children only: `index.html`, `.row-one-site`, `details`, `assets`, and
  `data`. It preserves unrelated files and refuses to clean unmarked output
  directories with generated children.
- Existing tests cover CLI help, dry-run serve URLs, direct HTTP server
  creation, schema contracts, app payloads, docs, scheduling snippets, and
  first-run smoke.

## Product Reading

The user wants a local website named ROW ONE that can be accessed through a
stable `ip:port` URL, refreshed every day at 04:00, and kept lightweight during
testing. For this codebase, the safest implementation is still "print and serve
locally" rather than installing system services or adding a process supervisor.
The tool should give the operator exact commands and machine-readable runtime
status so another app or agent can verify the site is ready.

## Proposed Shape

Add a small runtime readiness layer without changing data acquisition:

- A generated `data/runtime.json` file in every ROW ONE site.
- A self-describing runtime contract at the fixed `data/runtime.json` path so
  app clients can discover the fixed access pattern and refresh posture without
  scraping CLI output.
- A focused `row-one status` command that validates an already generated site
  and prints machine-readable or text status.
- A real CLI serve smoke test that launches `fashion-radar row-one serve` on an
  ephemeral port and fetches core assets.
- Documentation that makes the local 04:00 workflow explicit and explains that
  `latest_only=True` keeps only the latest ROW ONE site children in the site
  directory while dated reports remain normal report artifacts.

## Runtime Contract

`data/runtime.json` should be generated next to `data/edition.json` and
`data/manifest.json`.

Recommended shape:

```json
{
  "contract_version": "row-one-runtime/v1",
  "brand": "ROW ONE",
  "generated_at": "2026-07-03T04:00:00Z",
  "edition_date": "2026-07-03T04:00:00Z",
  "site": {
    "index_path": "index.html",
    "manifest_path": "data/manifest.json",
    "edition_path": "data/edition.json",
    "runtime_path": "data/runtime.json"
  },
  "refresh": {
    "recommended_time": "04:00",
    "command": "fashion-radar row-one refresh --as-of \"$AS_OF\" --output-dir reports/row-one/site",
    "latest_only_cleanup": true
  },
  "serve": {
    "default_host": "127.0.0.1",
    "default_port": 8787,
    "local_url": "http://127.0.0.1:8787",
    "lan_url_hint": "http://<LAN-IP>:8787"
  },
  "counts": {
    "story_count": 0,
    "section_count": 5,
    "evidence_count": 0
  },
  "readiness": {
    "status": "empty",
    "zh": "暂无故事",
    "en": "empty"
  }
}
```

The `row-one-runtime/v1` contract is additive and self-discoverable at the
fixed `data/runtime.json` path. It does not change `row-one-app/v1` or
`row-one-manifest/v1`. It gives external clients and local operators a stable
place to check generated-at time, counts, readiness, and the recommended
serve/refresh posture without requiring a manifest contract change.

## CLI Behavior

Add `row-one status`:

- Inputs:
  - `--site-dir`, default `reports/row-one/site`
  - `--host`, default existing ROW ONE host option
  - `--port`, default existing ROW ONE port option
  - `--json`, optional machine-readable output
- Behavior:
  - validate `.row-one-site` and `index.html` using existing server validation;
  - require `data/manifest.json`, `data/edition.json`, and `data/runtime.json`;
  - print site path, local URL, story count, generated timestamp, readiness, and
    missing file details;
  - exit non-zero if the site is not generated or required JSON files are
    missing/invalid.

Do not add a scheduler installer, daemon manager, web framework, paid service,
or background worker. Existing `row-one schedule` remains print-only.

## Retention Boundary

The user asked that the test site not consume disk space and that yesterday's
records disappear after refresh. In the current product architecture, there are
two distinct retention surfaces:

- ROW ONE site output: `latest_only=True` removes the previous generated site
  children before writing the new site. This meets the local website retention
  requirement for `reports/row-one/site`.
- Dated reports: `fashion-radar-YYYY-MM-DD.md/json/html` are existing local
  report artifacts outside the site directory. Stage 270 should document this
  distinction and should not silently delete dated reports unless a later stage
  introduces an explicit report-retention command.

## Serve Smoke

Add a real server smoke path in tests:

- build a minimal ROW ONE site in a temp directory;
- launch the CLI command in a subprocess on `127.0.0.1` and an allocated free
  port;
- fetch `/`, `/data/manifest.json`, `/data/edition.json`, `/data/runtime.json`,
  `/assets/row-one.css`, and `/assets/row-one.js`;
- terminate the process cleanly.

This complements existing unit tests for `create_row_one_http_server` and
`serve --dry-run` without keeping a long-running server in normal CLI flows.

## Documentation

Update `docs/row-one.md`, `docs/cli-reference.md`, and `docs/first-run.md` to
make the local runtime path explicit:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar row-one refresh --as-of "$AS_OF" --output-dir reports/row-one/site
uv run fashion-radar row-one status --site-dir reports/row-one/site --host 0.0.0.0 --port 8787
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 0.0.0.0 --port 8787
uv run fashion-radar row-one schedule --time 04:00
```

Docs should say the stable remote-access form is `http://<LAN-IP>:8787` when
binding to `0.0.0.0`, and should keep the warning that the local server has no
authentication.

## Tests

Focused tests should cover:

- runtime payload generation and manifest linkage;
- schema validation for the runtime payload;
- `row-one status` success and missing-site failures;
- `row-one status --json` output;
- real CLI `row-one serve` smoke;
- scheduling/local-ops docs mention 04:00 and fixed IP:port access;
- package archive includes any new schema/module files.

## Non-Goals

- No OpenDesign image generation.
- No new collectors, social-platform automation, cookies, or scraping.
- No daemon/scheduler installation.
- No cloud deployment.
- No authentication layer.
- No compliance-review product features.
- No deletion of dated reports outside the ROW ONE site directory.
- No change to `row-one-app/v1`.

## Acceptance Evidence

- Focused ROW ONE tests pass.
- `row-one status` validates a generated temp site and rejects an incomplete
  site.
- A subprocess smoke proves `fashion-radar row-one serve` serves real generated
  static files.
- Docs describe fixed IP:port serve, 04:00 scheduling, and site-output
  retention accurately.
- Full release gate passes before commit/push.
