# Stage 318 ROW ONE Detail Continue Reading Rail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only `Continue Reading / 继续阅读` rail to ROW ONE detail pages so each article offers deterministic next reads from the same daily edition.

**Architecture:** Keep this as deterministic HTML/CSS in `templates.py`. Select related stories from the already-loaded `RowOneEdition`, validate detail paths before rendering links, and write nothing to app/runtime/manifest JSON or schemas. Use existing story summaries, section labels, and detail routes.

**Tech Stack:** Python, deterministic string-rendered HTML/CSS, existing ROW ONE Pydantic models, pytest, Ruff, Claude Code plan/code review workflow.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Create: `docs/reviews/claude-code-stage-318-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-318-plan-review.md`
- Later implementation review artifacts:
  - `docs/reviews/claude-code-stage-318-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-318-code-review.md`

---

### Task 1: Detail Continue Reading Rail

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add failing render tests**

Add tests near existing detail-page render tests:

```python
def _detail_story(
    story_id: str,
    headline: str,
    *,
    section_key: str = "top_stories",
    summary_en: str | None = None,
    summary_zh: str | None = None,
) -> RowOneStory:
    return _edition().stories[0].model_copy(
        deep=True,
        update={
            "id": story_id,
            "headline": headline,
            "section_key": section_key,
            "summary": LocalizedText(
                zh=summary_zh if summary_zh is not None else f"{headline} 摘要。",
                en=summary_en if summary_en is not None else f"{headline} summary.",
            ),
            "detail_path": f"details/{story_id}.html",
        },
    )


def _edition_with_stories(*stories: RowOneStory) -> RowOneEdition:
    edition = _edition()
    edition.stories = list(stories)
    return edition


def test_render_row_one_detail_continue_reading_prioritizes_same_section_and_fallbacks(
    tmp_path,
) -> None:
    current = _edition().stories[0]
    same_section = _detail_story("same-section-1234567890", "Same Section <Story>")
    other_section = _detail_story(
        "other-section-1234567890",
        "Other Section Story",
        section_key="brand_moves",
    )
    unsafe = _detail_story("unsafe-story-1234567890", "Unsafe Story").model_copy(
        update={"detail_path": "../unsafe.html"}
    )
    duplicate = _detail_story("duplicate-story-1234567890", "Duplicate Story").model_copy(
        update={"detail_path": same_section.detail_path}
    )
    extra = _detail_story("extra-story-1234567890", "Extra Story", section_key="brand_moves")
    edition = _edition_with_stories(current, unsafe, other_section, duplicate, same_section, extra)

    render_row_one_site(edition, tmp_path)

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    rail_html = detail_html[
        detail_html.index('id="continue-reading"') : detail_html.index("</article>")
    ]

    assert '<span data-lang="en">Continue Reading</span>' in rail_html
    assert '<span data-lang="zh">继续阅读</span>' in rail_html
    assert "Same Section &lt;Story&gt;" in rail_html
    assert "Other Section Story" in rail_html
    assert "Extra Story" in rail_html
    assert "Unsafe Story" not in rail_html
    assert "Duplicate Story" not in rail_html
    assert "The Row signal" not in rail_html
    assert rail_html.index("Same Section &lt;Story&gt;") < rail_html.index("Other Section Story")
    assert 'href="same-section-1234567890.html"' in rail_html
    assert 'href="other-section-1234567890.html"' in rail_html
    assert 'href="details/same-section-1234567890.html"' not in rail_html
    assert rail_html.count('class="continue-reading-card"') == 3
```

Add omission and fallback tests:

```python
def test_render_row_one_detail_continue_reading_omits_without_related_stories(
    tmp_path,
) -> None:
    edition = _edition_with_stories(_edition().stories[0])

    render_row_one_site(edition, tmp_path)

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'id="continue-reading"' not in detail_html
    assert "Continue Reading" not in detail_html


def test_render_row_one_detail_continue_reading_uses_editorial_takeaway_fallback(
    tmp_path,
) -> None:
    current = _edition().stories[0]
    fallback_story = _detail_story(
        "fallback-story-1234567890",
        "Fallback Story",
        summary_en="",
        summary_zh="",
    ).model_copy(
        update={
            "editorial_takeaway": LocalizedText(
                zh="备用中文编辑摘录。",
                en="Fallback editorial excerpt.",
            )
        }
    )
    edition = _edition_with_stories(current, fallback_story)

    render_row_one_site(edition, tmp_path)

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert "Fallback editorial excerpt." in detail_html
    assert "备用中文编辑摘录。" in detail_html
```

- [ ] **Step 2: Verify render tests fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_prioritizes_same_section_and_fallbacks \
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_omits_without_related_stories \
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_uses_editorial_takeaway_fallback -q
```

Expected: fail because the rail is not rendered yet.

- [ ] **Step 3: Implement rail rendering**

In `src/fashion_radar/row_one/templates.py`:

- add constants near existing detail/local article constants:

```python
DETAIL_CONTINUE_READING_EXCERPT_CHARS = 120
DETAIL_CONTINUE_READING_MAX_ITEMS = 3
```

- in `render_detail_html()`, build and render the rail:

```python
continue_reading = _render_detail_continue_reading(edition, story)
```

- place `{continue_reading}` after the evidence-trail section and before `</article>`.
- do not add the continue-reading rail to the local article map or article contents nav.

- implement:

```python
def _render_detail_continue_reading(edition: RowOneEdition, story: RowOneStory) -> str:
    cards = [
        _render_detail_continue_reading_card(edition, related)
        for related in _detail_continue_reading_stories(edition, story)
    ]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""    <section id="continue-reading" class="continue-reading" aria-label="Continue reading">
      <div class="continue-reading-header">
        <p class="story-section">
          <span data-lang="en">Continue Reading</span>
          <span data-lang="zh">继续阅读</span>
        </p>
        <h2>
          <span data-lang="en">Continue Reading</span>
          <span data-lang="zh">继续阅读</span>
        </h2>
      </div>
      <div class="continue-reading-grid">{"".join(cards)}</div>
    </section>"""
```

- implement deterministic selection:

```python
def _detail_continue_reading_stories(
    edition: RowOneEdition,
    story: RowOneStory,
) -> list[RowOneStory]:
    candidates = [
        candidate
        for candidate in edition.stories
        if candidate.id != story.id and candidate.section_key == story.section_key
    ]
    candidates.extend(
        candidate
        for candidate in edition.stories
        if candidate.id != story.id and candidate.section_key != story.section_key
    )
    selected: list[RowOneStory] = []
    seen_paths: set[str] = set()
    for candidate in candidates:
        href = _detail_continue_reading_href(candidate.detail_path)
        if href is None or href in seen_paths:
            continue
        seen_paths.add(href)
        selected.append(candidate)
        if len(selected) >= DETAIL_CONTINUE_READING_MAX_ITEMS:
            break
    return selected
```

- implement card and helpers:

```python
def _render_detail_continue_reading_card(
    edition: RowOneEdition,
    story: RowOneStory,
) -> str:
    href = _detail_continue_reading_href(story.detail_path)
    if href is None:
        return ""
    section_title = _section_title(edition, story.section_key)
    excerpt = _detail_continue_reading_excerpt(
        story.summary.en or story.editorial_takeaway.en
    )
    excerpt_zh = _detail_continue_reading_excerpt(
        story.summary.zh or story.editorial_takeaway.zh
    )
    return f"""        <a class="continue-reading-card" href="{_esc(href)}">
          <span class="continue-reading-section">
            <span data-lang="en">{_esc(section_title.en)}</span>
            <span data-lang="zh">{_esc(section_title.zh)}</span>
          </span>
          <strong>{_esc(story.headline)}</strong>
          <span>{_esc(story.source_name)}</span>
          <span class="continue-reading-excerpt">
            <span data-lang="en">{_esc(excerpt)}</span>
            <span data-lang="zh">{_esc(excerpt_zh)}</span>
          </span>
        </a>"""


def _detail_continue_reading_href(detail_path: str) -> str | None:
    pure_path = validated_row_one_detail_relative_path(detail_path)
    if pure_path is None:
        return None
    return pure_path.name


def _detail_continue_reading_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=DETAIL_CONTINUE_READING_EXCERPT_CHARS,
    )
```

- add CSS:

```css
.continue-reading {
  border-top: 1px solid var(--ink);
  margin: 36px 0 0;
  padding: 24px 0 0;
}
.continue-reading-header {
  display: grid;
  gap: 6px;
  margin-bottom: 14px;
}
.continue-reading-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.8rem, 4vw, 3.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
}
.continue-reading-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.continue-reading-card {
  background: var(--panel);
  color: inherit;
  display: grid;
  gap: 10px;
  min-height: 190px;
  padding: 14px;
  text-decoration: none;
}
.continue-reading-card strong {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.1rem, 2vw, 1.7rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.continue-reading-card span {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.35;
}
.continue-reading-section {
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.continue-reading-excerpt {
  color: var(--ink);
}
```

- add mobile override:

```css
.continue-reading-grid { grid-template-columns: 1fr; }
```

inside the existing `@media (max-width: 760px)` block.

- [ ] **Step 4: Verify render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_prioritizes_same_section_and_fallbacks \
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_omits_without_related_stories \
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_uses_editorial_takeaway_fallback -q
```

Expected: pass.

---

### Task 2: Workflow and Docs Boundary Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add failing workflow assertions**

Extend `tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`:

```python
second_item_id = repository.upsert_item(
    CollectedItem(
        source_name="Vogue Business",
        source_type=SourceType.RSS,
        url="https://example.com/the-row-second",
        title="The Row second signal",
        published_at="2026-06-11T10:30:00Z",
        summary="Second The Row coverage.",
    ),
    collected_at=datetime(2026, 6, 11, 11, 30, tzinfo=UTC),
)
repository.replace_item_matches(
    second_item_id,
    [
        {
            "entity_name": "The Row",
            "entity_type": "brand",
            "alias": "The Row",
            "confidence": 1.0,
            "reason": "accepted",
            "context_terms": [],
        }
    ],
)
stored_second_before = repository.get_item(second_item_id)
matches_second_before = repository.list_item_matches(second_item_id)
item_count_before = repository.count_items()
...
stored_second_after = repository.get_item(second_item_id)
matches_second_after = repository.list_item_matches(second_item_id)
...
assert "continue-reading" in detail_html
assert "Continue Reading" in detail_html
assert "继续阅读" in detail_html
assert '"continue_reading"' not in generated_contract_payload
assert '"related_stories"' not in generated_contract_payload
assert stored_second_after == stored_second_before
assert matches_second_after == matches_second_before
```

Keep the existing first-item SQLite immutability assertions, contract-version
assertions, and top-level `data/*.json` allowlist unchanged. The added second
matched item is required because the rail intentionally omits itself for
one-story editions.

- [ ] **Step 2: Add failing docs guard**

In `tests/test_row_one_docs.py`, update Stage 317 slice boundaries:

```python
readme_stage_317 = readme[
    readme.index("Stage 317 adds detail saved paragraph previews") : readme.index(
        "Stage 318 adds"
    )
]
docs_stage_317 = docs[
    docs.index("Stage 317 adds detail saved paragraph previews") : docs.index(
        "Stage 318 adds"
    )
]
```

Add `test_row_one_docs_describe_detail_continue_reading_boundary()` with:

```python
readme_stage_318 = readme[
    readme.index("Stage 318 adds detail continue reading") : readme.index("Stage 310 adds")
]
docs_stage_318 = docs[
    docs.index("Stage 318 adds detail continue reading") : docs.index("Stage 310 adds")
]
```

Expected phrases:

- `detail continue reading`
- `generated-site only`
- `existing edition stories`
- `existing detail routes`
- `existing story summaries`
- `does not change \`row-one-app/v7\``
- `does not change \`data/edition.json\``
- `does not change \`row-one-manifest/v1\``
- `does not change \`row-one-runtime/v1\``
- `does not change detail routes`
- `does not change paragraph anchors`
- `does not change schemas`
- `does not write a new json artifact`
- `does not add source collection`
- `does not fetch article pages`
- `does not add scoring`
- `does not add llm calls`
- `does not add connectors`
- `not a compliance review feature`

Forbidden phrases:

- `row-one-app/v8`
- `row-one-manifest/v2`
- `row-one-runtime/v2`
- `changes schemas`
- `adds source collection`
- `adds scoring`
- `adds llm calls`
- `adds social connectors`
- `adds community connectors`
- `adds compliance review`

- [ ] **Step 3: Verify workflow/docs tests fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_continue_reading_boundary -q
```

Expected: fail before docs/rail are fully updated.

- [ ] **Step 4: Update docs**

Insert this paragraph after Stage 317 in both `README.md` and `docs/row-one.md`:

```markdown
Stage 318 adds detail continue reading to generated ROW ONE detail pages. It is
generated-site only and turns existing edition stories, existing detail routes,
and existing story summaries into a capped internal next-read rail. It does not
change `row-one-app/v7`, does not change `data/edition.json`, does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change
detail routes, does not change paragraph anchors, does not change schemas, does
not write a new json artifact, does not add source collection, does not fetch
article pages, does not add scoring, does not add llm calls, does not add
connectors, and is not a compliance review feature.
```

- [ ] **Step 5: Verify workflow/docs tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_saved_paragraph_previews_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_continue_reading_boundary -q
```

Expected: pass.

---

### Task 3: Review, Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-318-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-318-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_saved_paragraph_previews_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_continue_reading_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
git diff --check
```

Expected: pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/claude-code-stage-318-code-review-prompt.md` summarizing:

- Stage 318 goal
- files changed
- generated-site-only boundaries
- detail-to-detail sibling href behavior
- no app/runtime/manifest/schema changes
- focused verification already run

- [ ] **Step 3: Run Claude Code review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  -p "$(cat docs/reviews/claude-code-stage-318-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-318-code-review.md
```

Expected: no Critical or Important issues. Fix any Critical/Important before continuing.

- [ ] **Step 4: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git status --short --branch
```

Expected:

- full pytest passes
- lock check passes
- release hygiene passes
- only intended Stage 318 files are modified/untracked

- [ ] **Step 5: Commit and push**

Run:

```bash
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-318-code-review-prompt.md \
  docs/reviews/claude-code-stage-318-code-review.md \
  docs/reviews/claude-code-stage-318-plan-review-prompt.md \
  docs/reviews/claude-code-stage-318-plan-review.md \
  docs/superpowers/plans/2026-07-06-stage-318-row-one-detail-continue-reading-rail-plan.md \
  docs/superpowers/specs/2026-07-06-stage-318-row-one-detail-continue-reading-rail-design.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py
git commit -m "Stage 318: add row one detail continue reading"
git push origin main
git status --short --branch
```

Expected: pushed to `origin/main`, clean worktree.
