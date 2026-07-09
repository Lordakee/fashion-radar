**Generated-site-only boundary** — `render.py` passes the existing `local_article_page_hrefs_by_detail_path` map reused as `daily_local_theme_summary_strip_hrefs_by_detail_path`. No new artifact written, no new route family. `test_workflows.py` adds contract assertions (both the negative string checks and the artifact-path sweep) and the `test_stage_364_daily_local_theme_summary_strip_stays_generated_site_only` monkeypatch test. ✓

**No prohibited additions** — `templates.py` adds only constants, frozen dataclasses, and pure render/build functions. No schema mutations, no JSON I/O, no fetch, no LLM, no scheduling, no analytics, no recommendation logic. ✓

**URL/anchor safety** — `_daily_local_theme_summary_strip_card_target` delegates entirely to `_daily_local_coverage_map_card_target` (existing validated logic). The main safety test exercises wrong-prefix, absolute, traversal, nested, whitespace, leading-slash, leading-dot, double-slash, href-mismatch, missing-article, blank-source, and empty-paragraph cases — all asserted absent from output. ✓

**HTML escaping** — every data-derived value flowing into HTML uses `_esc()`: title, summary, count labels, ref name, ref label, link href, link title (both languages), source name. Static strings (class names, `data-lang` values, hardcoded UI copy) are literals. ✓

**Test coverage** — seven new unit tests cover: docs boundary, safety/URL filtering, omit-when-no-eligible-cards (parametrized 4 cases), ordering after coverage-map and before saved-organization, ordering without coverage-map present, CSS selector completeness, and the generated-site-only workflow contract. ✓

APPROVED
