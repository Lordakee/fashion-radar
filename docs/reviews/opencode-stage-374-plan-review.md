# Stage 374 Plan Review - opencode

## Critical

None remain.

## Important

None remain.

The Stage 374 Saved Local Article Route Health plan is feasible and safe to implement. The plan now addresses the main risks:

- Route/link health checks cover `articles/index.html`, the homepage `href="articles/index.html"` link, each `articles/<story-id>.html` page, and each same-directory library link.
- `row-one status --json` reuses the route-health object produced by strict `validate_row_one_generated_site_integrity(...)` validation, so it does not run an independent filesystem discovery pass.
- The `validate_row_one_generated_site_integrity(...)` return-value change is backward-compatible for existing callers that ignore the return.
- `ops-check` keeps the existing `unknown` priority for missing site or unknown freshness, and only reports `attention` for missing local article routes when the base site state is present and diagnosable.
- The analyzer is read-only: it uses file existence checks, directory globbing, filename stems, and guarded `read_text`.
- `local_article_routes` is CLI-only and is not written to generated app/runtime/manifest JSON contracts.
- Generated `*-route-health.json` and `*-route-health.html` artifacts are explicitly out of scope and guarded by the planned workflow tests.
- The validator test plan covers all four error branches: missing library route, missing homepage library link, missing article page, and missing library page link.

## Minor

1. The human status line for zero saved articles may read as `Local article routes: not_applicable (0 saved local articles)`. This is cosmetic and does not block implementation.
2. The defensive single-quote branch in `_html_contains_href(...)` is acceptable because the plan documents it as support for hand-edited generated sites, while generated ROW ONE HTML uses double-quoted attributes.

## Verdict

Proceed with implementation.
