## Stage 379 Plan Re-Review (opencode)

I verified the three targeted fixes against the actual source and test files.

**Fix 1 — Task 4 render tests use real `tests/test_row_one_render.py` fixtures** ✅ RESOLVED
Confirmed every fixture referenced in Task 4 Steps 1–5 exists in the render test module:
- `_edition()` (`test_row_one_render.py:240`), `edition.stories[0]`, `_detail_story(...)` (`:311`), `_edition_with_stories(...)` (`:338`), `_signal_briefing_local_article()` (`:382`), `_saved_article_library_fixture()` (`:344`), `_html_between` (`:3189`).
- `from dataclasses import dataclass, replace` already present (`:5`); `RowOneSavedArticleLocalReadingCompanion` imported (`:166`); `render_local_article_page_html` (`:232`), `render_row_one_site` (`:119`), `build_row_one_saved_article_content_organization` (`:129`) all imported.
- No `_story`/`_local_article`/`_edition(story)`/`_saved_article_library_entry` calls remain; Step 4 note explicitly forbids creating them.

**Fix 2 — Card href and anchor share canonical detail-path derivation** ✅ RESOLVED
- Builder derives `current_detail_path = _story_detail_path(story)` (`saved_article_local_reading_companion.py:97`) from validated `story.detail_path`; plan Task 3 Step 2 derives the card href from `current_detail_path`, explicitly not raw `story.id`.
- Library match is already keyed on the digest-path detail (`_library_entry_detail_path`, `:173-180`, digest-only), so `current_detail_path` and the entry agree byte-for-byte before any companion is built (`:102-104`).
- Plan Task 5 Step 3 derives the anchor from `entry.digest_path` only and explicitly forbids the reader-path-first `_saved_article_library_entry_detail_path` (`templates.py:10053`, tries `reader_path` first — confirmed).
- Task 4 Step 5 agreement test asserts `f"index.html#{card_anchor}"` is in the builder's filing_links.

**Fix 3 — Filing-trail renderer keeps validated `index.html#` links, not `#`-only** ✅ RESOLVED
- The `startswith("#")` filter lives at `templates.py:9218`; confirmed it would drop every `index.html#...` href.
- Plan Task 5 Step 4 explicitly states the filing-trail renderer must NOT reuse `_render_saved_article_local_reading_companion_links(...)` or its `#`-only filter, and must keep links passing `_saved_article_local_reading_companion_href(...)` that start with `index.html#`.
- Confirmed the current `_saved_article_local_reading_companion_href` (`:9320`) falls through to `_saved_article_read_next_cluster_href` (`:9104`), which rejects `index.html#...` (requires fragment `local-article-digest`) — so Task 5 Step 5's new cross-surface helper is required and correctly placed before that fall-through.

Also confirmed: `render.py:73` imports and `render.py:552` calls `build_row_one_saved_article_local_reading_companion` as a module global (C2 patch target reachable with `raising=True`); `test_workflows.py` has no `dataclasses` import, so the unconditional `from dataclasses import replace` is correct (I1); prior Minor items (CSS split, `details/<story-id>.html` doc phrase) are also resolved.

No remaining Critical or Important findings.

END_OF_REVIEW
