## Stage 357Review: Daily Local Key Signals Digest

**No blocking issues.** All five review areas pass. Residual risks are low-severity.

---

### Scope: homepage-only generated-site ✓

`render.py:147–150` — `build_row_one_daily_local_key_signals_digest` is called once in `render_row_one_site` and the result is passed only to `render_index_html` (line 199). No article-page renderer, library renderer, or detail renderer receives the digest object. The integration test at `test_row_one_render.py` (the new `test_render_row_one_site_writes_daily_local_key_signals_digest_homepage_only`) explicitly asserts the section class is absent from `articles/<id>.html`, `articles/index.html`, and `details/<id>.html`.

---

### No app/schema/runtime/manifest/JSON/sidecar changes ✓

The diff touches exactly: `render.py`, `templates.py`, new `daily_local_key_signals_digest.py`, tests, and docs. No model file is touched. The workflow guard at `test_workflows.py:923–935` sweeps 8 artifact stems × 3 directories × 2 suffixes (.json, .html) for stray files and explicitly checks the generated contract payloads (edition.json, manifest.json, runtime.json) for all variant spellings of the feature name.

---

### Builder safe filtering and href reconstruction ✓

`daily_local_key_signals_digest.py:80–91` — loop gate: `safe_local_article_story_id(story.id)` → `is_safe_row_one_detail_path(story.detail_path)` → local-article lookup → story_id mismatch check → `_daily_local_key_signals_digest_article_href` (which re-validates the story_id before constructing). Both href constructors (`_daily_local_key_signals_digest_article_href` at line 289 and `_daily_local_key_signals_digest_anchor_href` at line 295) reconstruct the href from parts rather than passing input through. `_daily_local_key_signals_digest_anchor_href` additionally validates the fragment against `_LOCAL_ARTICLE_FRAGMENT_RE.fullmatch`.

---

### Renderer escaping and href validation ✓

`templates.py:_render_daily_local_key_signals_digest_entry` — every user-supplied string is wrapped in `_esc()`. The validator `_safe_daily_local_key_signals_digest_href` (new function added around line 9200):
- Rejects non-`str`, whitespace, leading `/`, `.`, or `//`
- Rejects `http:`, `https:`, `javascript:`, `data:` schemes
- Requires exactly `articles/<name>.html` via `PurePosixPath` with `len(parts) == 2` and `parts[0] == "articles"` (blocks `../` traversal, nested paths, absolute paths)
- Requires a `#` separator (no bare-path hrefs pass)
- Validates story_id via `safe_local_article_story_id`
- Allows only `saved-article-key-signals-title`, `local-article-paragraph-[1-9][0-9]*`, or `local-article-content-section-[1-9][0-9]*` as fragments
- **Reconstructs** the output rather than returning the input href

The render test `test_render_index_html_includes_daily_local_key_signals_digest` injects `<script>` in a title and `<brand>` in a body to verify escaping, and uses six bad-href entries (`javascript:alert(1)`, `../details/…`, nested path `articles/unsafe/story.html`, arbitrary fragment `#summary`, zero-indexed `#local-article-paragraph-0`) to assert those entries are silently dropped — only the one valid brands entry renders.

---

### Placement ✓

`templates.py:353–358` — template string order is:

```
{saved_article_briefs_section}
{daily_local_key_signals_digest_section}
{saved_article_content_organization_section}
```

Exactly as specified. The doc-boundary test at `test_row_one_docs.py` also asserts that Stage 357 appears before Stage 356 in both `README.md` and `docs/row-one.md` and checks for a list of stale phrases (wrong placement phrases, schema/runtime/manifest references, sidecar/JSON/fetching/ranking/LLM variants).

---

### Tests/docs/workflow adequacy ✓

| File | Coverage |
|---|---|
| `test_row_one_daily_local_key_signals_digest.py` | Story order, href reconstruction, dedup + caps, headline fallback, unsafe story_id + mismatch returns None |
| `test_row_one_render.py` | Homepage-only placement, JSON/HTML artifact absence, XSS escaping, bad-href rejection (6 cases), bilingual content |
| `test_row_one_docs.py` | Spec boundary text present, ordering vs Stage 356, stale-phrase blocklist |
| `test_workflows.py` | Contract-payload contamination (12 string assertions), full generated-site-only guard via monkeypatch |

---

### Residual risks (non-blocking)

**Low — First-evidence href shared across all reference entries in a group** (`daily_local_key_signals_digest.py:217`). `href = _first_evidence_href(group, ...) or article_href` is computed once per signal group and used for every brand/product/people entry in that group. A signal group with two brands may link both to the same paragraph, which might only mention one of them. No security impact; minor signal-quality tradeoff.

**Low — 5-column CSS grid with fewer than 5 groups** (`templates.py`, `.daily-local-key-signals-digest-grid`). The grid is hardcoded to `repeat(5, minmax(0, 1fr))`. If only 1–3 groups render (e.g., only `why_it_matters` + `brands` when there are no products, people, or themes), empty columns produce a sparse desktop layout. Mobile override (`grid-template-columns: 1fr`) is in place. No correctness impact.

**Info — Builder regex is a local duplicate of templates' pair** (`daily_local_key_signals_digest.py:27–29`). `_LOCAL_ARTICLE_FRAGMENT_RE` combines the two patterns already in `templates.py`. The duplication is necessary to avoid a circular import (templates imports the builder). The patterns are semantically equivalent when used with `.fullmatch()`. Not a bug.

**Info — `safe_local_article_story_id` called twice per href** (lines 81 and 290 in the builder). The second call inside `_daily_local_key_signals_digest_article_href` is defense-in-depth. Correct, but future readers may wonder if it's a mistake.
