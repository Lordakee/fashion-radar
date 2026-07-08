The `_daily_edit_read_next` at line 5083 is confirmed to be a daily-edit/app_payload surface with a completely different naming convention — no conflict. I have enough to write up the review.

---

## Stage 353Plan Review — Saved Article Read Next Clusters

### Verdict: **Approved for implementation.** No blocking issues.

---

### Review Questions

**1. Generated-site-only boundary**
Met. The spec's architecture section, the plan's architecture comment, the workflow guard denylist, and the docs paragraph all explicitly prohibit schemas, SQLite tables, JSON artifacts, route families, app-contract fields, scraping, extraction, ranking, LLM calls, scheduling, deployment, analytics, personalization, recommendation, and compliance-review behavior. The builder is in-memory only.

**2. Cluster inputs limited to existing library/organization/local hrefs/anchors**
Met. The builder takes only `RowOneSavedArticleLibrary`, `RowOneSavedArticleContentOrganization`, and `local_article_page_hrefs_by_detail_path`. The spec explicitly rules out raw article text, raw source URLs, imported signals, external search, social data, downloaded HTML, and LLM output.

**3. Avoids ranking while still organizing**
Met. Groups are walked in existing content-organization order. Items within each cluster are sorted by library-order index, not by counts, chip frequency, support counts, or popularity. The plan states this explicitly in Task 2Step 3.

**4. Links constrained to safe local/same-site anchors**
Met. Two enforcement points: the builder's href helpers (prefer local page digest, fall back to `../details/…#local-article-content-section-N`, fall back to `../details/…#local-article-digest`), and a second render-time check in `_saved_article_read_next_cluster_href(...)` that rejects outbound, protocol-relative, `javascript:`, traversal, whitespace-bearing, empty, and wrong-fragment hrefs. Tests exercise all rejection cases.

**5. Test coverage**
The test plan covers caps (cluster, item, reference), order (group order + library order within cluster), dedupe by `(cluster_key, detail_path)`, empty/None omission, escaping, homepage/detail absence, all unsafe link forms, placement relative to reading queue and signal facets, CSS selector coverage, docs boundary, and workflow artifact denylist. Coverage is sufficient.

**6. Name conflicts**
No conflicts with existing surfaces:

- `saved_article_read_next_clusters` — new module, not used elsewhere.
- CSS classes `saved-article-read-next-clusters*` — distinct from `saved-article-theme-digest-*`, `saved-article-reading-queue-*`, `saved-article-signal-facets-*`, etc.
- `_daily_edit_read_next` (templates.py:5083) — daily-edit/app_payload surface, different naming prefix, no overlap.
- Dataclass names `RowOneSavedArticleReadNextCluster*` — no collision.

---

### Minor Observations (non-blocking, worth tracking during implementation)

**M1 — `body_source_label` conversion logic**
`_body_source_label(body_source: RowOneLocalArticleBodySource) → LocalizedText` already exists in `saved_article_reading_queue.py`. The new module needs the same mapping. The plan says "preserve body-source labels from library entries" without specifying import or re-implementation. Prefer importing the existing function (or extracting it to `saved_article_library.py`) over duplicating the four-line mapping. Either way it's small; just avoid drift.

**M2 — Duplicate group sub-headings on `articles/index.html`**
Both `saved-article-theme-digest` and `saved-article-read-next-clusters` will render `Read First`, `People & Brands`, `Products`, `Source Structure` as sub-headings on the same page. The spec is aware of the theme digest and treats the two sections as structurally distinct (different data, different href strategy, different card layout). This is a product design choice, not a plan defect. No action required unless the product decision changes.

**M3 — Render test assertions on shared strings**
`assert "Read First" in section_html` is safe only if `section_html` is the isolated output of `_render_saved_article_read_next_clusters(...)`, not the full library page HTML. The plan specifies direct render tests with a `RowOneSavedArticleReadNextClusters` fixture (Task 3Step 1), which isolates the section — this is correct. Just confirm the test does not accidentally use the full `library_html` for those string checks.
