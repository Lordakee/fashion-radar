Review the Stage 309 ROW ONE newsroom digest polish implementation.

Repo: `/home/ubuntu/fashion-radar`
Plan: `docs/superpowers/plans/2026-07-05-stage-309-row-one-newsroom-digest-polish-plan.md`

Changed files to review:
- `src/fashion_radar/row_one/local_intelligence.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_local_intelligence.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 309 plan/review artifacts under `docs/reviews/`

Implementation intent:
- Cluster duplicate saved local-article digest cards in `strongest_reads` and `heat_movers`.
- Use a deterministic cluster key based on normalized source name plus the full saved local article body.
- Keep canonical `paragraph_indices` and `segments` from the selected canonical article only, so generated detail anchors stay valid.
- Aggregate only existing `RowOneDailyLocalIntelligenceItem` fields: `story_count`, `article_count`, `source_names`, `evidence_count`, `heat_delta`, `references`, and `segments`.
- Improve Daily Local Intelligence action copy from "Open paragraph N" to evidence/source wording without changing paragraph anchor routes.
- Add compact local article provenance to detail pages, including safe original URL rendering only when the URL is accepted by the template safety helper.
- Sanitize unsafe digest detail hrefs so app payload links cannot render unsafe clickable URLs.
- Filter invalid/duplicate paragraph indices in Daily Local Intelligence segment metadata.
- Document that this is presentation/sidecar organization only and does not change source collection, ranking/scoring, `data/edition.json`, `row-one-app/v7`, `row-one-manifest/v1`, or `row-one-runtime/v1`.

Known verification already run before this review:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`
- `UV_NO_CONFIG=1 uv lock --check`
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-05T04:00:00Z --output-dir reports/row-one/site --latest-only`
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json`

Please check for correctness issues, missing tests, unsafe link/rendering regressions, schema/contract drift, and release-hygiene problems.

Return only:

## Verdict
Approve, Approve with Important fixes, or Reject.

## Critical Findings
- Finding, why it matters, concrete fix.

## Important Findings
- Finding, why it matters, concrete fix.

## Minor Findings
- Finding, concrete fix.

Do not modify files.
