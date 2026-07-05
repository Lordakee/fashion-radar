# Stage 295 ROW ONE Editorial Briefing Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the ROW ONE daily webpage and app payload organize the day's fashion information more explicitly by adding editorial topic-mix and heat-watch bullets to the existing edition brief.

**Architecture:** Keep the current `row-one-app/v7` contract and extend only the values of the already-required `edition_brief.summary_points` array. Derive the new points from existing story payloads and `daily_digest.briefing_topics`, so no crawler, source acquisition, scheduler, image generation, local article extraction, or generated-site persistence behavior changes.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering, JSON Schema draft 2020-12, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

Stage 295 closes the "report" side of the collect -> match -> report pipeline. ROW ONE already collects source material, matches it into stories, and renders a static website with local article bodies. This stage makes the homepage's first editorial block answer more of the user's daily questions directly:

- What should I read first?
- Which sections are active today?
- Which brands, products, designers, or people are represented?
- Are there positive heat signals worth watching?

This is deliberately a content-organization stage. It does not add compliance review, scraping, platform login, deployment, app UI, or persistent historical storage.

## File Structure

- Modify `src/fashion_radar/row_one/render.py`
  - Add focused helpers for topic-type counts and positive heat summaries.
  - Pass the story list into `_edition_brief_summary_points(...)`.
  - Append new localized summary points only when source data exists.
- Modify `tests/test_row_one_app_contract.py`
  - Add RED contract tests for topic-mix and heat-watch summary points.
  - Update existing `edition_brief` expectations where richer points are now emitted.
- Modify `tests/test_row_one_render.py`
  - Add RED static-rendering coverage that proves the new points appear on the homepage.
- Create `tests/test_row_one_briefing_topics.py`
  - Add focused unit coverage for `briefing_topics_payload(...)` because it is the shared input to the new topic-mix brief and currently has no direct unit test.
- Modify `docs/row-one.md`
  - Document that `edition_brief.summary_points` includes read-first, active-section, topic-mix, and heat-watch organization.
- Modify `tests/test_row_one_docs.py`
  - Guard the Stage 295 documentation phrases.
- Add review artifacts under `docs/reviews/`
  - `claude-code-stage-295-plan-review-prompt.md`
  - `claude-code-stage-295-plan-review.md`
  - `opencode-stage-295-plan-review-prompt.md`
  - `opencode-stage-295-plan-review.md`
  - Code-review artifacts after implementation.

## Task 1: Plan Review Gate

**Files:**
- Create: `docs/reviews/claude-code-stage-295-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-295-plan-review.md`
- Create: `docs/reviews/opencode-stage-295-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-295-plan-review.md`

- [ ] **Step 1: Write the Claude Code plan-review prompt**

Create `docs/reviews/claude-code-stage-295-plan-review-prompt.md` with:

```markdown
# Claude Code Stage 295 Plan Review Prompt

Use maximum reasoning effort. Do not edit files.

Review this implementation plan for Fashion Radar:

- `docs/superpowers/plans/2026-07-05-stage-295-row-one-editorial-briefing-depth-plan.md`

Context:

- The user wants ROW ONE to organize daily fashion information inside the generated local webpage, not just provide source links.
- The current priority is content depth and organization, not app development or visual polish.
- Do not add compliance-review product features.
- Keep generated `reports/row-one/` out of git.
- All dependency/test commands should use `UV_NO_CONFIG=1 uv --no-config run --frozen ...`.

Review questions:

1. Is the plan's choice to keep `row-one-app/v7` and enrich existing `edition_brief.summary_points` reasonable, or does it require a contract bump?
2. Are the proposed tests sufficient to prove the new content-organization behavior?
3. Are there any Critical or Important issues that must be fixed before implementation?

Return findings first, ordered by severity. If there are no Critical or Important findings, say that explicitly.
```

- [ ] **Step 2: Attempt Claude Code plan review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-295-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-295-plan-review.md
rm -f "$tmp_review"
```

Expected if Claude Code is still unavailable: a short completed record explaining the `401 API key is disabled` failure and that local opencode fallback is required.

- [ ] **Step 3: Write the opencode fallback plan-review prompt**

Create `docs/reviews/opencode-stage-295-plan-review-prompt.md` with:

```markdown
# opencode Stage 295 Plan Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review this implementation plan for Fashion Radar:

- `docs/superpowers/plans/2026-07-05-stage-295-row-one-editorial-briefing-depth-plan.md`

Also consider the Claude Code attempt:

- `docs/reviews/claude-code-stage-295-plan-review.md`

Context:

- The user wants ROW ONE to organize daily fashion information inside the generated local webpage, not just provide source links.
- The current priority is content depth and organization, not app development or visual polish.
- This stage deliberately avoids app contract migration by enriching `edition_brief.summary_points`.
- Do not add compliance-review product features.
- Keep generated `reports/row-one/` out of git.
- All dependency/test commands should use `UV_NO_CONFIG=1 uv --no-config run --frozen ...`.

Review questions:

1. Is keeping `row-one-app/v7` technically reasonable for this additive summary-point change?
2. Are the helper boundaries in `render.py` appropriately narrow?
3. Are the RED tests sufficient and correctly scoped?
4. Are docs/test updates enough for a GitHub-ready node?

Return findings first, ordered by severity. If there are no Critical or Important findings, say that explicitly.
```

- [ ] **Step 4: Run opencode fallback plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-295-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-295-plan-review.md
rm -f "$tmp_review"
```

Expected: completed plan review with no Critical or Important findings, or actionable findings that are fixed in the plan before Task 2.

## Task 2: App Payload Tests And Briefing Topic Regression Coverage

**Files:**
- Modify: `tests/test_row_one_app_contract.py`
- Create: `tests/test_row_one_briefing_topics.py`

- [ ] **Step 1: Add a direct briefing-topic unit test**

Create `tests/test_row_one_briefing_topics.py`:

```python
from __future__ import annotations

from fashion_radar.row_one.briefing_topics import briefing_topics_payload


def _story(
    story_id: str,
    *,
    evidence_count: int = 1,
    heat_delta: int = 0,
    entity_refs: list[dict[str, object]] | None = None,
    product_refs: list[dict[str, object]] | None = None,
    designer_refs: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "id": story_id,
        "headline": story_id,
        "detail_href": f"details/{story_id}.html",
        "evidence_count": evidence_count,
        "heat_delta": heat_delta,
        "entity_refs": entity_refs or [],
        "product_refs": product_refs or [],
        "designer_refs": designer_refs or [],
    }


def test_briefing_topics_payload_groups_explicit_topic_refs_once_per_story() -> None:
    topics = briefing_topics_payload(
        [
            _story(
                "the-row-signal-1234567890",
                evidence_count=2,
                heat_delta=5,
                entity_refs=[
                    {"name": "The Row", "type": "brand", "label": "brand"},
                    {"name": " the row ", "type": "retailer", "label": "duplicate"},
                    {"name": "Mary-Kate Olsen", "type": "designer", "label": "designer"},
                    {"name": "Zendaya", "type": "celebrity", "label": "person"},
                ],
                product_refs=[{"name": "Margaux", "type": "bag", "label": "bag"}],
                designer_refs=[{"name": "Ashley Olsen", "type": "designer", "label": "designer"}],
            ),
            _story(
                "the-row-followup-2222222222",
                evidence_count=1,
                heat_delta=-3,
                entity_refs=[{"name": "The Row", "type": "brand", "label": "brand"}],
            ),
        ]
    )

    by_type_and_title = {
        (topic["topic_type"], topic["title"]["en"]): topic for topic in topics
    }

    assert by_type_and_title[("brand", "The Row")]["story_count"] == 2
    assert by_type_and_title[("brand", "The Row")]["evidence_count"] == 3
    assert by_type_and_title[("brand", "The Row")]["positive_heat_delta_sum"] == 5
    assert by_type_and_title[("product", "Margaux")]["story_ids"] == [
        "the-row-signal-1234567890"
    ]
    assert by_type_and_title[("designer", "Mary-Kate Olsen")]["story_ids"] == [
        "the-row-signal-1234567890"
    ]
    assert by_type_and_title[("designer", "Ashley Olsen")]["story_ids"] == [
        "the-row-signal-1234567890"
    ]
    assert by_type_and_title[("person", "Zendaya")]["story_ids"] == [
        "the-row-signal-1234567890"
    ]
```

- [ ] **Step 2: Add RED app-payload expectations for richer edition brief**

In `tests/test_row_one_app_contract.py`, add a test near the existing edition-brief tests:

```python
def test_row_one_app_payload_edition_brief_summarizes_topic_mix_and_heat_watch(
    tmp_path: Path,
) -> None:
    edition = _edition()
    base_story = edition.stories[0]
    edition.stories = [
        base_story.model_copy(
            deep=True,
            update={
                "heat_delta": 7,
                "entity_refs": [
                    RowOneReference(name="The Row", type="brand", label="brand"),
                    RowOneReference(name="Zendaya", type="celebrity", label="person"),
                ],
                "product_refs": [RowOneReference(name="Margaux", type="bag", label="bag")],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "designer-signal-2222222222",
                "section_key": "brand_moves",
                "headline": "Designer signal",
                "detail_path": "details/designer-signal-2222222222.html",
                "heat_delta": 3,
                "entity_refs": [
                    RowOneReference(name="Mary-Kate Olsen", type="designer", label="designer")
                ],
            },
        ),
    ]

    payload = _payload(tmp_path, edition)
    brief = payload["edition_brief"]

    assert {
        "zh": "主题结构：品牌 1、单品 1、设计师 1、人物 1",
        "en": "Topic mix: 1 brand, 1 product, 1 designer, 1 person",
    } in brief["summary_points"]
    assert {
        "zh": "升温观察：2 条正向热度信号，最高 +7",
        "en": "Heat watch: 2 positive heat signals, highest +7",
    } in brief["summary_points"]
    _schema_validator().validate(payload)
```

- [ ] **Step 3: Update existing edition-brief expectation with the full strict list**

In `test_row_one_app_payload_includes_edition_brief_for_clients`, replace the
strict `brief["summary_points"] == [...]` expectation with this full ordered
list:

```python
assert brief["summary_points"] == [
    {"zh": "先读：The Row signal", "en": "Read first: The Row signal"},
    {
        "zh": "活跃栏目：今日重点、品牌动态",
        "en": "Active sections: Top Stories, Brand Moves",
    },
    {"zh": "整理主题：The Row", "en": "Briefing topics: The Row"},
    {"zh": "主题结构：品牌 1", "en": "Topic mix: 1 brand"},
    {
        "zh": "升温观察：1 条正向热度信号，最高 +4",
        "en": "Heat watch: 1 positive heat signal, highest +4",
    },
    {
        "zh": "后续路径：重点整理、升温信号",
        "en": "Follow-up path: Key Takeaways, Signals To Watch",
    },
]
```

- [ ] **Step 4: Run focused RED tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_briefing_topics.py \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_edition_brief_summarizes_topic_mix_and_heat_watch \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_edition_brief_for_clients \
  -q
```

Expected before implementation: the new `briefing_topics_payload` unit test is
regression coverage and may already pass, while the new app-payload test and
updated edition-brief expectation fail because the topic-mix and heat-watch
summary points do not exist yet.

## Task 3: GREEN Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`

- [ ] **Step 1: Extend `_edition_brief_payload(...)` to pass stories into summary generation**

Change:

```python
"summary_points": _edition_brief_summary_points(
    lead_story,
    active_sections,
    topics if isinstance(topics, list) else [],
    path_blocks,
),
```

to:

```python
"summary_points": _edition_brief_summary_points(
    lead_story,
    active_sections,
    topics if isinstance(topics, list) else [],
    path_blocks,
    stories,
),
```

- [ ] **Step 2: Add helper functions below `_edition_brief_dek(...)`**

Add:

```python
EDITION_BRIEF_TOPIC_TYPE_LABELS = {
    "brand": {"zh": "品牌", "en_singular": "brand", "en_plural": "brands"},
    "product": {"zh": "单品", "en_singular": "product", "en_plural": "products"},
    "designer": {"zh": "设计师", "en_singular": "designer", "en_plural": "designers"},
    "person": {"zh": "人物", "en_singular": "person", "en_plural": "people"},
}


def _edition_brief_topic_mix_point(topics: list[object]) -> dict[str, str] | None:
    counts = {topic_type: 0 for topic_type in EDITION_BRIEF_TOPIC_TYPE_LABELS}
    for topic in topics:
        if not isinstance(topic, dict):
            continue
        topic_type = str(topic.get("topic_type", ""))
        if topic_type in counts:
            counts[topic_type] += 1
    active_counts = [
        (topic_type, count)
        for topic_type, count in counts.items()
        if count > 0
    ]
    if not active_counts:
        return None
    zh_parts = [
        f"{EDITION_BRIEF_TOPIC_TYPE_LABELS[topic_type]['zh']} {count}"
        for topic_type, count in active_counts
    ]
    en_parts = [
        f"{count} {_plural_word(count, EDITION_BRIEF_TOPIC_TYPE_LABELS[topic_type]['en_singular'], EDITION_BRIEF_TOPIC_TYPE_LABELS[topic_type]['en_plural'])}"
        for topic_type, count in active_counts
    ]
    return {
        "zh": f"主题结构：{'、'.join(zh_parts)}",
        "en": f"Topic mix: {', '.join(en_parts)}",
    }


def _edition_brief_heat_watch_point(stories: list[dict[str, object]]) -> dict[str, str] | None:
    positive_heat_deltas = []
    for story in stories:
        heat_delta = story.get("heat_delta")
        if isinstance(heat_delta, int) and not isinstance(heat_delta, bool) and heat_delta > 0:
            positive_heat_deltas.append(heat_delta)
    if not positive_heat_deltas:
        return None
    signal_count = len(positive_heat_deltas)
    max_heat_delta = max(positive_heat_deltas)
    return {
        "zh": f"升温观察：{signal_count} 条正向热度信号，最高 +{max_heat_delta}",
        "en": (
            f"Heat watch: {signal_count} "
            f"{_plural_word(signal_count, 'positive heat signal', 'positive heat signals')}, "
            f"highest +{max_heat_delta}"
        ),
    }
```

- [ ] **Step 3: Append the new points in `_edition_brief_summary_points(...)`**

Update the function signature:

```python
def _edition_brief_summary_points(
    lead_story: dict[str, object] | None,
    active_sections: list[dict[str, object]],
    topics: list[object],
    path_blocks: list[dict[str, object]],
    stories: list[dict[str, object]],
) -> list[dict[str, str]]:
```

After the existing topic-title point, append:

```python
    topic_mix_point = _edition_brief_topic_mix_point(topics)
    if topic_mix_point is not None:
        points.append(topic_mix_point)
    heat_watch_point = _edition_brief_heat_watch_point(stories)
    if heat_watch_point is not None:
        points.append(heat_watch_point)
```

Keep the fallback no-stories point unchanged.

- [ ] **Step 4: Run GREEN focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_briefing_topics.py \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_edition_brief_summarizes_topic_mix_and_heat_watch \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_edition_brief_for_clients \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_empty_edition_brief_for_clients \
  -q
```

Expected after implementation: all selected tests pass.

## Task 4: Static Rendering And Docs

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add RED static rendering coverage**

In `tests/test_row_one_render.py`, add a test near the edition-brief renderer tests:

```python
def test_render_row_one_site_displays_edition_brief_topic_mix_and_heat_watch(tmp_path) -> None:
    edition = _edition()
    base_story = edition.stories[0]
    edition.stories = [
        base_story.model_copy(
            deep=True,
            update={
                "heat_delta": 7,
                "entity_refs": [
                    RowOneReference(name="The Row", type="brand", label="brand"),
                    RowOneReference(name="Zendaya", type="celebrity", label="person"),
                ],
                "product_refs": [RowOneReference(name="Margaux", type="bag", label="bag")],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "designer-signal-2222222222",
                "section_key": "brand_moves",
                "headline": "Designer signal",
                "detail_path": "details/designer-signal-2222222222.html",
                "heat_delta": 3,
                "entity_refs": [
                    RowOneReference(name="Mary-Kate Olsen", type="designer", label="designer")
                ],
            },
        ),
    ]

    render_row_one_site(edition, tmp_path)
    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert "Topic mix: 1 brand, 1 product, 1 designer, 1 person" in index_html
    assert "主题结构：品牌 1、单品 1、设计师 1、人物 1" in index_html
    assert "Heat watch: 2 positive heat signals, highest +7" in index_html
    assert "升温观察：2 条正向热度信号，最高 +7" in index_html
```

- [ ] **Step 2: Run the static rendering test and verify RED if Task 3 is not implemented yet**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_displays_edition_brief_topic_mix_and_heat_watch \
  -q
```

Expected before Task 3: FAIL because the strings are absent. Expected after Task 3: PASS.

- [ ] **Step 3: Update `docs/row-one.md`**

In the app JSON contract section, expand the `edition_brief` sentence so it states:

```markdown
`edition_brief.summary_points` now includes read-first orientation, active-section coverage, explicit topic-mix counts across brands, products, designers, and people, and positive heat-watch cues when local raw mention deltas are available.
```

- [ ] **Step 4: Add docs test coverage**

In `tests/test_row_one_docs.py`, add a new
`test_row_one_docs_describe_stage_295_edition_brief_content_organization`
asserting the normalized doc includes:

```python
"edition_brief.summary_points",
"read-first orientation",
"active-section coverage",
"explicit topic-mix counts",
"brands, products, designers, and people",
"positive heat-watch cues",
"local raw mention deltas",
```

- [ ] **Step 5: Run docs/render focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_displays_edition_brief_topic_mix_and_heat_watch \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_295_edition_brief_content_organization \
  -q
```

Expected: all selected tests pass.

## Task 5: Verification, Code Review, And Push

**Files:**
- Create: `docs/reviews/claude-code-stage-295-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-295-code-review.md`
- Create: `docs/reviews/opencode-stage-295-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-295-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_briefing_topics.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
  src/fashion_radar/row_one/render.py \
  tests/test_row_one_briefing_topics.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/render.py \
  tests/test_row_one_briefing_topics.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py
```

Expected: all focused tests and ruff checks pass.

- [ ] **Step 2: Run release verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv lock --check
```

Expected: full suite passes, release hygiene passes, and lockfile check passes.

- [ ] **Step 3: Rebuild today's ROW ONE site and scan the static HTML**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-05T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
rg --no-ignore -n "Topic mix|主题结构|Heat watch|升温观察" reports/row-one/site/index.html
```

Expected: the generated homepage contains the new editorial briefing points when
the day's data has topic refs or positive heat deltas. On a sparse-data day,
`rg` may exit 1 because there are no matching points; in that case inspect the
generated `data/edition.json` before treating it as a product failure. Generated
files remain ignored and are not committed.

- [ ] **Step 4: Write code-review prompts**

Create `docs/reviews/claude-code-stage-295-code-review-prompt.md` and `docs/reviews/opencode-stage-295-code-review-prompt.md` with the Stage 295 change summary, plan path, base SHA, head SHA, and verification commands.

- [ ] **Step 5: Attempt Claude Code code review, then opencode fallback if required**

Use Claude Code with `--effort max`. If Claude Code still fails with `401 API key is disabled`, record that failure and run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-295-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-295-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings, or fixes plus rereview before commit.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short
git add \
  src/fashion_radar/row_one/render.py \
  tests/test_row_one_briefing_topics.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  docs/row-one.md \
  docs/superpowers/plans/2026-07-05-stage-295-row-one-editorial-briefing-depth-plan.md \
  docs/reviews/claude-code-stage-295-plan-review-prompt.md \
  docs/reviews/claude-code-stage-295-plan-review.md \
  docs/reviews/opencode-stage-295-plan-review-prompt.md \
  docs/reviews/opencode-stage-295-plan-review.md \
  docs/reviews/claude-code-stage-295-code-review-prompt.md \
  docs/reviews/claude-code-stage-295-code-review.md \
  docs/reviews/opencode-stage-295-code-review-prompt.md \
  docs/reviews/opencode-stage-295-code-review.md
git diff --cached --check
git commit -m "Stage 295: deepen row one editorial briefing"
git push origin main
```

Expected: pushed commit on `origin/main`. `reports/row-one/` remains untracked/ignored and is not added.

## Handoff Summary Template

At the end of this node, report:

```markdown
**Handoff Summary**
- Repo: `/home/ubuntu/fashion-radar`
- Branch/commit: `main` at `<sha>`, pushed to `origin/main`
- Verified commands: `<focused tests>`, `<full suite>`, `<ruff>`, `<release hygiene>`, `<uv lock --check>`, `<site rebuild/static scan>`
- Uncommitted files: `<git status --short output>`
- Generated site: `reports/row-one/site` rebuilt but ignored
- Next step: Stage 296 should focus on article-detail body quality or daily 04:00 refresh wiring, depending on the user's priority.
```
