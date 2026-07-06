# Stage 314 ROW ONE Local Article Observability Design

## Objective

Make ROW ONE prove whether a generated site contains local saved article
content. Stage 310-313 can render and organize saved article sidecars, but a
real build can still finish successfully with zero `data/articles/*.json`
sidecars and no homepage saved-article modules. Stage 314 should make that state
visible in CLI output, `row-one status --json`, tests, and docs.

## User Need

The user wants articles downloaded/saved locally and published into the ROW ONE
website, not a page that only sends readers to outside links. When the generated
site has no saved local article bodies, the tool should make that obvious and
diagnosable instead of reporting only generic readiness.

## Current Context

The acquisition path already exists:

- `row-one build`, `row-one preview`, and `row-one refresh` call
  `write_row_one_site_files()`.
- `write_row_one_site_files()` builds the ROW ONE edition, calls
  `build_row_one_local_articles()`, and passes the resulting mapping to
  `render_row_one_site()`.
- `render_row_one_site()` writes `data/articles/<story-id>.json` when the
  mapping contains current-edition safe story IDs with nonblank paragraphs.
- `row_one_article.enabled: true` is configured for the primary RSS sources in
  `configs/sources.yaml`.

The remaining gap is observability and artifact-level proof:

- current generated `reports/row-one/site` can report `ok: true` while having no
  `data/articles/`;
- build/preview/refresh output does not show saved article counts;
- status JSON does not expose local article sidecar counts;
- tests prove lower-level rendering and workflow paths, but do not make the
  generated artifact proof explicit for Stage 313 homepage saved modules.

## Recommended Approach

Add a small generated-site metrics module for local article sidecars:

```text
src/fashion_radar/row_one/site_metrics.py
```

It should read the generated site directory, count current local article
sidecars, nonblank saved paragraphs, organized content sections, and distinct
sources, then expose a stable dictionary for CLI/status output.

Wire the metrics into:

- `row-one build`;
- `row-one preview`;
- `row-one refresh`;
- `row-one status`;
- `row-one status --json`.

Add deterministic tests that build a ROW ONE site with a fake local article
extractor through the existing workflow path and assert:

- `data/articles/<story-id>.json` exists;
- the detail page includes `id="local-article"`;
- the homepage includes at least one local saved article module such as
  `daily-local-intelligence`, `saved-article-coverage`, or
  `saved-article-briefs`;
- CLI/status metrics show nonzero local article counts.

## Boundaries

This stage is observability and proof only.

Do not add a compliance-review product feature.

Do not add, enable, or default social/community connectors. Social/community
connector work remains future opt-in and external-tool-ready, but this stage
must not touch connector setup, adapters, imports, handoff commands, or platform
collection behavior.

Do not change:

- `row-one-app/v7`;
- `data/edition.json`;
- `row-one-manifest/v1`;
- `data/manifest.json`;
- `row-one-runtime/v1`;
- `data/runtime.json`;
- schemas;
- story IDs;
- detail routes;
- paragraph anchors;
- source collection behavior;
- scraping behavior;
- scoring, ranking, matching, or sorting;
- scheduling;
- LLM calls;
- translation services;
- image generation.

Do not write a new generated JSON artifact. The new metrics are CLI/status
output derived from already generated files.

Do not republish full external articles on the homepage. Existing saved article
rendering remains capped and source-attributed.

## Data Model

Use an internal dataclass only:

```python
@dataclass(frozen=True)
class RowOneLocalArticleSiteMetrics:
    article_count: int
    paragraph_count: int
    organized_section_count: int
    source_count: int
```

The metrics module may also expose:

```python
def build_row_one_local_article_site_metrics(site_dir: Path) -> RowOneLocalArticleSiteMetrics
def row_one_local_article_site_metrics_payload(metrics: RowOneLocalArticleSiteMetrics) -> dict[str, int]
```

The metrics should tolerate missing `data/articles/` by returning zero counts.
`row-one status` still relies on the existing integrity validator to reject
invalid sidecars.

## CLI Output

`row-one build`, `row-one preview`, and `row-one refresh` should print at least:

```text
Saved local articles: N
Saved local paragraphs: N
```

`row-one status` should print the same counts.

`row-one status --json` should include:

```json
"local_articles": {
  "article_count": 0,
  "paragraph_count": 0,
  "organized_section_count": 0,
  "source_count": 0
},
"local_article_count": 0,
"local_article_paragraph_count": 0
```

These are status/ops fields, not app contract fields.

## Testing Strategy

Add focused tests for:

- metrics from an empty generated site;
- metrics from generated `data/articles/*.json`;
- status text and JSON output;
- build/preview/refresh output count wiring where practical;
- workflow artifact proof that an enabled source plus deterministic extractor
  produces a sidecar, detail local article section, and homepage saved article
  modules.

Verification should also build the real local site and run `row-one status
--json`; a zero article count is acceptable for the current local environment,
but it must be visible.

## Success Criteria

Stage 314 is complete when:

- the code still passes the full test suite and release hygiene;
- `row-one status --json` reports local article metrics;
- build/preview/refresh/status text output includes saved local article counts;
- deterministic workflow tests prove nonzero sidecars create local article
  detail content and homepage saved article modules;
- docs explain that full local article bodies require `row_one_article.enabled`
  sources and the optional article extraction dependency;
- no app/runtime/manifest contract changes occur.
