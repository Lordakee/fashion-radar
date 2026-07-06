## Stage 314 Review: Local Article Observability

All verification steps passed (2078 tests, ruff, uv lock, hygiene, and the two smoke runs). No Critical or Important findings. Here are the minor/nit observations and residual risks, ordered by potential impact.

### No Critical or Important Issues

### Minor Findings

#### M1 — Stale-sidecar fix is technically sound, but refresh has no integration-level stale test

File: `tests/test_row_one_cli.py:331-373`

The parametrized test `test_row_one_build_and_preview_metrics_ignore_stale_sidecars_without_latest_only` covers `build` and `preview`. The `refresh` command goes through the same `_write_row_one_site_from_cli_options` path, but its test (`test_row_one_refresh_runs_pipeline_and_writes_site`) mocks `_write_row_one_site_from_cli_options` and returns `RowOneLocalArticleSiteMetrics()` directly, so it never exercises the actual filter.

This is not a bug. The render logic under `build` and `preview` is identical to what `refresh` calls, but the integration gap means a regression in `_writable_local_articles` that only fires during a full render would be undetected in the refresh test. The risk is low, and it can be addressed in a later stage.

#### M2 — `build_row_one_local_article_metrics` silently ignores `organized_section_count` for the current-render path in one test

File: `tests/test_row_one_site_metrics.py:89-112`

`test_local_article_metrics_count_current_render_articles_without_scanning_site` does not assert `organized_section_count`. The current article has no `content_sections` set, so the expected value is 0, but the assertion is absent. This is a nit. The field is tested in every other test in the file, but if the metric's purpose is ever refactored, the omission here could mask a regression.

#### M3 — `article_count` vs writability asymmetry in site metrics

Files: `src/fashion_radar/row_one/site_metrics.py:33-43`, `src/fashion_radar/row_one/render.py:190-202`

`_writable_local_articles` requires `article.paragraphs` to be truthy before writing a sidecar to disk (`render.py:200`). That means freshly-rendered sidecars always have at least one paragraph, so `article_count` and `paragraph_count > 0` are aligned for fresh renders.

`build_row_one_local_article_site_metrics` (used by `row-one status`) scans the disk and counts sidecars with empty paragraph lists as valid articles (tested in `test_row_one_site_metrics.py:66-86`). This divergence is correct per the stated requirement, but it means the documentation phrase "valid generated `data/articles/<story-id>.json` sidecars" needs to be read carefully: it means parseable and schema-valid, not has body paragraphs. The docs and tests both reflect this, so no action required.

#### M4 — `source_count` normalization is opinionated in an undocumented way

File: `src/fashion_radar/row_one/site_metrics.py:44-46`

```python
sources.add(" ".join(source_name.split()).casefold())
```

Whitespace collapsing plus casefold deduplication means `"Vogue Business"` and `"vogue business"` are treated as the same source. This is reasonable defensive behavior, but it is not documented, and the metric label `source_count` gives no hint that case and whitespace normalization is applied. No action required unless `source_count` is ever surfaced in user-facing copy that makes uniqueness claims.

#### M5 — Workflow assertions cover contract JSON but not `data/articles/` indirectly

File: `tests/test_workflows.py:350-353`

The assertions confirm the three strings `"local_articles"`, `"local_article_count"`, and `"local_article_paragraph_count"` do not appear in the combined edition/manifest/runtime JSON payload, and that no `local-article-metrics.json` file is created (`line 353`). This is the correct level of assertion for the requirement. The test does not separately assert that each contract JSON file individually lacks those keys, but the combined-string check is sufficient since all three JSON files are serialized into the same `generated_contract_payload` string before the assertions.

### Nit

`RowOneRenderResult` is a frozen dataclass with a new field.

File: `src/fashion_radar/row_one/render.py:51-58`

The `local_article_metrics` field is added to the frozen dataclass. All construction sites in the codebase go through `render_row_one_site()` and the one mock in `test_row_one_cli.py:439-445` explicitly constructs `RowOneLocalArticleSiteMetrics()`. No risk of positional arg drift because the dataclass uses keyword construction everywhere.

### Summary Table

| # | Severity | File | Description | Action |
|---|----------|------|-------------|--------|
| M1 | Minor | `test_row_one_cli.py:331` | `refresh` stale-sidecar scenario not covered at integration level | Optional follow-on |
| M2 | Minor | `test_row_one_site_metrics.py:89` | `organized_section_count` not asserted in render-path test | Optional nit |
| M3 | Minor | `site_metrics.py:33` / `render.py:200` | `article_count` counts empty-paragraph sidecars on disk (by design) | No action, documented |
| M4 | Nit | `site_metrics.py:44` | Source deduplication is undocumented | No action |
| M5 | Nit | `test_workflows.py:350` | Contract assertion uses combined-string check, not per-file | No action, sufficient |

Stage 314 is clear to ship as-is. None of the above findings introduce data loss, contract drift, or backward-incompatible changes to CLI/status JSON output. The stale-sidecar fix is technically sound. All three JSON contracts remain unchanged.
