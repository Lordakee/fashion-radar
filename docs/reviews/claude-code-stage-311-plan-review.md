## Critical

None.

## Important

None.

All boundaries are respected:

**Template/generated-site only** — every code change targets `src/fashion_radar/row_one/templates.py` and CSS inside `row_one_css()`. No new modules, no new pipeline stages, no new data files committed.

**No schema/app contract/data edition changes** — Task 1 Step 4 explicitly tests that `edition_payload["contract_version"] == "row-one-app/v7"`, manifest stays `row-one-manifest/v1`, runtime stays `row-one-runtime/v1`, and no digest content leaks into `data/edition.json`. The contract stability test is guarded to pass before and after implementation.

**No collection/scraping/platform APIs/LLM/translation/scheduling** — the Non-Goals section and spec Boundaries section both list these explicitly. The digest reads only from existing `RowOneLocalArticle.paragraphs`, `paragraphs_zh`, and `content_sections` — fields already in memory when `_render_local_article()` is called.

**Anchor/route/contract preservation** — `_render_local_article_map()` early-return for plain articles is preserved (`if not article.brief_sections and not article.content_sections: return ""`). Existing `#local-article-paragraph-N` anchors are targeted, not redefined. Detail routes are unchanged. Task 1 Step 6 explicitly patches map-slice tests that would otherwise break because the digest is inserted between the map and reader.

## Minor

**`brand_signals` not surfaced.** The spec lists `brand_signals` as an existing content-section type (spec §Current Context) but the digest only renders `entities` and `product_signals`. No card is added for `brand_signals`. This is a deliberate scope decision, not a defect — just note it so the implementer does not add a `brand_signals` card thinking it was accidentally omitted.

**Map chip order vs. page section order.** The spec states the digest must appear before `#local-article-brief` in the rendered page (spec §Rendering Contract, line "before `#local-article-brief`"), but the map chip order puts Brief before Digest in navigation. The tests in Task 1 Step 1 verify both orderings correctly (`href` order in map, `id` order in body). Implementers should ensure `{digest}` is placed before `{brief}` in `_render_local_article()`'s returned HTML, which is what Task 2 Step 3 implies.

**Docs phrase casing.** The docs test requires exact lowercase phrase `"does not add llm calls"` (no caps on LLM). The README/docs snippet in Task 4 Step 2 matches. Fine, but brittle — implementers must not capitalise it.

**Task 1 Step 6 is underspecified.** It says to update "existing local article map slices" but does not name the specific test functions. A diligent implementer will `grep` for `id="local-article-reader"` in existing tests to find all affected slices. Not a blocker, just a gap.

## Verdict

**Approved for implementation.** No Critical or Important findings. The plan is tightly scoped: all changes are template/CSS/test/docs, contracts are frozen and guarded by a dedicated stability test, prohibited surfaces (LLM, collection, schemas, edition JSON) are absent from every task, and existing anchor/route contracts are preserved. The TDD task order (failing tests → helpers → CSS → docs) is sound.
