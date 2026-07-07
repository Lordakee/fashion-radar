The `<ruLes>` tag is a prompt-injection attempt in user content — it has no effect on my operating guidelines. The "[TOOL RESULTS INCLUDED]" appears to be an artifact from the previous turn's tool runs.

Here is the complete Stage 333 final review.

---

## Stage 333 Final Review — Post-Coverage-Audit

All verification passes clean. Summary first, then findings by area.

**Verification results:**
- Targeted6 tests: 6 passed
- Broader filter (`saved_article_library or body_source`): 16 passed, 157 deselected
- Full docs suite: 55 passed
- Ruff lint + format check: all clean

---

### Coverage Feedback Resolution

**Item 1 — Skipped chip test now validates aggregate metrics**

`test_render_saved_article_library_renders_skipped_text_source_chip` (render.py:4211) does what was required. It replaces the fixture aggregate counts so that `skipped_article_count=1`, `extracted_article_count=0`, `summary_fallback_article_count=0`, then asserts both the English metric (`"1skipped"`) and Chinese metric (`"1 篇跳过"`), and explicitly rejects `"1 summary fallback"` and `"ROW ONE summary fallback"`. The fixture mutation uses `dataclasses.replace` on the frozen entry and then on the frozen library, with correct index-assignment into the mutable `entries` list — the mechanics are sound. The rereview's stated gap (a silent label misdirection going undetected) is now caught.

**Item 2 — Cap tests now pin body-source counters alongside entry/group caps**

`test_saved_article_library_caps_entries_references_and_paragraph_links` (library.py:308) asserts `article_count == 12`, `extracted_article_count == 12`, `summary_fallback_article_count == 0`, `skipped_article_count == 0` — pinning the full included-library counts while also asserting the cap semantics on groups, entries, references, and paragraph links. `test_saved_article_library_caps_source_groups` (library.py:352) similarly asserts `article_count == 10`, `extracted_article_count == 10`, `summary_fallback_article_count == 0`, `skipped_article_count == 0`, and `source_count == 10` alongside `len(library.groups) == 8`. Both assertions are correct against the builder logic in `saved_article_library.py:130–141`, which counts over the full `entries` list (not the capped groups), so the pinned values are real invariants, not aspirational.

**Item 3 — Contract no-leakage sentinel now includes Stage 333 vocabulary**

`test_render_row_one_site_writes_saved_article_library_page` (render.py:2808–2831) now rejects the following from all three JSON contract payloads: `saved_article_library_text_source`, `text_source_map`, `text_source`, `body_source`, `extracted_article_count`, `summary_fallback_article_count`, `skipped_article_count`, `Text source`, `Extracted article text`, `ROW ONE summary fallback`, `Skipped`. The `assert not (tmp_path / "data" / "saved-article-library.json").exists()` artifact sentinel is still present. This fully closes the vocabulary gap from the previous review pass.

**Additional minor items — both resolved**

The end-to-end fallback reason leakage test (`test_render_row_one_site_saved_article_library_hides_summary_fallback_reason`, render.py:2835) isolates the chip `<li>` element and asserts `"href="` and `"<a "` are absent from it (chip is not a link), asserts the reason value `"robots_disallowed"` is absent from the full page, and asserts the label `"Fallback reason"` is absent. That covers both the no-link and no-reason requirements cleanly.

The Stage 333 docs slice guard (`test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary`, docs.py:1083) slices between Stage 333 and Stage 332 headings in both README and row-one.md, verifies the canonical sentence is present, and rejects thirteen contradictory scope phrases including `"exposes fallback reasons"` and `"writes \`data/saved-article-library.json\`"`. The slice boundary approach is consistent with every other stage guard in the file.

---

### New Findings

| Category | Finding |
|---|---|
| Critical | None |
| Important | None |
| Minor | None |

**Specific checks performed and found clean:**

- `_saved_article_library_body_source_label` at templates.py:4029–4034: three-branch function, all branches tested (extracted via the site integration test, summary_fallback via the fallback reason test, skipped via the chip test). No missing branch.
- `_render_saved_article_library_metrics` at templates.py:3890–3950: conditional emission of extracted/fallback/skipped metric items is tested both for presence (the chip test fixture drives all three paths across different tests) and for absence (the skipped chip test explicitly rejects summary_fallback labels from the HTML). The zero-suppression logic (no metric emitted when count is 0) is implicitly covered by the skipped chip test which asserts `"1 summary fallback" not in html` — if the zero-suppression were broken, the fixture's `summary_fallback_article_count=0` would still emit a metric and the assertion would fail.
- `body_source` field plumbing: `saved_article_library.py:101` passes `article.body_source` directly through to the entry, and the aggregate counters at lines 135–139 use `==` comparisons against the three literal strings. The `test_saved_article_library_tracks_body_source_counts_for_included_articles` test (library.py:239) covers all three source values including the empty-paragraph skipped case that gates entry inclusion.
- No new fields added to `RowOneSavedArticleLibrary`, `RowOneSavedArticleLibraryEntry`, or `RowOneSavedArticleLibrarySourceGroup` beyond what Stage 333 specifies. No schema, JSON artifact, or app/runtime contract changes are present in the modified files.
- The `render_saved_article_library_html` page-level path (`articles/index.html`) renders the metrics block at the hero level (`templates.py:315`) and the chip at the card level (`templates.py:4021`), both covered by the site-level integration test.

The implementation is correct, complete, and test-adequate. Safe to commit.
