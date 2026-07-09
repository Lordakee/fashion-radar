All key facts confirmed:
- `build_row_one_saved_article_content_organization` already imported at `test_row_one_render.py:129` ✅
- `from dataclasses import dataclass, replace` at line 5 ✅
- `_edition()`, `_detail_story()`, `_edition_with_stories()`, `_saved_article_library_fixture()` all exist ✅
- `build_row_one_saved_article_local_reading_companion` is at `render.py:73` (import) and `render.py:552` (call site) ✅

---

## Stage 379Plan Re-Review

I've verified the updated plan against both prior reviews, the actual source files, and the test module. Here is the disposition of every Critical and Important finding:

**Original C1 — `_companion_fixture` undefined (test collection break)**
RESOLVED. Task 4 Step 3 now constructs `RowOneSavedArticleLocalReadingCompanion(...)` inline with all required fields. No `_companion_fixture` call remains.

**Original C2 — workflow patches unverified module attribute**
RESOLVED. Task 6 Step 2 explicitly cites `render.py:73` (import) and `render.py:552` (call site) and adds `raising=True`. Both lines confirmed in the file.

**opencode C1 — Task 4 test bodies used wrong-module fixture family**
RESOLVED. All five Task 4 tests now use fixtures that exist in `test_row_one_render.py`: `_edition()` (line 240), `edition.stories[0]`, `_detail_story(...)` (line 311), `_edition_with_stories(...)` (line 338), `_signal_briefing_local_article()` (line 382), `_saved_article_library_fixture()` (line 344). No `_story(id)`, `_local_article(id)`, or `_edition(story)` calls remain.

**Original I1 — `replace` not imported in `test_workflows.py`**
RESOLVED. Task 6 Step 2 now unconditionally adds `from dataclasses import replace`.

**Original I2 — card anchor and card href derived from two independent paths**
RESOLVED. Task 3 Step 2 mandates `current_detail_path` (not raw `story.id`) as the canonical source for the card href. Task 5 Step 3 mandates `entry.digest_path`-only for the anchor, explicitly forbidding `_saved_article_library_entry_detail_path(...)` (which tries `reader_path` first). Task 4 Steps 4 and 5 add an isolated anchor helper test and a builder-to-anchor agreement test, respectively.

**Original I3 — group-key regex allow-list scope ambiguous**
RESOLVED. The Anchor And Href Rules section uses `r"[a-z][a-z0-9_]{0,63}"` (letter-first, underscores allowed). Task 2 Step 4 adds a boundary test: `top_stories` (underscore) accepted, `1bad` and `-bad` (non-letter start) rejected.

**Original I4 — render target placement ambiguous**
RESOLVED. Task 5 Step 4 shows the full updated `<article class="saved-article-local-reading-companion-current">…{links}{filing_trail}{refs}\n      </article>` skeleton with the closing tag explicit.

**opencode I2 — filing-trail renderer could silently inherit `startswith("#")` filter**
RESOLVED. Task 5 Step 4 explicitly states: "The filing-trail renderer must not reuse `_render_saved_article_local_reading_companion_links(...)` or its `href.startswith("#")` filter. It should keep any link whose href passes `_saved_article_local_reading_companion_href(...)` and starts with the new `index.html#` cross-surface pattern."

---

No remaining Critical or Important findings.

END_OF_REVIEW
