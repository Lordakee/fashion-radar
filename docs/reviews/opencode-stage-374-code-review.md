# Stage 374 Code Review - opencode

## Critical

None.

## Important

None.

The Stage 374 Saved Local Article Route Health implementation is safe to proceed. The reviewed implementation matches the spec and plan:

- Route/link validation checks the generated article library, homepage article-library link, per-story local article pages, and same-directory library links.
- HTML href matching uses `HTMLParser`, case-insensitive `href` attribute matching, `./` prefix normalization, and `convert_charrefs=True`.
- The analyzer is read-only and uses file existence checks, directory globbing, filename stems, and guarded file reads.
- `validate_row_one_generated_site_integrity(...)` returns the strict route-health object built from validated sidecar story ids, and `row-one status --json` reuses that object instead of doing a second discovery pass.
- `row-one status` includes CLI-only `local_article_routes` JSON and a human route-health line with article count.
- `row-one ops-check` includes route health in JSON, reports `attention` when routes are missing, appends the refresh action, and prints a human route-health line.
- Generated-site-only boundaries are preserved; route-health identifiers are guarded out of app/runtime/manifest contracts and generated artifacts.
- Focused and full test suites passed during review, and ruff check/format were clean on the touched files.

## Minor

1. `validate_row_one_local_article_route_health(...)` contains a defensive fallthrough `raise ValueError("row-one local article route health is missing")` that is unreachable for objects built by `build_row_one_local_article_route_health(...)`. Harmless.
2. `story_ids: Iterable[str] | None` admits a bare string, but the implementation wraps a string as one story id and this behavior is covered by tests.
3. `not_applicable` payloads report `library_present=false` and `homepage_library_link_present=false`; those booleans are semantically inactive when `article_count == 0`.
4. The Stage 374 generated-site-only workflow guard follows the existing stage pattern, but the strongest isolation proof is still the contract and artifact denylist.
5. `row-one status` prints route count while `row-one ops-check` prints route status only; this asymmetry is intentional per the Stage 374 spec.

## Verdict

Proceed with full gates, commit, and push.
