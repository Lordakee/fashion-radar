# opencode Stage 375 Plan Re-Review

## Verdict

The Stage 375 Local Article Content Health plan/spec is feasible and ready for implementation. I independently re-verified the plan against the renderer and existing status/ops-check code paths. No Critical or Important issues remain.

## Critical

None.

## Important

None.

## Confirmed Resolutions

- Prior I-1 is resolved. The plan now excludes empty-paragraph sidecars from renderable content-health expectations, which matches `_render_local_article(...)`: the renderer omits the whole local article section when `_render_local_article_paragraphs(...)` has no output. Strict `row-one status` already rejects empty-paragraph sidecars before content health runs, and read-only `ops-check` discovery now avoids false positives for valid-schema empty sidecars.
- Prior I-2 is resolved. The shared anchor helper now specifies both `parse_html_ids(html: str) -> set[str]` for existing cached status-integrity validation and `html_ids(path: Path) -> set[str]` for path-reading diagnostics. This preserves the current `html_cache` behavior instead of forcing repeated path reads.
- Renderer semantics are verified. Paragraph anchors preserve original one-based paragraph positions while skipping blank paragraphs, and content-section anchors are emitted once per `RowOneLocalArticle.content_sections` entry.
- Return-type blast radius is small. `validate_row_one_generated_site_integrity(...)` has a single CLI caller, and the already validated `article_sidecars` mapping is available for strict content-health validation.
- Read-only behavior is preserved. The planned analyzer reads only local sidecars and generated article HTML, and it writes no generated JSON, HTML, DB, config, or source-collection artifacts.

## Minor

- Product Shape should say `not_applicable` applies when there are no renderable sidecars, not only when there are no sidecars.
- The empty-paragraph test would benefit from an explicit assertion sketch to avoid underspecification.
- The spec should call out that `ops-check` route-health and content-health `article_count` can diverge only in read-only discovery cases, because route health counts safe stems and content health parses renderable sidecars.
- The parallel-worker prose should state that Workers B and C depend on Worker A's modules and should start after Task 3 lands.

## Net Assessment

The remaining items are documentation polish only. The stage can proceed once those minor notes are applied or accepted.
