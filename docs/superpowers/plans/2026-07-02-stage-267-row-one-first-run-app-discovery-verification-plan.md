# Stage 267 ROW ONE First-Run App Discovery Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `row-one preview`, first-run smoke, and docs prove that ROW ONE generated sites include a usable app discovery manifest and pass local serve dry-run validation.

**Architecture:** Keep the work in CLI output, smoke verification, and docs. Do not change ROW ONE models, schema, app payload fields, rendering contracts, collectors, scoring, or server behavior. `row-one preview` prints one new manifest path line; first-run smoke parses the generated manifest and verifies `row-one serve --dry-run` against the generated site.

**Tech Stack:** Python 3.11+, Typer CLI, existing first-run smoke helpers, pytest, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/cli.py`
  - Add `Manifest: <output>/data/manifest.json` to `row-one preview`.
- Modify: `scripts/check_first_run_smoke.py`
  - Validate ROW ONE manifest JSON and serve dry-run in the existing ROW ONE smoke block.
- Modify: `tests/test_row_one_cli.py`
  - Pin the new preview output.
- Modify: `tests/test_first_run_smoke.py`
  - Update the ROW ONE fake preview/site artifacts and serve dry-run mock.
- Modify: `tests/test_row_one_docs.py`
  - Pin docs language for preview manifest and first-run smoke validation.
- Modify: `docs/row-one.md`
  - Document preview manifest output.
- Modify: `docs/first-run.md`
  - Document that first-run smoke verifies the ROW ONE manifest and serve dry-run path.
- Modify: `README.md`
  - Mention ROW ONE manifest/serve dry-run verification in the first-run summary.

---

### Task 1: Preview Manifest Output

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add failing CLI assertion**

In `tests/test_row_one_cli.py`, update `test_row_one_preview_builds_site_and_prints_readiness`:

```python
assert (output_dir / "data" / "manifest.json").exists()
assert f"Manifest: {output_dir / 'data' / 'manifest.json'}" in result.output
```

- [ ] **Step 2: Run the targeted test and verify it fails**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_preview_builds_site_and_prints_readiness -q
```

Expected: FAIL because `row-one preview` does not print `Manifest:` yet.

- [ ] **Step 3: Add preview output line**

In `src/fashion_radar/cli.py`, inside `row_one_preview`, keep the existing `JSON:` line and add:

```python
typer.echo(f"Manifest: {result.output_dir / 'data' / 'manifest.json'}")
```

Place it immediately after:

```python
typer.echo(f"JSON: {result.output_dir / 'data' / 'edition.json'}")
```

- [ ] **Step 4: Run CLI test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_preview_builds_site_and_prints_readiness -q
```

Expected: PASS.

---

### Task 2: First-Run Smoke Manifest And Serve Dry-Run

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add smoke manifest validator**

In `scripts/check_first_run_smoke.py`, near `validate_row_one_schedule_output`, add:

```python
def validate_row_one_manifest(
    *,
    manifest_payload: Mapping[str, object],
    edition_payload: Mapping[str, object],
) -> None:
    assert_equal(
        "row-one manifest contract_version",
        manifest_payload.get("contract_version"),
        "row-one-manifest/v1",
    )
    app_contract = manifest_payload.get("app_contract")
    if not isinstance(app_contract, Mapping):
        raise SmokeError("row-one manifest app_contract must be a JSON object")
    assert_equal(
        "row-one manifest app contract path",
        app_contract.get("path"),
        "data/edition.json",
    )
    site = manifest_payload.get("site")
    if not isinstance(site, Mapping):
        raise SmokeError("row-one manifest site must be a JSON object")
    assert_equal("row-one manifest index path", site.get("index_path"), "index.html")
    assert_equal("row-one manifest manifest path", site.get("manifest_path"), "data/manifest.json")
    counts = manifest_payload.get("counts")
    if not isinstance(counts, Mapping):
        raise SmokeError("row-one manifest counts must be a JSON object")
    assert_equal(
        "row-one manifest story count",
        counts.get("story_count"),
        edition_payload.get("story_count"),
    )
    assert_equal(
        "row-one manifest evidence count",
        counts.get("evidence_count"),
        edition_payload.get("evidence_count"),
    )
    readiness = manifest_payload.get("readiness")
    if not isinstance(readiness, Mapping):
        raise SmokeError("row-one manifest readiness must be a JSON object")
    story_count = edition_payload.get("story_count")
    expected_status = "ready" if isinstance(story_count, int) and story_count > 0 else "empty"
    assert_equal(
        "row-one manifest readiness",
        readiness.get("status"),
        expected_status,
    )
```

The script already imports `Mapping`; if not, add it from `collections.abc`.

- [ ] **Step 2: Extend the real smoke block**

In the existing ROW ONE block in `scripts/check_first_run_smoke.py`, add `Manifest:` to preview output expectations:

```python
f"Manifest: {row_one_output_dir / 'data' / 'manifest.json'}",
```

After:

```python
assert_non_empty_file(row_one_output_dir / "data" / "edition.json")
```

add:

```python
row_one_edition_payload = validate_json_output(
    "row-one edition JSON",
    (row_one_output_dir / "data" / "edition.json").read_text(encoding="utf-8"),
)
assert_non_empty_file(row_one_output_dir / "data" / "manifest.json")
row_one_manifest_payload = validate_json_output(
    "row-one manifest JSON",
    (row_one_output_dir / "data" / "manifest.json").read_text(encoding="utf-8"),
)
validate_row_one_manifest(
    manifest_payload=row_one_manifest_payload,
    edition_payload=row_one_edition_payload,
)
```

Then call serve dry-run:

```python
row_one_serve_dry_run = run_cli(
    context,
    "row-one",
    "serve",
    "--site-dir",
    str(row_one_output_dir),
    "--host",
    "127.0.0.1",
    "--port",
    "8787",
    "--dry-run",
).stdout
assert_output_contains_text(
    "row-one serve --dry-run",
    row_one_serve_dry_run,
    ("Open: http://127.0.0.1:8787",),
)
```

- [ ] **Step 3: Update first-run smoke unit fake**

In `tests/test_first_run_smoke.py`, inside the fake `row-one preview` branch, write both JSON files:

```python
(row_one_data_dir / "edition.json").write_text(
    json.dumps({"story_count": 0, "evidence_count": 0}),
    encoding="utf-8",
)
(row_one_data_dir / "manifest.json").write_text(
    json.dumps(
        {
            "contract_version": "row-one-manifest/v1",
            "app_contract": {"path": "data/edition.json"},
            "site": {
                "index_path": "index.html",
                "manifest_path": "data/manifest.json",
            },
            "counts": {"story_count": 0, "evidence_count": 0},
            "readiness": {"status": "empty"},
        }
    ),
    encoding="utf-8",
)
```

Add the preview output line:

```python
f"Manifest: {row_one_output_dir / 'data' / 'manifest.json'}\n"
```

Add a fake serve dry-run branch before local-ops:

```python
if args[:2] == ("row-one", "serve") and "--dry-run" in args:
    return subprocess.CompletedProcess(
        ["python", "-m", "fashion_radar", *args],
        0,
        stdout="Open: http://127.0.0.1:8787\n",
        stderr="",
    )
```

- [ ] **Step 4: Update deterministic command sequence**

In `tests/test_first_run_smoke.py`, update `expected_first_run_flow_commands(...)` so the strict
command-order expectation includes the new serve dry-run call. Insert this tuple immediately after
the existing `row-one preview` tuple and before the existing `row-one local-ops` tuple:

```python
(
    "row-one",
    "serve",
    "--site-dir",
    str(context.reports_dir / "row-one" / "site"),
    "--host",
    "127.0.0.1",
    "--port",
    "8787",
    "--dry-run",
),
```

Do not rely only on an `in captured` assertion; the existing
`assert_first_run_flow_commands(captured, ...)` strict equality check must pass.

- [ ] **Step 5: Run first-run smoke tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
```

Expected: PASS.

---

### Task 3: Docs Pins

**Files:**
- Modify: `docs/row-one.md`
- Modify: `docs/first-run.md`
- Modify: `README.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs assertions**

In `tests/test_row_one_docs.py`, add:

```python
def test_row_one_docs_describe_manifest_preview_and_smoke_verification() -> None:
    row_one_doc = _read(ROW_ONE_DOC)
    first_run = _read(ROOT / "docs" / "first-run.md")
    readme = _read(ROOT / "README.md")

    assert "Manifest:" in row_one_doc
    assert "`data/manifest.json` path" in row_one_doc
    assert "row-one serve --dry-run" in row_one_doc
    assert "First-run smoke verifies the ROW ONE manifest" in first_run
    assert "row-one serve --dry-run" in first_run
    assert "ROW ONE manifest and serve dry-run" in readme
```

- [ ] **Step 2: Run docs test and verify it fails**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_manifest_preview_and_smoke_verification -q
```

Expected: FAIL because docs do not mention the new verification wording yet.

- [ ] **Step 3: Update docs**

In `docs/row-one.md`, update Daily Readiness And Preview:

```markdown
`row-one preview` builds the same static site as `row-one build` and prints the
site path, `data/edition.json` path, `data/manifest.json` path, story count,
section count, evidence link count, empty sections, generated timestamp, and
readiness label.
```

Add:

```markdown
The `Manifest:` preview line points to the generated `data/manifest.json` path
that app clients can read before loading `data/edition.json`.
```

Preserve the existing exact phrase `row-one serve --dry-run` in `docs/row-one.md`; the docs test
pins that phrase.

In `docs/first-run.md`, add after the ROW ONE sample block:

```markdown
First-run smoke verifies the ROW ONE manifest, checks that its counts align with
`data/edition.json`, and runs `row-one serve --dry-run` against the generated
site without starting a long-running server.
```

In `README.md`, add near first-run onboarding:

```markdown
The automated first-run smoke also checks the ROW ONE manifest and serve dry-run
path so app discovery and local serving stay verifiable.
```

- [ ] **Step 4: Run docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: PASS.

---

### Task 4: Focused Verification And Code Review Packet

**Files:**
- Modify only files touched by Tasks 1-3.
- Create: `docs/reviews/opencode-stage-267-code-review-prompt.md` after implementation.

- [ ] **Step 1: Run focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/cli.py scripts/check_first_run_smoke.py tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/cli.py scripts/check_first_run_smoke.py tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: all pass.

- [ ] **Step 2: Write opencode code review prompt**

Create `docs/reviews/opencode-stage-267-code-review-prompt.md` with:

```markdown
Review the Stage 267 implementation before commit/push.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-267-row-one-first-run-app-discovery-verification-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-267-row-one-first-run-app-discovery-verification-plan.md

Goal:
Expose ROW ONE `data/manifest.json` in preview output and verify the manifest
plus `row-one serve --dry-run` in first-run smoke.

Review criteria:
- Preview keeps existing `JSON:` output and adds `Manifest:` without changing build behavior.
- First-run smoke validates manifest fields and counts against `edition.json`.
- First-run smoke verifies `row-one serve --dry-run` without starting a server.
- No `row-one-app/v1` schema changes, provenance fields, collectors, scoring,
  scheduling, cleanup, deployment, image generation, LLM calls, or compliance-review features.
- Docs accurately describe the new verification surface.

Return Critical / Important / Minor findings and a verdict.
```

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-267-code-review-prompt.md)" > docs/reviews/opencode-stage-267-code-review.md
```

Expected: no Critical/Important findings before release gate.

- [ ] **Step 4: Run full release gate**

Run:

```bash
rm -rf dist
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

Expected: all pass.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/cli.py scripts/check_first_run_smoke.py tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py docs/row-one.md docs/first-run.md README.md docs/reviews/opencode-stage-267-code-review-prompt.md docs/reviews/opencode-stage-267-code-review.md docs/superpowers/plans/2026-07-02-stage-267-row-one-first-run-app-discovery-verification-plan.md docs/superpowers/specs/2026-07-02-stage-267-row-one-first-run-app-discovery-verification-design.md
git diff --cached --check
git commit -m "Stage 267: verify ROW ONE app discovery in first-run smoke"
git push origin main
```

Expected: commit and push succeed.
