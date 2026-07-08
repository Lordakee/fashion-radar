Re-review Stage 341 plan fixes only.

Files:
- docs/superpowers/specs/2026-07-08-stage-341-row-one-local-article-information-panel-design.md
- docs/superpowers/plans/2026-07-08-stage-341-row-one-local-article-information-panel-plan.md

Original review required:
1. Do not redefine `_local_article_body_source_label(article) -> str`; use `_local_article_body_source_label_localized()`.
2. Panel calls `_local_article_rendered_paragraph_indices(article)` before `_strict_valid_local_article_paragraph_indices()`.
3. Render-level invalid-index test uses `[0, 0, 99]`, not bool/string values.
4. `_signal_briefing_local_article()` exists; add module-level `_html_between()` if absent.
5. Insert `{information_panel}` after story source and before `{local_article_section}`; spell out contract JSON variables.

Answer briefly: Approved/Not approved; Critical blockers; Important blockers; Minor notes.
