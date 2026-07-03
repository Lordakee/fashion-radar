# Stage 271 ROW ONE App Content Organization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a structured app-facing content organization layer to ROW ONE so clients can render section rails, cards, and detail screens directly from `data/edition.json`.

**Architecture:** Bump `row-one-app/v1` to `row-one-app/v2` while keeping `data/edition.json` and `schemas/row-one-app.schema.json` as the stable app payload path/schema path. Derive `content_sections`, story `detail_sections`, and story `evidence_summary` from existing `RowOneEdition` and `RowOneStory` data; do not add acquisition, translation, image generation, scheduling installation, or deployment behavior.

**Tech Stack:** Python 3.11+, Typer CLI, Pydantic models, JSON Schema draft 2020-12, pytest, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/row_one/render.py`
  - Bump `ROW_ONE_APP_CONTRACT_VERSION`.
  - Add helper functions for content sections, cards, detail sections, and evidence summary.
  - Add fields to app payload and story payload.
- Modify: `schemas/row-one-app.schema.json`
  - Require `content_sections`.
  - Require `detail_sections` and `evidence_summary` on stories.
  - Add strict definitions for content sections, cards, detail sections, and evidence summary.
- Modify: `schemas/row-one-manifest.schema.json`
  - Keep `row-one-manifest/v1`, but update `app_contract.version.const` to `row-one-app/v2`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Align detail page labels with the new detail section model.
- Modify: `tests/test_row_one_app_contract.py`
  - Update contract version expectations.
  - Add grouping/card/detail/evidence summary tests.
  - Add drift rejection tests.
- Modify: `tests/test_row_one_render.py`
  - Add HTML detail organization assertions.
- Modify: `tests/test_row_one_cli.py`
  - Update active app contract version expectations found by the v1 sweep.
- Modify: `tests/test_first_run_smoke.py`
  - Update active smoke assertions that pin `row-one-app/v1`.
- Modify: `tests/test_row_one_docs.py`
  - Pin docs phrases for app content organization.
- Modify: `docs/row-one.md`, `README.md`
  - Document the richer app-facing organization layer and version bump.
- Add: `docs/reviews/opencode-stage-271-plan-review-prompt.md`
- Add after review: `docs/reviews/opencode-stage-271-plan-review.md`

## Task 1: Update App Contract Tests First

**Files:**
- Modify: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Add failing version and manifest expectations**

Change existing assertions so generated `edition.json` must contain:

```python
assert payload["contract_version"] == "row-one-app/v2"
```

and manifest `app_contract` must be:

```python
assert manifest["app_contract"] == {
    "version": "row-one-app/v2",
    "path": "data/edition.json",
    "schema_path": "schemas/row-one-app.schema.json",
}
```

- [ ] **Step 2: Add failing content section grouping test**

Add:

```python
def test_row_one_app_payload_groups_content_sections_for_clients(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    sections = payload["sections"]
    stories = payload["stories"]
    content_sections = payload["content_sections"]

    assert len(content_sections) == len(sections)
    for section, content_section in zip(sections, content_sections, strict=True):
        section_stories = [
            story for story in stories if story["section_key"] == section["key"]
        ]
        assert content_section["key"] == section["key"]
        assert content_section["title"] == section["title"]
        assert content_section["dek"] == section["dek"]
        assert content_section["href"] == section["href"]
        assert content_section["story_count"] == len(section_stories)
        assert content_section["story_ids"] == [story["id"] for story in section_stories]
        assert content_section["lead_story_id"] == (
            section_stories[0]["id"] if section_stories else None
        )
        assert [card["id"] for card in content_section["cards"]] == [
            story["id"] for story in section_stories
        ]
```

- [ ] **Step 3: Add failing card mirror test**

Add:

```python
def test_row_one_app_content_cards_mirror_story_display_fields(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    story = payload["stories"][0]
    card = payload["content_sections"][0]["cards"][0]

    assert card == {
        "id": story["id"],
        "headline": story["headline"],
        "summary": story["summary"],
        "editorial_takeaway": story["editorial_takeaway"],
        "reader_path": story["reader_path"],
        "detail_href": story["detail_href"],
        "display": story["display"],
        "source_name": story["source_name"],
        "published_date": story["published_date"],
        "tags": story["tags"],
        "evidence_count": story["evidence_count"],
    }
```

- [ ] **Step 4: Add failing detail section and evidence summary test**

Add:

```python
def test_row_one_app_stories_include_detail_sections_and_evidence_summary(
    tmp_path: Path,
) -> None:
    payload = _payload(tmp_path)
    story = payload["stories"][0]

    assert [section["key"] for section in story["detail_sections"]] == [
        "summary",
        "why_it_matters",
        "editorial_takeaway",
        "signal_context",
        "reader_path",
        "evidence",
    ]
    text_sections = {
        section["key"]: section for section in story["detail_sections"] if section["key"] != "evidence"
    }
    assert text_sections["summary"]["body"] == story["summary"]
    assert text_sections["why_it_matters"]["body"] == story["why_it_matters"]
    assert text_sections["editorial_takeaway"]["body"] == story["editorial_takeaway"]
    assert text_sections["signal_context"]["body"] == story["signal_context"]
    assert text_sections["reader_path"]["body"] == story["reader_path"]
    evidence_section = story["detail_sections"][-1]
    assert evidence_section["body"] is None
    assert evidence_section["evidence"] == story["evidence"]
    assert story["evidence_summary"] == {
        "safe_link_count": story["evidence_count"],
        "total_count": len(story["evidence"]),
        "primary_source_name": story["source_name"],
        "sources": ["Vogue Business"],
    }
```

- [ ] **Step 5: Run focused tests to verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py -q
```

Expected: failures for `row-one-app/v2`, missing `content_sections`, missing
`detail_sections`, and missing `evidence_summary`.

## Task 2: Implement Payload Builders

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`

- [ ] **Step 1: Bump the contract constant**

Change:

```python
ROW_ONE_APP_CONTRACT_VERSION = "row-one-app/v2"
```

- [ ] **Step 2: Add `content_sections` to `build_row_one_app_payload`**

The returned payload must include:

```python
"content_sections": [
    _content_section_payload(edition, section, stories)
    for section in edition.sections
],
```

where `stories` is the already-built list of canonical story payloads.

- [ ] **Step 3: Add content section helper**

Implement:

```python
def _content_section_payload(
    edition: RowOneEdition,
    section: RowOneSection,
    stories: list[dict[str, object]],
) -> dict[str, object]:
    section_stories = [story for story in stories if story["section_key"] == section.key]
    story_ids = [str(story["id"]) for story in section_stories]
    return {
        "key": section.key,
        "title": section.title.model_dump(mode="json"),
        "dek": section.dek.model_dump(mode="json"),
        "href": f"#{section.key}",
        "story_count": len(section_stories),
        "lead_story_id": story_ids[0] if story_ids else None,
        "story_ids": story_ids,
        "cards": [_content_card_payload(story) for story in section_stories],
    }
```

- [ ] **Step 4: Add content card helper**

Implement:

```python
def _content_card_payload(story: dict[str, object]) -> dict[str, object]:
    return {
        "id": story["id"],
        "headline": story["headline"],
        "summary": story["summary"],
        "editorial_takeaway": story["editorial_takeaway"],
        "reader_path": story["reader_path"],
        "detail_href": story["detail_href"],
        "display": story["display"],
        "source_name": story["source_name"],
        "published_date": story["published_date"],
        "tags": story["tags"],
        "evidence_count": story["evidence_count"],
    }
```

- [ ] **Step 5: Add story detail fields**

Inside `_story_payload`, add:

```python
"detail_sections": _detail_sections_payload(story),
"evidence_summary": _evidence_summary_payload(story),
```

- [ ] **Step 6: Add detail sections helper**

Implement deterministic localized titles:

```python
def _detail_sections_payload(story: RowOneStory) -> list[dict[str, object]]:
    return [
        {
            "key": "summary",
            "title": {"en": "Summary", "zh": "摘要"},
            "body": story.summary.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "why_it_matters",
            "title": {"en": "Why It Matters", "zh": "为什么重要"},
            "body": story.why_it_matters.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "editorial_takeaway",
            "title": {"en": "Editorial Takeaway", "zh": "编辑整理"},
            "body": story.editorial_takeaway.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "signal_context",
            "title": {"en": "Signal Context", "zh": "信号背景"},
            "body": story.signal_context.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "reader_path",
            "title": {"en": "Reader Path", "zh": "阅读路径"},
            "body": story.reader_path.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "evidence",
            "title": {"en": "Evidence Trail", "zh": "来源线索"},
            "body": None,
            "evidence": [_evidence_payload(link) for link in story.evidence],
        },
    ]
```

- [ ] **Step 7: Add evidence summary helper**

Implement:

```python
def _evidence_summary_payload(story: RowOneStory) -> dict[str, object]:
    sources: list[str] = []
    for link in story.evidence:
        if link.source_name not in sources:
            sources.append(link.source_name)
    return {
        "safe_link_count": _safe_evidence_count(story.evidence),
        "total_count": len(story.evidence),
        "primary_source_name": story.source_name,
        "sources": sources,
    }
```

- [ ] **Step 8: Run payload tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py -q
```

Expected: implementation-related tests pass except schema validation until the
schema is updated.

## Task 3: Update JSON Schema

**Files:**
- Modify: `schemas/row-one-app.schema.json`
- Modify: `schemas/row-one-manifest.schema.json`
- Modify: `tests/test_row_one_app_contract.py`
- Modify active files found by `rg -n "row-one-app/v1" src tests schemas docs README.md scripts`

- [ ] **Step 1: Bump contract const and required top-level field**

Set `contract_version.const` to `row-one-app/v2` and add
`content_sections` to the top-level `required` list and `properties`.

- [ ] **Step 1b: Update manifest schema app contract const**

In `schemas/row-one-manifest.schema.json`, keep the manifest contract itself at
`row-one-manifest/v1`, but update the nested app contract version const:

```json
"version": {
  "const": "row-one-app/v2"
}
```

- [ ] **Step 2: Add definitions**

Add strict definitions for:

- `contentSection`
- `contentCard`
- `detailSection`
- `evidenceSummary`

Use existing `$defs` for localized text, section key, detail href, display, and
evidence.

- [ ] **Step 3: Require story detail fields**

Add `detail_sections` and `evidence_summary` to story `required` and
`properties`.

- [ ] **Step 3b: Sweep active v1 references**

Run:

```bash
rg -n "row-one-app/v1" src tests schemas docs README.md scripts
```

Update active source, schema, tests, and current docs to `row-one-app/v2`.
Expected active files to check include:

- `schemas/row-one-manifest.schema.json`
- `tests/test_row_one_app_contract.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_cli.py`
- `tests/test_first_run_smoke.py`
- `tests/test_row_one_docs.py`
- `docs/row-one.md`
- `README.md`

Historical stage/review docs may keep old version strings. The existing schema
drift test that previously rejected `row-one-app/v2` must now reject
`row-one-app/v3`.

- [ ] **Step 4: Add schema drift tests**

In `tests/test_row_one_app_contract.py`, add parameterized drift cases:

```python
@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda payload: payload.__setitem__("content_sections", []), "content_sections"),
        (
            lambda payload: payload["content_sections"][0].__setitem__("extra", "x"),
            "additional properties",
        ),
        (
            lambda payload: payload["stories"][0]["detail_sections"][0].__setitem__(
                "key", "unknown"
            ),
            "not one of",
        ),
        (
            lambda payload: payload["stories"][0].__setitem__("evidence_summary", {}),
            "required",
        ),
    ],
)
def test_row_one_app_v2_schema_rejects_content_organization_drift(
    tmp_path: Path,
    mutation: object,
    message: str,
) -> None:
    payload = copy.deepcopy(_payload(tmp_path))
    mutation(payload)
    with pytest.raises(ValidationError, match=message):
        _schema_validator().validate(payload)
```

- [ ] **Step 5: Run schema tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py -q
```

Expected: all app contract tests pass.

## Task 4: Align HTML Detail Organization

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add failing render test**

Add a detail HTML assertion that checks labels:

```python
def test_row_one_detail_page_renders_organized_detail_sections(tmp_path: Path) -> None:
    edition = _edition_with_story()
    render_row_one_site(edition, tmp_path)
    detail_html = next((tmp_path / "details").glob("*.html")).read_text(encoding="utf-8")

    assert "Signal Context" in detail_html
    assert "Reader Path" in detail_html
    assert "Evidence Trail" in detail_html
    assert "编辑整理" in detail_html
```

Use the existing local helpers in `tests/test_row_one_render.py`; do not invent
new fixtures if a suitable one already exists.

- [ ] **Step 2: Update detail labels**

In `render_detail_html`, change the existing synthesis panel to expose:

- Summary
- Why It Matters
- Editorial Takeaway
- Signal Context
- Reader Path
- Evidence Trail

Keep the same story fields and escaping behavior.

- [ ] **Step 3: Run render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: render tests pass.

## Task 5: Documentation

**Files:**
- Modify: `docs/row-one.md`
- Modify: `README.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs assertions**

In `tests/test_row_one_docs.py`, assert `docs/row-one.md` contains:

- `row-one-app/v2`
- `content_sections`
- `detail_sections`
- `evidence_summary`
- `app clients can render section rails`

- [ ] **Step 2: Update docs**

Document that `edition.json` now includes `content_sections`,
`detail_sections`, and `evidence_summary`, while still being deterministic and
local.

- [ ] **Step 3: Run docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: docs tests pass.

## Task 6: Focused Gates And Review

**Files:**
- Add: `docs/reviews/opencode-stage-271-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-271-code-review.md`

- [ ] **Step 1: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py \
  tests/test_package_archives.py -q
```

- [ ] **Step 2: Run ruff**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py
```

- [ ] **Step 3: Request opencode review**

Use:

```bash
opencode run "Review Stage 271 code changes using docs/reviews/opencode-stage-271-code-review-prompt.md. Return APPROVED or NOT APPROVED." \
  --dir /home/ubuntu/fashion-radar \
  --model zhipuai-coding-plan/glm-5.2 \
  --variant max \
  --file docs/reviews/opencode-stage-271-code-review-prompt.md
```

Fix any blocking findings before final gates.

## Task 7: Full Gate, Commit, Push

- [ ] **Step 1: Run full gate**

Run with `set -e`:

```bash
tmp_env="$(mktemp -d)"
tmp_build="$tmp_env/dist"
git diff --check
UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config sync --locked --dev
UV_NO_CONFIG=1 uv --no-config sync --locked --dev --check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

- [ ] **Step 2: Commit and push**

```bash
git status --short
git add \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  schemas/row-one-app.schema.json \
  schemas/row-one-manifest.schema.json \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py \
  tests/test_row_one_docs.py \
  docs/row-one.md \
  README.md \
  docs/reviews/opencode-stage-271-plan-review-prompt.md \
  docs/reviews/opencode-stage-271-plan-review.md \
  docs/reviews/opencode-stage-271-code-review-prompt.md \
  docs/reviews/opencode-stage-271-code-review.md \
  docs/superpowers/specs/2026-07-03-stage-271-row-one-app-content-organization-design.md \
  docs/superpowers/plans/2026-07-03-stage-271-row-one-app-content-organization-plan.md
git commit -m "Stage 271: organize ROW ONE app content"
git push origin main
```

- [ ] **Step 3: Handoff Summary**

Report:

- repo status;
- commit SHA;
- verified commands;
- uncommitted files;
- next step.
