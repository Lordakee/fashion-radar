# Stage 286 ROW ONE Edition Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic ROW ONE edition brief that gives the app and homepage a concise daily overview assembled from existing edition, story, digest, section, topic, and evidence data.

**Architecture:** Keep the change additive and local. Add a top-level `edition_brief` object to the existing `row-one-app/v5` payload, derived only from already-built story payloads, `content_sections`, `daily_digest`, and `story_directory`; render the same object as a homepage `edition-brief` section before topic/path/story rails. Do not add collectors, LLM calls, image generation, scoring, ranking, sorting, story IDs, source inference, schedule/server/deployment changes, or dependency changes.

**Tech Stack:** Python 3.11+, JSON Schema draft 2020-12, static HTML/CSS/vanilla JS, pytest, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/row_one/render.py`
  - Add `_edition_brief_payload(edition, stories, content_sections, daily_digest, story_directory)`.
  - Add helper functions for deterministic section/topic/path summary fields.
  - Add top-level `edition_brief` to `build_row_one_app_payload` after `summary`.
- Modify: `schemas/row-one-app.schema.json`
  - Add top-level required `edition_brief`.
  - Add `$defs.editionBrief`, `$defs.editionBriefMetric`, and `$defs.editionBriefLink`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Add `_render_edition_brief(app_payload)` and insert it after edition nav and before lead story / briefing topics.
  - Add scoped CSS for `.edition-brief`.
- Modify: `tests/test_row_one_app_contract.py`
  - Assert `edition_brief` exists, mirrors existing payload counts, highlights read-first story, section coverage, topic count, path block count, and safe evidence count.
  - Add schema drift checks for missing `edition_brief` and malformed brief fields.
- Modify: `tests/test_row_one_render.py`
  - Assert generated JSON includes `edition_brief`.
  - Assert homepage renders the edition brief before lead story/topics/path/section blocks.
  - Assert escaping for hostile `edition_brief` payload values in `render_index_html`.
- Modify: `tests/test_row_one_docs.py`
  - Add docs guard for edition brief as deterministic overview from existing ROW ONE data.
- Modify: `docs/row-one.md`
  - Document `edition_brief` in Reader Orientation and App JSON Contract.
- Modify: `README.md`
  - Add concise ROW ONE summary/limits wording for edition brief.
- Add: `docs/reviews/claude-code-stage-286-plan-review-prompt.md`
- Add after review: `docs/reviews/claude-code-stage-286-plan-review.md`
- Add fallback review if Claude Code auth remains unavailable: `docs/reviews/opencode-stage-286-plan-review.md`
- Add after implementation: `docs/reviews/claude-code-stage-286-code-review-prompt.md`
- Add after implementation: `docs/reviews/claude-code-stage-286-code-review.md`
- Add fallback code review if needed: `docs/reviews/opencode-stage-286-code-review-prompt.md`
- Add fallback code review if needed: `docs/reviews/opencode-stage-286-code-review.md`

## Proposed `edition_brief` Shape

```json
{
  "title": {"zh": "今日总览", "en": "Edition Brief"},
  "dek": {
    "zh": "ROW ONE 将今日 2 条本地时尚信号整理成 2 个栏目、1 个主题和 1 条后续阅读路径。",
    "en": "ROW ONE organized 2 local fashion signals across 2 sections, 1 briefing topic, and 1 follow-up path block."
  },
  "lead_story_id": "the-row-signal-1234567890",
  "lead_story_href": "details/the-row-signal-1234567890.html",
  "lead_story_headline": "The Row signal",
  "story_directory_story_count": 2,
  "metrics": [
    {"key": "stories", "label": {"zh": "故事", "en": "Stories"}, "value": 2},
    {"key": "sections", "label": {"zh": "活跃栏目", "en": "Active Sections"}, "value": 2},
    {"key": "topics", "label": {"zh": "主题", "en": "Topics"}, "value": 1},
    {"key": "evidence", "label": {"zh": "证据链接", "en": "Evidence Links"}, "value": 2}
  ],
  "summary_points": [
    {"zh": "先读：The Row signal", "en": "Read first: The Row signal"},
    {"zh": "活跃栏目：今日重点、品牌动态", "en": "Active sections: Top Stories, Brand Moves"},
    {"zh": "整理主题：The Row", "en": "Briefing topics: The Row"},
    {"zh": "后续路径：重点整理、升温信号", "en": "Follow-up path: Key Takeaways, Signals To Watch"}
  ],
  "links": [
    {"key": "read_first", "label": {"zh": "先读", "en": "Read First"}, "href": "details/the-row-signal-1234567890.html"},
    {"key": "topics", "label": {"zh": "今日主题", "en": "Briefing Topics"}, "href": "#briefing-topics"},
    {"key": "path", "label": {"zh": "阅读路径", "en": "Briefing Path"}, "href": "#briefing-path"}
  ]
}
```

## Task 1: Add App Contract RED Tests

**Files:**
- Modify: `tests/test_row_one_app_contract.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add `edition_brief` assertions to app contract test**

Add a test near daily digest tests:

```python
def test_row_one_app_payload_includes_edition_brief_for_clients(tmp_path: Path) -> None:
    edition = _edition()
    brand_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "brand-move-2222222222",
            "section_key": "brand_moves",
            "headline": "Brand move",
            "detail_path": "details/brand-move-2222222222.html",
            "heat_delta": 4,
            "entity_refs": [RowOneReference(name="The Row", type="brand", label="rising")],
        },
    )
    edition.stories = [edition.stories[0], brand_story]

    payload = _payload(tmp_path, edition)
    brief = payload["edition_brief"]

    assert brief["title"] == {"zh": "今日总览", "en": "Edition Brief"}
    assert brief["lead_story_id"] == payload["daily_digest"]["lead_story_id"]
    assert brief["lead_story_href"] == payload["stories"][0]["detail_href"]
    assert brief["lead_story_headline"] == payload["stories"][0]["headline"]
    assert [metric["key"] for metric in brief["metrics"]] == [
        "stories",
        "sections",
        "topics",
        "evidence",
    ]
    assert [metric["value"] for metric in brief["metrics"]] == [2, 2, 1, 2]
    assert brief["summary_points"][0] == {
        "zh": "先读：The Row signal",
        "en": "Read first: The Row signal",
    }
    assert brief["summary_points"][1] == {
        "zh": "活跃栏目：今日重点、品牌动态",
        "en": "Active sections: Top Stories, Brand Moves",
    }
    assert brief["summary_points"][2] == {
        "zh": "整理主题：The Row",
        "en": "Briefing topics: The Row",
    }
    assert brief["summary_points"][3] == {
        "zh": "后续路径：重点整理、升温信号",
        "en": "Follow-up path: Key Takeaways, Signals To Watch",
    }
    assert brief["links"] == [
        {
            "key": "read_first",
            "label": {"zh": "先读", "en": "Read First"},
            "href": "details/the-row-signal-1234567890.html",
        },
        {
            "key": "topics",
            "label": {"zh": "今日主题", "en": "Briefing Topics"},
            "href": "#briefing-topics",
        },
        {
            "key": "path",
            "label": {"zh": "阅读路径", "en": "Briefing Path"},
            "href": "#briefing-path",
        },
    ]
    _schema_validator().validate(payload)
```

- [ ] **Step 2: Add JSON render assertion**

In `test_render_row_one_site_writes_json_payload`, after `summary`, add:

```python
    brief = payload["edition_brief"]
    assert brief["title"] == {"zh": "今日总览", "en": "Edition Brief"}
    assert brief["lead_story_id"] == story["id"]
    assert brief["lead_story_href"] == story["detail_href"]
    assert brief["metrics"][0] == {
        "key": "stories",
        "label": {"zh": "故事", "en": "Stories"},
        "value": 1,
    }
```

- [ ] **Step 3: Run RED app tests**

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_edition_brief_for_clients \
  tests/test_row_one_render.py::test_render_row_one_site_writes_json_payload \
  -q
```

Expected: fail because `edition_brief` is missing.

## Task 2: Implement App `edition_brief`

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `schemas/row-one-app.schema.json`

- [ ] **Step 1: Wire payload build without changing version**

In `build_row_one_app_payload`, create intermediate values and add `edition_brief`:

```python
    sections = [_section_payload(edition, section) for section in edition.sections]
    content_sections = [_content_section_payload(section, stories) for section in edition.sections]
    daily_digest = _daily_digest_payload(edition, stories)
    story_directory = _story_directory_payload(stories)
    evidence_count = sum(_safe_evidence_count(story.evidence) for story in edition.stories)
```

Then return those variables and:

```python
        "edition_brief": _edition_brief_payload(
            edition,
            stories,
            content_sections,
            daily_digest,
            story_directory,
            evidence_count,
        ),
```

- [ ] **Step 2: Add helper functions**

Add helpers after `_daily_digest_payload`:

```python
def _edition_brief_payload(
    edition: RowOneEdition,
    stories: list[dict[str, object]],
    content_sections: list[dict[str, object]],
    daily_digest: dict[str, object],
    story_directory: dict[str, object],
    evidence_count: int,
) -> dict[str, object]:
    active_sections = [section for section in content_sections if int(section["story_count"]) > 0]
    topics = daily_digest.get("briefing_topics", [])
    topic_count = len(topics) if isinstance(topics, list) else 0
    path_blocks = _edition_brief_path_blocks(daily_digest)
    lead_story = _story_by_id(stories, daily_digest.get("lead_story_id"))
    lead_href = lead_story["detail_href"] if lead_story is not None else None
    lead_headline = str(lead_story["headline"]) if lead_story is not None else None
    return {
        "title": {"zh": "今日总览", "en": "Edition Brief"},
        "dek": _edition_brief_dek(len(stories), len(active_sections), topic_count, len(path_blocks)),
        "lead_story_id": daily_digest.get("lead_story_id"),
        "lead_story_href": lead_href,
        "lead_story_headline": lead_headline,
        "metrics": [
            _edition_brief_metric("stories", {"zh": "故事", "en": "Stories"}, len(stories)),
            _edition_brief_metric(
                "sections",
                {"zh": "活跃栏目", "en": "Active Sections"},
                len(active_sections),
            ),
            _edition_brief_metric("topics", {"zh": "主题", "en": "Topics"}, topic_count),
            _edition_brief_metric(
                "evidence",
                {"zh": "证据链接", "en": "Evidence Links"},
                evidence_count,
            ),
        ],
        "summary_points": _edition_brief_summary_points(
            lead_story,
            active_sections,
            topics if isinstance(topics, list) else [],
            path_blocks,
        ),
        "links": _edition_brief_links(lead_href, topic_count, path_blocks),
        "story_directory_story_count": story_directory["story_count"],
    }
```

Also add these helpers:

```python
def _edition_brief_metric(key: str, label: dict[str, str], value: int) -> dict[str, object]:
    return {"key": key, "label": label, "value": value}


def _story_by_id(stories: list[dict[str, object]], story_id: object) -> dict[str, object] | None:
    return next((story for story in stories if story["id"] == story_id), None)


def _edition_brief_path_blocks(daily_digest: dict[str, object]) -> list[dict[str, object]]:
    blocks = daily_digest.get("blocks", [])
    if not isinstance(blocks, list):
        return []
    return [
        block
        for block in blocks
        if isinstance(block, dict)
        and block.get("key") in {"key_takeaways", "signals_to_watch"}
        and int(block.get("story_count", 0)) > 0
    ]


def _edition_brief_dek(
    story_count: int,
    active_section_count: int,
    topic_count: int,
    path_block_count: int,
) -> dict[str, str]:
    if story_count == 0:
        return {
            "zh": "暂无可整理的 ROW ONE 故事。",
            "en": "No ROW ONE stories are available to organize yet.",
        }
    return {
        "zh": (
            f"ROW ONE 将今日 {story_count} 条本地时尚信号整理成 "
            f"{active_section_count} 个栏目、{topic_count} 个主题和 "
            f"{path_block_count} 条后续阅读路径。"
        ),
        "en": (
            f"ROW ONE organized {story_count} local fashion signals across "
            f"{active_section_count} sections, "
            f"{topic_count} {_plural_word(topic_count, 'briefing topic', 'briefing topics')}, and "
            f"{path_block_count} {_plural_word(path_block_count, 'follow-up path block', 'follow-up path blocks')}."
        ),
    }
```

```python
def _plural_word(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


def _edition_brief_summary_points(
    lead_story: dict[str, object] | None,
    active_sections: list[dict[str, object]],
    topics: list[object],
    path_blocks: list[dict[str, object]],
) -> list[dict[str, str]]:
    points: list[dict[str, str]] = []
    if lead_story is not None:
        headline = str(lead_story["headline"])
        points.append({"zh": f"先读：{headline}", "en": f"Read first: {headline}"})
    if active_sections:
        zh_sections = "、".join(str(section["title"]["zh"]) for section in active_sections)
        en_sections = ", ".join(str(section["title"]["en"]) for section in active_sections)
        points.append({"zh": f"活跃栏目：{zh_sections}", "en": f"Active sections: {en_sections}"})
    topic_titles = [
        str(topic["title"]["en"])
        for topic in topics
        if isinstance(topic, dict) and isinstance(topic.get("title"), dict)
    ][:4]
    if topic_titles:
        topic_text = ", ".join(topic_titles)
        points.append({"zh": f"整理主题：{topic_text}", "en": f"Briefing topics: {topic_text}"})
    if path_blocks:
        zh_blocks = "、".join(str(block["title"]["zh"]) for block in path_blocks)
        en_blocks = ", ".join(str(block["title"]["en"]) for block in path_blocks)
        points.append({"zh": f"后续路径：{zh_blocks}", "en": f"Follow-up path: {en_blocks}"})
    if not points:
        points.append({"zh": "暂无可整理的故事。", "en": "No stories are ready to organize yet."})
    return points
```

```python
def _edition_brief_links(
    lead_href: object,
    topic_count: int,
    path_blocks: list[dict[str, object]],
) -> list[dict[str, object]]:
    links: list[dict[str, object]] = []
    if isinstance(lead_href, str):
        links.append({"key": "read_first", "label": {"zh": "先读", "en": "Read First"}, "href": lead_href})
    if topic_count > 0:
        links.append({"key": "topics", "label": {"zh": "今日主题", "en": "Briefing Topics"}, "href": "#briefing-topics"})
    if path_blocks:
        links.append({"key": "path", "label": {"zh": "阅读路径", "en": "Briefing Path"}, "href": "#briefing-path"})
    return links
```

- [ ] **Step 3: Add schema definitions**

Add top-level `edition_brief` to required/properties and add defs:

```json
"editionBrief": {
  "type": "object",
  "required": [
    "title",
    "dek",
    "lead_story_id",
    "lead_story_href",
    "lead_story_headline",
    "metrics",
    "summary_points",
    "links",
    "story_directory_story_count"
  ],
  "additionalProperties": false,
  "properties": {
    "title": {"$ref": "#/$defs/localizedText"},
    "dek": {"$ref": "#/$defs/localizedText"},
    "lead_story_id": {"anyOf": [{"$ref": "#/$defs/storyId"}, {"type": "null"}]},
    "lead_story_href": {"anyOf": [{"$ref": "#/$defs/detailHref"}, {"type": "null"}]},
    "lead_story_headline": {"$ref": "#/$defs/nullableString"},
    "metrics": {"type": "array", "minItems": 4, "maxItems": 4, "items": {"$ref": "#/$defs/editionBriefMetric"}},
    "summary_points": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/localizedText"}},
    "links": {"type": "array", "items": {"$ref": "#/$defs/editionBriefLink"}},
    "story_directory_story_count": {"type": "integer", "minimum": 0}
  }
}
```

```json
"editionBriefMetric": {
  "type": "object",
  "required": ["key", "label", "value"],
  "additionalProperties": false,
  "properties": {
    "key": {"enum": ["stories", "sections", "topics", "evidence"]},
    "label": {"$ref": "#/$defs/localizedText"},
    "value": {"type": "integer", "minimum": 0}
  }
},
"editionBriefLink": {
  "type": "object",
  "required": ["key", "label", "href"],
  "additionalProperties": false,
  "properties": {
    "key": {"enum": ["read_first", "topics", "path"]},
    "label": {"$ref": "#/$defs/localizedText"},
    "href": {"type": "string", "pattern": "^(details/[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\\.html|#briefing-topics|#briefing-path)$"}
  }
}
```

- [ ] **Step 4: Run GREEN app tests**

Run the RED app tests again plus schema syntax:

```bash
UV_NO_CONFIG=1 uv --no-config run python -m json.tool schemas/row-one-app.schema.json >/dev/null
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_edition_brief_for_clients \
  tests/test_row_one_render.py::test_render_row_one_site_writes_json_payload \
  -q
```

## Task 3: Add Homepage Edition Brief Rendering

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add homepage render RED test**

Add near briefing path tests:

```python
def test_render_row_one_site_includes_edition_brief_overview(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    brief_match = re.search(
        r'<section class="edition-brief" aria-label="Edition brief">(?P<brief>.*?)</section>',
        index_html,
        re.S,
    )

    assert brief_match is not None
    brief_html = brief_match.group("brief")
    assert "Edition Brief" in brief_html
    assert "今日总览" in brief_html
    assert "Stories" in brief_html
    assert "Active Sections" in brief_html
    assert "Topics" in brief_html
    assert "Evidence Links" in brief_html
    assert "Read first: The Row" in brief_html
    assert 'href="details/the-row-signal-1234567890.html"' in brief_html
    assert index_html.index('class="edition-brief"') < index_html.index('class="lead-story"')
```

- [ ] **Step 2: Add escaping test for payload-only render**

```python
def test_render_row_one_site_escapes_edition_brief_payload_values() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {
                "title": {"en": "Brief <script>", "zh": "总览 <script>"},
                "dek": {"en": "Dek & quote", "zh": "说明 & <tag>"},
                "lead_story_id": "hostile-1111111111",
                "lead_story_href": "details/hostile-1111111111.html",
                "lead_story_headline": 'Headline <img src=x onerror="alert(1)">',
                "metrics": [
                    {"key": "stories", "label": {"en": "Stories <x>", "zh": "故事 <x>"}, "value": 1}
                ],
                "summary_points": [{"en": "Point <b>", "zh": "要点 <b>"}],
                "links": [
                    {
                        "key": "read_first",
                        "label": {"en": "Open <x>", "zh": "打开 <x>"},
                        "href": "details/hostile-1111111111.html",
                    }
                ],
            }
        },
    )

    assert "Brief &lt;script&gt;" in index_html
    assert "Headline &lt;img" in index_html
    assert "Point &lt;b&gt;" in index_html
    assert "Open &lt;x&gt;" in index_html
    assert 'onerror="alert' not in index_html
    assert "onerror=&quot;alert" in index_html
    assert '<script>' not in index_html
```

- [ ] **Step 3: Run RED homepage tests**

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_edition_brief_overview \
  tests/test_row_one_render.py::test_render_row_one_site_escapes_edition_brief_payload_values \
  -q
```

Expected: fail because no edition brief render exists.

- [ ] **Step 4: Implement template render**

In `render_index_html`, compute:

```python
    edition_brief = _render_edition_brief(app_payload)
```

Render it after `{contents_nav}` and before `{lead_story_block}`.

Add helper near `_render_briefing_topics`:

```python
def _render_edition_brief(app_payload: dict[str, object] | None) -> str:
    brief = _app_payload_edition_brief(app_payload)
    if not brief:
        return ""
    title = _localized_from_payload(brief.get("title"))
    dek = _localized_from_payload(brief.get("dek"))
    metrics = _render_edition_brief_metrics(brief.get("metrics"))
    points = _render_edition_brief_points(brief.get("summary_points"))
    links = _render_edition_brief_links(brief.get("links"))
    lead_headline = _esc(brief.get("lead_story_headline") or "")
    lead = f'<p class="edition-brief-lead">{lead_headline}</p>' if lead_headline else ""
    return f"""<section class="edition-brief" aria-label="Edition brief">
  <div class="edition-brief-header">
    <p class="story-section"><span data-lang="en">Daily Overview</span><span data-lang="zh">每日总览</span></p>
    <h2><span data-lang="en">{_esc(title.en)}</span><span data-lang="zh">{_esc(title.zh)}</span></h2>
    <p><span data-lang="en">{_esc(dek.en)}</span><span data-lang="zh">{_esc(dek.zh)}</span></p>
    {lead}
  </div>
  {metrics}
  {points}
  {links}
</section>"""
```

Add supporting helpers:

```python
def _app_payload_edition_brief(app_payload: dict[str, object] | None) -> dict[str, object] | None:
    if not app_payload:
        return None
    brief = app_payload.get("edition_brief")
    return brief if isinstance(brief, dict) else None


def _localized_from_payload(value: object) -> LocalizedText:
    if isinstance(value, dict):
        zh = value.get("zh")
        en = value.get("en")
        if isinstance(zh, str) and isinstance(en, str):
            return LocalizedText(zh=zh, en=en)
    return LocalizedText(zh="", en="")
```

```python
def _render_edition_brief_metrics(value: object) -> str:
    if not isinstance(value, list):
        return ""
    cards = []
    for metric in value:
        if not isinstance(metric, dict):
            continue
        label = _localized_from_payload(metric.get("label"))
        cards.append(
            f"""<div class="edition-brief-metric">
      <strong>{_esc(metric.get("value", 0))}</strong>
      <span data-lang="en">{_esc(label.en)}</span>
      <span data-lang="zh">{_esc(label.zh)}</span>
    </div>"""
        )
    return f'<div class="edition-brief-metrics">{"".join(cards)}</div>' if cards else ""
```

```python
def _render_edition_brief_points(value: object) -> str:
    if not isinstance(value, list):
        return ""
    items = []
    for point in value:
        text = _localized_from_payload(point)
        if text.en or text.zh:
            items.append(f'<li><span data-lang="en">{_esc(text.en)}</span><span data-lang="zh">{_esc(text.zh)}</span></li>')
    return f'<ul class="edition-brief-points">{"".join(items)}</ul>' if items else ""
```

```python
def _render_edition_brief_links(value: object) -> str:
    if not isinstance(value, list):
        return ""
    links = []
    for link in value:
        if not isinstance(link, dict):
            continue
        href = link.get("href")
        if not isinstance(href, str) or not (href.startswith("details/") or href.startswith("#")):
            continue
        label = _localized_from_payload(link.get("label"))
        links.append(
            f'<a href="{_esc(href)}"><span data-lang="en">{_esc(label.en)}</span><span data-lang="zh">{_esc(label.zh)}</span></a>'
        )
    return f'<div class="edition-brief-links">{"".join(links)}</div>' if links else ""
```

Add CSS:

```css
.edition-brief {
  background: var(--panel);
  border: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  margin: 0 0 36px;
  padding: 22px;
}
.edition-brief-header h2,
.edition-brief-header p { margin: 0; }
.edition-brief-header { display: grid; gap: 8px; }
.edition-brief-lead { color: var(--ink); font-family: RowOneSerif, Georgia, serif; }
.edition-brief-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 1px; background: var(--line); }
.edition-brief-metric { background: var(--panel); display: grid; gap: 4px; padding: 12px; }
.edition-brief-metric strong { font-size: 1.4rem; }
.edition-brief-points { margin: 0; padding-left: 20px; }
.edition-brief-links { display: flex; flex-wrap: wrap; gap: 10px; }
.edition-brief-links a { border: 1px solid var(--line); color: var(--accent); padding: 8px 10px; text-decoration: none; }
```

Also add real anchor targets to the existing destination sections:

```html
<section id="briefing-topics" class="briefing-topics" aria-label="Briefing topics">
...
<section id="briefing-path" class="briefing-path" aria-label="Briefing path">
```

- [ ] **Step 5: Run GREEN homepage tests**

Run the RED homepage tests again.

## Task 4: Add Schema Drift And Docs

**Files:**
- Modify: `tests/test_row_one_app_contract.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `docs/row-one.md`
- Modify: `README.md`

- [ ] **Step 1: Add schema drift cases**

In existing schema drift parametrization, add:

```python
(lambda payload: payload.pop("edition_brief"), "'edition_brief' is a required property"),
(
    lambda payload: payload["edition_brief"].__setitem__("extra", True),
    "Additional properties",
),
(
    lambda payload: payload["edition_brief"]["metrics"][0].__setitem__("key", "bad"),
    "not one",
),
(
    lambda payload: payload["edition_brief"]["links"][0].__setitem__("href", "../escape.html"),
    "does not match",
),
(
    lambda payload: payload["edition_brief"].pop("story_directory_story_count"),
    "'story_directory_story_count' is a required property",
),
(
    lambda payload: payload["edition_brief"].__setitem__("metrics", payload["edition_brief"]["metrics"][:3]),
    "is too short",
),
(
    lambda payload: payload["edition_brief"]["summary_points"][0].__setitem__("extra", True),
    "Additional properties",
),
```

- [ ] **Step 2: Add docs test**

```python
def test_row_one_docs_describe_stage_286_edition_brief() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "edition_brief",
        "edition brief",
        "daily overview",
        "derived from existing row one story, section, digest, topic, and route data",
        "does not add source collection",
        "does not change matching, ranking, scoring, sorting, or story ids",
    ):
        assert phrase in row_one

    for phrase in (
        "edition_brief",
        "daily overview",
        "derived from existing row one stories and digest blocks",
    ):
        assert phrase in readme
```

- [ ] **Step 3: Update docs**

Add concise wording to `docs/row-one.md` Reader Orientation and App JSON Contract:

```markdown
The app payload also includes `edition_brief`, a deterministic daily overview
that summarizes the read-first story, active sections, briefing topics, follow-up
path blocks, story counts, and evidence counts. It is derived from existing ROW
ONE story, section, digest, topic, and route data; it does not add source
collection and does not change matching, ranking, scoring, sorting, or story IDs.
```

Add concise README wording:

```markdown
ROW ONE also emits `edition_brief`, a daily overview derived from existing ROW
ONE stories and digest blocks, so app clients and the homepage can present the
edition before readers drill into cards or detail pages.
```

- [ ] **Step 4: Run docs/schema tests**

```bash
UV_NO_CONFIG=1 uv --no-config run pytest tests/test_row_one_docs.py tests/test_row_one_app_contract.py -q
```

## Task 5: Verify, Review, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-286-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-286-code-review.md`
- Add if needed: `docs/reviews/opencode-stage-286-code-review-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-286-code-review.md`

- [ ] **Step 1: Focused verification**

```bash
UV_NO_CONFIG=1 uv --no-config run python -m json.tool schemas/row-one-app.schema.json >/dev/null
UV_NO_CONFIG=1 uv --no-config run pytest tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py -q
```

- [ ] **Step 2: Full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run ruff check .
UV_NO_CONFIG=1 uv --no-config run ruff format --check .
UV_NO_CONFIG=1 uv --no-config run pytest -q
UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git diff --exit-code -- uv.lock pyproject.toml
```

- [ ] **Step 3: Review gate**

Try Claude Code with `--effort max`. If local auth still returns `401` / disabled API key / authentication failure, record that in the Claude review file and use the local opencode fallback:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar --pure "$(cat docs/reviews/opencode-stage-286-code-review-prompt.md)"
```

Fix Critical/Important findings before commit.

- [ ] **Step 4: Commit and push**

```bash
git status --short
git add README.md docs/row-one.md schemas/row-one-app.schema.json \
  src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py \
  tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py \
  docs/superpowers/plans/2026-07-04-stage-286-row-one-edition-brief-plan.md \
  docs/reviews/claude-code-stage-286-plan-review-prompt.md \
  docs/reviews/claude-code-stage-286-plan-review.md \
  docs/reviews/opencode-stage-286-plan-review.md \
  docs/reviews/claude-code-stage-286-code-review-prompt.md \
  docs/reviews/claude-code-stage-286-code-review.md \
  docs/reviews/opencode-stage-286-code-review-prompt.md \
  docs/reviews/opencode-stage-286-code-review.md
git commit -m "Stage 286: add row one edition brief"
git push origin main
```

- [ ] **Step 5: Handoff Summary**

Report repo status, verified commands, uncommitted files, and next step.

## Self-Review

- Spec coverage: Adds an overview layer to app JSON and homepage, moving ROW ONE closer to a useful daily information tool instead of a link/card list.
- Boundary check: No source collection, social connectors, browser automation, LLM calls, image generation, scoring, matching, ranking, sorting, story ID, deployment, server, schedule, or dependency changes.
- Contract safety: Additive top-level required field under existing v4; schema and drift tests must update together because `additionalProperties: false` is used.
- Test coverage: App payload, JSON file, homepage rendering, escaping, schema drift, docs, focused/full verification.
