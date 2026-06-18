I'll review the Stage 96 design and plan. Let me start by reading all the relevant files in parallel.
Let me verify a critical detail - the apostrophe character used in the doc vs. the test phrase, which is a common source of test failures.
All 19 phrases match. The apostrophe is straight ASCII, so no encoding issue. Let me check a few more things: whether the target test file already exists, whether Stages 91-95 are independent, and confirm the existing overlap in `test_cli_docs.py`.
Let me verify the prior stages follow the same standalone-test-file pattern, confirming independence, and check the project's test verification commands.
The standalone-test-file pattern matches prior stages exactly. Let me compare style with one sibling to confirm consistency, and check the project's frozen-run convention.
# Stage 96 Plan Review — Findings

I verified every proposed test phrase against the current `docs/entity-packs.md` (normalized via `" ".join(text.split()).casefold()`, matching the planned helper).

## Findings by Severity

### Critical
None.

### Important
None.

### Low / Informational (no action required before implementation)

**L1 — Phrases all verified present and stable.** All 19 planned phrases match the current normalized doc. The apostrophe in "Fashion Radar's" (`docs/entity-packs.md:5`) is straight ASCII (`'`), so the test phrase `"without changing fashion radar's runtime behavior"` resolves correctly.

**L2 — Phrases are sufficiently specific, not over-broad.** Each assertion is a multi-word boundary clause (e.g., "does not add live collection", "local sample rows are synthetic", "no fetching urls", "no connectors"). No phrase is a single common word that would trivially pass.

**L3 — Intentional, acceptable overlap with `tests/test_cli_docs.py`.** Two existing tests already assert a subset of the same boundaries:
- `tests/test_cli_docs.py:1086` `test_entity_pack_docs_describe_optional_matching_layer_sequence` ("only changes local entity matching", "does not add sources/ingestion/live collection", etc.)
- `tests/test_cli_docs.py:1056` `test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack` ("local sample rows are synthetic", "not a hot-list", etc.)

Stage 96's standalone file is a focused drift guard and the duplication is defensive — not a blocker.

**L4 — Minor stylistic divergence from Stage 91 sibling.** `tests/test_data_retention_docs.py` asserts against raw text (no whitespace/case normalization), while Stage 96 normalizes. Both styles exist in the repo (`test_cli_docs.py` normalizes heavily), so this is fine.

## Answers to Review Questions

1. **Docs assertions present?** Yes — all 19 phrases verified in current `docs/entity-packs.md`.
2. **Stable / not over-broad?** Yes — all multi-word boundary clauses.
3. **Test-only & independent of Stages 91–95?** Yes. Only `tests/test_entity_packs_docs.py` + review artifacts are touched. It follows the same one-file-per-stage convention as Stages 91–95 (`test_data_retention_docs.py`, `test_scheduling_docs.py`, `test_dashboard_docs.py`, `test_source_pack_quality_docs.py`, and the Stage 95 architecture file). Each stage reads its own doc — no cross-stage coupling. Disallowed files (`docs/entity-packs.md`, `configs/entity-packs/`, `src/`, schemas, manifests, `uv.lock`, CI, `tests/test_cli_docs.py`, runtime entity-pack tests) are all respected by the plan.
4. **Verification commands sufficient?** Yes. Task 3 covers focused pytest (new file alone + alongside `tests/test_entity_packs.py`), `ruff check`, and `ruff format --check`; Task 4 adds full suite, full ruff, `uv lock --check`, release hygiene, and staged-hygiene gating.
5. **Critical/Important blockers?** **No.** There are no Critical or Important blockers before implementation.
