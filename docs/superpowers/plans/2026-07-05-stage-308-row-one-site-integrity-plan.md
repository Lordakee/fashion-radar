# Stage 308 ROW ONE Site Integrity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `row-one status` and the release smoke catch generated ROW ONE site drift where JSON contracts pass but files, routes, sidecars, anchors, or local HTTP serving are broken.

**Architecture:** Add a read-only generated-site integrity validator under `fashion_radar.row_one`, call it from the existing `row-one status` command after runtime/manifest/edition semantic checks, and keep the JSON schemas/app payload unchanged. Add a first-run smoke helper that launches the real `row-one serve` CLI on an ephemeral local port and fetches a tiny fixed set of generated routes.

**Tech Stack:** Python 3.12, Typer CLI, Pydantic models already in `fashion_radar.row_one.models`, pytest, stdlib `http.client`/`subprocess` for smoke, existing `uv --frozen` verification.

---

## Non-Goals

- Do not add compliance/product review features.
- Do not change source collection, ranking, matching, scoring, sorting, story IDs, schemas, or `row-one-app/v7`.
- Do not network-check external URLs, evidence links, remote story images, Instagram/TikTok/X/XHS links, or source availability.
- Do not make `row-one status` rebuild, refresh, collect, deploy, publish, start a long-running server, or write generated files.
- Do not reject arbitrary extra files under `details/`; only require current referenced generated files to exist.

## Files

- Create: `src/fashion_radar/row_one/status_integrity.py`
  - Owns read-only filesystem, route, sidecar, paragraph-index, and local asset checks for an already generated ROW ONE site.
- Modify: `src/fashion_radar/cli.py`
  - Calls the new validator from `row_one_status(...)` after `_validate_row_one_status_payloads(...)`.
- Modify: `tests/test_row_one_cli.py`
  - Adds focused status/preflight tests for missing assets, missing details, local image assets, stale/mismatched article sidecars, unsafe/unknown local-intelligence links, and bad paragraph indices.
- Modify: `scripts/check_first_run_smoke.py`
  - Adds `run_row_one_local_http_serve_smoke(context, site_dir)` and calls it after `row-one serve --dry-run`.
- Modify: `tests/test_first_run_smoke.py`
  - Unit-tests the new smoke helper via monkeypatching and asserts the first-run flow calls it.
- Modify: `README.md`, `docs/row-one.md`, `docs/cli-reference.md`
  - Documents Stage 308 site integrity/preflight as CLI-only, read-only, and not a schema/app contract change.
- Modify: `tests/test_row_one_docs.py`
  - Pins the new docs language and forbidden-schema-change wording.
- Generated artifact refresh: `reports/row-one/site/**`
  - Regenerate the checked-in local site after code changes so it reflects Stage 307/308 HTML and sidecar shape.

## Task 1: Write Failing `row-one status` Integrity Tests

**Files:**
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add local helper functions near the existing ROW ONE status tests**

Add helpers that render a populated site with one current story, extract the first story payload, and write JSON back without changing unrelated fixtures:

```python
def _render_populated_status_site(tmp_path: Path) -> dict[str, object]:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/status-integrity",
                "title": "The Row local article evidence strengthens",
                "summary": "Local desk notes a concrete product and brand signal.",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    render_row_one_site(edition, tmp_path)
    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    return payload["stories"][0]
```

If existing helper names already cover this without duplication, reuse them.

Reuse the existing `AS_OF` constant from `tests/test_row_one_cli.py`; do not add a second timestamp constant.

- [ ] **Step 2: Add failing tests for required generated files and detail routes**

Add tests with these expected failures:

```python
def test_row_one_status_rejects_missing_generated_asset(tmp_path: Path) -> None:
    _render_populated_status_site(tmp_path)
    (tmp_path / "assets" / "row-one.css").unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "assets/row-one.css" in result.output


def test_row_one_status_rejects_missing_current_detail_page(tmp_path: Path) -> None:
    story = _render_populated_status_site(tmp_path)
    detail_href = str(story["detail_href"])
    assert not detail_href.startswith("/")
    (tmp_path / detail_href).unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert str(story["detail_href"]) in result.output
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q
```

Expected: these new tests fail because `row-one status` does not yet validate assets/detail files.

- [ ] **Step 3: Add failing tests for article sidecars and local intelligence**

Add tests with these expected failures:

Define the local-article helper explicitly before the tests:

```python
def _render_status_site_with_local_article(tmp_path: Path) -> dict[str, object]:
    """Render a site with one story, one article sidecar, and one local-intelligence item."""
    story = _render_populated_status_site(tmp_path)
    story_id = str(story["id"])
    articles_dir = tmp_path / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / f"{story_id}.json").write_text(
        json.dumps(
            {
                "story_id": story_id,
                "url": "https://example.com/local-article",
                "source_name": "Local Desk",
                "extracted_at": AS_OF,
                "paragraphs": ["First paragraph.", "Second paragraph."],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "data" / "local-intelligence.json").write_text(
        json.dumps(
            [
                {
                    "key": "strongest_reads",
                    "title": {"en": "Strongest Reads", "zh": "最强阅读"},
                    "dek": {"en": "Key local signals.", "zh": "关键本地信号。"},
                    "items": [
                        {
                            "title": {"en": "Local insight", "zh": "本地洞察"},
                            "body": {"en": "Insight body.", "zh": "洞察正文。"},
                            "detail_path": str(story["detail_href"]) + "#local-article",
                            "paragraph_indices": [0],
                        }
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    return story
```

```python
def test_row_one_status_rejects_stale_article_sidecar(tmp_path: Path) -> None:
    _render_populated_status_site(tmp_path)
    articles_dir = tmp_path / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / "old-story.json").write_text(
        json.dumps(
            {
                "story_id": "old-story",
                "url": "https://example.com/old",
                "source_name": "Archive",
                "extracted_at": AS_OF,
                "paragraphs": ["Stale paragraph."],
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "old-story" in result.output


def test_row_one_status_rejects_article_sidecar_story_id_mismatch(tmp_path: Path) -> None:
    story = _render_populated_status_site(tmp_path)
    article_path = tmp_path / "data" / "articles" / f"{story['id']}.json"
    article_path.parent.mkdir(parents=True, exist_ok=True)
    article_path.write_text(
        json.dumps(
            {
                "story_id": "mismatched-story",
                "url": "https://example.com/current",
                "source_name": "Local Desk",
                "extracted_at": AS_OF,
                "paragraphs": ["Current paragraph."],
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "story_id" in result.output
```

Also add local-intelligence tests that mutate `data/local-intelligence.json` after rendering a site with a valid local article:

```python
def test_row_one_status_rejects_unsafe_local_intelligence_detail_path(tmp_path: Path) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    payload[0]["items"][0]["detail_path"] = "../escape.html#local-article"
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "local-intelligence" in result.output
    assert "detail_path" in result.output


def test_row_one_status_rejects_local_intelligence_missing_paragraph_anchor(tmp_path: Path) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    payload[0]["items"][0]["paragraph_indices"] = [99]
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "paragraph_indices" in result.output
```

Use existing `RowOneLocalArticle` fixture patterns from `tests/test_row_one_render.py` to build `_render_status_site_with_local_article(tmp_path)`.

- [ ] **Step 4: Add local image asset checks**

Add one test that mutates the generated `edition.json` story display image to `assets/story-card.jpg`, creates that local file, asserts status passes, deletes the file, then asserts status fails. In the same test or a neighboring test, mutate the image to `https://example.com/remote.jpg` and assert status still passes without any network mock.

Expected error for missing local asset: contains `assets/story-card.jpg`.

## Task 2: Implement Read-Only Site Integrity Validator

**Files:**
- Create: `src/fashion_radar/row_one/status_integrity.py`
- Modify: `src/fashion_radar/cli.py`

- [ ] **Step 1: Implement safe path primitives**

Create `status_integrity.py` with small helpers:

```python
from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urldefrag

from pydantic import ValidationError

from fashion_radar.row_one.display import safe_story_image_src
from fashion_radar.row_one.models import (
    RowOneDailyLocalIntelligenceSection,
    RowOneLocalArticle,
)

_SAFE_STORY_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_PARAGRAPH_FRAGMENT_PREFIX = "local-article-paragraph-"


def _require_file(site_dir: Path, relative_path: str) -> Path:
    path = site_dir / relative_path
    if not path.is_file():
        raise ValueError(f"row-one generated file is missing: {relative_path}")
    return path
```

Add `_validate_detail_path(value: object, *, label: str) -> str` that accepts only `details/<name>.html` with no absolute paths, no `..`, no backslashes, and no extra fragments. Use `PurePosixPath`.

Add `_validate_local_intelligence_href(value: object, *, label: str) -> tuple[str, str]` that defrags the value and accepts only no fragment, `local-article`, or `local-article-paragraph-N` fragments with `N >= 1`. The fragment `N` is one-based; validate it against `paragraphs[N - 1]`.

- [ ] **Step 2: Implement article sidecar validation**

Add:

```python
def _load_article_sidecars(site_dir: Path, current_story_ids: set[str]) -> dict[str, RowOneLocalArticle]:
    ...
```

Behavior:
- If `data/articles/` is missing, return `{}`.
- Reject non-safe filename stems.
- Reject any filename stem not in `current_story_ids`.
- Parse each JSON file as a JSON object and validate with `RowOneLocalArticle.model_validate(...)`.
- Reject if payload `story_id` differs from filename stem.
- Reject if all `paragraphs` are blank.
- Reject if `paragraphs_zh` is non-empty and `len(paragraphs_zh) != len(paragraphs)`.
- Reject paragraph indices in `content_sections[].items[]` when an index is out of range or maps to a blank paragraph.

- [ ] **Step 3: Implement local-intelligence validation**

Add:

```python
def _validate_local_intelligence(
    *,
    site_dir: Path,
    detail_to_story_id: dict[str, str],
    article_sidecars: dict[str, RowOneLocalArticle],
) -> None:
    ...
```

Behavior:
- Missing `data/local-intelligence.json` is allowed.
- Parse the file as a JSON list.
- Validate each section with `RowOneDailyLocalIntelligenceSection.model_validate(...)`.
- For each item and nested segment item:
  - Validate `detail_path` if present.
  - Require its base detail path belongs to a current story.
  - Require the base detail HTML file exists.
  - For `#local-article`, require that story has a sidecar with at least one nonblank paragraph.
  - For `#local-article-paragraph-N`, require sidecar paragraph index `N - 1` exists and is nonblank.
  - Validate every `paragraph_indices[]` entry against the same sidecar paragraph list.

- [ ] **Step 4: Implement top-level validator and CLI wiring**

Expose:

```python
def validate_row_one_generated_site_integrity(
    *,
    site_dir: Path,
    edition: dict[str, object],
) -> None:
    ...
```

Behavior:
- Require fixed files:
  - `index.html`
  - `data/edition.json`
  - `data/manifest.json`
  - `data/runtime.json`
  - `assets/row-one.css`
  - `assets/row-one.js`
- Build `story_id -> detail_href` and `detail_href -> story_id` from `edition["stories"]`.
- Require every current story id is a non-empty string.
- Require every current story detail file exists.
- For every story display image:
  - Use `safe_story_image_src(src)`.
  - If it returns a local `assets/...` path, require the file exists.
  - If it returns remote `http`/`https`, do not fetch it.
- Load article sidecars and validate local intelligence.

In `src/fashion_radar/cli.py`, import this validator and call it after `_validate_row_one_status_payloads(...)`:

```python
validate_row_one_generated_site_integrity(site_dir=site_dir, edition=edition)
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q
```

Expected: status tests pass.

## Task 3: Add First-Run Local HTTP Serve Smoke

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add helper primitives to first-run smoke script**

Add imports if missing: `http.client`, `socket`, `time`.

Add a helper:

```python
def _reserve_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
```

Add:

```python
def _fetch_local_http_path(port: int, path: str) -> str:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.75)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        connection.close()
    if response.status != 200:
        raise OSError(f"{path} returned HTTP {response.status}")
    return body
```

- [ ] **Step 2: Add `run_row_one_local_http_serve_smoke`**

Add:

```python
def run_row_one_local_http_serve_smoke(context: SmokeContext, site_dir: Path) -> None:
    ...
```

Behavior:
- Try up to 3 reserved ports to avoid a closed-socket port race.
- Launch the real CLI via:
  - `cli_command(context, "row-one", "serve", "--site-dir", str(site_dir), "--host", "127.0.0.1", "--port", str(port))`
  - `subprocess.Popen(..., stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=command_environment(context, source_checkout=context.source_checkout), cwd=context.repo_root)`
- Poll HTTP until ready for up to 10 seconds. Do not wait on stdout.
- Sleep 0.1 seconds between poll attempts to avoid a spin-wait.
- Fetch and assert:
  - `/` contains `ROW ONE`
  - `/data/manifest.json` parses and has `contract_version == "row-one-manifest/v1"`
  - `/data/edition.json` parses and has `contract_version == "row-one-app/v7"`
  - `/data/runtime.json` parses and has `contract_version == "row-one-runtime/v1"`
  - `/assets/row-one.css` returns HTTP 200 with a non-empty body
  - `/assets/row-one.js` returns HTTP 200 with a non-empty body
- If the edition has a first `story_directory.routes[].detail_href`, fetch that detail path and assert HTTP 200.
- Always terminate/wait/kill in `finally`.
- If the process exits early, raise `SmokeError` with stdout/stderr snippets.

- [ ] **Step 3: Call helper from `run_first_run_flow`**

Call after the existing `row-one serve --dry-run` assertion and before `row-one local-ops`:

```python
run_row_one_local_http_serve_smoke(context, row_one_output_dir)
```

- [ ] **Step 4: Add unit tests without starting a real server**

In `tests/test_first_run_smoke.py`:
- Monkeypatch the new helper in `test_run_first_run_flow_uses_deterministic_local_command_sequence`, capture `(context, site_dir)`, and assert it is called once with `context` and `context.reports_dir / "row-one" / "site"`.
- Add a focused helper test that monkeypatches `_reserve_local_port`, `subprocess.Popen`, and `_fetch_local_http_path` to prove the helper launches `row-one serve`, validates fixed paths, terminates the process, and parses contract JSON.
- Add an early-exit test where fake process `poll()` returns a non-`None` code and assert `SmokeError`.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
```

Expected: tests pass.

## Task 4: Documentation and Drift Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Update docs language**

Add or align these facts:
- `row-one status --json` is the script-facing preflight surface.
- Stage 308 site integrity/preflight validates an already generated ROW ONE site before serving.
- The check is read-only and does not rebuild, write files, start a server, collect sources, call external services, deploy, or alter ranking/scoring/story IDs.
- It validates `.row-one-site`, `index.html`, fixed JSON paths, core assets, current detail routes, local image asset existence, article sidecars, local-intelligence detail paths, and paragraph anchors.
- The additive status fields are CLI output only and do not add fields to `row-one-runtime/v1`, `row-one-manifest/v1`, or `row-one-app/v7`.
- `data/edition.json` remains `row-one-app/v7`, `data/manifest.json` remains `row-one-manifest/v1`, and `data/runtime.json` remains `row-one-runtime/v1`.
- The first-run smoke now performs a local HTTP serve fetch, not just `serve --dry-run`.

- [ ] **Step 2: Add docs tests**

Add tests that assert the phrases above exist in `docs/row-one.md`, README, and `docs/cli-reference.md`.

Add a negative drift test asserting these phrases are absent from README, `docs/row-one.md`, `docs/cli-reference.md`, and first-run docs if present:

```python
for forbidden in (
    "row-one-app/v8",
    "row-one-manifest/v2",
    "row-one-runtime/v2",
    "new app contract",
    "new schema contract",
    "schema migration",
    "writes data/status.json",
    "status starts the server",
    "status rebuilds the site",
    "status collects sources",
    "status deploys",
):
    assert forbidden not in docs_text
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: docs tests pass.

## Task 5: Regenerate Checked-In ROW ONE Site Snapshot

**Files:**
- Modify generated files under `reports/row-one/site/**`

- [ ] **Step 1: Regenerate with latest code**

Run:

```bash
AS_OF=2026-07-05T06:56:53Z
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one preview \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --output-dir reports/row-one/site \
  --as-of "$AS_OF" \
  --latest-only \
  --dry-run-serve-url
```

- [ ] **Step 2: Verify generated site reflects Stage 307/308 local content**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
rg --no-ignore -q 'daily-local-intelligence-action' reports/row-one/site/index.html
rg --no-ignore -q 'daily-local-intelligence-paragraph-link' reports/row-one/site/index.html
rg --no-ignore -q '#local-article-paragraph-' reports/row-one/site/index.html
rg --no-ignore -q 'local-article-paragraph-' reports/row-one/site/details
python - <<'PY'
import json
payload = json.loads(open("reports/row-one/site/data/local-intelligence.json", encoding="utf-8").read())
assert any(item.get("segments") for section in payload for item in section.get("items", []))
PY
if rg --no-ignore -q '<a class="daily-local-intelligence-card"' reports/row-one/site/index.html; then
  echo "FAIL: forbidden full-card daily local intelligence anchor found"
  exit 1
fi
```

Expected: all commands pass.

## Task 6: Full Verification, Review, Commit, Push

**Files:**
- Modify: `docs/reviews/claude-code-stage-308-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-308-code-review.md`

- [ ] **Step 1: Run focused and full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_first_run_smoke.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv lock --check
```

- [ ] **Step 2: Ask Claude Code for code review**

Create a prompt summarizing changed files and verification commands, then run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-308-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-308-code-review.md
```

Fix Critical/Important findings, rerun targeted verification, and re-review if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/status_integrity.py src/fashion_radar/cli.py \
  tests/test_row_one_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py \
  README.md docs/row-one.md docs/cli-reference.md tests/test_row_one_docs.py \
  reports/row-one/site docs/superpowers/plans/2026-07-05-stage-308-row-one-site-integrity-plan.md \
  docs/reviews/claude-code-stage-308-plan-review-prompt.md \
  docs/reviews/claude-code-stage-308-plan-review.md \
  docs/reviews/claude-code-stage-308-code-review-prompt.md \
  docs/reviews/claude-code-stage-308-code-review.md
git commit -m "Stage 308: validate row one generated site integrity"
git push origin main
```

Then pause and report a Handoff Summary with repo status, verified commands, uncommitted files, and next step.
