# Stage 387 Daily Local Brand, Product & People Signal Digest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Add a generated-site-only ROW ONE homepage digest that merges existing saved local article brand, product, and people references into traceable daily coverage signals.

**Architecture:** A new pure Python builder receives the current edition, already-loaded local article sidecars, and already-generated article hrefs. It aggregates only existing content_sections[*].items[*].references into deterministic Brands, Products, and People buckets, retaining up to three same-site saved-content-section supports for each entity. render_row_one_site() builds the optional payload after article hrefs exist and passes it solely to render_index_html(); templates.py escapes content and revalidates every href before writing only the existing index.html.

**Tech Stack:** Python 3.12 dataclasses, existing ROW ONE Pydantic local-article models, server-rendered HTML/CSS, pytest, ruff, uv frozen/no-config checks.

---

## Scope and Invariants

- Add the homepage-only Daily Local Brand, Product & People Signal Digest section.
- Reuse current-edition stories, current-edition saved local article sidecars, existing generated local article page routes, content-section items, references, and existing local-article-content-section-N anchors.
- Keep presentation in current edition / section / item / reference first-seen order. Counts are saved-coverage facts only; do not score, rank, infer trend heat, or call an external service.
- Show at most three buckets, five merged entities per bucket, and three supports per entity.
- Omit the digest unless at least two valid current-edition saved local articles contribute usable allowed references.
- Render only in existing index.html, after Daily Saved Text Takeaways and before Daily Local Saved Article Organizer.
- Do not add JSON artifacts, standalone pages, route families, app/runtime/manifest/schema fields, article sidecars, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM calls, connectors, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.

## File Map

- Create src/fashion_radar/row_one/daily_local_brand_product_people_signal_digest.py
  - Own output dataclasses, type-to-bucket mapping, safe local href construction, aggregation, first-seen caps, and evidence excerpt normalization.
- Create tests/test_row_one_daily_local_brand_product_people_signal_digest.py
  - Exercise the pure builder with local article fixtures.
- Modify src/fashion_radar/row_one/render.py
  - Build the payload after _local_article_page_hrefs_by_story_id(...); pass it only to render_index_html(...).
- Modify src/fashion_radar/row_one/templates.py
  - Import output types, add the optional index renderer argument, render and validate the homepage-only section, and add responsive CSS.
- Modify tests/test_row_one_render.py
  - Cover rendered output, escaping, href rejection, bilingual markup, omission, and exact homepage section order.
- Modify tests/test_workflows.py
  - Add contract denylist terms, no-artifact stems, and a Stage 387 homepage-only sentinel.
- Modify README.md, docs/row-one.md, and tests/test_row_one_docs.py
  - State the exact generated-site-only boundary and non-goals.
- Create review artifacts under docs/reviews
  - Capture Stage 387 plan and code review summaries without credentials or raw tool logs.

## Task 1: RED builder tests

**Files:**
- Create: tests/test_row_one_daily_local_brand_product_people_signal_digest.py

- [ ] **Step 1: Write shared fixtures for current-edition stories, matching local articles, structured references, and safe page hrefs.**

~~~python
AS_OF = datetime(2026, 7, 13, 4, 0, tzinfo=UTC)

def _reference(name: str, reference_type: str) -> RowOneReference:
    return RowOneReference(name=name, type=reference_type, label=reference_type)

def _item(
    label: str,
    body: str,
    *references: RowOneReference,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label),
        body=_lt(body),
        references=list(references),
        paragraph_indices=[0],
    )
~~~

- [ ] **Step 2: Write an aggregation test for a repeated brand and product across two saved articles.**

~~~python
digest = build_row_one_daily_local_brand_product_people_signal_digest(
    _edition([_story(first_id), _story(second_id)]),
    {
        first_id: _article(
            first_id,
            sections=[
                _section(
                    "brand_signals",
                    _item(
                        "The Row",
                        "A saved local note.",
                        _reference("The Row", "brand"),
                        _reference("Margaux", "bag"),
                        _reference("Mary-Kate Olsen", "designer"),
                    ),
                )
            ],
        ),
        second_id: _article(
            second_id,
            source_name="WWD",
            sections=[
                _section(
                    "entities",
                    _item(
                        "The Row",
                        "A second saved local note.",
                        _reference("The Row", "brand"),
                        _reference("Margaux", "bag"),
                    ),
                )
            ],
        ),
    },
    {first_id: f"{first_id}.html", second_id: f"{second_id}.html"},
)

assert digest is not None
assert [bucket.key for bucket in digest.buckets] == ["brands", "products", "people"]
assert digest.buckets[0].items[0].name.en == "The Row"
assert digest.buckets[0].items[0].article_count == 2
assert digest.buckets[0].items[0].source_count == 2
assert digest.buckets[0].items[0].supports[0].href == (
    f"articles/{first_id}.html#local-article-content-section-1"
)
~~~

- [ ] **Step 3: Add sparse-input and safety tests.**

~~~python
assert build_row_one_daily_local_brand_product_people_signal_digest(
    _edition([_story(first_id)]),
    {first_id: _article(first_id)},
    {first_id: f"{first_id}.html"},
) is None

assert build_row_one_daily_local_brand_product_people_signal_digest(
    _edition([_story(first_id), _story(second_id)]),
    {
        first_id: _article("other-story-1234567890"),
        second_id: _article(second_id),
    },
    {
        first_id: f"{first_id}.html",
        second_id: "https://example.com/unsafe.html",
    },
) is None
~~~

Assert that unsupported event references produce no bucket, repeated references in
one content section create one support, and the configured item/support caps keep
the first-seen entries. Assert a label and excerpt with only one language uses
the available language for both output values.

- [ ] **Step 4: Run the RED command.**

Run:

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_brand_product_people_signal_digest.py -q
~~~

Expected: import failure because the builder module does not yet exist.

## Task 2: Implement the pure builder

**Files:**
- Create: src/fashion_radar/row_one/daily_local_brand_product_people_signal_digest.py
- Modify: tests/test_row_one_daily_local_brand_product_people_signal_digest.py

- [ ] **Step 1: Add bounded immutable output types.**

~~~python
DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_ITEM_LIMIT = 5
DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SUPPORT_LIMIT = 3
DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_EXCERPT_CHARS = 170
_BUCKET_ORDER = ("brands", "products", "people")

@dataclass(frozen=True)
class RowOneDailyLocalBrandProductPeopleSignalDigestSupport:
    title: LocalizedText
    source_name: str
    label: LocalizedText
    excerpt: LocalizedText
    href: str

@dataclass(frozen=True)
class RowOneDailyLocalBrandProductPeopleSignalDigestItem:
    name: LocalizedText
    reference_type: str
    article_count: int
    source_count: int
    supports: tuple[RowOneDailyLocalBrandProductPeopleSignalDigestSupport, ...]
~~~

Add matching Bucket and top-level Digest dataclasses with bilingual title/deck
and factual article/source/entity counts.

- [ ] **Step 2: Implement safe deterministic aggregation.**

~~~python
def build_row_one_daily_local_brand_product_people_signal_digest(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalBrandProductPeopleSignalDigest | None:
    drafts = {bucket_key: {} for bucket_key in _BUCKET_ORDER}
    contributing_story_ids: set[str] = set()
    contributing_source_keys: set[str] = set()

    for story in edition.stories:
        article = _valid_article(story.id, local_articles_by_story_id)
        page_href = _safe_article_page_href(
            story.id,
            article_hrefs_by_story_id.get(story.id),
        )
        if article is None or page_href is None:
            continue
        if _add_article_references(drafts, story, article, page_href):
            contributing_story_ids.add(story.id)
            contributing_source_keys.add(_source_key(article.source_name or story.source_name))

    if len(contributing_story_ids) < 2:
        return None
    return _build_digest(drafts, contributing_story_ids, contributing_source_keys)
~~~

The article walker must preserve story, section, item, and reference order; only
map existing allowed type terms to the three buckets; deduplicate one entity per
story/section; use item body then section body as evidence text; create only
articles/<safe-story-id>.html#local-article-content-section-N supports; and
retain at most three supports per entity. _build_digest() keeps dictionary
insertion order and must not calculate a score or sort by coverage counts.

- [ ] **Step 3: Add local text and href guards.**

~~~python
def _safe_article_page_href(story_id: str, value: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(value, str):
        return None
    path = PurePosixPath(value)
    if value != value.strip() or path.is_absolute() or len(path.parts) != 1:
        return None
    if path.name != f"{story_id}.html" or not path.name.endswith(".html"):
        return None
    return path.name
~~~

Use normalize_row_one_paragraph(), bilingual fallback, and a bounded
_truncate(). Reject blank labels/references/text, invalid source identities,
malformed story IDs, traversal, URLs, whitespace, query strings, and invalid
fragments.

- [ ] **Step 4: Run the builder tests until green.**

Run:

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_brand_product_people_signal_digest.py -q
~~~

Expected: all new builder tests pass.

## Task 3: RED index-render tests

**Files:**
- Modify: tests/test_row_one_render.py

- [ ] **Step 1: Add imports and a digest fixture.**

~~~python
from fashion_radar.row_one.daily_local_brand_product_people_signal_digest import (
    RowOneDailyLocalBrandProductPeopleSignalDigest,
    RowOneDailyLocalBrandProductPeopleSignalDigestBucket,
    RowOneDailyLocalBrandProductPeopleSignalDigestItem,
    RowOneDailyLocalBrandProductPeopleSignalDigestSupport,
)
~~~

Include bilingual text, a hostile entity/excerpt value for escaping, one valid
local content-section anchor, and an unsafe href variant.

- [ ] **Step 2: Add a failing section-order and safe-output test.**

~~~python
html = render_index_html(
    edition,
    daily_local_saved_text_takeaways=_daily_local_saved_text_takeaways_fixture(),
    daily_local_brand_product_people_signal_digest=(
        _daily_local_brand_product_people_signal_digest_fixture()
    ),
    daily_local_saved_article_organizer=(
        _daily_local_saved_article_organizer_fixture()
    ),
)

assert '<section class="daily-local-brand-product-people-signal-digest"' in html
assert html.index("daily-local-saved-text-takeaways") < html.index(
    "daily-local-brand-product-people-signal-digest"
) < html.index("daily-local-saved-article-organizer")
assert 'href="articles/the-row-signal-1234567890.html#local-article-content-section-1"' in html
assert "&lt;entity&gt;" in html
~~~

- [ ] **Step 3: Add failing href-rejection and omission tests.**

~~~python
assert "https://unsafe.example/" not in html
assert _daily_local_brand_product_people_signal_digest_section_html(
    render_index_html(
        edition,
        daily_local_brand_product_people_signal_digest=None,
    )
) == ""
~~~

- [ ] **Step 4: Run the RED selection.**

Run:

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k brand_product_people_signal_digest -q
~~~

Expected: failure because render_index_html() lacks the argument and renderer.

## Task 4: Integrate the homepage-only renderer

**Files:**
- Modify: src/fashion_radar/row_one/render.py
- Modify: src/fashion_radar/row_one/templates.py
- Modify: tests/test_row_one_render.py

- [ ] **Step 1: Build and pass the optional payload in render.py.**

~~~python
daily_local_brand_product_people_signal_digest = (
    build_row_one_daily_local_brand_product_people_signal_digest(
        edition,
        local_articles_by_story_id,
        local_article_page_hrefs_by_story_id,
    )
)
~~~

Pass it only in the existing render_index_html() call. Do not add it to an app
payload, JSON writer, detail renderer, or article renderer.

- [ ] **Step 2: Add the optional index argument and exact render location.**

~~~python
def render_index_html(
    edition: RowOneEdition,
    *,
    daily_local_saved_text_takeaways: RowOneDailyLocalSavedTextTakeaways | None = None,
    daily_local_brand_product_people_signal_digest: (
        RowOneDailyLocalBrandProductPeopleSignalDigest | None
    ) = None,
    daily_local_saved_article_organizer: (
        RowOneDailyLocalSavedArticleOrganizer | None
    ) = None,
) -> str:
    ...
~~~

Create the section variable after daily_local_saved_text_takeaways_section and
before daily_local_saved_article_organizer_section. Insert that variable in the
page f-string at the same position.

- [ ] **Step 3: Add safe HTML helpers and responsive styles.**

~~~python
def _render_daily_local_brand_product_people_signal_digest(
    digest: RowOneDailyLocalBrandProductPeopleSignalDigest | None,
) -> str:
    if digest is None or not digest.buckets:
        return ""
    buckets = [
        html
        for bucket in digest.buckets
        if (
            html := _render_daily_local_brand_product_people_signal_digest_bucket(
                bucket
            )
        )
    ]
    if not buckets:
        return ""
    return (
        '<section class="daily-local-brand-product-people-signal-digest" '
        'aria-labelledby="daily-local-brand-product-people-signal-digest-title">'
        + "".join(buckets)
        + "</section>"
    )
~~~

Revalidate every support in a dedicated safe-href helper that accepts exactly
articles/<safe-story-id>.html#local-article-content-section-N. Escape every
interpolated value with _esc. Add a bounded grid using existing ROW ONE
typography/color conventions and collapse it to one column at the existing
mobile breakpoint.

- [ ] **Step 4: Run focused renderer tests until green.**

Run:

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k brand_product_people_signal_digest -q
~~~

Expected: all selected render tests pass.

## Task 5: Enforce generated-site-only boundaries

**Files:**
- Modify: tests/test_workflows.py

- [ ] **Step 1: Add contract and artifact denylist values.**

Add these terms to the generated-contract payload assertions and no-artifact
stem loop:

~~~python
"daily_local_brand_product_people_signal_digest",
"daily_brand_product_people_signal_digest",
"brand_product_people_signal_digest",
"daily-local-brand-product-people-signal-digest",
"daily-brand-product-people-signal-digest",
"brand-product-people-signal-digest",
"Daily Local Brand Product People Signal Digest",
"Brand Product People Signal Digest",
"daily-local-brand-product-people-signals",
"brand-product-people-signals",
~~~

- [ ] **Step 2: Add a sentinel proving homepage-only emission.**

~~~python
def test_stage_387_daily_local_brand_product_people_signal_digest_stays_homepage_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    sentinel = "STAGE_387_DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SENTINEL"
    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_brand_product_people_signal_digest",
        lambda _digest: sentinel,
        raising=True,
    )
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
~~~

Collect all generated .html and .json payloads, assert the sentinel appears
only at index.html, and assert it is absent from articles/index.html, every
article page, detail page, data/edition.json, data/manifest.json,
data/runtime.json, and every data/articles/*.json payload.

- [ ] **Step 3: Run the focused workflow test.**

Run:

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k stage_387_daily_local_brand_product_people_signal_digest -q
~~~

Expected: pass.

## Task 6: Document the boundary

**Files:**
- Modify: README.md
- Modify: docs/row-one.md
- Modify: tests/test_row_one_docs.py

- [ ] **Step 1: Add the same Stage 387 paragraph directly above Stage 386 in both docs.**

~~~markdown
Stage 387 adds a generated-site-only Daily Local Brand, Product & People Signal Digest section on the ROW ONE homepage in index.html; it reuses current-edition ROW ONE stories, current-edition saved local article sidecars, existing generated local article page routes, saved content-section items, references, and local article content-section anchors to organize factual brand, product, and people coverage without changing app-facing contracts; it does not create data/daily-local-brand-product-people-signal-digest.json, does not create daily-local-brand-product-people-signal-digest.html, does not create new article-source sidecars or route families, does not alter articles/index.html, articles/<story-id>.html, detail pages, data/edition.json, data/manifest.json, or data/runtime.json, does not publish full article bodies on the homepage, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
~~~

Use the repository's normal inline-code styling in the actual docs; the plan
omits backticks only to keep the code example readable here.

- [ ] **Step 2: Add docs presence, ordering, and stale-phrase tests.**

~~~python
for text in (_read(README), _read(ROW_ONE_DOC)):
    assert paragraph in text
    assert text.index(paragraph) < text.index(
        "Stage 386 adds a generated-site-only"
    )
    stage_387_slice = text[text.index(paragraph) : text.index("Stage 386 adds")]
    assert "creates data/daily-local-brand-product-people-signal-digest.json" not in (
        _normalized(stage_387_slice)
    )
    assert "changes app-facing contracts" not in _normalized(stage_387_slice)
~~~

Also cover the established complete non-goal phrase family: artifacts, routes,
app/runtime/manifest/schema, source/fetch/scrape/match/extract/score/rank/LLM,
connector/schedule/deployment/analytics/personalization/recommendation/demand
proof/coverage verification/compliance-review.

- [ ] **Step 3: Run the focused docs test.**

Run:

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -k stage_387_daily_local_brand_product_people_signal_digest -q
~~~

Expected: pass.

## Task 7: Review, gates, commit, and push

**Files:**
- Create: docs/reviews/claude-code-stage-387-plan-review.md
- Create: docs/reviews/opencode-stage-387-plan-review.md
- Create: docs/reviews/claude-code-stage-387-code-review.md
- Create: docs/reviews/opencode-stage-387-code-review.md
- Modify: only files required by confirmed review findings.

- [ ] **Step 1: Submit the written plan before product-code changes.**

Use Claude Code with --effort max and OpenCode with
--model zhipuai-coding-plan/glm-5.2. Ask both reviewers to assess architecture,
safety boundaries, data semantics, test coverage, and conflicts with existing
ROW ONE surfaces. Record concise, credential-free review summaries. If a tool
times out, record the timeout and independent checks instead of raw logs.

- [ ] **Step 2: Run related tests after implementation.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_brand_product_people_signal_digest.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q
~~~

Expected: all selected tests pass.

- [ ] **Step 3: Submit the completed diff to both reviewers.**

Apply only specific, technically valid findings, then rerun the affected test
group and revise the review note.

- [ ] **Step 4: Run full release gates.**

~~~bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git diff --cached --check
~~~

Expected: every command exits 0.

- [ ] **Step 5: Inspect, commit, and push.**

~~~bash
git status --short
git diff --check
git add README.md docs/row-one.md docs/reviews docs/superpowers/specs docs/superpowers/plans src/fashion_radar/row_one/daily_local_brand_product_people_signal_digest.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_brand_product_people_signal_digest.py tests/test_row_one_docs.py tests/test_row_one_render.py tests/test_workflows.py
git commit -m "Stage 387: add daily brand product people signal digest"
git push origin main
~~~

Expected: the node is pushed without credentials in its diff and with a clean
post-push worktree apart from deliberately retained local-only runtime files.
