# Stage 262 ROW ONE Reader Orientation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic reader-orientation layer to ROW ONE so the daily static site is easier to scan and navigate.

**Architecture:** Keep Stage 262 inside the existing ROW ONE presentation layer. Compute homepage contents, story-card metadata, and detail back-to-section links from `RowOneEdition`, `RowOneSection`, and `RowOneStory` in `templates.py`; do not change source collection, matching, scoring, ranking, story IDs, server behavior, or the JSON contract.

**Tech Stack:** Python 3.11+, Pydantic models already in `fashion_radar.row_one.models`, static HTML/CSS/JS template strings, pytest, Ruff, Claude Code review gates.

---

## Stage Boundary

Stage 262 closes the ROW ONE navigation/readability gap in the `collect -> match
-> report -> ROW ONE` path. Stage 260 created a static site and Stage 261 added
editorial synthesis. Stage 262 makes the site easier to orient in: homepage
contents, section jump links, card metadata, and detail-page return links.

This stage does not add new source acquisition, scraping, browser automation,
platform APIs, account/session behavior, translation, LLM calls, image
generation, paid APIs, deployment, demand proof, platform coverage verification,
or compliance-review product work.

## Stage Direction Rationale

The current user goal is a polished ROW ONE daily web/app experience. This is a
third presentation-only ROW ONE stage, but it is intentionally scoped this way
because the immediately visible product gap is reader navigation and scanning,
not collection breadth or matching logic. The stage remains compatible with the
release-track preference for coverage/matching work by avoiding source
acquisition, ranking, scoring, and external-tool changes.

If the user does not continue prioritizing ROW ONE app/site work after this
stage, the next release-track stage should return to curated source coverage or
deterministic matching quality. Stage 263 should become app-facing JSON contract
work only if the user continues the ROW ONE app/site direction.

## Files And Artifacts

- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_row_one_cli.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `docs/row-one.md`
- Create: `docs/superpowers/specs/2026-07-02-stage-262-row-one-reader-orientation-design.md`
- Create: `docs/superpowers/plans/2026-07-02-stage-262-row-one-reader-orientation-plan.md`
- Create: `docs/reviews/claude-code-stage-262-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-262-plan-review.md` after completed review capture
- Create if fallback is needed: `docs/reviews/opencode-stage-262-plan-review-prompt.md`
- Create if fallback is needed: `docs/reviews/opencode-stage-262-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-262-code-review-prompt.md`
- Create after implementation: `docs/reviews/claude-code-stage-262-code-review.md`
- Create if fixes require rereview: `docs/reviews/claude-code-stage-262-code-rereview-prompt.md`
- Create if fixes require rereview: `docs/reviews/claude-code-stage-262-code-rereview.md`
- Create before push: `docs/reviews/claude-code-stage-262-release-review-prompt.md`
- Create before push: `docs/reviews/claude-code-stage-262-release-review.md`

## Task 1: Add Homepage Contents Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Extend the render fixture with an empty section**

Update `_edition()` so `sections` includes both `top_stories` and an empty
`brand_moves` section. Keep the single existing story in `top_stories`:

```python
sections=[
    RowOneSection(
        key="top_stories",
        title=LocalizedText(zh="今日重点", en="Top Stories"),
        dek=LocalizedText(zh="今日最值得先看的时尚信号。", en="Read first."),
    ),
    RowOneSection(
        key="brand_moves",
        title=LocalizedText(zh="品牌动态", en="Brand Moves"),
        dek=LocalizedText(zh="品牌、零售与商业动作。", en="Brand and retail context."),
    ),
],
```

- [ ] **Step 2: Write failing contents assertions**

Add a new test:

```python
def test_render_row_one_site_writes_edition_contents_navigation(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="edition-nav"' in index_html
    assert 'aria-label="Edition contents"' in index_html
    assert 'href="#top_stories"' in index_html
    assert 'href="#brand_moves"' in index_html
    assert 'id="top_stories"' in index_html
    assert 'id="brand_moves"' in index_html
    nav_match = re.search(
        r'<nav class="edition-nav" aria-label="Edition contents">(?P<nav>.*?)</nav>',
        index_html,
        re.S,
    )
    assert nav_match is not None
    nav_html = nav_match.group("nav")
    assert "Top Stories" in nav_html
    assert "Brand Moves" in nav_html
    assert "1 story" in nav_html
    assert "0 stories" in nav_html
    assert "1 条" in nav_html
    assert "0 条" in nav_html
    assert "No stories in this section yet." in index_html
```

- [ ] **Step 3: Run the failing test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_edition_contents_navigation -q
```

Expected: FAIL because `edition-nav` does not exist.

## Task 2: Render Homepage Contents Navigation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Update imports and add contents rendering helpers**

In `templates.py`, ensure the import includes `RowOneSection`:

```python
from fashion_radar.row_one.models import (
    RowOneEdition,
    RowOneLink,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)
```

Then add helpers after `row_one_js()` and before `_render_section()`:

```python
def _render_edition_nav(edition: RowOneEdition) -> str:
    rows = "\n".join(
        _render_edition_nav_item(edition, section) for section in edition.sections
    )
    return f"""<nav class="edition-nav" aria-label="Edition contents">
  <p class="story-section">
    <span data-lang="en">Edition Contents</span>
    <span data-lang="zh">今日目录</span>
  </p>
  <div class="edition-nav-grid">{rows}</div>
</nav>"""


def _render_edition_nav_item(
    edition: RowOneEdition,
    section: RowOneSection,
) -> str:
    story_count = len(edition.section_stories(section.key))
    count_en = "1 story" if story_count == 1 else f"{story_count} stories"
    count_zh = f"{story_count} 条"
    return f"""<a class="edition-nav-item" href="#{_esc(section.key)}">
  <span class="edition-nav-title">
    <span data-lang="en">{_esc(section.title.en)}</span>
    <span data-lang="zh">{_esc(section.title.zh)}</span>
  </span>
  <span class="edition-nav-count">
    <span data-lang="en">{_esc(count_en)}</span>
    <span data-lang="zh">{_esc(count_zh)}</span>
  </span>
  <span class="edition-nav-dek">
    <span data-lang="en">{_esc(section.dek.en)}</span>
    <span data-lang="zh">{_esc(section.dek.zh)}</span>
  </span>
</a>"""
```

- [ ] **Step 2: Insert the nav into the homepage**

In `render_index_html`, compute the nav and render it before section blocks:

```python
contents_nav = _render_edition_nav(edition)
story_cards = "\n".join(_render_section(edition, section.key) for section in edition.sections)
```

Then change the `<main>` body to:

```html
<main>
{contents_nav}
{story_cards}
</main>
```

- [ ] **Step 3: Add CSS for the contents block**

In `row_one_css()`, add styles near the section/story styles:

```css
.edition-nav {
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--ink);
  padding: 24px 0;
  margin-bottom: 32px;
}
.edition-nav-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}
.edition-nav-item {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  min-height: 150px;
  padding: 16px;
  text-decoration: none;
}
.edition-nav-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.25rem;
  line-height: 1;
}
.edition-nav-count {
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.edition-nav-dek {
  color: var(--muted);
  font-size: 0.86rem;
  line-height: 1.35;
}
```

Add this inside the mobile media query:

```css
  .edition-nav-grid { grid-template-columns: 1fr; }
```

- [ ] **Step 4: Run the contents test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_edition_contents_navigation -q
```

Expected: PASS.

## Task 3: Add Story Card Metadata And Detail Return Tests

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add failing story-card metadata assertions**

Extend `test_render_row_one_site_escapes_html_and_omits_unsafe_links` with:

```python
orientation_match = re.search(
    r'<p class="story-orientation">(?P<orientation>.*?)</p>',
    index_html,
    re.S,
)
assert orientation_match is not None
orientation_html = orientation_match.group("orientation")
assert "Top Stories" in orientation_html
assert "Vogue Business" in orientation_html
assert "2026-07-02" in orientation_html
assert "2 evidence links" in orientation_html
assert "2 条线索" in orientation_html
```

Do not assert the English abbreviated month label because `%b` depends on the
runtime `LC_TIME` locale; the ISO date assertion is the stable date check.

- [ ] **Step 2: Add failing singular evidence and undated assertions**

Add a focused render test that uses one evidence link and no `published_at`:

```python
def test_render_row_one_site_story_orientation_handles_single_link_and_undated(
    tmp_path,
) -> None:
    edition = _edition()
    edition.stories[0].published_at = None
    edition.stories[0].evidence = [edition.stories[0].evidence[0]]

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    orientation_match = re.search(
        r'<p class="story-orientation">(?P<orientation>.*?)</p>',
        index_html,
        re.S,
    )
    assert orientation_match is not None
    orientation_html = orientation_match.group("orientation")
    assert "Undated" in orientation_html
    assert "时间未标注" in orientation_html
    assert "1 evidence link" in orientation_html
    assert "1 条线索" in orientation_html
```

- [ ] **Step 3: Add failing detail back-to-section assertions**

In `test_render_row_one_site_escapes_html_and_omits_unsafe_links`, add these
assertions against the already-read `detail_html`:

```python
assert 'href="../index.html#top_stories"' in detail_html
assert "Back to section" in detail_html
assert "回到栏目" in detail_html
```

- [ ] **Step 4: Add CLI smoke assertion**

In `test_row_one_build_command_writes_non_ascii_story_detail_path`, bind the
homepage HTML before the assertions:

```python
index_html = (output_dir / "index.html").read_text(encoding="utf-8")
```

Then assert the generated build contains the nav:

```python
assert 'class="edition-nav"' in index_html
assert 'href="#top_stories"' in index_html
assert "上海新锐设计师品牌升温" in index_html
```

- [ ] **Step 5: Run failing tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_escapes_html_and_omits_unsafe_links tests/test_row_one_cli.py::test_row_one_build_command_writes_non_ascii_story_detail_path -q
```

Expected: FAIL because card metadata and detail section return links do not
exist.

## Task 4: Render Story Card Metadata And Detail Return Links

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Update imports and render story cards with section context**

In `templates.py`, ensure the import includes `LocalizedText` and
`RowOneSection`:

```python
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)
```

Then update `_render_section()` so story cards receive the current section title
instead of looking it up from a duplicated map:

```python
cards = "\n".join(_render_story_card(story, section.title) for story in stories)
```

Update the story-card signature:

```python
def _render_story_card(
    story: RowOneStory,
    section_title: LocalizedText,
) -> str:
```

- [ ] **Step 2: Add metadata helpers**

In `templates.py`, add:

```python
def _render_story_orientation(story: RowOneStory, section_title: LocalizedText) -> str:
    published = _published_label(story)
    evidence_count = len(story.evidence)
    evidence_en = (
        "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    )
    evidence_zh = f"{evidence_count} 条线索"
    en_parts = (
        section_title.en,
        story.source_name,
        published.en,
        evidence_en,
    )
    zh_parts = (
        section_title.zh,
        story.source_name,
        published.zh,
        evidence_zh,
    )
    en_text = " · ".join(en_parts)
    zh_text = " · ".join(zh_parts)
    return f"""<p class="story-orientation">
    <span data-lang="en">{_esc(en_text)}</span>
    <span data-lang="zh">{_esc(zh_text)}</span>
  </p>"""


def _published_label(story: RowOneStory) -> LocalizedText:
    if story.published_at is None:
        return LocalizedText(zh="时间未标注", en="Undated")
    return LocalizedText(
        zh=story.published_at.strftime("%Y-%m-%d"),
        en=story.published_at.strftime("%b %d, %Y"),
    )
```

- [ ] **Step 3: Render metadata inside story cards**

In `_render_story_card`, remove the standalone source-only
`<p class="story-meta">...</p>` line from the card header and add
`{_render_story_orientation(story, section_title)}` after the headline block and
before `story-takeaway`:

```html
  {_render_story_orientation(story, section_title)}
  <p class="story-takeaway">
```

- [ ] **Step 4: Render back-to-section link on detail pages**

In `render_detail_html`, add after `<p class="story-section">...</p>` and
before the `<h1>`:

```html
    <p class="section-return">
      <a href="../index.html#{_esc(story.section_key)}">
        <span data-lang="en">Back to section</span>
        <span data-lang="zh">回到栏目</span>
      </a>
    </p>
```

- [ ] **Step 5: Add CSS for orientation and return links**

In `row_one_css()`, add:

```css
.story-orientation {
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  margin: 10px 0 0;
  text-transform: uppercase;
}
.section-return {
  margin: 0 0 22px;
}
.section-return a {
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}
```

- [ ] **Step 6: Run focused render/CLI tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_cli.py -q
```

Expected: PASS.

## Task 5: Documentation And Boundary Tests

**Files:**
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs assertions**

Add a docs test:

```python
def test_row_one_docs_describe_reader_orientation_boundary() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))

    for phrase in (
        "reader orientation",
        "edition contents",
        "section jump links",
        "story-card metadata",
        "back to section",
        "presentation-only",
    ):
        assert phrase in normalized
```

- [ ] **Step 2: Run docs test and verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_reader_orientation_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 3: Update ROW ONE docs**

Add after the `## Editorial Synthesis` section and before `## Generated Files`:

```markdown
## Reader Orientation

ROW ONE includes a deterministic reader orientation layer for the generated
static site. The homepage renders edition contents with section jump links and
current story counts. Story cards include lightweight story-card metadata such
as section, source, date, and evidence count. Detail pages include a back to
section link so readers can return to the relevant homepage section.

This remains presentation-only. Reader orientation does not change ranking,
scoring, story IDs, source collection, JSON contract semantics, or publishing.
```

- [ ] **Step 4: Run docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: PASS.

## Task 6: Full Verification, Reviews, Commit, And Push

**Files:**
- Create: `docs/reviews/claude-code-stage-262-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-262-code-review.md`
- Create if needed: `docs/reviews/claude-code-stage-262-code-rereview-prompt.md`
- Create if needed: `docs/reviews/claude-code-stage-262-code-rereview.md`
- Create: `docs/reviews/claude-code-stage-262-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-262-release-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen ruff format src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py
uv --no-config run --frozen pytest tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/row_one src/fashion_radar/cli.py tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py
```

Expected: PASS.

- [ ] **Step 2: Run full verification**

Run:

```bash
git diff --check
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen python -m build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen python scripts/check_first_run_smoke.py
```

Expected: PASS.

- [ ] **Step 3: Request Claude Code code review**

Use:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-262-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-262-code-review.md
rm -f "$tmp_review"
```

Fix all Critical and Important findings. If fixes are needed, create a
rereview prompt and capture
`docs/reviews/claude-code-stage-262-code-rereview.md`.

- [ ] **Step 4: Run full verification again**

Run the full verification commands from Step 2 after review fixes.

Expected: PASS.

- [ ] **Step 5: Request Claude Code release review**

Use:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-262-release-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-262-release-review.md
rm -f "$tmp_review"
```

Fix all Critical and Important findings before commit.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add docs/row-one.md docs/reviews/claude-code-stage-262-*.md docs/reviews/opencode-stage-262-*.md docs/superpowers/plans/2026-07-02-stage-262-row-one-reader-orientation-plan.md docs/superpowers/specs/2026-07-02-stage-262-row-one-reader-orientation-design.md src/fashion_radar/row_one/templates.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_row_one_render.py
git commit -m "Stage 262: add ROW ONE reader orientation"
git push origin main
git status --short --untracked-files=all
git log -1 --oneline
```

Expected: commit and push succeed, status is clean.

- [ ] **Step 7: Handoff Summary**

After push, report:

- repo status;
- latest commit;
- changed capability;
- verified commands and results;
- review artifacts;
- uncommitted files;
- known deferred minors;
- next step.
