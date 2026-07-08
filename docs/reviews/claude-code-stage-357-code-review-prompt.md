# Stage 357 Code Review Prompt

Review the current worktree against base commit
`a5f4a24d52bcbbe346541c089051b53f6742e056`.

Stage 357 goal: add a generated-site-only `Daily Local Key Signals Digest`
homepage section for ROW ONE. It aggregates Stage 356 per-article `Saved
Article Key Signals` from current-edition saved local articles, renders only on
`index.html`, links only to generated local article pages and safe local article
anchors, and does not change app payloads, schemas, runtime, manifest, sidecar
artifacts, route families, fetching, extraction, scoring, LLM, connector,
scheduling, deployment, recommendation, analytics, personalization, or
compliance-review behavior.

Please inspect both tracked modifications and untracked Stage 357 files:

- `src/fashion_radar/row_one/daily_local_key_signals_digest.py`
- `tests/test_row_one_daily_local_key_signals_digest.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`
- `tests/test_row_one_docs.py`
- Stage 357 plan/spec/review artifacts under `docs/superpowers/...` and
  `docs/reviews/...`

Review focus:

1. Homepage-only and generated-site-only boundary.
2. No app contract/schema/runtime/manifest/JSON/sidecar artifact changes.
3. Builder correctness:
   - skips unsafe story IDs, unsafe detail paths, mismatched article IDs, and
     missing Stage 356 signals;
   - preserves edition order;
   - reconstructs `articles/<story-id>.html#...` hrefs from Stage 356
     fragment-only evidence/theme links;
   - dedupes references/themes while keeping support counts from full eligible
     input before display caps;
   - handles missing local article titles by falling back to the story headline.
4. Template correctness:
   - escapes all display text;
   - revalidates every digest href;
   - rejects external URLs, traversal, nested paths, malformed fragments, and
     paragraph/content-section zero;
   - places the section after Saved Article Briefs and before Saved Article
     Content Organization.
5. Test coverage and docs/workflow guards.

Commands already run locally:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_key_signals_digest.py tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_key_signals_digest_homepage_only tests/test_row_one_render.py::test_render_index_html_includes_daily_local_key_signals_digest tests/test_row_one_render.py::test_render_index_html_places_daily_local_key_signals_digest_between_saved_sections tests/test_workflows.py::test_stage_357_daily_local_key_signals_digest_stays_generated_site_only tests/test_row_one_docs.py::test_row_one_docs_describe_stage_357_daily_local_key_signals_digest_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py tests/test_row_one_saved_article_key_signals.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/daily_local_key_signals_digest.py src/fashion_radar/row_one/templates.py src/fashion_radar/row_one/render.py tests/test_row_one_daily_local_key_signals_digest.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/daily_local_key_signals_digest.py src/fashion_radar/row_one/templates.py src/fashion_radar/row_one/render.py tests/test_row_one_daily_local_key_signals_digest.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
git diff --check
```

Report findings by severity with file/line references. If there are no blocking
issues, say so and note any residual risks.
