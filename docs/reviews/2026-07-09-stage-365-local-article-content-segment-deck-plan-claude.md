**Review findings — Stage 365 Local Article Content Segment Deck**

**Feasibility: confirmed.**
All four referenced helpers exist in `templates.py` at lines15107–15161:
- `_local_article_rendered_paragraph_indices` (15107)
- `_local_article_paragraph_anchor` (15111)
- `_local_article_content_section_anchor` (15116)
- `_strict_valid_local_article_paragraph_indices` (15135)

`RowOneLocalArticle`, `content_sections`, and `RowOneLocalArticleContentSection` all exist in the model layer. `_signal_briefing_local_article()` test fixture exists at `tests/test_row_one_render.py:294`.

**Insertion point: clean.**
The `render_local_article_page_html` f-string ends with `{key_signals}` then immediately `{local_article_section}`. Inserting a new `{content_segment_deck}` variable between them requires no signature change — `_render_local_article_content_segment_deck(local_article)` derives everything from the already-present `local_article` parameter.

**Boundaries: solid.**
- Deck is computed only inside `render_local_article_page_html`, which is called only for `articles/<story-id>.html`.
- Denylist covers all snake/kebab/title/Chinese variants across contract JSON and artifact stems.
- Non-goals list is exhaustive and matches the denylist entries.
- Workflow monkeypatch guard pattern (`_render_local_article_content_segment_deck → ""`) follows the established Stage N boundary-test convention.

**Tests: complete.**
Five coverage areas are addressed: direct render, filter/escape, omission, placement ordering (with/without key signals), and generated-site boundary. The `_local_article_content_segment_deck_html(index_html)` extractor helper follows the existing section-extractor pattern used by prior stages.

**Risks: none blocking.**
- No new parameters added to the public render function — zero call-site impact.
- Caps (4/3/5/3/180) are deterministic; no randomness or sorting ambiguity.
- Same-page-anchor-only constraint is enforced by reusing existing validators — no new URL validation surface.
- The plan explicitly requires asserting no paragraph body duplication, closing the most likely spec drift.
- Stage 365 names don't appear anywhere in the codebase yet — no collision risk.

---

READY FOR IMPLEMENTATION.
