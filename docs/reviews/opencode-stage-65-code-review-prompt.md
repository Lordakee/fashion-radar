Review the Stage 65 implementation in /home/ubuntu/fashion-radar.

Use model-level scrutiny, but keep the output concise. Report only concrete
Critical or Important issues that should block commit/push. Ignore style-only
comments and do not propose unrelated refactors.

Stage 65 goal:
- Add `fashion-radar imported-entity-evidence`.
- It must be local read-only and imported-only.
- It must show retained local `manual_import` evidence rows behind one exact
  stored matched entity.
- It must not add scraping, browser automation, platform APIs, account/cookie
  behavior, dashboard browsing, monitoring, scheduling, demand proof, coverage
  verification, or compliance-review product features.

Expected behavior:
- Join `items` to `item_entities`.
- Filter `items.source_type == manual_import`.
- Filter exact `entity_name`, exact `entity_type`, and optional exact
  `source_name`.
- Use `imported-entity-deltas` window semantics:
  baseline: `baseline_window_start < collected_at <= current_window_start`
  current: `current_window_start < collected_at <= as_of`
- Deduplicate by `items.id`.
- Sort current first, then newest `collected_at`, then higher item id.
- Expose only privacy-safe row fields: `window`, `id`, `source_name`, `title`,
  `url`, `published_at`, `collected_at`.
- CLI validates invalid `--as-of`, blank `--entity-name`, and blank
  `--entity-type` before query.
- Imported review workflow has 7 steps and includes
  `review_imported_entity_evidence` after entity deltas.

Review these files:
- `src/fashion_radar/imported_entity_evidence.py`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/imported_review_workflow.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_imported_entity_evidence.py`
- `tests/test_cli.py`
- `tests/test_imported_review_workflow.py`
- `tests/test_first_run_smoke.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/dashboard.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`

Verification already run before this review:
- `uv --no-config run --frozen pytest tests/test_imported_entity_evidence.py -q`
- `uv --no-config run --frozen pytest tests/test_cli.py -q -k "imported_entity_evidence or imported_review_workflow"`
- `uv --no-config run --frozen pytest tests/test_imported_review_workflow.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q`
- `uv --no-config run --frozen ruff check ...`
- `uv --no-config run --frozen ruff format --check ...`

Output format:
- Verdict: PASS or BLOCKED
- Critical findings
- Important findings
- Test gaps, if any
