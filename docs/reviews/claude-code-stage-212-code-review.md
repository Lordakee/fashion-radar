# Stage 212 Code Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

None.

## Nits

**`test_collect_sources_skips_article_enrichment_for_html_and_sitemap` tests HTML only.**
The test name promises both HTML and SITEMAP, but the fixture only creates an `html_source` and an `rss_source` — no `sitemap_source` row is exercised through the runner. The guard covers both types via the same set literal, so behaviour is correct, but the test doesn't make that claim. Worth adding a `sitemap_source` alongside `html_source` and asserting its item is also un-enriched.

## Résumé

All five verification areas pass:

1. **`source.py`** — `HTML`/`SITEMAP` enum values inserted before `MANUAL_IMPORT`; `seed_urls` placed correctly after `url` with `Field(default_factory=list)`; both validator branches raise the right messages.
2. **`html.py` / `sitemap.py`** — Minimal, identical no-op stubs; correct `collect(source, *, started_at)` signature; return `CollectorResult.success` with empty items; zero extraction logic.
3. **`workflows.py`** — Both collectors imported and registered under the new `SourceType` keys; existing RSS/GDELT entries untouched.
4. **`runner.py`** — Guard correctly extended to `source_article_extractor is not None and source.type not in {SourceType.HTML, SourceType.SITEMAP}`; `SourceType` already imported; RSS still enriches, HTML/SITEMAP skip.
5. **Scope discipline** — No extraction, no schema change, no dependency change, no matching/scoring/report touch. `uv.lock`/`pyproject.toml` clean per pre-verified checks.

Test coverage is thorough for `test_source_model.py` (all seven branches), both collector no-op files, and the `_default_collectors` registration test. The only gap is the single nit above.
