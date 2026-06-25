# Stage 205 Code Review Prompt

Review the Stage 205 code and documentation changes.

Goal: carry candidate score components from the latest report JSON into the
dashboard Candidate Signals table, with backward-compatible defaults for older
report JSON.

Changed files:

- `src/fashion_radar/dashboard/queries.py`
- `tests/test_dashboard.py`
- `docs/dashboard.md`
- `tests/test_dashboard_docs.py`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-25-stage-205-dashboard-candidate-score-parity-plan.md`
- `docs/reviews/opencode-stage-205-plan-review-prompt.md`
- `docs/reviews/opencode-stage-205-plan-review.md`

Verification already run:

```bash
uv --no-config run --frozen pytest \
  tests/test_dashboard.py::test_latest_candidate_rows_reads_latest_report \
  tests/test_dashboard.py::test_latest_candidate_rows_defaults_score_components_for_legacy_report \
  tests/test_dashboard.py::test_latest_candidate_rows_preserves_legacy_growth_fields_without_components \
  -q
uv --no-config run --frozen pytest tests/test_dashboard.py tests/test_dashboard_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/dashboard/queries.py tests/test_dashboard.py docs/dashboard.md tests/test_dashboard_docs.py CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-205-dashboard-candidate-score-parity-plan.md docs/reviews/opencode-stage-205-plan-review.md docs/reviews/opencode-stage-205-plan-review-prompt.md
uv --no-config run --frozen ruff format --check src/fashion_radar/dashboard/queries.py tests/test_dashboard.py tests/test_dashboard_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
git diff --exit-code -- uv.lock pyproject.toml
```

Important context:

- The RED dashboard tests failed before `latest_candidate_report()` was changed
  because the row projection dropped the new fields.
- `latest_candidate_report()` now preserves these report-backed candidate
  fields: `weighted_mention_component`, `growth_component`,
  `source_diversity_component`, `growth_ratio`, and `first_seen_at`.
- Legacy report JSON must stay readable: component fields default to `0.0`,
  while `growth_ratio` and `first_seen_at` default to `None`.
- `app.py` already renders candidate rows directly through `st.dataframe`, so
  this stage intentionally makes no Streamlit layout or column-config change.
- This stage must not change scoring, ranking, report generation, database
  schema, dashboard writes, sources, collectors, source packs, entity packs,
  social/platform connectors, scraping, demand proof, platform coverage
  verification, dependency files, `uv.lock`, `pyproject.toml`, or
  compliance-review product behavior.

Please review:

1. Does `latest_candidate_report()` preserve the five report-backed candidate
   transparency fields with correct legacy defaults?
2. Are the new dashboard tests sufficient for full-field preservation, missing
   legacy fields, and partial legacy growth metadata?
3. Are the dashboard docs and changelog accurate about read-only report-backed
   transparency without implying demand proof or platform coverage?
4. Is leaving representative items, entity evidence, and Streamlit UI layout
   changes out of this node correct?
5. Does the stage avoid dependency, source acquisition, connector, scraper,
   platform coverage verification, demand-proof, and compliance-review behavior
   changes?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
