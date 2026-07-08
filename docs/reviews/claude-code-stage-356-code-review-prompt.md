# Stage 356 Code Review Prompt

Review the current working tree for Stage 356, `Saved Article Key Signals`.

Scope:

- New builder: `src/fashion_radar/row_one/saved_article_key_signals.py`
- Render integration:
  - `src/fashion_radar/row_one/render.py`
  - `src/fashion_radar/row_one/templates.py`
- Tests/docs:
  - `tests/test_row_one_saved_article_key_signals.py`
  - `tests/test_row_one_render.py`
  - `tests/test_row_one_docs.py`
  - `tests/test_workflows.py`
  - `README.md`
  - `docs/row-one.md`
  - Stage 356 spec/plan/review docs

Requirements:

1. `Saved Article Key Signals` is generated-site-only and renders only inside
   eligible `articles/<story-id>.html` local article pages.
2. Render order is after the Stage 355 local section binder when present and
   always before `id="local-article"` when key signals render.
3. No app contract, schema, runtime, manifest, generated JSON artifact, sidecar,
   route family, fetcher, extractor, scorer, ranker, LLM, connector,
   scheduler, deployment, analytics, personalization, recommendation, or
   compliance-review behavior changes.
4. Builder uses only existing `RowOneStory` and `RowOneLocalArticle` inputs.
5. `Why It Matters` prefers
   `local_article.brief_sections[key="why_it_matters"]`; it falls back only to
   `RowOneStory.why_it_matters` when the local article has at least one
   nonblank saved paragraph. It must not invent paragraph evidence for story
   fallback text.
6. `Brands`, `Products`, and `People` are built from existing item references
   bucketed through `row_one_saved_article_reference_bucket(...)`, skip blank
   reference names, and dedupe by normalized displayed name.
7. Non-Why-It-Matters groups carry readable support statements when available
   and should not become pure link directories.
8. `Themes` uses displayed content section titles and item labels only; raw
   section keys are not displayed as theme labels, and displayed reference names
   are not repeated as theme labels.
9. Paragraph evidence rejects bools, non-ints, negatives, duplicates,
   out-of-range indices, and blank source paragraphs. Hrefs must be one-based
   `#local-article-paragraph-N`.
10. Renderer revalidates all hrefs and accepts only
    `#local-article-paragraph-N` and `#local-article-content-section-N`.
11. Rendered text is escaped.
12. Tests cover builder behavior, render behavior, generated-site-only scope,
    docs wording, and workflow artifact/contract absence.

Please return findings ordered by severity. If there are no blockers or
important issues, say that clearly and mention any residual risk.
