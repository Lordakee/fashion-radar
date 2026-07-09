# Stage 374 Saved Local Article Route Health Design

## Goal

Stage 374 adds read-only Saved Local Article Route Health for generated ROW ONE sites. The feature verifies that every current saved local article sidecar has a reachable same-site article page and that the generated article library route is present and linked.

## User Value

ROW ONE already downloads or saves local article bodies and has many organization surfaces for them. The remaining operational risk is simpler and more damaging: a site can contain `data/articles/*.json` sidecars while the user-facing generated site does not expose `articles/index.html` or `articles/<story-id>.html`.

Stage 374 turns that gap into a concrete health signal. `row-one status` rejects incomplete generated sites, and `row-one ops-check` reports the route health with an action telling the operator to refresh the generated site.

## Product Shape

Feature name: **Saved Local Article Route Health** / **本地文章路由健康检查**.

The health check is generated-site-only and read-only. It does not render a new page section. It inspects existing files:

- `data/articles/*.json`
- `index.html`
- `articles/index.html`
- `articles/<story-id>.html`

When no saved local article sidecars exist, the health status is `not_applicable`.

When saved local article sidecars exist, the status is `ready` only if:

- `articles/index.html` exists
- `index.html` contains the same-site `href="articles/index.html"` library link
- every saved article story id has `articles/<story-id>.html`
- `articles/index.html` contains same-directory links to those article pages

Otherwise the status is `missing`.

## Architecture

Create a focused module:

`src/fashion_radar/row_one/local_article_route_health.py`

The module owns a pure dataclass and analyzer:

```python
@dataclass(frozen=True)
class RowOneLocalArticleRouteHealth:
    status: str
    article_count: int
    library_path: str
    library_present: bool
    homepage_library_link_present: bool
    missing_article_pages: tuple[str, ...]
    missing_library_links: tuple[str, ...]
```

The analyzer accepts `site_dir` plus an optional current story-id collection. When story ids are supplied, it uses that exact validated set. When not supplied, it discovers safe `data/articles/*.json` filename stems for read-only ops diagnostics.

The module also exposes:

- `row_one_local_article_route_health_payload(...)`
- `validate_row_one_local_article_route_health(...)`

`row_one status` and `status_integrity.py` use the strict validation path after the existing sidecar validation has accepted current story ids. `validate_row_one_generated_site_integrity(...)` returns the computed route-health object after validation so `row-one status --json` reports the same validated story-id set instead of running a second independent discovery pass. Existing callers that ignore the return value keep working.

`row-one ops-check` uses the read-only analyzer discovery path and includes the payload as an ops diagnostic.

## Data Sources

Stage 374 reuses only current generated site files and existing saved local article sidecar filenames.

It does not read remote URLs, call source collection, fetch articles, extract article bodies, score stories, rank stories, call LLMs, use connectors, schedule jobs, deploy services, generate images, or review compliance.

## Status Integration

`validate_row_one_generated_site_integrity(...)` should call the route-health validator after `_load_article_sidecars(...)` returns current validated sidecars, keep the existing local-intelligence validation, and return the validated route-health object to the CLI status payload builder.

If sidecars exist and route health is not `ready`, `row-one status` fails with a clear message naming the missing route or link, such as:

- `row-one local article library route is missing: articles/index.html`
- `row-one local article route is missing: articles/the-row-signal-1234567890.html`
- `row-one local article library link is missing from index.html: articles/index.html`
- `row-one local article library page is missing article link: the-row-signal-1234567890.html`

The machine-readable status payload adds a CLI-only top-level `local_article_routes` object. This is not written into `data/edition.json`, `data/manifest.json`, `data/runtime.json`, `row-one-app/v7`, `row-one-manifest/v1`, or `row-one-runtime/v1`.

The human `row-one status` output adds a compact line:

`Local article routes: ready (N saved local articles)`

## Ops-Check Integration

`build_row_one_ops_check_payload(...)` adds top-level `local_article_routes`.

If saved local article sidecars exist but route health is `missing`, the overall ops status becomes `attention` and actions include:

`Run `fashion-radar row-one refresh --output-dir <site_dir>`.`

The human `row-one ops-check` output adds:

`Local article routes: ready|missing|not_applicable`

## Site Integration Boundaries

Stage 374 does not create:

- `data/local-article-route-health.json`
- `data/article-route-health.json`
- `data/route-health.json`
- `local-article-route-health.html`
- `article-route-health.html`
- `route-health.html`

It does not add a new route family. It validates the existing `articles/index.html` and `articles/<story-id>.html` route family created by earlier stages.

It does not alter `index.html`, `articles/index.html`, `articles/<story-id>.html`, or detail page rendering. It does not publish full articles outside existing local article pages and does not add outbound article URLs as primary navigation.

## Documentation Boundary Paragraph

Stage 374 adds read-only generated-site Saved Local Article Route Health to `row-one status` and `row-one ops-check`; it reuses current generated `data/articles/*.json` saved local article sidecars, current validated story ids, existing `index.html`, existing `articles/index.html`, and existing `articles/<story-id>.html` routes to verify that already-saved local article bodies are reachable through same-site generated article pages without changing app-facing contracts; it adds CLI-only route-health status payload fields, but it does not create `data/local-article-route-health.json`, does not create `data/article-route-health.json`, does not create `data/route-health.json`, does not create `local-article-route-health.html`, does not create `article-route-health.html`, does not create `route-health.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, `articles/<story-id>.html`, or detail page rendering, does not publish full articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

## Tests

Analyzer tests should prove:

- no sidecars returns `not_applicable`
- complete library and article pages return `ready`
- missing `articles/index.html` returns `missing`
- missing homepage library link returns `missing`
- missing article pages are reported deterministically
- missing links from `articles/index.html` are reported deterministically
- unsafe discovered sidecar stems are ignored in read-only ops discovery
- supplied story ids are used exactly and sorted deterministically

Status tests should prove:

- `row-one status --json` includes CLI-only `local_article_routes`
- `row-one status` succeeds for a generated site with a saved article library
- `row-one status` rejects a missing `articles/index.html` when saved article sidecars exist
- `row-one status` rejects a missing `articles/<story-id>.html`
- `row-one status` rejects a missing homepage library link
- `row-one status` rejects a missing article link inside `articles/index.html`

Ops-check tests should prove:

- route health is included in JSON payloads
- missing local article routes produce `attention`
- missing local article routes produce a refresh action
- human ops-check output includes the route-health line

Docs and workflow tests should prove:

- README and `docs/row-one.md` include the exact Stage 374 boundary paragraph before Stage 373
- stale boundary phrases are absent
- generated app/runtime/manifest contracts do not contain Stage 374 identifiers
- forbidden Stage 374 artifact names are not generated
- the route-health analyzer is read-only and generated-site-only

## Out of Scope

Stage 374 does not add social platform connectors, crawling, article acquisition, article extraction, LLM summarization, recommendation logic, analytics, app UI, deployment, image generation, homepage modules, article library visual modules, article-page visual modules, or compliance-review behavior.
