All235 tests pass. Here are the findings.

---

## Critical

None.

---

## Important

None. All three prior Important findings are fixed:

**Prior Important 1 — `_html_contains_href` brittle literal matching: FIXED.**
The implementation replaced the `in html` substring check with a proper `_HrefCollector(HTMLParser)` subclass that collects actual `href` attributes from parsed HTML, plus a `_normalize_href` helper that strips leading `./` prefixes. The attribute check uses `name.lower() == "href"`, making it case-insensitive. A dedicated new test `test_route_health_accepts_html_href_variants` covers `HREF = "./articles/index.html"` and `HREF = './{story_id}.html'`, explicitly documenting the format assumptions the parser handles.

**Prior Important 2 — `story_ids` str-guard undocumented: FIXED to Minor.**
The `isinstance(story_ids, str)` guard still carries no inline comment and the annotation still says `Iterable[str] | None`, but `test_route_health_uses_supplied_story_ids_exactly` now explicitly passes a bare string and asserts it is treated as a single-element collection. The behavior is documented by test. Remaining annotation gap is Minor.

**Prior Important 3 — validator priority for multi-condition missing states: FIXED.**
`test_validate_route_health_raises_clear_errors` now constructs a `missing` health object with all three failure flags set simultaneously (`homepage_library_link_present=False`, `missing_article_pages`, `missing_library_links`) and asserts the homepage-link condition fires first, explicitly confirming priority order.

---

## Minor

**1. (Prior 4 — unchanged)** Unreachable fallthrough `raise ValueError("row-one local article route health is missing")` at `local_article_route_health.py:115`. The construction logic in `build_row_one_local_article_route_health` guarantees at least one condition flag is set whenever `status == "missing"`, so this branch can never execute. Harmless dead code.

**2. (Prior 2 — downgraded)** `_resolve_story_ids` annotation still says `Iterable[str] | None` even though a bare `str` is silently wrapped. The behavior is tested, but the type annotation is technically inaccurate. Tightening to `Sequence[str] | set[str] | None` would make the implicit contract visible to type checkers.

**3. (Prior 5 — unchanged)** `not_applicable` return value sets `library_present=False` and `homepage_library_link_present=False`. Under `status="not_applicable"` these flags have no meaningful content but a consumer reading the JSON payload sees them as `false`. No code comment explains that these fields are only meaningful when `article_count > 0`.

**4. (Prior 6 — unchanged)** `test_stage_374_saved_local_article_route_health_stays_generated_site_only` monkeypatches `status_integrity.build_row_one_local_article_route_health` and `validate_row_one_local_article_route_health` then calls the site-file-write test. Because the site generation path never calls those functions in the first place, the monkeypatch has no effect on the test outcome — it passes regardless of whether the patch is applied. The real isolation guarantee is carried by the contract/artifact denylist assertions in other workflow tests; this test overstates its proof.

**5. (Prior 7 — FIXED)** `not_applicable` payload shape is now covered. `test_route_health_payload_is_stable` asserts the full `not_applicable` dict, closing the shape-regression gap from the prior review.

**6. (Prior 8 — unchanged, by design)** `row-one status` prints `Local article routes: ready (N saved local article)` with count; `row-one ops-check` prints `Local article routes: ready` without count. Per-spec asymmetry, no change needed.

**7. (New)** `_HrefCollector` at `local_article_route_health.py:157` calls `super().__init__()` without `convert_charrefs=True`. The sibling parser `_IdCollectingHTMLParser` in `status_integrity.py:502` explicitly passes `convert_charrefs=True`. ROW ONE generates clean ASCII hrefs so entity decoding never matters in practice, but the inconsistency could silently fail if a rendered href ever contained an HTML entity (e.g. `&#47;` for `/`). A one-line fix: `super().__init__(convert_charrefs=True)`.
