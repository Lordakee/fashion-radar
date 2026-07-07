Review the Stage 328 plan for /home/ubuntu/fashion-radar.

Files to review:
- docs/superpowers/specs/2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-design.md
- docs/superpowers/plans/2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-plan.md
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- src/fashion_radar/row_one/saved_signal_index.py
- src/fashion_radar/row_one/templates.py
- tests/test_row_one_saved_signal_index.py
- tests/test_row_one_render.py
- tests/test_row_one_docs.py
- tests/test_workflows.py

Stage 328 objective:
- Add display-only evidence excerpts to the existing ROW ONE Saved Signal Index inside articles/index.html.
- Excerpts must derive only from already saved RowOneLocalArticle content item bodies or saved paragraphs.
- Keep the feature generated-site-only and contract-safe.

Hard boundaries:
- Do not propose a separate generated page.
- Do not add saved-signal-index.html, saved-signal-excerpt.html, saved-signal-index.json, or saved-signal-excerpts.json.
- Do not add saved_signal_excerpt, signal_excerpt, or related fields to row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, or JSON artifacts.
- Do not add source collection, fetching, extraction, matching, scoring, ranking, LLM calls, connectors, scheduling, deployment, market grouping, domestic/international classification, or compliance-review product behavior.
- Hrefs, ids, classes, filenames, and fragments must not derive from display strings or excerpt text.

Please review the plan for:
1. Feasibility with the current saved signal index builder/template architecture.
2. TDD completeness and whether the RED/GREEN steps can actually catch missing excerpt behavior.
3. Contract and route safety.
4. Whether any step risks touching frozen surfaces.

Return a concise complete review with Critical, Important, Medium, and Minor findings.
If there are no findings in a severity, write `None`.
Do not edit files.
