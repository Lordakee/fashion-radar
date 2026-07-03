# Stage 270 ROW ONE Runtime Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add ROW ONE runtime readiness metadata, a status command, stronger real-serve smoke coverage, and clearer local 04:00 operations docs.

**Architecture:** Keep ROW ONE as a static-site output served by Python's standard-library HTTP server. Extend the existing render layer with an additive self-describing `row-one-runtime/v1` payload at `data/runtime.json`, keep the existing manifest contract unchanged, add a validation-only CLI status command, and verify actual CLI serving in tests without adding a daemon or external scheduler.

**Tech Stack:** Python 3.11+, Typer CLI, Pydantic models already in use, JSON Schema draft 2020-12, stdlib `http.server`, pytest, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/row_one/render.py`
  - Add `ROW_ONE_RUNTIME_CONTRACT_VERSION`.
  - Write `data/runtime.json`.
  - Add `build_row_one_runtime_payload(...)`.
- Create: `schemas/row-one-runtime.schema.json`
  - Validate the new additive runtime payload.
- Modify: `tests/test_row_one_app_contract.py`
  - Validate generated runtime payload and schema drift cases.
- Modify: `src/fashion_radar/row_one/server.py`
  - Add a small site-status reader/validator if it belongs closer to server validation.
- Modify: `src/fashion_radar/cli.py`
  - Add `row-one status`.
- Modify: `tests/test_row_one_cli.py`
  - Cover `row-one status` text output, JSON output, failure cases, and actual CLI serve subprocess smoke.
- Modify: `tests/test_package_archives.py`
  - Require `schemas/row-one-runtime.schema.json` in package archives.
- Modify: `docs/row-one.md`
  - Document `runtime.json`, `row-one status`, 04:00 refresh, fixed IP:port serve, and retention boundary.
- Modify: `docs/cli-reference.md`
  - List `row-one status`.
- Modify: `docs/first-run.md`
  - Include the status command in the ROW ONE first-run flow.
- Modify: `tests/test_row_one_docs.py`
  - Guard the new docs.
- Modify: `scripts/check_first_run_smoke.py`
  - Validate runtime payload and add `row-one status` to first-run smoke.

---

## Parallel Ownership

Workers must not edit files outside their ownership. If a worker needs a file
owned by another worker, it must return `NEEDS_CONTEXT`.

- Worker A, runtime contract:
  - `src/fashion_radar/row_one/render.py`
  - `schemas/row-one-runtime.schema.json`
  - `tests/test_row_one_app_contract.py`
  - `tests/test_package_archives.py`
- Worker B, CLI status and serve smoke:
  - `src/fashion_radar/cli.py`
  - `src/fashion_radar/row_one/server.py`
  - `tests/test_row_one_cli.py`
- Worker C, smoke/docs:
  - `scripts/check_first_run_smoke.py`
  - `docs/row-one.md`
  - `docs/cli-reference.md`
  - `docs/first-run.md`
  - `tests/test_row_one_docs.py`

Suggested order:

1. Run Worker A first or locally in the main session because B/C depend on the runtime file path.
2. Run Worker B and Worker C in parallel after Worker A lands.
3. Run plan/code review before full gate.

---

### Task 1: Runtime Payload And Schema

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Create: `schemas/row-one-runtime.schema.json`
- Modify: `tests/test_row_one_app_contract.py`
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add failing runtime payload test**

Add a test to `tests/test_row_one_app_contract.py`:

```python
def test_row_one_runtime_payload_validates_generated_site(tmp_path: Path) -> None:
    render_row_one_site(_edition(), tmp_path)
    runtime = json.loads((tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas" / "row-one-runtime.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(runtime)
    assert runtime["contract_version"] == "row-one-runtime/v1"
    assert runtime["brand"] == "ROW ONE"
    assert runtime["site"]["index_path"] == "index.html"
    assert runtime["site"]["manifest_path"] == "data/manifest.json"
    assert runtime["site"]["edition_path"] == "data/edition.json"
    assert runtime["site"]["runtime_path"] == "data/runtime.json"
    assert runtime["refresh"]["recommended_time"] == "04:00"
    assert runtime["refresh"]["latest_only_cleanup"] is True
    assert runtime["serve"]["default_port"] == 8787
    assert runtime["counts"]["story_count"] == 1
```

- [ ] **Step 2: Add manifest non-regression assertion**

Extend the existing manifest payload test to prove the manifest contract remains
unchanged and does not grow a `runtime_path` field:

```python
assert "runtime_path" not in manifest["site"]
```

- [ ] **Step 3: Run red tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_runtime_payload_validates_generated_site -q
```

Expected: FAIL because `data/runtime.json` and its schema do not exist.

- [ ] **Step 4: Implement runtime payload writer**

In `src/fashion_radar/row_one/render.py`, add:

```python
ROW_ONE_RUNTIME_CONTRACT_VERSION = "row-one-runtime/v1"
ROW_ONE_RUNTIME_SCHEMA_PATH = "schemas/row-one-runtime.schema.json"
ROW_ONE_RUNTIME_PATH = "data/runtime.json"
```

Add `runtime.json` writing after the `edition.json` write and before the
`manifest_payload = build_row_one_manifest_payload(...)` line in
`src/fashion_radar/row_one/render.py`:

```python
runtime_payload = build_row_one_runtime_payload(edition, app_payload)
(data_dir / "runtime.json").write_text(
    json.dumps(runtime_payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
manifest_payload = build_row_one_manifest_payload(edition, app_payload)
```

Add:

```python
def build_row_one_runtime_payload(
    edition: RowOneEdition,
    app_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    app_payload = app_payload or build_row_one_app_payload(edition)
    readiness = build_row_one_readiness(edition)
    return {
        "contract_version": ROW_ONE_RUNTIME_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": isoformat_z(edition.generated_at),
        "edition_date": isoformat_z(edition.edition_date),
        "site": {
            "index_path": "index.html",
            "manifest_path": "data/manifest.json",
            "edition_path": "data/edition.json",
            "runtime_path": "data/runtime.json",
        },
        "refresh": {
            "recommended_time": "04:00",
            "command": 'fashion-radar row-one refresh --as-of "$AS_OF" --output-dir reports/row-one/site',
            "latest_only_cleanup": True,
        },
        "serve": {
            "default_host": "127.0.0.1",
            "default_port": 8787,
            "local_url": "http://127.0.0.1:8787",
            "lan_url_hint": "http://<LAN-IP>:8787",
        },
        "counts": {
            "story_count": int(app_payload["story_count"]),
            "section_count": len(edition.sections),
            "evidence_count": int(app_payload["evidence_count"]),
        },
        "readiness": {
            "status": readiness.readiness.en,
            "zh": readiness.readiness.zh,
            "en": readiness.readiness.en,
        },
    }
```

Import `build_row_one_readiness` from `fashion_radar.row_one.readiness`.

- [ ] **Step 5: Preserve manifest contract**

Do not change `schemas/row-one-manifest.schema.json` and do not add
`runtime_path` to `build_row_one_manifest_payload`. The runtime payload is
available at the fixed `data/runtime.json` path and is validated by its own
schema.

- [ ] **Step 6: Add runtime schema**

Create `schemas/row-one-runtime.schema.json` with a strict object schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fashion-radar.local/schemas/row-one-runtime.schema.json",
  "title": "ROW ONE Runtime Contract",
  "type": "object",
  "required": ["contract_version", "brand", "generated_at", "edition_date", "site", "refresh", "serve", "counts", "readiness"],
  "additionalProperties": false,
  "properties": {
    "contract_version": { "const": "row-one-runtime/v1" },
    "brand": { "const": "ROW ONE" },
    "generated_at": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$" },
    "edition_date": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$" },
    "site": {
      "type": "object",
      "required": ["index_path", "manifest_path", "edition_path", "runtime_path"],
      "additionalProperties": false,
      "properties": {
        "index_path": { "const": "index.html" },
        "manifest_path": { "const": "data/manifest.json" },
        "edition_path": { "const": "data/edition.json" },
        "runtime_path": { "const": "data/runtime.json" }
      }
    },
    "refresh": {
      "type": "object",
      "required": ["recommended_time", "command", "latest_only_cleanup"],
      "additionalProperties": false,
      "properties": {
        "recommended_time": { "const": "04:00" },
        "command": { "type": "string", "minLength": 1 },
        "latest_only_cleanup": { "const": true }
      }
    },
    "serve": {
      "type": "object",
      "required": ["default_host", "default_port", "local_url", "lan_url_hint"],
      "additionalProperties": false,
      "properties": {
        "default_host": { "const": "127.0.0.1" },
        "default_port": { "const": 8787 },
        "local_url": { "const": "http://127.0.0.1:8787" },
        "lan_url_hint": { "const": "http://<LAN-IP>:8787" }
      }
    },
    "counts": {
      "type": "object",
      "required": ["story_count", "section_count", "evidence_count"],
      "additionalProperties": false,
      "properties": {
        "story_count": { "type": "integer", "minimum": 0 },
        "section_count": { "type": "integer", "minimum": 0 },
        "evidence_count": { "type": "integer", "minimum": 0 }
      }
    },
    "readiness": {
      "type": "object",
      "required": ["status", "zh", "en"],
      "additionalProperties": false,
      "properties": {
        "status": { "enum": ["ready", "empty"] },
        "zh": { "type": "string", "minLength": 1 },
        "en": { "enum": ["ready", "empty"] }
      }
    }
  }
}
```

- [ ] **Step 7: Update package archive required files**

Add `schemas/row-one-runtime.schema.json` to the package archive required-path
tests in `tests/test_package_archives.py`.

- [ ] **Step 8: Run focused runtime contract tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py tests/test_package_archives.py -q
```

Expected: PASS.

---

### Task 2: CLI Status Command And Real Serve Smoke

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/row_one/server.py` if a helper is useful
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add failing status success test**

In `tests/test_row_one_cli.py`, add:

```python
def test_row_one_status_prints_generated_site_readiness(tmp_path: Path) -> None:
    render_row_one_site(build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF), tmp_path)
    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--host", "0.0.0.0", "--port", "8787"],
    )
    assert result.exit_code == 0, result.output
    assert "ROW ONE status" in result.output
    assert f"Site: {tmp_path}" in result.output
    assert "Manifest: data/manifest.json" in result.output
    assert "Edition: data/edition.json" in result.output
    assert "Runtime: data/runtime.json" in result.output
    assert "Open locally: http://127.0.0.1:8787" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
```

- [ ] **Step 2: Add failing JSON status test**

Add:

```python
def test_row_one_status_json_outputs_machine_readable_payload(tmp_path: Path) -> None:
    render_row_one_site(build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF), tmp_path)
    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["site_dir"] == str(tmp_path)
    assert payload["paths"]["manifest"] == "data/manifest.json"
    assert payload["paths"]["edition"] == "data/edition.json"
    assert payload["paths"]["runtime"] == "data/runtime.json"
    assert payload["runtime"]["contract_version"] == "row-one-runtime/v1"
```

- [ ] **Step 3: Add failing missing runtime test**

Add:

```python
def test_row_one_status_rejects_missing_runtime_payload(tmp_path: Path) -> None:
    render_row_one_site(build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF), tmp_path)
    (tmp_path / "data" / "runtime.json").unlink()
    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "data/runtime.json" in result.output
```

- [ ] **Step 4: Implement `row-one status`**

In `src/fashion_radar/cli.py`, add a command before `row_one_schedule`:

```python
@row_one_app.command(name="status")
def row_one_status(
    site_dir: Path = ROW_ONE_SITE_DIR_OPTION,
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON status."),
) -> None:
    """Validate a generated ROW ONE site and print runtime readiness."""
    try:
        validate_row_one_site_dir(site_dir)
        manifest = _read_json_file(site_dir / "data" / "manifest.json")
        edition = _read_json_file(site_dir / "data" / "edition.json")
        runtime = _read_json_file(site_dir / "data" / "runtime.json")
    except Exception as exc:
        typer.echo(f"ROW ONE status failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    payload = {
        "ok": True,
        "site_dir": str(site_dir),
        "access": format_row_one_site_access_message(host, port),
        "paths": {
            "manifest": "data/manifest.json",
            "edition": "data/edition.json",
            "runtime": "data/runtime.json",
        },
        "manifest": manifest,
        "runtime": runtime,
        "story_count": edition.get("story_count"),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("ROW ONE status")
    typer.echo(f"Site: {site_dir}")
    typer.echo("Manifest: data/manifest.json")
    typer.echo("Edition: data/edition.json")
    typer.echo("Runtime: data/runtime.json")
    typer.echo(f"Stories: {payload['story_count']}")
    typer.echo(f"Generated at: {runtime.get('generated_at', 'unknown')}")
    typer.echo(f"Readiness: {runtime.get('readiness', {}).get('en', 'unknown')}")
    typer.echo(payload["access"])
```

Add a small private helper near existing CLI helpers:

```python
def _read_json_file(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload
```

If `json` is not imported at the top of `cli.py`, import it.

- [ ] **Step 5: Add real CLI serve subprocess smoke**

Add a test that launches the Typer CLI as a subprocess. Use an ephemeral port
from a socket bound to `127.0.0.1` and close the socket before starting the
process. Fetch the same core files promised by the design: `/`,
`/data/manifest.json`, `/data/edition.json`, `/data/runtime.json`,
`/assets/row-one.css`, and `/assets/row-one.js`.

```python
def test_row_one_serve_cli_process_serves_generated_site(tmp_path: Path) -> None:
    render_row_one_site(build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF), tmp_path)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
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
        deadline = time.monotonic() + 10
        fetched: dict[str, str] = {}
        while time.monotonic() < deadline:
            try:
                for path in (
                    "/",
                    "/data/manifest.json",
                    "/data/edition.json",
                    "/data/runtime.json",
                    "/assets/row-one.css",
                    "/assets/row-one.js",
                ):
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=0.5)
                    conn.request("GET", path)
                    response = conn.getresponse()
                    body = response.read().decode("utf-8")
                    conn.close()
                    assert response.status == 200
                    fetched[path] = body
                if len(fetched) == 6:
                    break
            except OSError:
                time.sleep(0.1)
        assert len(fetched) == 6
        assert "ROW ONE" in fetched["/"]
        assert '"contract_version": "row-one-manifest/v1"' in fetched["/data/manifest.json"]
        assert '"contract_version": "row-one-app/v1"' in fetched["/data/edition.json"]
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
```

Add imports for `subprocess`, `sys`, and `time` if absent.

- [ ] **Step 6: Run focused CLI tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q
```

Expected: PASS.

---

### Task 3: Docs And First-Run Smoke

**Files:**
- Modify: `docs/row-one.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/first-run.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add failing docs drift test**

In `tests/test_row_one_docs.py`, add a test that reads the three docs and
asserts these strings:

```python
assert "row-one status" in row_one_doc
assert "data/runtime.json" in row_one_doc
assert "http://<LAN-IP>:8787" in row_one_doc
assert "04:00" in row_one_doc
assert "site output" in row_one_doc.lower()
assert "dated reports" in row_one_doc.lower()
assert "row-one status" in cli_reference
assert "row-one status" in first_run
```

- [ ] **Step 2: Update docs**

In `docs/row-one.md`, add a `Runtime Status` section:

```markdown
## Runtime Status

Every generated site writes `data/runtime.json` next to `data/edition.json` and
`data/manifest.json`. It records the ROW ONE runtime contract, generated time,
04:00 refresh recommendation, default local serve URL, LAN URL hint, counts, and
readiness label.

Use `row-one status` before starting or after refreshing the local server:

```bash
uv run fashion-radar row-one status --site-dir reports/row-one/site --host 0.0.0.0 --port 8787
```
```

Also update the existing quickstart command block to include `row-one status`.

Add a `Retention Boundary` subsection to `docs/row-one.md` with this exact
distinction:

```markdown
`latest_only=True` keeps only the latest ROW ONE site output children inside the
generated site directory. Dated reports (`fashion-radar-YYYY-MM-DD.md`,
`fashion-radar-YYYY-MM-DD.json`, and matching HTML) live outside the site
directory and are not deleted by ROW ONE refresh.
```

Also add `data/runtime.json` to the generated files list.

In `docs/cli-reference.md`, add `row-one status` to the ROW ONE command list and
one bullet describing it.

In `docs/first-run.md`, add `row-one status` between preview and serve in the
ROW ONE section.

- [ ] **Step 3: Update first-run smoke**

In `scripts/check_first_run_smoke.py`, update ROW ONE smoke by adding a
`validate_row_one_runtime(runtime_payload: Any, *, expected_story_count: int)`
helper next to `validate_row_one_manifest`, then call it through
`validate_json_output("row-one runtime", row_one_runtime_path.read_text(...))`
in the existing ROW ONE preview block after `row_one_manifest_path` is
validated. Also run the status command in that same block using existing
`run_cli(...)` and `assert_output_contains_text(...)` helpers:

- assert `data/runtime.json` exists;
- parse runtime payload and assert `contract_version == "row-one-runtime/v1"`;
- assert runtime counts match the generated edition story count;
- run `row-one status --site-dir <site> --host 127.0.0.1 --port 8787`;
- assert output includes `ROW ONE status`, `Runtime: data/runtime.json`, and
  `http://127.0.0.1:8787`.

- [ ] **Step 4: Run docs and smoke tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_first_run_smoke.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: PASS.

---

### Task 4: Integration Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-270-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-270-plan-review.md`
- Create: `docs/reviews/opencode-stage-270-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-270-code-review.md`

- [ ] **Step 1: Run plan review before implementation**

Use the local review process requested by the user before implementing code.
The plan review prompt must ask whether Stage 270:

- builds on existing `refresh/schedule/local-ops/serve` commands instead of
  duplicating them;
- keeps `row-one-manifest/v1` unchanged and treats `data/runtime.json` as a
  fixed-path, self-describing additive contract;
- keeps scheduling print-only;
- avoids deleting dated reports outside the ROW ONE site directory;
- avoids OpenDesign, collectors, platform automation, and compliance features;
- has enough tests for runtime payload, status command, real serve smoke, docs,
  and package archives.

- [ ] **Step 2: After implementation, run code review**

Ask the reviewer to inspect all changed Stage 270 files and answer whether the
runtime contract, status command, serve smoke, docs, and package archive changes
match this plan.

- [ ] **Step 3: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_cli.py \
  tests/test_row_one_render.py \
  tests/test_row_one_edition.py \
  tests/test_row_one_readiness.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_docs.py \
  tests/test_scheduling.py \
  tests/test_scheduling_docs.py \
  tests/test_first_run_smoke.py \
  tests/test_release_hygiene.py \
  tests/test_package_archives.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one src/fashion_radar/cli.py tests/test_row_one_cli.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py scripts/check_first_run_smoke.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one src/fashion_radar/cli.py tests/test_row_one_cli.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py scripts/check_first_run_smoke.py
git diff --check
```

- [ ] **Step 4: Full release gate**

Run:

```bash
tmp_env="$(mktemp -d)"
tmp_build="$tmp_env/dist"
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

- [ ] **Step 5: Commit and push**

After review approval and full gate pass:

```bash
git status --short
git add docs/row-one.md docs/cli-reference.md docs/first-run.md \
  docs/reviews/opencode-stage-270-plan-review-prompt.md \
  docs/reviews/opencode-stage-270-plan-review.md \
  docs/reviews/opencode-stage-270-code-review-prompt.md \
  docs/reviews/opencode-stage-270-code-review.md \
  docs/superpowers/specs/2026-07-03-stage-270-row-one-runtime-readiness-design.md \
  docs/superpowers/plans/2026-07-03-stage-270-row-one-runtime-readiness-plan.md \
  schemas/row-one-runtime.schema.json \
  src/fashion_radar/cli.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/server.py \
  tests/test_row_one_app_contract.py tests/test_row_one_cli.py tests/test_row_one_docs.py \
  tests/test_package_archives.py scripts/check_first_run_smoke.py
git commit -m "Stage 270: add ROW ONE runtime readiness"
git push origin main
```

Then report a Handoff Summary with repo status, verified commands, uncommitted
files, and next step.

---

## Self-Review Notes

- This plan does not add OpenDesign calls or image generation.
- This plan does not add collectors or platform automation.
- This plan does not install cron/systemd timers.
- This plan explicitly preserves dated reports outside the ROW ONE site output.
- Runtime contract is additive and does not change `row-one-app/v1`.
- Tests cover runtime payload, status command, real serving, docs, smoke, and
  package archives.
