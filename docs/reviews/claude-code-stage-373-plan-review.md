# Stage 373 Plan Review Findings

## Critical

**C1: `story` is not in scope when `_render_local_article_paragraphs` is called — the plan as written cannot be implemented.**

`render_local_article_page_html` calls `_render_local_article(local_article, include_body_filing_cues=True)`. Neither `_render_local_article` nor `_render_local_article_paragraphs` receive `story`. Yet the plan (Task 5 Step 3) says to call `build_row_one_local_article_body_section_markers(story=story, local_article=...)` inside `_render_local_article_paragraphs`, which only holds `article`. The builder requires `story` for both its identity guard (`story.id == local_article.story_id`) and the `safe_local_article_story_id(story.id)` filesystem-safety check; without it the call site is incomplete.

Fix: pre-build markers in `render_local_article_page_html` where `story` is already available — exactly the pattern used for `build_row_one_saved_article_body_organizer` and `build_row_one_local_article_intelligence_brief` at lines 851–861. Pass the resulting `tuple[RowOneLocalArticleBodySectionMarker, ...]` into `_render_local_article` and then into `_render_local_article_paragraphs` as a keyword argument (e.g., `body_section_markers=`). This keeps both function signatures stable and avoids threading `story` deeper into the render tree. The plan must be updated in Task 4 Step 1 (test fixture setup), Task 5 Steps 1–3, and the monkeypatch target in Task 6 Step 2 before implementation begins.

**C2: The new builder module cannot safely reuse the existing paragraph-index validation logic — circular import risk is unaddressed.**

`templates.py` defines `_strict_valid_local_article_paragraph_indices` (line 17484), which implements the exact bool/non-int/negative/out-of-range/duplicate rejection semantics the spec prescribes for the builder. `saved_article_body_organizer.py` has a near-identical `_strict_valid_paragraph_indices` with an explicit comment to keep semantics aligned with `saved_article_filing_inbox`. Adding a third standalone copy in `local_article_body_section_markers.py` creates a three-way alignment obligation with no enforcement.

The plan cannot simply import from either existing module: `templates.py` will import the new builder, so importing `templates.py` from the builder creates a circular import; `saved_article_body_organizer.py` is also imported by `templates.py`, making its private `_strict_valid_paragraph_indices` inaccessible without restructuring. Fix: extract the shared validation logic into a function in `text.py` or `utils.py` before Stage 373 lands, then import it from all three call sites. The plan must add this extraction as a step (before Task 3 Step 2) or acknowledge the duplication explicitly with an alignment comment convention.

---

## Important

**I1: The new `_safe_local_article_body_section_marker_href` helper duplicates two compiled regexes that already exist at module level in `templates.py`.**

`_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE = re.compile(r"local-article-paragraph-[1-9][0-9]*$")` (line 176) and `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE = re.compile(r"local-article-content-section-[1-9][0-9]*$")` (line 177–179) cover exactly the two fragment patterns the new href validator must accept. The plan does not reference these. If the implementation defines new regex patterns instead of reusing these, they will diverge silently on any future pattern fix. Task 5 Step 2 must explicitly reference and reuse both existing compiled regexes.

**I2: The workflow guard monkeypatch target is underdefined and will be wrong if C1 is fixed as recommended.**

Stages 368–372 each monkeypatch a render function inside `templates.py` (e.g., `_render_local_article_body_organizer`, `_render_daily_local_reading_itinerary`). The plan says to "monkeypatch the marker builder/render path" but does not name the attribute. If C1 is fixed by pre-building markers in `render_local_article_page_html` and passing them in, the correct monkeypatch target is `build_row_one_local_article_body_section_markers` in `fashion_radar.row_one.local_article_body_section_markers`, not a render helper. If instead a render helper is introduced (e.g., `_render_local_article_body_section_markers`), that becomes the target. The plan must name the exact `monkeypatch.setattr` symbol and module after C1 is resolved, to avoid a non-raising no-op that silently lets markers through.

**I3: The empty-tuple test case "mismatched story/local article ids" requires helper constructors to be designed carefully — the plan gives no guidance.**

The plan names `_story()` and `_article()` as test helpers but does not define them. The mismatch path requires `_story()` to return a story with a known ID (e.g., `story_id="the-row-signal-123"`) while the mismatch variant of `_article()` returns a local article with a different `story_id`. If `_article()` defaults to matching the default `_story()` ID, every test that passes without an override implicitly depends on that alignment. The unsafe-story-id path (e.g., a story ID with `../` or a blank ID) also needs a controlled helper variant. The plan should define the helper signatures explicitly before the RED test step to prevent fragile test state.

---

## Minor

**M1: Chinese title fallback string is inconsistent with the established project convention.**

The plan prescribes `LocalizedText(en=f"Section {section_position}", zh=f"Section {section_position}")` for the fallback title when a section has no title. `saved_article_body_organizer.py` (line 144–
