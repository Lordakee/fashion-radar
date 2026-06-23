# Stage 179 Code Review

## Summary

Stage 179 meets its objective: the documented source-pack quality JSON sample
is now guarded against top-level key drift relative to the runtime
`SourcePackLintResult` payload. The change adds exactly two lines to the
existing `test_source_pack_quality_json_sample_matches_public_pack_lint_output`
test — `runtime_payload = result.model_dump(mode="json")` and
`assert set(payload) == set(runtime_payload)` — placed immediately after the
`documented_path` computation and before the value-level assertions. All
existing value-level assertions remain unchanged, so the documented relative
`path` exception is preserved. This directly resolves the optional follow-up
recorded in Stage 176 Minor #3. The change is strictly test-only; no runtime,
docs content, collector, source config, availability check, demand proof,
ranking, coverage-verification, compliance-review product feature, dependency,
or `uv.lock` behavior was touched.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Review-question coverage, in order:
   - **Q1 (plan match):** Yes. The implementation matches Task 1 Step 2 of the
     approved plan precisely. The two-line insertion lands at the specified
     anchor (`documented_path = PUBLIC_SOURCE_PACK.relative_to(ROOT).as_posix()`),
     uses the specified `result.model_dump(mode="json")` reference, and the
     specified `assert set(payload) == set(runtime_payload)` form. All existing
     value-level assertions are retained verbatim.
   - **Q2 (key-set correctness, bidirectionality, scoping):** Yes. `set()`
     applied to a dict yields its key set, and `==` on sets is symmetric, so
     the assertion catches both missing and extra keys bidirectionally. The
     comparison is correctly scoped to top-level keys only (no nested
     comparison of `type_counts`/`tag_counts`/`findings`). The reference is
     sound: `SourcePackLintResult` declares `model_config =
     ConfigDict(extra="forbid")` (`src/fashion_radar/source_packs.py:35`), so
     no silent extras can appear, and the four `@property` accessors
     (`error_count`, `warning_count`, `info_count`, `ok`) are correctly
     excluded by Pydantic's `model_dump()`. The documented sample exposes the
     same seven keys (`path`, `source_count`, `enabled_count`,
     `disabled_count`, `type_counts`, `tag_counts`, `findings`) as the model's
     seven declared fields, so the assertion passes today and will fail
     informatively on either direction of drift.
   - **Q3 (relative `path` exception):** Yes. The value-level
     `assert payload["path"] == documented_path` assertion remains at line 107
     and is not replaced with `result.path`. Because the key-set check compares
     only keys, the intentional value difference (documented relative
     `configs/...` form vs runtime `str(PUBLIC_SOURCE_PACK)` absolute form)
     does not affect the new assertion. The exception is preserved exactly as
     the plan and design require.
   - **Q4 (out-of-scope slips):** No. `git status` shows only
     `tests/test_source_pack_quality_docs.py` modified, plus the untracked
     Stage 179 spec, plan, and plan-review artifacts — all within the
     test-only + review-artifact scope. No `source_packs.py`, CLI, YAML config,
     `pyproject.toml`, or `uv.lock` changes. No source acquisition,
     collector/source config, availability, demand-proof, ranking,
     coverage-verification, or compliance-review product features were added.
   - **Q5 (critical/important blockers before release verification):** None.

2. Ordering: the key-set assertion is placed ahead of the value-level
   assertions (as the plan specified). This is marginally preferable because a
   key-set failure produces an informative symmetric diff rather than a
   `KeyError` on a missing field. Informational only; the plan did not need to
   call out the ordering choice.

3. `mode="json"` is technically immaterial for a top-level-key comparison
   (`model_dump()` and `model_dump(mode="json")` produce identical keys; none
   of the top-level fields are enums). Keeping `mode="json"` is harmless, costs
   nothing, and is the more semantically faithful reference for "what the
   documented JSON sample should match." No change required; noted only so
   future reviewers do not misread it as a bug.

## Verification Assessment

- Objective met: yes. The top-level-key parity guard is added in place to the
  existing JSON parity test; the documented sample key set is now provably
  pinned to the runtime `SourcePackLintResult` key set.
- Independent re-run confirms the provided evidence:
  - `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q`
    -> 5 passed.
  - `uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py`
    -> All checks passed!
  - `uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py`
    -> 1 file already formatted.
- GREEN->GREEN baseline is internally consistent: the guard is a pure
  strengthening, and the assertion passes today because the seven documented
  keys exactly match the seven model fields (verified by manual cross-check of
  `docs/source-pack-quality.md:72-108` against
  `src/fashion_radar/source_packs.py:34-43`, accounting for `extra="forbid"`
  and the four `@property` methods).
- Verification commands follow the project's `uv --no-config run --frozen`
  convention.
- Scope discipline verified via `git status`: only the intended test file is
  modified; remaining entries are untracked in-scope spec/plan/review
  artifacts.

## Verdict

Approve. No critical or important findings. The implementation is the minimal,
correct, bidirectional top-level-key guard specified in the approved plan; it
preserves the documented relative `path` value exception by retaining all
existing value-level assertions; it stays strictly within the test-only scope
boundary with no runtime, docs, source acquisition, source config,
availability, demand-proof, ranking, coverage-verification, compliance-review,
dependency, or `uv.lock` changes; and independent focused pytest/ruff
verification is green. The minor notes are informational and do not block
release verification.
