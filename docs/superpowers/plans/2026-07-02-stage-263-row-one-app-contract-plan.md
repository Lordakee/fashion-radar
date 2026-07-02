# Stage 263 ROW ONE App Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a stable `row-one-app/v1` JSON contract for ROW ONE app clients.

**Architecture:** Keep `RowOneEdition` as the internal presentation model and add a deterministic payload builder for `data/edition.json`. The builder derives client-ready fields from existing edition/section/story data and validates against a committed JSON Schema, without changing HTML rendering, collection, matching, ranking, cleanup, server, or schedule behavior.

**Tech Stack:** Python 3.11+, existing Pydantic ROW ONE models, stdlib JSON output, explicit `jsonschema` dev/test dependency with format checking plus regex fallbacks for date/date-time fields, pytest, Ruff, Claude Code/opencode review gates.

---

## Stage Boundary

Stage 263 closes the ROW ONE app-consumption gap in the `collect -> match -> report -> ROW ONE` path. Stage 260 created the local static site, Stage 261 added deterministic editorial synthesis, and Stage 262 added reader orientation in HTML. Stage 263 makes the generated JSON a versioned public contract for the user's app.

This stage does not add source acquisition, scraping, browser automation, platform APIs, account/session behavior, translation, LLM calls, image generation, paid APIs, deployment, remote hosting, demand proof, platform coverage verification, or compliance-review product work.

## Files And Artifacts

- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_row_one_cli.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `docs/row-one.md`
- Modify: `docs/architecture.md`
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`
- Create: `schemas/row-one-app.schema.json`
- Create: `tests/test_row_one_app_contract.py`
- Create: `docs/superpowers/specs/2026-07-02-stage-263-row-one-app-contract-design.md`
- Create: `docs/superpowers/plans/2026-07-02-stage-263-row-one-app-contract-plan.md`
- Create: `docs/reviews/claude-code-stage-263-plan-review-prompt.md`
- Create after review: `docs/reviews/claude-code-stage-263-plan-review.md`
- Create: `docs/reviews/opencode-stage-263-plan-review-prompt.md`
- Create after review: `docs/reviews/opencode-stage-263-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-263-code-review-prompt.md`
- Create after implementation if Claude completes: `docs/reviews/claude-code-stage-263-code-review.md`
- Create if fallback needed: `docs/reviews/opencode-stage-263-code-review-prompt.md`
- Create if fallback needed: `docs/reviews/opencode-stage-263-code-review.md`
- Create before push: `docs/reviews/claude-code-stage-263-release-review-prompt.md`
- Create before push if Claude completes: `docs/reviews/claude-code-stage-263-release-review.md`
- Create if fallback needed: `docs/reviews/opencode-stage-263-release-review-prompt.md`
- Create if fallback needed: `docs/reviews/opencode-stage-263-release-review.md`

## Task 1: Add App Contract Payload Tests

**Files:**
- Modify: `tests/test_row_one_render.py`
- Create: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Add failing render assertions for the app payload**

In `tests/test_row_one_render.py`, update `test_render_row_one_site_writes_json_payload` so it expects the new app contract:

```python
assert payload["contract_version"] == "row-one-app/v1"
assert payload["brand"] == "ROW ONE"
assert payload["generated_at"] == "2026-07-02T04:00:00Z"
assert payload["edition_date"] == "2026-07-02T04:00:00Z"
assert payload["summary"]["zh"] == "ROW ONE 今日整理了 1 条本地时尚信号。"

sections = {section["key"]: section for section in payload["sections"]}
assert sections["top_stories"]["href"] == "#top_stories"
assert sections["top_stories"]["story_count"] == 1
assert sections["brand_moves"]["href"] == "#brand_moves"
assert sections["brand_moves"]["story_count"] == 0

story = payload["stories"][0]
assert story["id"] == "the-row-signal-1234567890"
assert story["section_key"] == "top_stories"
assert story["section"] == {
    "key": "top_stories",
    "title": {"zh": "今日重点", "en": "Top Stories"},
    "href": "#top_stories",
}
assert story["detail_path"] == "details/the-row-signal-1234567890.html"
assert story["detail_href"] == "details/the-row-signal-1234567890.html"
assert story["published_at"] == "2026-07-02T04:00:00Z"
assert story["published_date"] == "2026-07-02"
assert story["evidence_count"] == 1
assert story["source_url"] == "https://example.com/the-row"
assert story["evidence"][0]["url"] == "https://example.com/evidence"
assert story["evidence"][1]["url"] is None
```

- [ ] **Step 2: Add failing source URL sanitization assertion**

Update `test_render_row_one_site_sanitizes_json_source_url` so it also confirms the contract remains app-facing:

```python
assert payload["contract_version"] == "row-one-app/v1"
assert payload["stories"][0]["source_url"] is None
```

- [ ] **Step 3: Add schema validation test**

Create `tests/test_row_one_app_contract.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from fashion_radar.row_one.render import render_row_one_site
from tests.test_row_one_render import _edition

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "row-one-app.schema.json"


def test_row_one_app_contract_schema_validates_generated_payload(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
```

- [ ] **Step 4: Run failing tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_json_payload tests/test_row_one_render.py::test_render_row_one_site_sanitizes_json_source_url tests/test_row_one_app_contract.py -q
```

Expected: FAIL because `contract_version`, app-derived fields, and schema do not exist.

## Task 2: Build The App Payload

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`

- [ ] **Step 1: Add contract constant and replace raw dump writer**

In `render.py`, add:

```python
ROW_ONE_APP_CONTRACT_VERSION = "row-one-app/v1"
```

Then change the `edition.json` write call to:

```python
json.dumps(build_row_one_app_payload(edition), ensure_ascii=False, indent=2) + "\n"
```

- [ ] **Step 2: Add payload builder**

Replace `_sanitized_edition_payload()` with:

```python
def build_row_one_app_payload(edition: RowOneEdition) -> dict[str, object]:
    return {
        "contract_version": ROW_ONE_APP_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": _isoformat_z(edition.generated_at),
        "edition_date": _isoformat_z(edition.edition_date),
        "summary": edition.summary.model_dump(mode="json"),
        "sections": [_section_payload(edition, section) for section in edition.sections],
        "stories": [_story_payload(edition, story) for story in edition.stories],
    }
```

- [ ] **Step 3: Add section/story helpers**

Add these helpers below `build_row_one_app_payload()`:

```python
def _section_payload(edition: RowOneEdition, section) -> dict[str, object]:
    return {
        "key": section.key,
        "title": section.title.model_dump(mode="json"),
        "dek": section.dek.model_dump(mode="json"),
        "href": f"#{section.key}",
        "story_count": len(edition.section_stories(section.key)),
    }


def _story_payload(edition: RowOneEdition, story) -> dict[str, object]:
    section = _section_for_story(edition, story.section_key)
    published_at = _isoformat_z(story.published_at) if story.published_at else None
    return {
        "id": story.id,
        "section_key": story.section_key,
        "section": {
            "key": section.key,
            "title": section.title.model_dump(mode="json"),
            "href": f"#{section.key}",
        },
        "headline": story.headline,
        "summary": story.summary.model_dump(mode="json"),
        "why_it_matters": story.why_it_matters.model_dump(mode="json"),
        "editorial_takeaway": story.editorial_takeaway.model_dump(mode="json"),
        "signal_context": story.signal_context.model_dump(mode="json"),
        "reader_path": story.reader_path.model_dump(mode="json"),
        "source_name": story.source_name,
        "source_url": _safe_external_url(story.source_url),
        "published_at": published_at,
        "published_date": story.published_at.date().isoformat() if story.published_at else None,
        "detail_path": story.detail_path,
        "detail_href": _app_detail_href(story.detail_path),
        "tags": list(story.tags),
        "evidence_count": sum(
            1 for link in story.evidence if _safe_external_url(link.url) is not None
        ),
        "evidence": [_evidence_payload(link) for link in story.evidence],
    }
```

- [ ] **Step 4: Add validation/detail helpers**

Add:

```python
def _section_for_story(edition: RowOneEdition, section_key):
    for section in edition.sections:
        if section.key == section_key:
            return section
    raise ValueError(f"ROW ONE story references missing section: {section_key}")


def _evidence_payload(link) -> dict[str, object]:
    return {
        "title": link.title,
        "url": _safe_external_url(link.url),
        "source_name": link.source_name,
    }


def _app_detail_href(detail_path: str) -> str | None:
    pure_path = _validated_detail_relative_path(detail_path)
    return str(pure_path) if pure_path is not None else None


def _isoformat_z(value) -> str:
    return value.isoformat().replace("+00:00", "Z")
```

Use precise imports/types as Ruff requires; do not broaden model behavior.

- [ ] **Step 5: Run app payload tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_json_payload tests/test_row_one_render.py::test_render_row_one_site_sanitizes_json_source_url -q
```

Expected: PASS.

## Task 3: Add JSON Schema

**Files:**
- Create: `schemas/row-one-app.schema.json`
- Modify: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Create schema file**

Create `schemas/row-one-app.schema.json` with a Draft 2020-12 object schema requiring:

- `contract_version`, `brand`, `generated_at`, `edition_date`, `summary`, `sections`, `stories`
- localized text objects with required `zh` and `en`
- section objects with `key`, `title`, `dek`, `href`, `story_count`
- story objects with all app-facing fields described in the design
- evidence objects with `title`, nullable `url`, and `source_name`
- `additionalProperties: false` for top-level, localized text, section, story section reference, story, and evidence objects

- [ ] **Step 2: Run schema validation test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_app_contract.py -q
```

Expected: PASS.

## Task 4: Update CLI Smoke And Docs

**Files:**
- Modify: `tests/test_row_one_cli.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add CLI smoke assertions**

In `test_row_one_build_command_writes_non_ascii_story_detail_path`, after loading `payload`, add:

```python
assert payload["contract_version"] == "row-one-app/v1"
assert payload["stories"][0]["detail_href"].startswith("details/")
```

- [ ] **Step 2: Add docs drift test**

In `tests/test_row_one_docs.py`, add:

```python
def test_row_one_docs_describe_app_json_contract() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "row-one-app/v1",
        "app-facing json contract",
        "schemas/row-one-app.schema.json",
        "section story counts",
        "detail hrefs",
        "sanitized url fields",
        "does not change html rendering",
    ):
        assert phrase in normalized
```

- [ ] **Step 3: Update docs**

Add after `## Reader Orientation` and before `## Generated Files`:

```markdown
## App JSON Contract

`data/edition.json` is the app-facing JSON contract for ROW ONE. Stage 263
uses `row-one-app/v1` and validates the payload with
`schemas/row-one-app.schema.json`. The contract includes section story counts,
section anchors, story detail hrefs, published dates, safe evidence-link counts,
and sanitized URL fields so an app can render the daily edition without scraping
HTML.

This contract does not change HTML rendering, ranking, story IDs, source
collection, cleanup behavior, server behavior, scheduling, deployment, LLM use,
translation, demand proof, or platform coverage verification.
```

- [ ] **Step 4: Run docs and CLI tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_build_command_writes_non_ascii_story_detail_path tests/test_row_one_docs.py::test_row_one_docs_describe_app_json_contract -q
```

Expected: PASS.

## Task 5: Focused Verification And Reviews

**Files:**
- Create review prompts and review outputs under `docs/reviews/` as needed

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen ruff format src/fashion_radar/row_one/render.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_app_contract.py
uv --no-config run --frozen pytest tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_app_contract.py -q
uv --no-config run --frozen ruff check src/fashion_radar/row_one src/fashion_radar/cli.py tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_app_contract.py
```

Expected: PASS.

- [ ] **Step 2: Request code review**

Create `docs/reviews/claude-code-stage-263-code-review-prompt.md`, then run Claude primary code review. If Claude times out, create and run `docs/reviews/opencode-stage-263-code-review-prompt.md` using GLM 5.2 max. Fix all Critical and Important findings.

## Task 6: Full Verification, Release Review, Commit, And Push

**Files:**
- Create final code/release review artifacts under `docs/reviews/`

- [ ] **Step 1: Run full release gate**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
git diff --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest -q
rm -rf dist build
uv --no-config build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen python scripts/check_first_run_smoke.py
rm -rf dist build
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git status --short --branch --untracked-files=all
```

Expected: PASS.

- [ ] **Step 2: Request release review**

Create `docs/reviews/claude-code-stage-263-release-review-prompt.md`, then run Claude primary release review. If Claude times out, create and run `docs/reviews/opencode-stage-263-release-review-prompt.md` using GLM 5.2 max. Fix all Critical and Important findings.

- [ ] **Step 3: Commit and push**

Run:

```bash
git add docs/row-one.md docs/reviews/claude-code-stage-263-*.md docs/reviews/opencode-stage-263-*.md docs/superpowers/plans/2026-07-02-stage-263-row-one-app-contract-plan.md docs/superpowers/specs/2026-07-02-stage-263-row-one-app-contract-design.md schemas/row-one-app.schema.json src/fashion_radar/row_one/render.py tests/test_row_one_app_contract.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_render.py
git commit -m "Stage 263: add ROW ONE app contract"
git push origin main
git status --short --branch --untracked-files=all
git log -1 --oneline
```

Expected: commit and push succeed, status is clean.

- [ ] **Step 4: Handoff Summary**

After push, report:

- repo status;
- latest commit;
- changed capability;
- verified commands and results;
- review artifacts;
- uncommitted files;
- known deferred minors;
- next step.
