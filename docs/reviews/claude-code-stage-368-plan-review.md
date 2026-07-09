---

## Stage 368 Plan Review — Local Article Body Organizer

**Reviewer:** Claude Code (primary)
**Date:** 2026-07-09
**Files reviewed:** plan, design spec, `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, `src/fashion_radar/row_one/templates.py`, `models.py`, `saved_article_filing_inbox.py`, `tests/test_row_one_render.py`

---

### Critical

None.

---

### Important

**1. Placement description contradicts the actual template order (Task 5)**

The plan (Task 5) says: *"Insert the rendered organizer after the local article content segment deck and before Saved Article Key Signals."* The design doc repeats the same ordering.

The actual `render_local_article_page_html` (templates.py:795–856) renders in this order:

```
information_panel          ← line 851
local_reading_companion    ← line 852
local_section_binder       ← line 853
key_signals                ← line 854   ← BEFORE content_segment_deck
content_segment_deck       ← line 855
local_article_section      ← line 856
```

`key_signals` comes **before** `content_segment_deck`, not after it. "After content_segment_deck and before Saved Article Key Signals" is therefore impossible as written. The design's intended placement (organizer visible above the saved body, below the content deck) corresponds to inserting between `content_segment_deck` (line 855) and `local_article_section` (line 856). Update the plan and design to say exactly that: *"between the content segment deck and the local article section"* with the line reference.

**2. Private helper duplication without extraction**

`saved_article_filing_inbox.py:122–150` already defines `_rendered_paragraph_indices` and `_strict_valid_paragraph_indices` with identical logic to what the plan proposes for the new module. Copying them silently creates divergence risk — if the filing inbox logic is fixed later, the body organizer won't be updated.

Options (choose one):
- Extract both to a shared internal utility (e.g., `_paragraph_index_utils.py`) and import from both callers.
- Keep the duplication but add a comment in both files pointing to the sibling, and note in the plan that the only intentional difference is the return type (`tuple[int, ...]` vs `set[int]` for ordering).

The plan must state which option is chosen before coding starts.

---

### Minor

**3. `_render_local_article_digest_read_first` overlap not addressed in tests**

`_render_local_article_digest_read_first` (templates.py:15254) already renders a *"Read First"* heading and paragraph jump links inside the local article body section. The body organizer adds a separate `read_first_route` above the body. These are distinguishable by placement and CSS class (`.local-article-body-organizer-route` vs `.local-article-digest-card`), but Task 3's render tests do not assert that the two read-first surfaces use distinct class names and do not share duplicated paragraph anchor links. Add a one-line assertion confirming the body organizer's route section uses `.local-article-body-organizer-route`, not any `digest-card` class.

**4. Monkeypatch target unspecified in Task 6**

`test_stage_368_local_article_body_organizer_stays_generated_site_only` says to `monkeypatch _render_local_article_body_organizer` without specifying the full module path. The correct target is `fashion_radar.row_one.templates._render_local_article_body_organizer`. State this in the task to avoid guesswork.

**5. Item labels cap not explicitly asserted in the caps test**

`test_build_saved_article_body_organizer_caps_rows_deterministically` mentions "more than 3 paragraph links per section row" and "more than 5 read-first links" but does not explicitly call out that `LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ITEM_LABELS = 3` is also verified. Add "assert item labels per section row are capped at 3" to the test description.

---

### Summary

The plan is architecturally sound. It correctly targets only `articles/<story-id>.html`, derives everything from existing `RowOneLocalArticle` and `RowOneStory` state, follows the established builder+renderer pattern (consistent with the filing inbox), and specifies boundary tests thoroughly. No app contract, schema, JSON artifact, route, or collection behavior is introduced.

**Verdict: Approved with changes.**

Fix the two Important findings — placement wording and helper duplication decision — in the plan before beginning Task 2. The Minor findings can be addressed inline during implementation.
