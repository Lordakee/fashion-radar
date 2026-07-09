## Critical

### C1 — Test fixture violates `RowOneLocalArticle` model constraints; all analyzer tests structurally broken

The `RowOneLocalArticle` model has `extra="forbid"` and requires `extracted_at: datetime` (no default). The plan's Task 2 fixture includes `"canonical_url"` (not in the model) and omits `extracted_at` entirely. Both violations raise `ValidationError` at `model_validate()`, so every test that uses this fixture fails at setup, never reaching the intended `ModuleNotFoundError` RED or a passing GREEN. The affected tests cover the core of the analyzer test plan:

```python
# Plan fixture — will ValidationError before any assert runs
{
    "story_id": "the-row-signal",
    "url": "https://example.com/the-row-signal",
    "canonical_url": "...",        # ← not in model, extra="forbid" → ValidationError
    "title": "The Row signal",
    "source_name": "Example",
    # extracted_at omitted        # ← required field, no default → ValidationError
    "body_source": "extracted",
    ...
}
```

Fix: remove `canonical_url`, add `"extracted_at": "2026-07-10T04:00:00Z"`.

---

### C2 — `_section_is_reader_visible` criterion not anchored to actual renderer behavior; false-positive risk in `row-one status`

The spec defines reader-visibility for content sections as: non-empty title/body OR item label/body OR item reference OR valid paragraph index. The existing `local_article_body_section_markers.py` uses a stricter criterion — a section only receives a marker (and therefore a jump link in the article body) if `_section_first_valid_paragraph_index` returns non-None, meaning at least one item has a valid paragraph index pointing to a non-empty saved paragraph.

These are two different documents: the markers drive body jump links; the rendered content section blocks in the article page may or may not follow the same rule. Until `render.py` is read and confirmed, the spec's definition of `_section_is_reader_visible` is an assumption rather than a derivation. If the renderer writes `id="local-article-content-section-N"` only for sections with paragraph connections (following the markers logic), the health check would flag "missing anchor" for sections the renderer correctly omits — making `row-one status` reject a properly generated site.

Fix before implementation: read the article-page rendering path in `render.py` to determine the exact predicate the renderer uses to decide whether to write `id="local-article-content-section-N"` for a given section, and derive `_section_is_reader_visible` from that predicate exactly. If the renderer always writes anchors for every content section with any items, the spec is correct; if it gates on paragraph indices, the spec must adopt the tighter criterion.

---

## Important

### I1 — `_html_ids` / `_IdCollectingHTMLParser` duplicated; two independent implementations risk silent divergence

`status_integrity.py:495–509` already defines private `_html_ids()` and `_IdCollectingHTMLParser`. The new module defines the same logic again. Two independent implementations can diverge silently: a bug fix or `convert_charrefs` behavior change applied to one will not propagate to the other. The plan should extract the parser to a shared private utility (e.g., `row_one/_html_ids.py`) and import it in both places, or import the existing private function from `status_integrity`.

---

### I2 — Anchor constants redefined rather than shared; no compile-time guarantee of consistency

`status_integrity.py` privately defines `_LOCAL_ARTICLE_FRAGMENT = "local-article"` and `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX = "local-article-paragraph-"`. The new module re-declares these as public constants `LOCAL_ARTICLE_BODY_ANCHOR` and `LOCAL_ARTICLE_PARAGRAPH_ANCHOR_PREFIX`. Both files also introduce `LOCAL_ARTICLE_CONTENT_SECTION_ANCHOR_PREFIX = "local-article-content-section-"` independently. With separate definitions, a typo or refactor in one module is not caught by the type checker, and the existing `_validate_local_intelligence` path would silently diverge from the new content-health path. Extract to a single shared constants module (e.g., `row_one/local_article_anchors.py`) and import in both `status_integrity.py` and `local_article_content_health.py`.

---

### I3 — `RowOneGeneratedSiteHealth` wrapper not described in the spec; return-type break is unspecified

The spec's Architecture section describes `RowOneLocalArticleContentHealth` but does not describe the `RowOneGeneratedSiteHealth` wrapper dataclass or the signature change to `validate_row_one_generated_site_integrity`. The CLI currently assigns:

```python
local_article_route_health = validate_row_one_generated_site_integrity(
    site_dir=site_dir, edition=edition,
)
```

The plan's Task 5 changes this return type without specifying in the spec what the combined object looks like or how the CLI extracts the route-health member. Parallel workers (Worker B handles `status_integrity.py` and `cli.py`; Worker A is in a different scope) must share an interface contract that currently lives only in the plan's pseudocode. The spec should include the `RowOneGeneratedSiteHealth` dataclass definition to serve as that contract.

---

### I4 — Plan says "In `_render_row_one_ops_check_text(...)`" without clarifying the file

Task 7 Step 2 instructs: "In `_render_row_one_ops_check_text(...)`, add: `f"Local article content: {local_article_content.get('status', 'unknown')}"`." That function is defined in **`cli.py:2353`**, not in `ops_check.py`. A worker reading the plan alongside the file structure would naturally look in `ops_check.py` first (the stated file for Task 7) and miss the actual target. The plan must specify `cli.py` as the file to modify for this step, which also means `cli.py` should appear in the Worker C scope or be coordinated with Worker B.

---

## Minor

### m1 — No test for `skipped=True` articles; regression risk on empty-paragraph edge case

`RowOneLocalArticle` allows `skipped=True` with empty `paragraphs`. There is no planned test `test_content_health_handles_skipped_local_articles`. Without it, a regression could cause the health check to expect `id="local-article-paragraph-1"` for an article with no non-empty paragraphs, producing a spurious `missing` status. Add a fixture with `skipped=True, paragraphs=[]` and assert `health.paragraph_anchor_count == 0` and `health.missing_paragraph_anchors == ()`.

---

### m2 — `_format_saved_local_article_count` reuse not called out in Task 5

The human output line in Task 5 Step 2 invokes `_format_saved_local_article_count(local_article_content['article_count'])`. That function is already defined at `cli.py:2282`. The plan doesn't flag it as an existing reuse; a worker might accidentally duplicate or shadow it. The plan should note the reuse explicitly.

---

### m3 — Task 6 RED filter includes already-passing `local_article_route` tests without a clear explanation

Task 6 Step 2 runs:

```bash
pytest tests/test_row_one_ops_check.py -q -k "local_article_content or local_article_route"
```

The `local_article_route` tests in that file currently pass. Mixing them into the expected-RED run is not wrong, but the plan's "Expected:" line says only the new tests fail. This is true but could confuse a worker who sees some tests pass and wonders if they've already implemented something. Add a note clarifying only `local_article_content` tests are expected to fail at this step.

---

### m4 — Docs test for Stage 375 boundary paragraph ordered before Stage 374, but plan doesn't confirm the ordering test

The documentation test in Task 8 must verify the Stage 375 paragraph appears **before** the Stage 374 paragraph in both docs. The plan says "Insert the exact Stage 375 documentation boundary paragraph before the Stage 374 paragraph" but the test skeleton only specifies an exact-paragraph presence check. An ordering assertion (the Stage 375 paragraph's position index is less than Stage 374's) should be added to `test_row_one_docs.py` to prevent a worker from appending rather than inserting the paragraph.
