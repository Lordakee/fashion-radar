# Stage 179 Code Review Prompt

Review the Stage 179 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree.
Start the response exactly with:

# Stage 179 Code Review

Objective:

Add a focused regression guard that ensures the documented source-pack quality
JSON sample exposes the same top-level keys as the runtime
`SourcePackLintResult` payload.

Changed files:

- `tests/test_source_pack_quality_docs.py`
  - Adds `runtime_payload = result.model_dump(mode="json")`.
  - Adds `assert set(payload) == set(runtime_payload)` before the existing
    value-level assertions.
- Stage 179 spec, plan, plan-review prompt, and plan-review artifact.

Review context:

- `docs/superpowers/plans/2026-06-24-stage-179-source-pack-quality-json-keyset-guard-plan.md`
- `docs/reviews/opencode-stage-179-plan-review.md`
- `src/fashion_radar/source_packs.py`
- `docs/source-pack-quality.md`
- `docs/reviews/opencode-stage-176-code-review.md`

Scope boundaries:

- Test-only hardening.
- No runtime behavior changes.
- No docs content changes.
- No source acquisition, collector/source config changes, availability checks,
  demand proof, ranking, coverage verification features, compliance-review
  product features, dependency changes, or `uv.lock` changes.

Expected implementation:

- The existing JSON parity test is strengthened in place.
- The new assertion compares only top-level keys via `set(payload)` and
  `set(result.model_dump(mode="json"))`.
- The existing `payload["path"] == documented_path` assertion remains and must
  not be replaced with `result.path`.
- The implementation must not compare full dictionaries, because the documented
  `path` value is intentionally relative while runtime `result.path` is built
  from `PUBLIC_SOURCE_PACK`.
- Existing value assertions for counts, maps, and `findings == []` remain.

Verification evidence:

- Baseline GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q`
  - Result before adding guard: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q`
  - Result after adding guard: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q`
  - Result: 5 passed.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py`
  - Result: 1 file already formatted.

Review questions:

1. Does the implementation match the approved Stage 179 plan?
2. Is the key-set assertion correct, bidirectional, and appropriately scoped?
3. Does the implementation preserve the documented relative `path` exception?
4. Did any out-of-scope runtime, docs, source acquisition, source config,
   availability, demand proof, ranking, coverage-verification feature,
   compliance-review product feature, dependency, or lockfile behavior slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
