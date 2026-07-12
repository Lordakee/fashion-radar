# Stage 383 Daily Local Synthesis Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Daily Local Synthesis Brief to the ROW ONE homepage so the daily site gives a compact cross-article editorial read from already saved local article text, not only article links, lanes, maps, and timelines.

**Architecture:** Add a deterministic homepage builder that reuses current-edition `RowOneStory` objects, current-edition `RowOneLocalArticle` sidecars, existing bare local article page hrefs, and Stage 382 per-article synthesis candidates to produce a small index-page synthesis section. Render it only inside `index.html`, after the Daily Local Article Intelligence Brief and before the Daily Local Saved Article Organizer, without creating JSON artifacts, routes, schemas, app/runtime/manifest contracts, source collection behavior, scraping behavior, LLM behavior, scheduling behavior, connector behavior, analytics behavior, recommendation behavior, personalization behavior, or compliance-review product behavior.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, deterministic text helpers, Stage 382 local article synthesis builder, `templates.py` server-rendered HTML helpers, pytest, ruff, uv with frozen `--no-config` verification commands.

---

## Product Gap

Stage 370 already gives the homepage a Daily Local Article Intelligence Brief with entity lanes, article cards, and local routes. Stages 371, 372, 376, and 382 improved daily reading organization and per-article synthesis. The remaining homepage gap is an editorial "what does today add up to?" layer: readers can see many organized modules, but they do not yet get one short cross-article read that names the strongest daily thesis, the evidence mix, and the best next local article route. A parallel read-only review suggested an alternate insertion point after Daily Local Reading Itinerary; this plan intentionally keeps the first implementation closer to the article-intelligence cluster, after Daily Local Article Intelligence Brief and before Daily Local Saved Article Organizer, so review should explicitly validate that placement before implementation.

Stage 383 should close that gap without becoming a new data contract or summary engine. It should assemble a brief from fields already stored in the current edition and saved local article sidecars, with deterministic fallback order and strict generated-site-only boundaries.

## Scope Decision From Pre-Plan Exploration

- Add a new builder module: `src/fashion_radar/row_one/daily_local_synthesis_brief.py`.
- Add a new homepage-only HTML section inside `index.html`.
- Place the section after `{daily_local_article_intelligence_brief_section}` and before `{daily_local_saved_article_organizer_section}` in `render_index_html(...)`. This is a deliberate first-pass placement: it turns the intelligence brief into a compact daily judgment before the reader reaches the saved-article organizer. Plan review must challenge this if the existing homepage flow would be clearer after Daily Local Reading Itinerary instead.
- Reuse existing current-edition story order, current-edition saved local articles, generated local article page hrefs, and Stage 382 `build_row_one_local_article_synthesis_brief(...)`.
- Keep the brief distinct from existing homepage surfaces:
  - do not render entity lanes already handled by Daily Local Article Intelligence Brief;
  - do not render source maps already handled by Daily Local Coverage Map / Source Desk;
  - do not render chronological rows already handled by Daily Local News Timeline;
  - do not render reading sequence cards already handled by Daily Local Reading Itinerary;
  - do not render raw article bodies or full paragraphs on the homepage.
- Use at most three article-backed cards plus one compact opening read.
- Avoid proof-like claims such as `confirmed`, `proves`, `demand proof`, or `coverage verified`; use conservative copy such as `local read`, `connects`, `suggests`, and `article-backed`.
- Use existing story/local-article text only.
- Do not call an LLM.
- Do not fetch, scrape, collect, match, score, rank, schedule, personalize, or recommend anything.
- Do not add compliance-review product features.
- Do not add social connectors or source adapters.

## File Map

- Create `src/fashion_radar/row_one/daily_local_synthesis_brief.py`
  - Add frozen dataclasses for the homepage synthesis brief and article cards.
  - Add `build_row_one_daily_local_synthesis_brief(edition, local_articles_by_story_id, article_hrefs_by_story_id)`.
  - Reuse `build_row_one_local_article_synthesis_brief(...)` to get article-level synthesis candidates.
  - Normalize, dedupe, and cap text deterministically.
  - Validate local article/story ID alignment through the Stage 382 builder and the existing bare local article page href map. Store bare page hrefs in builder cards; prepend `articles/` only in the template when rendering homepage links.
- Modify `src/fashion_radar/row_one/render.py`
  - Build `daily_local_synthesis_brief` after local article page hrefs are known.
  - Pass it to `render_index_html(...)`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import the new dataclasses.
  - Add a `daily_local_synthesis_brief` parameter to `render_index_html(...)`.
  - Render the section between Daily Local Article Intelligence Brief and Daily Local Saved Article Organizer.
  - Add `_render_daily_local_synthesis_brief(...)` and child helpers.
  - Add CSS selectors for `.daily-local-synthesis-brief` and children, including mobile fallback.
- Create `tests/test_row_one_daily_local_synthesis_brief.py`
  - Add focused builder tests.
- Modify `tests/test_row_one_render.py`
  - Add render ordering, escaping, CSS, homepage-only placement, and JSON contract-leak tests.
- Modify `tests/test_workflows.py`
  - Extend generated contract and artifact denylists.
  - Add a Stage 383 generated-site-only sentinel test.
- Modify `tests/test_row_one_docs.py`
  - Add docs boundary test.
- Modify `README.md` and `docs/row-one.md`
  - Add one Stage 383 generated-site-only boundary paragraph above Stage 382.
- Create review artifacts under `docs/reviews/`
  - `claude-code-stage-383-plan-review.md`
  - `opencode-stage-383-plan-review.md`
  - `claude-code-stage-383-code-review.md`
  - `opencode-stage-383-code-review.md`
  - Rereview files only when Critical or Important findings require fixes.

## Internal Builder Model

These frozen dataclasses are internal Python render models only; they are not app-facing, JSON, schema, route, runtime, manifest, connector, analytics, personalization, recommendation, or compliance-review contracts.

Add:

```python
@dataclass(frozen=True)
class RowOneDailyLocalSynthesisBriefCard:
    title: LocalizedText
    source_name: str
    href: str
    read: LocalizedText
    adds: LocalizedText
    route_label: LocalizedText


@dataclass(frozen=True)
class RowOneDailyLocalSynthesisBrief:
    title: LocalizedText
    dek: LocalizedText
    opening_read: LocalizedText
    thesis: LocalizedText
    article_count: int
    source_count: int
    card_count: int
    cards: tuple[RowOneDailyLocalSynthesisBriefCard, ...]
    basis_note: LocalizedText
```

The builder is:

```python
def build_row_one_daily_local_synthesis_brief(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalSynthesisBrief | None:
    ...
```

The builder returns `None` when fewer than two safe, current-edition, locally saved articles can produce meaningful article-level synthesis cards. This keeps the homepage synthesis from pretending one article is a daily pattern.

## Builder Rules

- `title`:
  - English: `Daily Local Synthesis Brief`
  - Chinese: `每日本地综合简报`
- `dek`:
  - English: `A cross-article read assembled from today's saved local text.`
  - Chinese: `基于今日已保存本地正文整理出的跨文章判断。`
- Eligible articles:
  - Iterate `edition.stories` in current edition order.
  - Require `story.id` in `local_articles_by_story_id`.
  - Require `story.id` in `article_hrefs_by_story_id`.
  - Require the raw href map value to be a bare filename, not a prefixed path: one `PurePosixPath` part only, ending in `.html`, no whitespace, no `..`, no absolute path, no query string, no fragment, no URL scheme, stem equal to the current `story.id`, and `safe_local_article_story_id(stem)` true. Values like `articles/<story-id>.html` are invalid at the builder input layer because `article_hrefs_by_story_id` stores bare filenames such as `<story-id>.html`.
  - Require `build_row_one_local_article_synthesis_brief(story=story, local_article=article)` to return non-`None`.
  - Skip only duplicate normalized `(title, href)` pairs and duplicate normalized `read` text. Same-title/different-href articles remain eligible if their `read` text is distinct; same-source articles remain eligible.
- Card construction:
  - `title` uses `local_article.title` or `story.headline`, normalized with Chinese fallback to English.
  - `source_name` uses the article-level synthesis brief source name, falling back to normalized story source name.
  - `href` is the safe bare local article page filename from `article_hrefs_by_story_id`, for example `<story-id>.html`. The template converts it to `articles/<story-id>.html` when rendering `index.html`.
  - `read` uses the article-level synthesis `lead`, capped to 150 characters.
  - `adds` uses the article-level synthesis `article_adds`, capped to 140 characters.
  - `route_label` is deterministic:
    - English: `Read the saved article`
    - Chinese: `阅读保存文章`
- Opening read:
  - Use the first eligible card's `read` as the daily opening anchor.
  - "First title" and "second title" mean the first two post-dedupe eligible cards in current edition order.
  - If at least two cards have different normalized `read` text, combine them into a compact daily read:
    - English: `Today’s local read connects {first title} with {second title}.`
    - Chinese: `今日本地阅读把《{first title}》与《{second title}》连接起来。`
  - Pre-truncate each title before assembly using a named constant such as `DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS = 56`.
  - Title pre-truncation should happen on a word boundary for English when possible, with `...` appended only when text is shortened. Chinese may be character-capped with the same `...` convention.
  - After assembling the opening sentence, apply the 180-character cap as a final safety net only; normal long-title cases should be handled by the per-title cap so the sentence does not cut through the second title.
  - Add a regression test with two titles longer than the per-title cap. Assert `opening_read.en` is at most 180 characters, includes both shortened titles, ends cleanly with punctuation, and does not contain an obvious mid-word second-title fragment.
  - When the combined-read branch cannot be used, the single-card fallback is the first eligible card's `read`, capped to 180 characters with the same truncation helper.
  - Use ASCII apostrophe: `Today's`.
- Thesis:
  - Prefer the first non-duplicate article-level `thesis`.
  - Fall back to the first non-duplicate article-level `article_adds`.
  - Cap to 160 characters.
  - Do not read `RowOneStory.why_it_matters` directly in the Stage 383 builder; consume only the Stage 382 article synthesis fields (`lead`, `thesis`, and `article_adds`).
- Cards:
  - Render at most 3 cards.
  - Require at least 2 cards.
  - Dedupe by normalized `(title, href)` and normalized `read`. Do not dedupe by source name: multiple current-edition stories from the same source are valid. Use named constants for all card/text/reference limits; do not scatter magic numbers.
  - Preserve current edition order; do not rank by computed heat or engagement.
- Counts:
  - `article_count` is the number of post-dedupe eligible article-level synthesis candidates before the three-card cap is applied.
  - `source_count` is the number of distinct normalized source names among post-dedupe eligible article-level synthesis candidates before the three-card cap is applied.
  - `card_count` is `len(cards)`.
- `basis_note`:
  - English: `Built from current-edition ROW ONE stories and saved local article synthesis already generated for article pages.`
  - Chinese: `基于当前版本 ROW ONE 故事与文章页已生成的本地文章综合简报整理。`
- Chinese fallback:
  - For localized fields, use Chinese text when present.
  - If Chinese text is absent or misaligned, fall back to English text.
  - Never produce blank Chinese spans when English text exists.

## Render Rules

- Build the brief in `render_row_one_site(...)` after `local_article_page_hrefs_by_story_id` is available:

```python
daily_local_synthesis_brief = build_row_one_daily_local_synthesis_brief(
    edition,
    local_articles_by_story_id,
    local_article_page_hrefs_by_story_id,
)
```

- Add `daily_local_synthesis_brief` to the `render_index_html(...)` call.
- Add `daily_local_synthesis_brief: RowOneDailyLocalSynthesisBrief | None = None` to `render_index_html(...)`.
- Render after `{daily_local_article_intelligence_brief_section}` and before `{daily_local_saved_article_organizer_section}`:

```python
{daily_local_article_intelligence_brief_section}
{daily_local_synthesis_brief_section}
{daily_local_saved_article_organizer_section}
```

- Omit the entire section when the builder returns `None`.
- HTML structure:

```html
<section class="daily-local-synthesis-brief" aria-labelledby="daily-local-synthesis-brief-title">
  <div class="daily-local-synthesis-brief-header">
    <h2 id="daily-local-synthesis-brief-title">...</h2>
    <p>...</p>
  </div>
  <div class="daily-local-synthesis-brief-metrics">...</div>
  <p class="daily-local-synthesis-brief-opening">...</p>
  <p class="daily-local-synthesis-brief-thesis">...</p>
  <div class="daily-local-synthesis-brief-grid">
    <article class="daily-local-synthesis-brief-card">...</article>
  </div>
  <p class="daily-local-synthesis-brief-basis">...</p>
</section>
```

- Escape every interpolated value with `_esc(...)`.
- Validate rendered card hrefs with a dedicated local template helper for homepage links:
  - accept only `articles/<safe-story-id>.html` after the template prepends `articles/` to the builder's bare filename;
  - reject `articles/index.html`, absolute URLs, query strings, fragments, whitespace, URL schemes, and `..`;
  - do not add outbound URLs.
- The builder-layer href helper validates bare filenames only. The render-layer href helper validates the prefixed homepage href. Keep these two layers explicit so the builder does not reject every real `article_hrefs_by_story_id` entry.
- CSS should follow existing homepage generated-site-only section patterns:
  - `.daily-local-synthesis-brief`
  - `.daily-local-synthesis-brief-header`
  - `.daily-local-synthesis-brief-metrics`
  - `.daily-local-synthesis-brief-opening`
  - `.daily-local-synthesis-brief-thesis`
  - `.daily-local-synthesis-brief-grid`
  - `.daily-local-synthesis-brief-card`
  - `.daily-local-synthesis-brief-basis`
  - mobile fallback under `@media (max-width: 760px)`.

## Tests

### Builder Tests

Create `tests/test_row_one_daily_local_synthesis_brief.py`.

Add tests:

- `test_build_daily_local_synthesis_brief_uses_current_edition_saved_articles`
  - Build an edition with at least three stories and local articles.
  - Assert title/dek/basis note.
  - Assert two or three cards are produced in edition order.
  - Assert `article_count`, `source_count`, and `card_count`.
  - Assert card reads and adds come from Stage 382 article synthesis output.
- `test_build_daily_local_synthesis_brief_requires_two_articles`
  - Provide only one eligible local article.
  - Assert builder returns `None`.
- `test_build_daily_local_synthesis_brief_filters_unsafe_or_missing_hrefs`
  - Include raw href map values `https://example.com`, `index.html`, `../unsafe.html`, `<story-id>.html?x=1`, `<story-id>.html#local-article-paragraph-1`, `articles/<story-id>.html`, `<other-story-id>.html`, a whitespace href, and one safe bare `<story-id>.html` href.
  - Assert unsafe cards are skipped for the intended reasons and the section returns `None` if fewer than two safe bare filename hrefs remain.
- `test_build_daily_local_synthesis_brief_dedupes_titles_hrefs_and_reads`
  - Provide duplicate href/title/read candidates and multiple same-source candidates.
  - Assert duplicate `(title, href)` pairs and duplicate reads do not inflate cards.
  - Assert same-title/different-href articles are kept when their reads are distinct.
  - Assert same-source-but-distinct articles are kept.
- `test_build_daily_local_synthesis_brief_handles_missing_zh`
  - Provide English-only local article fields.
  - Assert zh fields fall back to English.
- `test_build_daily_local_synthesis_brief_returns_none_when_all_articles_lack_synthesis`
  - Provide articles whose Stage 382 synthesis builder returns `None`.
  - Assert the daily builder returns `None`.
- `test_build_daily_local_synthesis_brief_caps_text_and_cards`
  - Provide long text, two titles longer than `DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS`, and more than three eligible articles.
  - Assert card text caps, per-title opening truncation, final opening cap, clean punctuation, and `len(cards) == 3`.

### Render Tests

Modify `tests/test_row_one_render.py`.

Add tests:

- `test_render_index_includes_daily_local_synthesis_brief_between_intelligence_and_organizer`
  - Render an index with eligible local articles.
  - Assert the section appears after `.daily-local-article-intelligence-brief` and before `.daily-local-saved-article-organizer`.
  - Assert title, dek, opening, thesis, basis, metrics, and cards render.
  - Assert rendered card links are prefixed as `articles/<story-id>.html` even though builder cards store bare filenames.
- `test_render_daily_local_synthesis_brief_escapes_and_filters_hrefs`
  - Monkeypatch the builder to return one safe bare href card and unsafe rendered href candidates.
  - Assert `<script>` is escaped.
  - Assert fragmentless safe `articles/<story-id>.html` renders.
  - Assert unsafe hrefs and labels do not render.
- `test_render_row_one_site_writes_daily_local_synthesis_brief_only_on_homepage`
  - Render the site.
  - Assert section appears in `index.html`.
  - Assert it does not appear in `articles/index.html`, `articles/<story-id>.html`, detail pages, `data/edition.json`, `data/manifest.json`, `data/runtime.json`, or `data/articles/*.json`.
- `test_row_one_css_includes_daily_local_synthesis_brief_styles`
  - Assert all selectors and mobile fallback exist.

### Workflow Tests

Modify `tests/test_workflows.py`.

Add a Stage 383 sentinel:

- Monkeypatch `_render_daily_local_synthesis_brief` to return `STAGE_383_DAILY_LOCAL_SYNTHESIS_BRIEF_SENTINEL`.
- Run `write_row_one_site_files(...)` with at least two local article sidecars.
- Assert sentinel appears only in `index.html`.
- Assert sentinel does not appear in `articles/index.html`, `articles/*.html`, `details/*.html`, `data/edition.json`, `data/manifest.json`, `data/runtime.json`, or `data/articles/*.json`.
- Assert no standalone artifacts exist for stems:
  - `daily-local-synthesis-brief`
  - `local-synthesis-brief`
  - `daily-synthesis-brief`
  - `daily_local_synthesis_brief`
  - `local_synthesis_brief`
  - `daily_synthesis_brief`

Extend existing generated contract denylists with those same names plus:

- `RowOneDailyLocalSynthesisBrief`
- `RowOneDailyLocalSynthesisBriefCard`
- `Daily Local Synthesis Brief`
- `每日本地综合简报`

### Docs Tests

Modify `tests/test_row_one_docs.py`.

Add one docs boundary paragraph test. The exact paragraph should appear in both `README.md` and `docs/row-one.md`, above Stage 382. Assert `text.index(paragraph) < text.index("Stage 382 adds")`.

```text
Stage 383 adds generated-site-only Daily Local Synthesis Brief copy inside `index.html` after the Daily Local Article Intelligence Brief and before the Daily Local Saved Article Organizer; it reuses current-edition ROW ONE stories, current-edition saved local article sidecars, existing generated local article page routes, and existing Local Article Synthesis Brief text to give readers a compact cross-article daily interpretation without changing app-facing contracts; it does not create `data/daily-local-synthesis-brief.json`, does not create `data/local-synthesis-brief.json`, does not create `data/daily-synthesis-brief.json`, does not create `daily-local-synthesis-brief.html`, does not create `local-synthesis-brief.html`, does not create `daily-synthesis-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
```

Add stale phrase checks for:

- `creates data/daily-local-synthesis-brief.json`
- `writes data/daily-local-synthesis-brief.json`
- `creates daily-local-synthesis-brief.html`
- `writes daily-local-synthesis-brief.html`
- `adds source collection`
- `adds fetching`
- `adds scraping`
- `adds matching`
- `adds extraction`
- `adds scoring`
- `adds ranking`
- `adds llm`
- `adds connector`
- `adds scheduling`
- `adds analytics`
- `adds personalization`
- `adds recommendation`
- `adds compliance-review`

## Implementation Tasks

### Task 1: Builder RED Tests

**Files:**
- Create: `tests/test_row_one_daily_local_synthesis_brief.py`

- [ ] Write fixture helpers for `LocalizedText`, `RowOneStory`, `RowOneLocalArticle`, local article brief sections, local article content sections, and article href maps.
- [ ] Write the six builder tests listed above.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_synthesis_brief.py -q
```

Expected: fails because `fashion_radar.row_one.daily_local_synthesis_brief` does not exist.

### Task 2: Builder Implementation

**Files:**
- Create: `src/fashion_radar/row_one/daily_local_synthesis_brief.py`
- Test: `tests/test_row_one_daily_local_synthesis_brief.py`

- [ ] Add the frozen dataclasses.
- [ ] Add `build_row_one_daily_local_synthesis_brief(...)`.
- [ ] Add helpers for safe href validation, candidate iteration, localized text cleanup, title/source fallback, text truncation, and normalized dedupe keys.
- [ ] Reuse `build_row_one_local_article_synthesis_brief(...)` for per-article synthesis.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_synthesis_brief.py -q
```

Expected: passes.

### Task 3: Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Add helper `_daily_local_synthesis_brief_html(...)`.
- [ ] Add the four render/CSS/generated-site-only tests listed above.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "daily_local_synthesis_brief" -q
```

Expected: fails because render integration and CSS do not exist.

### Task 4: Render Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Test: `tests/test_row_one_render.py`

- [ ] Import the new builder in `render.py`.
- [ ] Build `daily_local_synthesis_brief` after `local_article_page_hrefs_by_story_id`.
- [ ] Pass it to `render_index_html(...)`.
- [ ] Import the dataclasses in `templates.py`.
- [ ] Add the `render_index_html(...)` parameter and render section variable.
- [ ] Insert the section after Daily Local Article Intelligence Brief and before Daily Local Saved Article Organizer.
- [ ] Add `_render_daily_local_synthesis_brief(...)` and card/metric/href helpers.
- [ ] Add CSS and mobile fallback.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "daily_local_synthesis_brief" -q
```

Expected: passes.

### Task 5: Workflow and Docs Boundary Tests

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] Add the Stage 383 workflow sentinel and artifact denylist.
- [ ] Extend generated contract denylists.
- [ ] Add the Stage 383 docs paragraph test.
- [ ] Add the exact Stage 383 paragraph to README/docs above Stage 382.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_stage_383_daily_local_synthesis_brief_stays_generated_site_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_383_daily_local_synthesis_brief_boundary \
  -q
```

Expected: passes.

### Task 6: Focused and Broad Verification

**Files:**
- All Stage 383 files.

- [ ] Run focused Stage 383 suite:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_daily_local_synthesis_brief.py \
  tests/test_row_one_render.py -k "daily_local_synthesis_brief" \
  tests/test_workflows.py::test_stage_383_daily_local_synthesis_brief_stays_generated_site_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_383_daily_local_synthesis_brief_boundary \
  -q
```

- [ ] Run broader related suite:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_daily_local_synthesis_brief.py \
  tests/test_row_one_local_article_synthesis_brief.py \
  -q
```

### Task 7: Required Reviews

**Files:**
- Create: `docs/reviews/claude-code-stage-383-code-review.md`
- Create: `docs/reviews/opencode-stage-383-code-review.md`
- Create rereview artifacts only if Critical/Important findings require fixes.

- [ ] Run Claude Code review:

```bash
claude --print --effort max --add-dir /home/ubuntu/fashion-radar < /tmp/stage383-code-review-prompt.md > docs/reviews/claude-code-stage-383-code-review.md
```

- [ ] Run opencode review:

```bash
NO_COLOR=1 opencode run --model zhipuai-coding-plan/glm-5.2 --variant max "$(cat /tmp/stage383-code-review-prompt.md)" > docs/reviews/opencode-stage-383-code-review.md
```

- [ ] Remove any opencode process chatter before the first review heading.
- [ ] Fix every Critical and Important finding before final gates.

### Task 8: Final Frozen Gates and Commit

**Files:**
- All Stage 383 files.

- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
git diff --cached --check
```

- [ ] Commit:

```bash
git add README.md docs/row-one.md docs/reviews docs/superpowers/plans \
  src/fashion_radar/row_one/daily_local_synthesis_brief.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_daily_local_synthesis_brief.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py
git commit -m "Stage 383: add daily local synthesis brief"
git push origin main
```

## Review Requirements Before Implementation

Before any implementation code is written:

- Run Claude Code plan review with `--effort max`.
- Run opencode plan review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.
- Save review artifacts under `docs/reviews/`.
- Remove review process chatter from artifacts.
- Fix every Critical and Important plan finding.
- Create rereview artifacts when Critical or Important findings are fixed.

## Acceptance Criteria

- `index.html` has a Daily Local Synthesis Brief after Daily Local Article Intelligence Brief and before Daily Local Saved Article Organizer when at least two eligible saved local articles exist.
- The section is deterministic and built only from current-edition stories, saved local article sidecars, generated local article page hrefs, and Stage 382 article synthesis output.
- The section renders no full article bodies and no outbound article URLs.
- The section does not appear in `articles/index.html`, `articles/<story-id>.html`, detail pages, or any JSON payload.
- No standalone Stage 383 artifact files are created.
- No app contract, schema, runtime, manifest, source collection, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, analytics, personalization, recommendation, or compliance-review behavior changes.
- Focused and broad tests pass.
- Claude Code and opencode code reviews have no unresolved Critical or Important findings.
- Full frozen gates pass before commit and push.
