# Claude Code Stage387 Code Review

## Verdict
APPROVED

## Scope Reviewed

- `src/fashion_radar/row_one/daily_local_brand_product_people_signal_digest.py` (new builder)
- `src/fashion_radar/row_one/render.py` and `templates.py` (modified)
- `tests/test_row_one_daily_local_brand_product_people_signal_digest.py` (new,800lines, committed)
- `tests/test_row_one_render.py` and `tests/test_row_one_docs.py` (unstaged)
- `tests/test_workflows.py` (committed, sentinel + contract/artifact denylist)
- `README.md`, `docs/row-one.md`, plan, and design (unstaged docs)
- `docs/reviews/claude-code-stage-387-plan-review.md`, `docs/reviews/opencode-stage-387-plan-review.md`
- Base diff: `git diff f6cdd0f..HEAD` plus all unstaged Stage 387 changes

## Findings

None.

**Safety and escaping:** Every user-facing string is routed through `_esc()` in the renderer, confirmed by the hostile-string test fixtures (`<entity>`, `<Business>`, `<evidence>`). The builder's `_safe_article_page_href` rejects URLs, traversals, query strings, fragment characters, absolute paths, multi-part paths, whitespace, and `index.html`; the template's `_safe_daily_local_brand_product_people_signal_digest_href` independently re-validates every support href using `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch`, correctly distinguishing content-section anchors from paragraph anchors and rejecting section-0.

**Sidecar integrity:** `_valid_article` guards both `safe_local_article_story_id(story_id)` and `article.story_id != story_id`; the mismatched-third-sidecar test confirms a mismatched sidecar contributes neither an item nor a support — closing both plan-review residual risks.

**Scope boundary:** `render_row_one_site` builds the payload and passes it only to `render_index_html`; the homepage-only sentinel test monkeypatches `_render_daily_local_brand_product_people_signal_digest` and asserts the sentinel appears exclusively in `index.html`, absent from `articles/index.html`, every article/detail page, `data/edition.json`, `data/manifest.json`, `data/runtime.json`, and all `data/articles/*.json` payloads. The contract and artifact denylists (11 and 10 terms respectively) enforce the JSON non-creation boundary.

**Ordering and counts:** Bucket display order (brands, products, people) matches the spec. Entity insertion order is preserved by dict key order; no coverage sort is applied. The rendered entity-count metric is re-derived from actually-rendered items (defensive against invalid hrefs) rather than from `digest.entity_count`, which is the correct behavior. Article/source counts are set-based and cannot double-count.

**Reference atlas alignment:** `row_one_saved_article_reference_bucket` is imported and reused for bucket assignment, giving correct brands > people > products precedence; `source_context` results are filtered by checking against `_BUCKET_ORDER = ("brands", "products", "people")`. The label-over-type and hyphenated creative-director cases are tested and handled.

**Test coverage:** Builder tests cover aggregation, first-seen ordering, support deduplication per `(story_id, section_position)` key, item and support caps, excerpt truncation, fallback from section body, one-language bilingual fallback, mismatched sidecar rejection, unsupported event type filtering, blank-source handling, same-source deduplication, label-based bucket override, and second-section anchor positioning. Renderer tests cover bilingual output, escaping, href rejection (six unsafe patterns), omission (None and all-invalid-href cases), section ordering, CSS selector presence including mobile collapse, and rendered count recalculation. Workflow tests cover the full integration render. Docs tests cover exact paragraph text, ordering before Stage 386, and a50+-phrase stale-claim denylist.

**Release hygiene:** Plan and code review records are complete, credential-free, and contain no live-capture stubs. The docs paragraph is identical in README.md and docs/row-one.md and matches the exact string asserted in the docs test.

## Verification Assessment

590 Stage 387 tests passed across builder, renderer, workflow, and docs suites. Ruff check and format check passed. Lockfile validation passed (`UV_NO_CONFIG=1 uv --no-config lock --check`). No test failures, no import errors, no whitespace issues in tracked diffs.

## Residual Risks

The rendered entity-count header metric reflects only entities whose supports survive the template's href re-validation, not the builder's total `entity_count`. In practice the builder's href guard and the template's guard enforce the same rules, so the counts will agree on any well-formed payload; on a manually constructed digest with invalid hrefs the metric could undercount. This is intentional defensive behavior, not a regression, and the test `test_render_daily_local_brand_product_people_digest_counts_safe_rendered_items` documents it explicitly.
