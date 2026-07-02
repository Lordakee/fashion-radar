# Stage 265 ROW ONE Local Daily Ops Design

## Goal

Make the current ROW ONE local site easier to operate from this machine by adding a deterministic local daily-ops surface that prints exactly how to refresh the site at 04:00, serve it at a fixed IP:port, and keep only the latest generated ROW ONE site files.

## User Need

The user wants ROW ONE to behave like a daily local website:

- Refresh automatically every day at 04:00.
- Be reachable from a stable local-network URL such as `http://<LAN-IP>:8787`.
- Keep only the current generated ROW ONE site during testing so disk usage stays low.
- Preserve the existing professional static site and app JSON behavior.

Stage 265 productizes the local operating instructions and verification surface. It does not install cron/systemd jobs automatically because that changes host state. It prints deterministic commands and checks the user can run manually or paste into a local scheduler.

## Non-Goals

- No automatic system service installation.
- No daemon/process manager.
- No deployment automation, tunnel, public hosting, authentication, or HTTPS.
- No new collectors, scraping, platform APIs, LLM calls, translation services, image generation, or scoring/ranking changes.
- No change to `row-one-app/v1` JSON.

## Proposed Surface

Add a new ROW ONE subcommand:

```bash
fashion-radar row-one local-ops --time 04:00 --host 0.0.0.0 --port 8787
```

The command prints a compact runbook with:

1. Refresh command sequence with explicit local directories:
   - `fashion-radar run --config-dir ... --data-dir ... --reports-dir ... --as-of "$AS_OF"`
   - `fashion-radar row-one build --config-dir ... --data-dir ... --reports-dir ... --output-dir ... --as-of "$AS_OF" --latest-only`
2. Preview command:
   - `fashion-radar row-one preview --config-dir ... --data-dir ... --reports-dir ... --output-dir ... --latest-only --dry-run-serve-url`
3. Serve command:
   - `fashion-radar row-one serve --site-dir ... --host ... --port ...`
4. Cron snippet using the selected `--time`, `--config-dir`, `--data-dir`, `--reports-dir`, and `--output-dir`.
5. Fixed access URL guidance:
   - `Open locally: http://127.0.0.1:<port>` when bound to `0.0.0.0`.
   - `Open from LAN: http://<LAN-IP>:<port>`.
6. Storage note:
   - `--latest-only` removes only known generated ROW ONE children inside a directory marked with a `.row-one-site` file.

## Architecture

Create a ROW ONE-owned pure helper module:

- `fashion_radar.row_one.ops.render_row_one_local_ops_runbook(...)`

The helper reuses existing pure utilities:

- `fashion_radar.scheduling.render_row_one_cron_example(...)`
- `fashion_radar.scheduling.raw_as_of_shell(...)`
- `fashion_radar.scheduling.validate_hhmm(...)`
- `fashion_radar.row_one.server.format_row_one_site_access_message(...)`

This keeps `scheduling.py` as a general scheduling helper and avoids making it depend on the ROW ONE package. The CLI command only prints the rendered runbook. It must not read config, open SQLite, build the site, start a server, install cron, or write files.

## Test Strategy

- Unit-test the runbook renderer with fixed paths/time/host/port.
- CLI-test `row-one local-ops --help` and one full invocation.
- Docs-test `docs/row-one.md`, `docs/cli-reference.md`, README, and upload checklist references.
- First-run smoke should call `row-one local-ops --help` and `row-one local-ops --time 04:00` and assert the key commands/URL guidance appear.
- Package archive checks should include the new `src/fashion_radar/row_one/ops.py` module.

## Release Gate

Run the existing release gate:

```bash
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest -q
uv --no-config build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```
