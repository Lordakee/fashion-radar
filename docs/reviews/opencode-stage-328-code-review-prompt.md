Review final Stage 328 code changes in /home/ubuntu/fashion-radar.

Scope:
- Generated-site-only evidence excerpts for the existing ROW ONE Saved Signal Index.
- Existing `articles/index.html` only.
- Excerpts derive only from already saved `RowOneLocalArticle` item bodies or saved paragraphs.
- No new generated page, no JSON sidecar, no app/runtime/manifest/schema contract change.
- No source collection, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review product feature.

Changed areas to inspect:
- `src/fashion_radar/row_one/saved_signal_index.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_signal_index.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`
- Stage 328 plan/spec/review artifacts under `docs/superpowers/` and `docs/reviews/`

Please identify Critical, Important, Medium, and Minor issues.
Focus on:
- correctness of excerpt selection and fallback behavior
- escaping and link/id/class safety
- contract and artifact containment
- TDD coverage and regression risk
- whether the implementation satisfies `docs/superpowers/plans/2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-plan.md`

Known prior review findings already addressed:
- added item-body test for blank English/nonblank Chinese fallback
- renamed the excerpt length constant to `SAVED_SIGNAL_INDEX_EXCERPT_CHARS`

Return a concise complete review under 140 lines with sections:
`Critical`, `Important`, `Medium`, `Minor`, and `Verdict`.
If there are no findings for a severity, write `None`.
Do not edit files.
