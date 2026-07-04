# Stage 287 ROW ONE Signal Synthesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic ROW ONE signal synthesis layer so app clients and the homepage can show local observed brand, product, designer, and person signals that need review, instead of only showing story links and cards.

**Architecture:** Keep the work additive inside the new `row-one-app/v6` contract by adding a required top-level `signal_synthesis` object. Derive it only from already-built ROW ONE story payloads: `entity_refs`, `product_refs`, `designer_refs`, `heat_delta`, `evidence_count`, section membership, and safe detail links. Do not add collectors, social-platform integrations, LLM calls, image generation, scoring/ranking changes, story-ID changes, scheduler/server changes, dependency changes, or compliance-review product features.

**Tech Stack:** Python 3.11+, JSON Schema draft 2020-12, static HTML/CSS/vanilla JS, pytest, ruff, uv.

---

## Product Gap Closed

This closes the report-side gap in the collect -> match -> report pipeline: collected and matched signals already exist, but ROW ONE app clients still need a compact, explicit signal surface instead of scraping HTML sections or interpreting story cards. `daily_digest.briefing_topics` already owns the canonical topic extraction and normalization, so Stage 287 derives `signal_synthesis.groups` from `briefing_topics_payload(stories)` and only reshapes those existing topics into grouped, bilingual, app-friendly brand/product/designer/person summaries with local observed/review-required boundary language. This prevents the new surface from disagreeing with shipped briefing topics while giving ROW ONE clients a stable field for daily information organization.

## Files

- Modify: `src/fashion_radar/row_one/render.py`
  - Add `_signal_synthesis_payload(stories)` and helpers.
  - Add top-level required `signal_synthesis` to `build_row_one_app_payload`.
  - Bump `ROW_ONE_APP_CONTRACT_VERSION` to `row-one-app/v6` because the root schema uses `additionalProperties: false` and this adds a new app-facing top-level field.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Add `_render_signal_synthesis(app_payload)` and insert it after `edition_brief` and before lead story / briefing topics / briefing path.
  - Add scoped `.signal-synthesis*` CSS.
  - Escape all labels/text and sanitize story hrefs through existing detail-path validation.
- Modify: `schemas/row-one-app.schema.json`
  - Add required top-level `signal_synthesis`.
  - Add `$defs.signalSynthesis`, `$defs.signalSynthesisGroup`, and `$defs.signalSynthesisSignal`.
  - Keep `additionalProperties: false` in all new objects.
- Modify: `schemas/row-one-manifest.schema.json`
  - Bump nested `app_contract.version` const to `row-one-app/v6`.
- Modify: `src/fashion_radar/cli.py`
  - Update ROW ONE status validation to expect v6 and validate required `signal_synthesis`.
- Modify: `scripts/check_first_run_smoke.py`
  - Update first-run ROW ONE validation fixtures and checks to expect v6 and required `signal_synthesis`.
- Modify: `tests/test_first_run_smoke.py`
  - Update v6 contract fixtures and add first-run signal synthesis validator tests.
- Modify: `tests/test_row_one_app_contract.py`
  - Add contract tests for populated and empty `signal_synthesis`.
  - Add drift tests for malformed nested fields and extra properties.
- Modify: `tests/test_row_one_cli.py`
  - Update v6 status fixtures and add signal synthesis drift tests.
- Modify: `tests/test_row_one_render.py`
  - Assert generated JSON includes `signal_synthesis`.
  - Assert homepage renders synthesis before story rails.
  - Assert hostile payload values are escaped and unsafe hrefs are not emitted.
- Modify: `tests/test_row_one_docs.py`
  - Add docs guard for deterministic signal synthesis.
- Modify: `docs/row-one.md`
  - Document `signal_synthesis` in App JSON Contract and Editorial Web Experience.
- Modify: `README.md`
  - Add one concise ROW ONE line explaining signal synthesis and its limits.
- Add: `docs/reviews/claude-code-stage-287-plan-review-prompt.md`
- Add after review: `docs/reviews/claude-code-stage-287-plan-review.md`
- Add fallback review if Claude Code auth remains unavailable: `docs/reviews/opencode-stage-287-plan-review.md`
- Add after implementation: `docs/reviews/claude-code-stage-287-code-review-prompt.md`
- Add after implementation: `docs/reviews/claude-code-stage-287-code-review.md`
- Add fallback code review if needed: `docs/reviews/opencode-stage-287-code-review-prompt.md`
- Add fallback code review if needed: `docs/reviews/opencode-stage-287-code-review.md`

## Proposed `signal_synthesis` Shape

```json
{
  "title": {"zh": "今日信号整理", "en": "Signal Synthesis"},
  "dek": {
    "zh": "ROW ONE 从今日 2 条故事中整理出 3 个可读信号。",
    "en": "ROW ONE organized 3 readable signals from 2 stories today."
  },
  "group_count": 3,
  "signal_count": 3,
  "boundaries": {"zh": "本地观察，需人工复核。", "en": "Local observed signals; review required."},
  "groups": [
    {
      "key": "brand",
      "label": {"zh": "品牌", "en": "Brands"},
      "signal_count": 1,
      "signals": [
        {
          "name": "The Row",
          "type": "brand",
          "label": "rising",
          "story_count": 2,
          "evidence_count": 2,
          "positive_heat_delta_sum": 6,
          "max_heat_delta": 4,
          "lead_story_id": "the-row-signal-1234567890",
          "lead_story_href": "details/the-row-signal-1234567890.html",
          "summary": {
            "zh": "The Row 出现在 2 条故事中，最高本地提及增量 +4，带有 2 条证据链接。",
            "en": "The Row appears in 2 stories, with max local mention delta +4 and 2 evidence links."
          },
          "story_ids": ["the-row-signal-1234567890", "brand-move-2222222222"]
        }
      ]
    }
  ]
}
```

## Deterministic Rules

1. Build signal candidates by calling `briefing_topics_payload(stories)` from `src/fashion_radar/row_one/briefing_topics.py`; do not reimplement entity reference normalization in Stage 287.
2. Keep the existing briefing-topic type mapping exactly:
   - `entity_refs` type `brand` or `retailer` -> `brand`.
   - `entity_refs` type `actor`, `artist`, `celebrity`, `creator`, `influencer`, `model`, `person`, or `stylist` -> `person`.
   - `entity_refs` type `designer` -> `designer`.
   - `entity_refs` type `product` -> `product`.
   - `product_refs` -> `product`.
   - `designer_refs` -> `designer`.
3. Preserve the `briefing_topics_payload` topic identity and story aggregation, including first-encounter `story_ids` order.
4. Sort groups in fixed order: `brand`, `product`, `designer`, `person`.
5. Sort signals inside each group by:
   - `positive_heat_delta_sum` descending,
   - `evidence_count` descending,
   - `story_count` descending,
   - normalized display name ascending.
6. Use the safe counts already returned by each briefing topic: `story_count`, `evidence_count`, `positive_heat_delta_sum`, `max_heat_delta`, `story_ids`, and `lead_story_id`.
7. Derive `name = topic["title"]["en"]`, preserving the first-encounter display name and case from `briefing_topics_payload`.
8. Derive `label = topic["source_refs"][0]["label"]` when present, preserving the first-encounter reference label; otherwise use an empty string.
9. Select `lead_story_id = story_ids[0]` in briefing-topic encounter order; set `lead_story_href` from the matching story's safe `detail_href`.
10. Generate `boundaries` exactly as `{"zh": "本地观察，需人工复核。", "en": "Local observed signals; review required."}` for populated and empty editions.
11. Generate summaries with deterministic local-observed wording only:
   - zh: `"{name} 出现在 {story_count} 条故事中，最高本地提及增量 +{max_heat_delta}，带有 {evidence_count} 条证据链接。"`
   - en: `"{name} appears in {story_count} stories, with max local mention delta +{max_heat_delta} and {evidence_count} evidence links."`
12. Generate populated `dek` only when `signal_count > 0`, with singular/plural-aware English:
   - zh: `"ROW ONE 从今日 {story_count} 条故事中整理出 {signal_count} 个可读信号。"`
   - en plural example: `"ROW ONE organized {signal_count} readable signals from {story_count} stories today."`
   - en singular example: `"ROW ONE organized 1 readable signal from 1 story today."`
13. Omit empty groups from the fixed group order; a brand/product/designer-only edition emits those three groups and no empty person group.
14. Any no-signal edition emits `group_count: 0`, `signal_count: 0`, `groups: []`, and empty `dek` exactly as, even when stories exist but have no explicit entity/product/designer references:
   - zh: `"暂无可整理的 ROW ONE 信号。"`
   - en: `"No ROW ONE signals are ready to organize yet."`

## Task 1: Add App Contract RED Tests

**Files:**
- Modify: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Add populated `signal_synthesis` test**

Add a test near `edition_brief` tests:

```python
def test_row_one_app_payload_includes_signal_synthesis_for_clients(tmp_path: Path) -> None:
    edition = _edition()
    first_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "heat_delta": 4,
            "entity_refs": [RowOneReference(name="The Row", type="brand", label="rising")],
            "product_refs": [RowOneReference(name="Margaux", type="product", label="bag")],
            "designer_refs": [
                RowOneReference(name="Mary-Kate Olsen", type="designer", label="designer")
            ],
        },
    )
    second_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "brand-move-2222222222",
            "section_key": "brand_moves",
            "headline": "The Row Brand Move",
            "detail_path": "details/brand-move-2222222222.html",
            "heat_delta": 2,
            "entity_refs": [RowOneReference(name="the row", type="brand", label="rising")],
            "product_refs": [],
            "designer_refs": [],
        },
    )
    edition.stories = [first_story, second_story]

    payload = _payload(tmp_path, edition)
    synthesis = payload["signal_synthesis"]

    assert synthesis["title"] == {"zh": "今日信号整理", "en": "Signal Synthesis"}
    assert synthesis["boundaries"] == {
        "zh": "本地观察，需人工复核。",
        "en": "Local observed signals; review required.",
    }
    assert synthesis["group_count"] == 3
    assert synthesis["signal_count"] == 3
    assert [group["key"] for group in synthesis["groups"]] == ["brand", "product", "designer"]
    brand = synthesis["groups"][0]["signals"][0]
    assert brand == {
        "name": "The Row",
        "type": "brand",
        "label": "rising",
        "story_count": 2,
        "evidence_count": 2,
        "positive_heat_delta_sum": 6,
        "max_heat_delta": 4,
        "lead_story_id": "the-row-signal-1234567890",
        "lead_story_href": "details/the-row-signal-1234567890.html",
        "summary": {
            "zh": "The Row 出现在 2 条故事中，最高本地提及增量 +4，带有 2 条证据链接。",
            "en": "The Row appears in 2 stories, with max local mention delta +4 and 2 evidence links.",
        },
        "story_ids": ["the-row-signal-1234567890", "brand-move-2222222222"],
    }
    _schema_validator().validate(payload)
```

- [ ] **Step 2: Add empty synthesis test**

```python
def test_row_one_app_payload_includes_empty_signal_synthesis_for_clients(tmp_path: Path) -> None:
    edition = _edition()
    edition.stories = []

    payload = _payload(tmp_path, edition)
    synthesis = payload["signal_synthesis"]

    assert synthesis["boundaries"] == {
        "zh": "本地观察，需人工复核。",
        "en": "Local observed signals; review required.",
    }
    assert synthesis["group_count"] == 0
    assert synthesis["signal_count"] == 0
    assert synthesis["groups"] == []
    assert synthesis["dek"] == {
        "zh": "暂无可整理的 ROW ONE 信号。",
        "en": "No ROW ONE signals are ready to organize yet.",
    }
    _schema_validator().validate(payload)
```

Add a non-empty/no-reference test so the empty dek is keyed by `signal_count == 0`, not `len(stories) == 0`:

```python
def test_row_one_app_payload_uses_empty_signal_synthesis_dek_when_stories_have_no_refs(
    tmp_path: Path,
) -> None:
    edition = _edition()
    edition.stories[0].entity_refs = []
    edition.stories[0].product_refs = []
    edition.stories[0].designer_refs = []

    payload = _payload(tmp_path, edition)
    synthesis = payload["signal_synthesis"]

    assert synthesis["group_count"] == 0
    assert synthesis["signal_count"] == 0
    assert synthesis["groups"] == []
    assert synthesis["dek"] == {
        "zh": "暂无可整理的 ROW ONE 信号。",
        "en": "No ROW ONE signals are ready to organize yet.",
    }
    _schema_validator().validate(payload)
```

- [ ] **Step 3: Add schema drift checks**

Add a helper near the existing contract drift helpers so group/signal drift cases do not depend on the default fixture having populated signal groups:

```python
def _contract_drift_signal_group(
    payload: dict[str, object],
    *,
    group_overrides: dict[str, object] | None = None,
    signal_overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    lead_story = payload["stories"][0]
    signal = {
        "name": "The Row",
        "type": "brand",
        "label": "rising",
        "story_count": 1,
        "evidence_count": 1,
        "positive_heat_delta_sum": 1,
        "max_heat_delta": 1,
        "lead_story_id": lead_story["id"],
        "lead_story_href": lead_story["detail_href"],
        "summary": {
            "zh": "The Row 出现在 1 条故事中，最高本地提及增量 +1，带有 1 条证据链接。",
            "en": "The Row appears in 1 stories, with max local mention delta +1 and 1 evidence links.",
        },
        "story_ids": [lead_story["id"]],
    }
    if signal_overrides:
        signal.update(signal_overrides)
    group = {
        "key": "brand",
        "label": {"zh": "品牌", "en": "Brands"},
        "signal_count": 1,
        "signals": [signal],
    }
    if group_overrides:
        group.update(group_overrides)
    return group
```

Extend the existing contract drift parametrization with self-contained mutations:

```python
(
    lambda payload: payload["signal_synthesis"].__setitem__("extra", True),
    "Additional properties",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups", [_contract_drift_signal_group(payload, group_overrides={"extra": True})]
    ),
    "Additional properties",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups", [_contract_drift_signal_group(payload, signal_overrides={"extra": True})]
    ),
    "Additional properties",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups",
        [
            _contract_drift_signal_group(
                payload, signal_overrides={"lead_story_href": "../escape.html"}
            )
        ],
    ),
    "does not match",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups", [_contract_drift_signal_group(payload, group_overrides={"key": "retailer"})]
    ),
    "is not one of",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups", [_contract_drift_signal_group(payload, signal_overrides={"type": "retailer"})]
    ),
    "is not one of",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups", [_contract_drift_signal_group(payload, signal_overrides={"story_count": 0})]
    ),
    "is less than the minimum",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups",
        [
            _contract_drift_signal_group(
                payload, signal_overrides={"positive_heat_delta_sum": -1}
            )
        ],
    ),
    "is less than the minimum",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups", [_contract_drift_signal_group(payload, signal_overrides={"lead_story_id": None})]
    ),
    "is not of type",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups",
        [_contract_drift_signal_group(payload, signal_overrides={"lead_story_id": "../escape"})],
    ),
    "does not match",
),
(
    lambda payload: payload["signal_synthesis"].__setitem__(
        "groups", [_contract_drift_signal_group(payload, signal_overrides={"story_ids": []})]
    ),
    "should be non-empty",
),
```

- [ ] **Step 4: Add mapping parity RED test**

Add a test proving `signal_synthesis` and `daily_digest.briefing_topics` reuse the same reference normalizer:

```python
def test_signal_synthesis_uses_briefing_topic_reference_mapping(tmp_path: Path) -> None:
    edition = _edition()
    edition.stories = [
        edition.stories[0].model_copy(
            deep=True,
            update={
                "entity_refs": [
                    RowOneReference(name="Dover Street Market", type="retailer", label="store"),
                    RowOneReference(name="Zendaya", type="celebrity", label="actor"),
                ],
                "product_refs": [],
                "designer_refs": [],
            },
        )
    ]

    payload = _payload(tmp_path, edition)
    topics = payload["daily_digest"]["briefing_topics"]
    synthesis_groups = payload["signal_synthesis"]["groups"]

    assert [topic["topic_type"] for topic in topics] == ["brand", "person"]
    assert [group["key"] for group in synthesis_groups] == ["brand", "person"]
    assert synthesis_groups[0]["signals"][0]["name"] == "Dover Street Market"
    assert synthesis_groups[1]["signals"][0]["name"] == "Zendaya"
    _schema_validator().validate(payload)
```

- [ ] **Step 5: Run RED app contract tests**

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_signal_synthesis_for_clients \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_empty_signal_synthesis_for_clients \
  -q
```

Expected: fail because `signal_synthesis` is missing.

## Task 2: Implement JSON Payload And Schema

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `schemas/row-one-app.schema.json`

- [ ] **Step 1: Add top-level payload field**

In `build_row_one_app_payload`, add:

```python
        "signal_synthesis": _signal_synthesis_payload(stories),
```

Place it after `edition_brief`.

- [ ] **Step 2: Add helper implementation**

Add helper functions near `_edition_brief_payload`:

```python
SIGNAL_SYNTHESIS_GROUPS = (
    ("brand", {"zh": "品牌", "en": "Brands"}),
    ("product", {"zh": "单品", "en": "Products"}),
    ("designer", {"zh": "设计师", "en": "Designers"}),
    ("person", {"zh": "人物", "en": "People"}),
)


def _signal_synthesis_payload(stories: list[dict[str, object]]) -> dict[str, object]:
    groups = _signal_synthesis_groups(stories)
    signal_count = sum(int(group["signal_count"]) for group in groups)
    return {
        "title": {"zh": "今日信号整理", "en": "Signal Synthesis"},
        "dek": _signal_synthesis_dek(len(stories), signal_count),
        "group_count": len(groups),
        "signal_count": signal_count,
        "boundaries": {
            "zh": "本地观察，需人工复核。",
            "en": "Local observed signals; review required.",
        },
        "groups": groups,
    }
```

Then implement `_signal_synthesis_groups`, `_signal_payload_from_topic`,
`_signal_summary`, `_signal_synthesis_dek`, `_signal_story_href_map`,
and `_localized_signal_group_label` using the deterministic rules above. `_signal_synthesis_groups` must consume `briefing_topics_payload(stories)` output rather than rebuilding candidates from raw story references.

- [ ] **Step 3: Add schema defs**

Add top-level required property and include it in the root `required` array:

```json
"signal_synthesis": {
  "$ref": "#/$defs/signalSynthesis"
}
```

Add defs with `additionalProperties: false`:

```json
"signalSynthesis": {
  "type": "object",
  "required": ["title", "dek", "group_count", "signal_count", "boundaries", "groups"],
  "additionalProperties": false,
  "properties": {
    "title": {"$ref": "#/$defs/localizedText"},
    "dek": {"$ref": "#/$defs/localizedText"},
    "group_count": {"type": "integer", "minimum": 0},
    "signal_count": {"type": "integer", "minimum": 0},
    "boundaries": {"$ref": "#/$defs/localizedText"},
    "groups": {
      "type": "array",
      "items": {"$ref": "#/$defs/signalSynthesisGroup"}
    }
  }
}
```

`signalSynthesisGroup` includes:

```json
{
  "type": "object",
  "required": ["key", "label", "signal_count", "signals"],
  "additionalProperties": false,
  "properties": {
    "key": {"type": "string", "enum": ["brand", "product", "designer", "person"]},
    "label": {"$ref": "#/$defs/localizedText"},
    "signal_count": {"type": "integer", "minimum": 0},
    "signals": {
      "type": "array",
      "items": {"$ref": "#/$defs/signalSynthesisSignal"}
    }
  }
}
```

`signalSynthesisSignal` includes:

```json
{
  "type": "object",
  "required": [
    "name",
    "type",
    "label",
    "story_count",
    "evidence_count",
    "positive_heat_delta_sum",
    "max_heat_delta",
    "lead_story_id",
    "lead_story_href",
    "summary",
    "story_ids"
  ],
  "additionalProperties": false,
  "properties": {
    "name": {"type": "string", "minLength": 1},
    "type": {"type": "string", "enum": ["brand", "product", "designer", "person"]},
    "label": {"type": "string"},
    "story_count": {"type": "integer", "minimum": 1},
    "evidence_count": {"type": "integer", "minimum": 0},
    "positive_heat_delta_sum": {"type": "integer", "minimum": 0},
    "max_heat_delta": {"type": "integer", "minimum": 0},
    "lead_story_id": {"$ref": "#/$defs/storyId"},
    "lead_story_href": {"$ref": "#/$defs/detailHref"},
    "summary": {"$ref": "#/$defs/localizedText"},
    "story_ids": {
      "type": "array",
      "minItems": 1,
      "items": {"$ref": "#/$defs/storyId"}
    }
  }
}
```

- [ ] **Step 4: Run GREEN app contract tests**

```bash
UV_NO_CONFIG=1 uv --no-config run pytest tests/test_row_one_app_contract.py -q
```

Expected: pass.

## Task 3: Render Homepage Signal Synthesis

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add RED render tests**

Add tests:

```python
def test_render_row_one_site_includes_signal_synthesis_section(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].entity_refs = [
        RowOneReference(name="The Row", type="brand", label="rising")
    ]

    render_row_one_site(edition, tmp_path)
    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="signal-synthesis"' in index_html
    assert "Signal Synthesis" in index_html
    assert index_html.index('class="edition-brief"') < index_html.index(
        'class="signal-synthesis"'
    )
    assert index_html.index('class="signal-synthesis"') < index_html.index(
        'class="lead-story"'
    )
```

Add a hostile payload test using `render_index_html` with a custom `app_payload` where signal names/labels contain markup and `lead_story_href` is unsafe:

```python
def test_render_row_one_site_escapes_signal_synthesis_payload(tmp_path) -> None:
    html = render_index_html(_edition(), app_payload={"signal_synthesis": {
        "title": {"zh": "<script>标题</script>", "en": "<b>Signal</b>"},
        "dek": {"zh": "本地 <b>观察</b>", "en": "Local <b>observed</b>"},
        "boundaries": {"zh": "本地观察，需人工复核。", "en": "Local observed signals; review required."},
        "group_count": 1,
        "signal_count": 1,
        "groups": [
            {
                "key": "brand",
                "label": {"zh": "<b>品牌</b>", "en": "<b>Brands</b>"},
                "signal_count": 1,
                "signals": [
                    {
                        "name": "<img src=x onerror=alert(1)>",
                        "type": "brand",
                        "label": "<script>alert(1)</script>",
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 1,
                        "max_heat_delta": 1,
                        "lead_story_id": "the-row-signal-1234567890",
                        "lead_story_href": "../escape.html",
                        "summary": {
                            "zh": "<b>危险</b>",
                            "en": "<b>Unsafe</b>",
                        },
                        "story_ids": ["the-row-signal-1234567890"],
                    }
                ],
            }
        ],
    }})

    assert "<script>" not in html
    assert "<img src=x" not in html
    assert "&lt;b&gt;Signal&lt;/b&gt;" in html
    assert "../escape.html" not in html
```

- [ ] **Step 2: Implement `_render_signal_synthesis`**

In `render_index_html`, compute:

```python
    signal_synthesis = _render_signal_synthesis(app_payload)
```

Insert it after `{edition_brief}`.

The renderer should:
1. Return `""` if payload missing or has zero groups.
2. Render group cards with bilingual group labels.
3. Render up to three signals per group.
4. Link only safe detail hrefs.
5. Escape all text with `_esc`.

- [ ] **Step 3: Add CSS**

Add scoped selectors:

```css
.signal-synthesis { ... }
.signal-synthesis-header { ... }
.signal-synthesis-grid { ... }
.signal-synthesis-group { ... }
.signal-synthesis-card { ... }
```

Use existing ROW ONE typography, borders, `--panel`, `--line`, `--ink`, and `--accent`.

- [ ] **Step 4: Run render tests**

```bash
UV_NO_CONFIG=1 uv --no-config run pytest tests/test_row_one_render.py -q
```

Expected: pass.

## Task 4: Docs And Status Validation

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_row_one_cli.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `docs/row-one.md`
- Modify: `README.md`

- [ ] **Step 1: Add status/smoke validators**

Add required v6 validation for `signal_synthesis`:
1. `group_count == len(groups)`.
2. `signal_count == sum(group.signal_count)`.
3. Each group `signal_count == len(signals)`.
4. Each signal `lead_story_id` exists in `stories`.
5. Each signal `lead_story_href` matches that story's `detail_href`.

Require `signal_synthesis` for `row-one-app/v6`, because the new root field is a contract-versioned app surface.

- [ ] **Step 2: Add status/smoke tests**

Add negative drift cases for incorrect `signal_count` and unknown `lead_story_id`.

- [ ] **Step 3: Add docs guards**

Document that `signal_synthesis`:
1. Organizes brands/products/designers/people from explicit existing story references.
2. Uses local heat delta and safe evidence counts.
3. Does not add collection, ranking, scoring, market-demand claims, source-scope verification, or external enrichment.

Add a docs guard that extracts the `signal_synthesis` section from `docs/row-one.md` and asserts:

```python
section = _markdown_section(docs, "signal_synthesis").lower()
assert "local observed" in section
assert "review required" in section
for forbidden in ("demand proof", "verified coverage", "platform heat", "globally trending"):
    assert forbidden not in section
```

- [ ] **Step 4: Replace every `row-one-app/v5` literal with `row-one-app/v6`**

Update all remaining app-contract literals in:

```text
src/fashion_radar/row_one/render.py
src/fashion_radar/cli.py
schemas/row-one-app.schema.json
schemas/row-one-manifest.schema.json
scripts/check_first_run_smoke.py
tests/test_row_one_render.py
tests/test_first_run_smoke.py
tests/test_row_one_app_contract.py
tests/test_row_one_cli.py
tests/test_row_one_docs.py
README.md
docs/row-one.md
```

- [ ] **Step 5: Run docs/status/smoke tests**

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_docs.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py \
  -q
```

Expected: pass.

## Task 5: Verification And Review Gate

**Files:**
- Add: `docs/reviews/claude-code-stage-287-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-287-code-review.md`
- Add fallback if needed: `docs/reviews/opencode-stage-287-code-review-prompt.md`
- Add fallback if needed: `docs/reviews/opencode-stage-287-code-review.md`

- [ ] **Step 1: Run full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run ruff check .
UV_NO_CONFIG=1 uv --no-config run ruff format --check .
UV_NO_CONFIG=1 uv --no-config run pytest -q
UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run python scripts/check_release_hygiene.py --repo-root .
git diff --check
git diff --exit-code -- uv.lock pyproject.toml
```

- [ ] **Step 2: Attempt Claude Code code review**

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-287-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-287-code-review.md
rm -f "$tmp_review"
```

If Claude Code still returns `401 API key is disabled`, record that in the Claude review artifact and use opencode fallback:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-287-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-287-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 3: Fix Critical and Important findings**

Run targeted tests after each fix, then rerun full verification.

- [ ] **Step 4: Commit and push**

```bash
git status --short
git add README.md docs/row-one.md docs/reviews/claude-code-stage-287-* docs/reviews/opencode-stage-287-* docs/superpowers/plans/2026-07-04-stage-287-row-one-signal-synthesis-plan.md schemas/row-one-app.schema.json scripts/check_first_run_smoke.py src/fashion_radar/cli.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_first_run_smoke.py tests/test_row_one_app_contract.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_render.py
git commit -m "Stage 287: add row one signal synthesis"
git push origin main
```

## Out Of Scope

- No v5 root-field addition; Stage 287 uses `row-one-app/v6` for the new top-level app surface.

- No Instagram/TikTok/X/Xiaohongshu collection.
- No social login, cookies, browser automation, proxy, CAPTCHA, or external APIs.
- No LLM summarization or image generation.
- No compliance-review product features.
- No schedule/server/deployment changes.
- No changes to heat scoring, matching, sorting, ranking, story IDs, source liveness, or source coverage claims.

## Self-Review

- Spec coverage: covers deterministic information synthesis for brands/products/designers/people using existing ROW ONE story data.
- Placeholder scan: no TODO/TBD placeholders; helper bodies are specified by deterministic rules and concrete test expectations rather than copied in full.
- Type consistency: `signal_synthesis`, `signalSynthesis`, `signalSynthesisGroup`, and `signalSynthesisSignal` names are consistent.
- Scope check: one additive report/presentation node; no source collection or external integrations.
