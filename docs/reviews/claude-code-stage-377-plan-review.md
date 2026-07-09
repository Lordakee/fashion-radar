## Stage 377Plan/Spec Review

### Critical

None.

---

### Important

**I-1: `RowOneStory` and `RowOneLocalArticle` fixture fields not shown — risk of Pydantic `ValidationError` in RED phase**

The plan shows only the `_content_section` fixture shape. Both `RowOneStory` and `RowOneLocalArticle` use `ConfigDict(extra="forbid")` and have multiple required fields that are not shown or documented:

- `RowOneStory` requires `id`, `section_key`, `story_type`, `headline`, `summary`, `why_it_matters`, `editorial_takeaway`, `signal_context`, `reader_path`, `source_name`, `detail_path` — all non-optional. `story_type` and `section_key` are `Literal` types; wrong string values fail immediately.
- `RowOneLocalArticle` requires `story_id`, `url`, `source_name`, `extracted_at`. `extracted_at` requires a parseable datetime string or `datetime` object.
- `RowOneEdition` requires `generated_at`, `edition_date`, `summary`.

If any fixture omits or misspells a required field, every builder test fails with `ValidationError` instead of the expected `ImportError`, making RED-phase verification misleading. **Fix:** add a minimal complete fixture factory for `RowOneStory`, `RowOneLocalArticle`, and `RowOneEdition` in the plan's Task 2 Step 1, similar to the `_content_section` shape shown.

---

### Minor

**M-1: Two `{local_article_section}` occurrences in templates.py**

`local_article_section` appears at two template sites (~line 936 and ~line 1020). The plan should clarify that only the occurrence inside `render_local_article_page_html` (line ~936) receives the `{local_related_reads}` insertion, not any other usage, to avoid an accidental double-render.

**M-2: Builder test anchor assertion depends on implicit fixture paragraph index**

The example assertion `related.cards[0].href == "shared-row-2222222222.html#local-article-paragraph-2"` implies the shared-reference content item sets `paragraph_indices=[1]` (zero-based index1 → anchor `local-article-paragraph-2`). The plan does not state this explicitly. Since the zero-to-one conversion is correct in `local_article_paragraph_anchor` (`index + 1`), this is not a spec error, but documenting the expected index value in the test fixture would prevent silent test mismatch.

**M-3: Anchor conversion is correctly specified; no action needed**

`local_article_paragraph_anchor(index)` returns `f"local-article-paragraph-{index + 1}"`. The spec's instruction to use this function (rather than hand-constructing fragments) is correct and complete. No blocker.

END_OF_REVIEW
