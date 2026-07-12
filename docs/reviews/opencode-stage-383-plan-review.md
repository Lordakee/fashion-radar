# Stage 383 Plan Review — opencode (GLM 5.2, max)

**Verdict: BLOCK on one Critical finding.** The plan is well-structured, within scope, and mostly faithful to established Stage 371/372/376/382 patterns, but it contains one feasibility-blocking contradiction in its href handling that will make the builder return `None` for 100% of real editions. Important and minor findings follow.

## Critical

### C1 — Href validation rule is inverted from the real href-map shape; the builder will always return `None` in production

The plan (Builder Rules, line 129; Render Rules, lines 212–215) requires the href to **start with `articles/`** and to be a relative path of the form `articles/<safe-story-id>.html`, and the unsafe-href test fixture list (lines 244–246) treats `articles/index.html`, `articles/story.html?x=1` as the realistic inputs.

The actual `local_article_page_hrefs_by_story_id` map that `render_row_one_site` builds and passes to all sibling builders stores **bare filenames** `<story-id>.html`, with **no `articles/` prefix**:

- `src/fashion_radar/row_one/render.py:443-446` — `_local_article_page_href(story_id)` returns `f"{story_id}.html"`.
- `src/fashion_radar/row_one/render.py:458-464` — `_local_article_page_hrefs_by_story_id` builds `{story.id: article_page_href}` straight from those bare values.
- `src/fashion_radar/row_one/render.py:601` — `_local_article_page_specs` sets `article_page_href = _local_article_page_href(story.id)` (bare).

Every sibling builder validates the **bare filename**, not a prefixed path, via an identical `_safe_article_page_href(story_id, href)` helper that **requires `len(path.parts) == 1`** (single path component) and returns the bare filename:

- `src/fashion_radar/row_one/daily_local_article_intelligence_brief.py:251-270`
- `src/fashion_radar/row_one/daily_local_saved_article_organizer.py:482-501`
- `src/fashion_radar/row_one/daily_local_news_timeline.py:97`
- `src/fashion_radar/row_one/daily_local_reading_itinerary.py:537`

The `articles/` prefix is added **only at render time**, by a separate `_converted_href(page_href, fragment_href)` step (e.g. `daily_local_article_intelligence_brief.py:273-284`: `return f"articles/{page_href}#{fragment}"`). The template-side validator `_safe_daily_local_article_intelligence_href` (`templates.py:14115-14143`) then re-validates the fully-formed `articles/<id>.html#fragment` shape.

**Consequence for Stage 383 as written:** `build_row_one_daily_local_synthesis_brief(...)` consumes `article_hrefs_by_story_id` (the bare-filename map). Its rule "Require href to start with `articles/`" rejects every entry → no eligible articles → "fewer than two safe ... articles" → builder returns `None` for every real edition → the headline acceptance criterion ("index.html has a Daily Local Synthesis Brief ... when at least two eligible saved local articles exist", line 525) is **unreachable**. This is a stage-wide feasibility blocker, not an edge case.

**Required fix before implementation:**

1. Split the href policy into two layers, mirroring the sibling pattern:
   - **Builder layer:** validate the bare filename via a `_safe_article_page_href(story_id, href)` equivalent (single `PurePosixPath` part, stem matches `story_id`, `safe_local_article_story_id(stem)`, ends `.html`, no whitespace, no `..`). Store the bare filename in `RowOneDailyLocalSynthesisBriefCard.href` (matching how sibling builders store `page_href`).
   - **Render layer:** prepend `articles/` when emitting the anchor (or have the builder pre-prefix and the template re-validate, but pick one). Do not require the map value itself to start with `articles/`.
2. Reuse the existing `_safe_article_page_href` by import (the plan's line 212 "must not duplicate regex allow-lists already maintained elsewhere" already points at this — the bullets that follow contradict it). There are already four near-identical copies; do not add a fifth.
3. Rewrite the unsafe-href test fixture list (line 244–246) to use realistic bare-filename inputs: `<story-id>.html` (safe), `index.html`, `../unsafe.html`, `https://example.com`, ` ` (whitespace), `<story-id>.html?x=1`, `<other-story-id>.html` (story-id mismatch). Drop the `articles/...` examples unless they are reclassified as render-layer inputs.

## Important

### I1 — Fragment policy for card hrefs is unspecified and collides with the only existing template-side validator

`_safe_daily_local_article_intelligence_href` (`templates.py:14115-14143`) **requires** a `#fragment` (`if not separator: return None`, lines 14123–14124) and only accepts `#local-article-paragraph-N` / `#local-article-content-section-N`. The plan's cards render `route_label` "Read the saved article" but never say whether the href is fragmentless `articles/<id>.html` or a deep link `articles/<id>.html#local-article-...`. If the implementer reuses the only existing template validator verbatim, every fragmentless card is dropped silently; if they write a new one, they risk duplicating the allow-list (which the plan itself forbids, line 212).

**Fix:** State the fragment policy explicitly (fragmentless is simplest and matches "Read the saved article"). Specify whether the render helper reuses `_safe_daily_local_article_intelligence_href` (too strict — requires fragment), wraps it, or adds a thin sibling that accepts `articles/<id>.html` without fragment. Add a render test that asserts a fragmentless safe href renders and a fragment-required validator does not silently drop it.

### I2 — Dedupe by "consumed article source IDs" is unjustified and will collapse same-source editions below the 2-card minimum

Plan line 156: "Dedupe by normalized `(title, href)`, normalized `read`, and consumed article source IDs." No sibling builder dedupes by source — the intelligence brief and organizer both allow multiple cards from the same source. Real editions routinely carry 2–3 stories from the same source (e.g. a single publisher's feed); source-ID dedupe collapses them to one card, the `< 2 cards` guard fires, and the section disappears for those editions. The plan gives no rationale for the stricter rule.

**Fix:** Either drop the source-ID dedupe and rely on `(title, href, read)` (matches sibling semantics), or justify the "one card per source" product decision and add a test pinning the intended behavior (`test_build_daily_local_synthesis_brief_collapses_or_keeps_same_source_articles`). Without this, `source_count` (line 160) and `card_count` will drift in ways the test suite does not lock down.

### I3 — Builder test fixtures encode the wrong href shape, so they will not catch C1

Tied to C1: the unsafe-href fixture list (lines 244–246) treats `articles/index.html`, `articles/story.html?x=1` as the realistic map values. If the implementer writes fixtures matching the plan's prose, the tests pass against an implementation that follows the (incorrect) rule, and C1 ships to production undetected. The fix in C1 (rewrite fixtures as bare filenames) is also required here; calling it out separately because test correctness is what would have caught C1 in a RED/GREEN cycle.

### I4 — `opening_read` truncation vs. title substitution is underspecified

Plan lines 143–147 assemble `Today's local read connects {first title} with {second title}.` and then "Cap to 180 characters." If `{first title} + {second title}` plus the scaffold exceeds 180, the cap truncates **mid-title**, producing garbled copy (`...connects *Brand X Launches New Col* with *Wholesa*…`). The plan does not say whether each title is pre-truncated (with ellipsis? at word boundary?), whether the cap is applied to the final string only, or what fallback is used when the cap would eat into the second title.

**Fix:** Specify truncation order — e.g., pre-truncate each title to a per-title constant (the plan already says "Use named constants for all card/text/reference limits; do not scatter magic numbers," line 156), then assemble, then assert the final string fits. Add a test with two 120-character titles asserting no mid-word truncation and a trailing ellipsis (or whatever convention is chosen).

## Minor

### M1 — `why_it_matters` is referenced as if it exists on the Stage 382 brief; it does not

Plan line 152: "Do not use `why_it_matters` directly unless it was already chosen by the Stage 382 article synthesis builder." `RowOneLocalArticleSynthesisBrief` (`local_article_synthesis_brief.py:33-42`) has fields `title, source_name, lead, thesis, article_adds, reader_move, basis_note, anchors` — **no `why_it_matters`** (that field lives on `RowOneStory`). Reword to: "Do not reach into `RowOneStory.why_it_matters`; consume only the Stage 382 brief's `thesis` / `article_adds` / `lead`."

### M2 — `RowOneDailyLocalSynthesisBriefCard.href` field shape is not pinned

The dataclass (line 85) has `href: str` but does not say whether it holds the bare filename or the prefixed `articles/...` path. Once C1 is fixed, state explicitly that the builder stores the **bare filename** (matching `page_href` in sibling builders) and the template prepends `articles/`. This prevents the implementer from storing the wrong form and forcing a second fix.

### M3 — Docs boundary test is missing the neighboring-stage anchor assertion

The established pattern (e.g. Stage 382 docs test at `tests/test_row_one_docs.py:5073`) asserts `text.index(paragraph) < text.index("Stage 381 adds")` to pin "above the previous stage." The Stage 383 docs test (plan lines 304–311) asserts the paragraph appears but does not assert `< text.index("Stage 382 adds")`. Add the anchor so a future edit that moves the paragraph below Stage 382 fails the test.

### M4 — No builder test for "all Stage 382 article synthesis returns `None`"

The six builder tests cover count, href, dedupe, zh-fallback, and caps, but not the realistic case where `build_row_one_local_article_synthesis_brief(...)` returns `None` for every (story, article) pair (degenerate content, consumed-text collisions — the `lead`/`thesis`/`article_adds` guard at `local_article_synthesis_brief.py:79-80`). Add `test_build_daily_local_synthesis_brief_returns_none_when_all_articles_lack_synthesis` to lock that path.

### M5 — `article_count` vs `card_count` metrics may confuse readers

Plan lines 158–161: `article_count` = eligible candidates **before** the 3-card cap; `card_count` = `len(cards)`. When `article_count=5` and `card_count=3`, the metrics line shows both numbers. Readers seeing "5 articles / 3 cards" may wonder where the other 2 are. Not blocking, but consider whether `article_count` should be renamed (e.g. `eligible_article_count`) or whether showing the pre-cap total adds editorial value on the homepage.

### M6 — Curly-apostrophe convention check is deferred without a mechanical anchor

Plan line 147: "Use curly apostrophe only if surrounding files already use it; otherwise use ASCII `Today's`." Good intent; make the check mechanical so the implementer doesn't guess — e.g., "grep `Today['’]s` in `src/fashion_radar/row_one/templates.py` and match the dominant form; if split, default to ASCII." Pin the chosen form in a test assertion.

## Things the plan gets right (explicit validation)

- **Placement in the homepage flow** (lines 184–190): the chosen insertion between `{daily_local_article_intelligence_brief_section}` (currently `templates.py:651`) and `{daily_local_saved_article_organizer_section}` (`templates.py:652`, immediately consecutive today) is **feasible without touching existing ordering tests**. Existing assertions (`tests/test_row_one_render.py:16248-16253` intelligence-brief < organizer < content-organization; `16420-16425` organizer < itinerary) all remain satisfied with a synthesis section inserted between brief and organizer. The placement rationale (synthesize a daily judgment right after the intelligence cluster, before the organizer) is editorially defensible. The alternate "after Daily Local Reading Itinerary" placement is **not** recommended — it would push the synthesis below three granular modules and weaken the "what does today add up to?" framing the plan opens with. Keep the chosen placement.
- **Scope boundaries** (lines 25–37, 525–530): the generated-site-only disclaimers correctly cover JSON, schema, route, runtime, manifest, source collection, scraping, LLM, connector, scheduling, analytics, personalization, recommendation, compliance-review. Aligns with AGENTS.md scope rules. No boundary violation.
- **Stage 382 builder reuse** (line 130): the call `build_row_one_local_article_synthesis_brief(story=story, local_article=article)` matches the real keyword-only signature (`local_article_synthesis_brief.py:51-55`). The fields it consumes (`lead`, `thesis`, `article_adds`, `source_name`) all exist on `RowOneLocalArticleSynthesisBrief`; `source_name` is correctly typed `str` (line 84) matching the source model.
- **Render integration point** (lines 172–180): inserting the builder call in `render_row_one_site` after `local_article_page_hrefs_by_story_id` is built (`render.py:207-216`) matches the sibling call pattern (`render.py:217-236`). Feasible.
- **Workflow sentinel test** (lines 283–294): the monkeypatch-`_render_daily_local_synthesis_brief`-to-sentinel + assert-only-in-`index.html` pattern correctly **inverts** the Stage 382 article-page-only sentinel (`tests/test_workflows.py:1807-1917`), which is what homepage-only placement requires. Artifact-stem denylist (lines 288–294) is comprehensive including both kebab and snake variants plus the Chinese title.
- **Review artifact hygiene** (lines 67–72): "Rereview files only when Critical or Important findings require fixes" matches `docs/REVIEW_PROTOCOL.md:103-122`. Naming follows the `claude-code-stage-N-{plan,code}-{review,rereview}.md` / `opencode-stage-N-{plan,code}-{review,rereview}.md` convention.
- **Implementation sequencing** (Tasks 1–8): RED test → implementation → render RED → render impl → workflow+docs → verification → review → frozen gates is the established TDD cycle and matches how Stages 371/372/376/382 were shipped. Frozen `UV_NO_CONFIG=1 uv --no-config run --frozen ...` commands match AGENTS.md mirror-safety rules.

## Summary

| Severity | Count | IDs |
|---|---|---|
| Critical | 1 | C1 |
| Important | 4 | I1, I2, I3, I4 |
| Minor | 6 | M1–M6 |

**Recommendation:** Revise the plan to fix C1 (split builder/render href validation, reuse `_safe_article_page_href`, store bare filename in the card dataclass) and I1–I4 before writing any implementation code. With those fixes the plan is implementable as a clean sibling of the Stage 371/372/376/382 homepage sections. No code or docs were modified during this review.
