# Stage 320 ROW ONE Homepage Daily Edit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only `Daily Edit / 今日编辑简报` section to the ROW ONE homepage that organizes existing payload and sidecar information into a scan-first editorial briefing surface.

**Architecture:** Keep the feature deterministic and local to generated HTML. Build a private homepage-only view model from existing `app_payload` objects inside `templates.py`, render it immediately, and do not serialize it into `data/edition.json` or any new JSON artifact. Reuse existing localization, escaping, and route-safety helpers.

**Tech Stack:** Python, string-rendered HTML/CSS, existing ROW ONE Pydantic payloads and dictionaries, pytest, Ruff, Claude Code plan/code review workflow.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Create: `docs/reviews/claude-code-stage-320-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-320-plan-review.md`
- Later implementation review artifacts:
  - `docs/reviews/claude-code-stage-320-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-320-code-review.md`

---

## Task 1: Homepage Daily Edit Render Tests

**Files:**

- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add the primary failing homepage render test**

Add near existing homepage overview tests:

```python
def test_render_row_one_site_includes_daily_edit_section(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_start = index_html.index('class="daily-edit"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert '<span data-lang="en">Daily Edit</span>' in section_html
    assert '<span data-lang="zh">今日编辑简报</span>' in section_html
    assert '<span data-lang="en">What To Know</span>' in section_html
    assert '<span data-lang="zh">今日重点</span>' in section_html
    assert '<span data-lang="en">Signals To Watch</span>' in section_html
    assert '<span data-lang="zh">值得关注</span>' in section_html
    assert '<span data-lang="en">Read Next</span>' in section_html
    assert '<span data-lang="zh">阅读路径</span>' in section_html
    assert '<span data-lang="en">Evidence Note</span>' in section_html
    assert '<span data-lang="zh">线索边界</span>' in section_html
    assert "The Row" in section_html
    assert "evidence" in section_html
    assert "review the underlying stories before acting" in section_html
    assert 'href="details/the-row-signal-1234567890.html"' in section_html
    assert index_html.index('class="edition-brief"') < section_start
    assert index_html.index('class="signal-synthesis"') < section_start
    assert section_start < index_html.index('class="daily-local-intelligence"')
    assert section_start < index_html.index('class="lead-story"')
```

- [ ] **Step 2: Add omission behavior test**

Add:

```python
def test_render_row_one_site_omits_daily_edit_without_usable_payload() -> None:
    index_html = render_index_html(_edition(), app_payload={})
    index_html_none = render_index_html(_edition(), app_payload=None)

    assert 'class="daily-edit"' not in index_html
    assert "Daily Edit" not in index_html
    assert "今日编辑简报" not in index_html
    assert 'class="daily-edit"' not in index_html_none
    assert "Daily Edit" not in index_html_none
    assert "今日编辑简报" not in index_html_none
```

- [ ] **Step 3: Add escaping and unsafe link test**

Add:

```python
def test_render_row_one_site_escapes_daily_edit_payload_values() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {
                "title": {"en": "Brief", "zh": "总览"},
                "dek": {"en": "Dek", "zh": "说明"},
                "lead_story_headline": 'Lead <script>alert(1)</script>',
                "lead_story_href": "javascript:alert(1)",
                "summary_points": [
                    {"en": "Point <b>bold</b>", "zh": "要点 <b>粗体</b>"},
                ],
                "metrics": [
                    {"key": "evidence", "label": {"en": "Evidence", "zh": "证据"}, "value": 1},
                ],
                "links": [],
            },
            "signal_synthesis": {
                "title": {"en": "Signals", "zh": "信号"},
                "dek": {"en": "Dek", "zh": "说明"},
                "boundaries": {"en": "Boundary <i>", "zh": "边界 <i>"},
                "groups": [
                    {
                        "label": {"en": "Brands", "zh": "品牌"},
                        "signals": [
                            {
                                "name": "Signal <script>",
                                "summary": {"en": "Summary <b>", "zh": "摘要 <b>"},
                                "lead_story_href": "https://evil.example/story",
                                "story_count": 1,
                                "evidence_count": 2,
                                "max_heat_delta": 3,
                                "label": "brand",
                            }
                        ],
                    }
                ],
            },
            "daily_digest": {"blocks": [], "briefing_topics": []},
        },
    )

    section_start = index_html.index('class="daily-edit"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "Lead &lt;script&gt;alert(1)&lt;/script&gt;" in section_html
    assert "Point &lt;b&gt;bold&lt;/b&gt;" in section_html
    assert "Signal &lt;script&gt;" in section_html
    assert "Summary &lt;b&gt;" in section_html
    assert "Boundary &lt;i&gt;" in section_html
    assert "<script>" not in section_html
    assert "<b>" not in section_html
    assert "javascript:alert" not in section_html
    assert "https://evil.example" not in section_html
    assert 'href="#main-content"' in section_html
```

- [ ] **Step 4: Add fallback path tests**

Add:

```python
def test_render_row_one_site_daily_edit_uses_briefing_topic_fallback() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {"summary_points": [], "metrics": [], "links": []},
            "signal_synthesis": {
                "title": {"en": "Signals", "zh": "信号"},
                "dek": {"en": "No signals", "zh": "暂无信号"},
                "boundaries": {"en": "Existing evidence only.", "zh": "仅限现有证据。"},
                "groups": [{"label": {"en": "Brands", "zh": "品牌"}, "signals": [{"name": ""}]}],
            },
            "daily_digest": {
                "evidence_count": 2,
                "blocks": [],
                "briefing_topics": [
                    {
                        "topic_type": "brand",
                        "title": {"en": "Fallback Brand", "zh": "备用品牌"},
                        "label": {"en": "Brand", "zh": "品牌"},
                        "story_count": 1,
                        "evidence_count": 2,
                        "positive_heat_delta_sum": 4,
                        "lead_story": {
                            "detail_href": "details/fallback-brand-1234567890.html",
                            "headline": {"en": "Fallback brand signal", "zh": "备用品牌信号"},
                            "editorial_takeaway": {
                                "en": "Topic fallback summary.",
                                "zh": "主题备用摘要。",
                            },
                        },
                    }
                ],
            },
        },
    )

    section_start = index_html.index('class="daily-edit"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "Fallback Brand" in section_html
    assert "备用品牌" in section_html
    assert "Topic fallback summary." in section_html
    assert 'href="details/fallback-brand-1234567890.html"' in section_html


def test_render_row_one_site_daily_edit_uses_digest_block_read_next() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {"summary_points": [], "metrics": [], "links": []},
            "signal_synthesis": {
                "title": {"en": "Signals", "zh": "信号"},
                "dek": {"en": "Signals dek", "zh": "信号说明"},
                "boundaries": {"en": "Existing evidence only.", "zh": "仅限现有证据。"},
                "groups": [],
            },
            "daily_digest": {
                "evidence_count": 1,
                "briefing_topics": [],
                "blocks": [
                    {
                        "key": "read_first",
                        "story_ids": ["read-first-1234567890"],
                        "cards": [{"id": "read-first-1234567890"}],
                    },
                    {
                        "key": "key_takeaways",
                        "cards": [
                            {
                                "id": "read-next-1234567890",
                                "detail_href": "details/read-next-1234567890.html",
                                "headline": {"en": "Read next headline", "zh": "继续阅读标题"},
                                "editorial_takeaway": {
                                    "en": "Read next summary.",
                                    "zh": "继续阅读摘要。",
                                },
                            }
                        ],
                    },
                ],
            },
        },
    )

    section_start = index_html.index('class="daily-edit"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "Read next headline" in section_html
    assert "继续阅读标题" in section_html
    assert "Read next summary." in section_html
    assert 'href="details/read-next-1234567890.html"' in section_html
```

- [ ] **Step 5: Add CSS selector failing test**

Extend the existing CSS selector tests or add:

```python
def test_row_one_css_includes_daily_edit_styles(tmp_path) -> None:
    index_path = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (index_path.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".daily-edit",
        ".daily-edit-header",
        ".daily-edit-grid",
        ".daily-edit-card",
        ".daily-edit-card-meta",
        ".daily-edit-link",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)

    assert "@media (max-width: 760px)" in css_text
    assert re.search(r"\.daily-edit-grid\s*\{[^}]*grid-template-columns:\s*1fr", css_text)
```

- [ ] **Step 6: Run render tests and verify they fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_daily_edit_section \
  tests/test_row_one_render.py::test_render_row_one_site_omits_daily_edit_without_usable_payload \
  tests/test_row_one_render.py::test_render_row_one_site_escapes_daily_edit_payload_values \
  tests/test_row_one_render.py::test_render_row_one_site_daily_edit_uses_briefing_topic_fallback \
  tests/test_row_one_render.py::test_render_row_one_site_daily_edit_uses_digest_block_read_next \
  tests/test_row_one_render.py::test_row_one_css_includes_daily_edit_styles -q
```

Expected: failures because `daily-edit` rendering and CSS do not exist yet.

---

## Task 2: Daily Edit Homepage Implementation

**Files:**

- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Wire the section into `render_index_html()`**

Add after `signal_synthesis = _render_signal_synthesis(app_payload)`:

```python
daily_edit = _render_daily_edit(app_payload)
```

Insert `{daily_edit}` after `{signal_synthesis}` and before
`{daily_local_intelligence}`.

- [ ] **Step 2: Add private helper constants**

Near other homepage/detail constants:

```python
DAILY_EDIT_MAX_CARDS = 4
DAILY_EDIT_MAX_SIGNALS = 3
DAILY_EDIT_MAX_PATH_ITEMS = 3
```

- [ ] **Step 3: Add section renderer**

Add helpers near `_render_signal_synthesis()` and `_render_briefing_topics()`:

```python
def _render_daily_edit(app_payload: dict[str, object] | None) -> str:
    cards = _daily_edit_cards(app_payload)
    if not cards:
        return ""
    rendered_cards = "\n".join(_render_daily_edit_card(card) for card in cards)
    return f"""<section class="daily-edit" aria-label="Daily edit">
  <div class="daily-edit-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Edit</span>
        <span data-lang="zh">今日编辑简报</span>
      </p>
      <h2>
        <span data-lang="en">What matters today</span>
        <span data-lang="zh">今天值得先看什么</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">A scan-first edit from existing ROW ONE signals.</span>
      <span data-lang="zh">基于现有 ROW ONE 信号整理的快速编辑简报。</span>
    </p>
  </div>
  <div class="daily-edit-grid">
{rendered_cards}
  </div>
</section>"""
```

- [ ] **Step 4: Add card builders**

Implement:

```python
def _daily_edit_cards(app_payload: dict[str, object] | None) -> list[dict[str, object]]:
    if app_payload is None:
        return []
    cards = [
        _daily_edit_what_to_know(app_payload),
        _daily_edit_signals_to_watch(app_payload),
        _daily_edit_read_next(app_payload),
        _daily_edit_evidence_note(app_payload),
    ]
    return [card for card in cards if card is not None][:DAILY_EDIT_MAX_CARDS]
```

Each card returns:

```python
{
    "title": LocalizedText(en="...", zh="..."),
    "body": LocalizedText(en="...", zh="..."),
    "meta": list[LocalizedText],
    "href": str | None,
}
```

- [ ] **Step 5: Implement `What To Know` card**

Read from `edition_brief.summary_points[0]`, falling back to
`edition_brief.lead_story_headline`. Use `_safe_daily_edit_href()` on
`edition_brief.lead_story_href`.

Title: `LocalizedText(en="What To Know", zh="今日重点")`.

- [ ] **Step 6: Implement `Signals To Watch` card**

Read the first usable `signal_synthesis.groups[].signals[]` with a non-empty
`name`. Body should use its localized `summary`. Meta should include story
count, evidence count, and positive heat delta when present. Link should use
`_safe_daily_edit_href(signal.get("lead_story_href"))`.

If no usable signal synthesis exists, fall back to first
`daily_digest.briefing_topics[]` topic with a usable `lead_story.detail_href`.

Title: `LocalizedText(en="Signals To Watch", zh="值得关注")`.

- [ ] **Step 7: Implement `Read Next` card**

Read `daily_digest.blocks` for `key_takeaways` then `signals_to_watch`. Pick
the first usable card not in the read-first block. Body should use the card
headline or editorial takeaway. Link should use `_safe_daily_edit_href()`.

Title: `LocalizedText(en="Read Next", zh="阅读路径")`.

- [ ] **Step 8: Implement `Evidence Note` card**

Read existing evidence counts from `edition_brief.metrics` or
`daily_digest.evidence_count`, and boundaries from `signal_synthesis.boundaries`.
Render bounded language such as "Based on existing ROW ONE evidence links; review
the underlying stories before acting." Do not claim trend certainty.

Title: `LocalizedText(en="Evidence Note", zh="线索边界")`.

- [ ] **Step 9: Add safe link and render helpers**

Add:

```python
def _safe_daily_edit_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href in {"#main-content", "#briefing-topics", "#briefing-path"}:
        return href
    if _validated_detail_relative_path(href) is not None:
        return href
    return None
```

Add `_render_daily_edit_card(card)` that escapes title, body, meta, and href.
Invalid/missing href renders `href="#main-content"`.

For optional in-page anchors such as `#briefing-topics` and `#briefing-path`,
callers should only pass them when the corresponding section exists.

- [ ] **Step 10: Add CSS**

Add `.daily-edit`, `.daily-edit-header`, `.daily-edit-grid`,
`.daily-edit-card`, `.daily-edit-card-meta`, and `.daily-edit-link` styles near
other homepage briefing sections. Add mobile collapse:

```css
.daily-edit-grid { grid-template-columns: 1fr; }
```

inside the existing `@media (max-width: 760px)` block.

- [ ] **Step 11: Run focused render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_daily_edit_section \
  tests/test_row_one_render.py::test_render_row_one_site_omits_daily_edit_without_usable_payload \
  tests/test_row_one_render.py::test_render_row_one_site_escapes_daily_edit_payload_values \
  tests/test_row_one_render.py::test_render_row_one_site_daily_edit_uses_briefing_topic_fallback \
  tests/test_row_one_render.py::test_render_row_one_site_daily_edit_uses_digest_block_read_next \
  tests/test_row_one_render.py::test_row_one_css_includes_daily_edit_styles -q
```

Expected: all pass.

---

## Task 3: Workflow And Docs Boundaries

**Files:**

- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Extend workflow boundary test**

In `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`,
add HTML assertions:

```python
assert 'class="daily-edit"' in index_html
assert "Daily Edit" in index_html
assert "今日编辑简报" in index_html
```

Add contract absence assertions:

```python
assert '"daily_edit"' not in generated_contract_payload
assert '"daily_information_layer"' not in generated_contract_payload
```

- [ ] **Step 2: Add docs paragraphs**

In `README.md` and `docs/row-one.md`, insert after Stage 319 and before Stage
310:

```markdown
Stage 320 adds homepage daily edit to generated ROW ONE index pages. It is
generated-site only and organizes existing `edition_brief`, `signal_synthesis`,
`daily_digest.briefing_topics`, `daily_digest.blocks`, and existing story route
metadata into a compact `Daily Edit / 今日编辑简报` section before the lead story.
It does not change `row-one-app/v7`, does not change `data/edition.json`, does
not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not
change detail routes, does not change paragraph anchors, does not change
schemas, does not write a new json artifact, does not add source collection,
does not fetch article pages, does not add scoring, does not add llm calls, does
not add connectors, and is not a compliance review feature.
```

- [ ] **Step 3: Add docs boundary test**

In `tests/test_row_one_docs.py`, update the Stage 319 slice end from
`"Stage 310 adds"` to `"Stage 320 adds"`, then add:

```python
def test_row_one_docs_describe_homepage_daily_edit_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_320 = readme[
        readme.index("Stage 320 adds homepage daily edit") : readme.index("Stage 310 adds")
    ]
    docs_stage_320 = docs[
        docs.index("Stage 320 adds homepage daily edit") : docs.index("Stage 310 adds")
    ]
    readme_stage_320_normalized = _normalized(readme_stage_320)
    docs_stage_320_normalized = _normalized(docs_stage_320)

    expected_phrases = [
        "homepage daily edit",
        "generated-site only",
        "existing `edition_brief`",
        "existing `signal_synthesis`",
        "daily_digest.briefing_topics",
        "daily_digest.blocks",
        "daily edit / 今日编辑简报",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_320_normalized
        assert phrase in docs_stage_320_normalized
```

- [ ] **Step 4: Run docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_signal_briefing_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_homepage_daily_edit_boundary -q
```

Expected: all pass.

---

## Task 4: Review And Verification

**Files:**

- Create: `docs/reviews/claude-code-stage-320-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-320-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
git diff --check
```

- [ ] **Step 2: Request Claude Code code review**

Create a focused review prompt covering Stage 320 goals, files, boundaries, and
verification already run. Run:

```bash
claude --bare --effort max --permission-mode plan --no-session-persistence --print \
  "$(cat docs/reviews/claude-code-stage-320-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-320-code-review.md
```

Fix Critical/Important findings and rerun focused verification.

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git status --short --branch
```

- [ ] **Step 4: Commit and push**

Run:

```bash
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-320-code-review-prompt.md \
  docs/reviews/claude-code-stage-320-code-review.md \
  docs/reviews/claude-code-stage-320-plan-review-prompt.md \
  docs/reviews/claude-code-stage-320-plan-review.md \
  docs/superpowers/plans/2026-07-07-stage-320-row-one-homepage-daily-edit-plan.md \
  docs/superpowers/specs/2026-07-07-stage-320-row-one-homepage-daily-edit-design.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py
git commit -m "Stage 320: add row one homepage daily edit"
git push origin main
```

---

## Self-Review Checklist

- Spec coverage: the plan covers homepage rendering, omission, escaping,
  link safety, CSS, workflow contract absence, docs boundary, review, and full
  verification.
- Placeholder scan: no TODO/TBD/fill-later placeholders.
- Type consistency: new helpers use existing `dict[str, object]`, `LocalizedText`,
  and existing route validation helpers.
- Boundary check: the plan does not add serialized `daily_edit`, dependencies,
  collection, scoring, LLMs, connectors, schemas, or new JSON artifacts.
