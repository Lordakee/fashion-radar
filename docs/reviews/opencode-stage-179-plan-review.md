# Stage 179 Plan Review

## Summary

Stage 179 is a tightly scoped, test-only hardening that directly resolves the
optional follow-up recorded in Stage 176's Minor finding #3. The plan adds one
key-set parity assertion (`assert set(payload) == set(runtime_payload)`) to the
existing
`test_source_pack_quality_json_sample_matches_public_pack_lint_output` test,
leaves the existing value-level assertions (including the documented relative
`path` exception) untouched, and keeps all runtime/docs/collector/dependency
surfaces out of scope. The design and plan correctly reason about why
`SourcePackLintResult.model_dump(mode="json")` is the right runtime reference,
why only top-level keys are compared, and why the relative-path value exception
remains intact. The verification, review, release, commit, and push steps match
the project's `uv --no-config run --frozen`, `UV_NO_CONFIG=1 uv lock --check`,
secret-scan, and local-opencode review conventions. No critical or important
issues; a few informational minor notes only.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Review-question coverage, in order:
   - Q1 (Stage 176 follow-up): Yes. Stage 176 code review Minor #3 explicitly
     suggested "a future stage could optionally add an explicit
     documented-keys-equals-runtime-keys assertion." Stage 179 Task 1 Step 2
     adds exactly that comparison, so the plan is a direct, traceable response
     rather than a tangential change.
   - Q2 (sufficiency and scoping of the two-line addition): Yes. The
     `SourcePackLintResult` model has `extra="forbid"` and defines exactly seven
     top-level fields (`path`, `source_count`, `enabled_count`,
     `disabled_count`, `type_counts`, `tag_counts`, `findings`); the
     `error_count`/`warning_count`/`info_count`/`ok` accessors are `@property`
     methods and are correctly excluded from `model_dump()`. The documented
     sample exposes the same seven keys, so the assertion passes today and will
     catch both directions of drift (a new runtime field without a docs update,
     or a documented field removed from runtime). Placement inside the existing
     parity test (rather than a new test) is appropriately minimal and reuses
     the already-loaded `payload` and `result`.
   - Q3 (relative `path` exception): Yes. The design (lines 51-55) and the plan
     (Task 1 Step 2 commentary) both state the key-set comparison must not
     replace the value-level assertions, and the value-level
     `payload["path"] == documented_path` assertion remains. Because the key-set
     check compares only keys, the relative-vs-absolute `path` value difference
     (docs use the relative form; `lint_source_pack(PUBLIC_SOURCE_PACK)` stores
     `str(path)` of the absolute `PUBLIC_SOURCE_PACK`) does not affect the new
     assertion. The exception is preserved.
   - Q4 (verification/review/release/commit/push sufficiency): Yes. Task 1 runs
     the existing parity test as a pre-guard baseline (confirming
     GREEN->GREEN strengthening rather than a fix), then adds and re-runs the
     assertion. Task 2 runs focused pytest plus `ruff check` and
     `ruff format --check` on the touched file, then creates and captures a
     local-opencode code review with the required `# Stage 179 Code Review`
     header. Task 3 runs the full release gate (proxy-stripped full pytest,
     `check_first_run_smoke.py`, `check_release_hygiene.py`, repo-wide ruff,
     `UV_NO_CONFIG=1 uv lock --check`, `git diff --check`, `ghp_` token scan,
     and extraheader check), a release review, then stages the exact file set
     and pushes. This matches prior stages and AGENTS.md conventions.
   - Q5 (critical/important blockers): None identified.

2. The insertion point specified in Task 1 Step 2 ("immediately after
   `documented_path = PUBLIC_SOURCE_PACK.relative_to(ROOT).as_posix()`") places
   the new key-set assertion ahead of the existing value-level assertions.
   Functionally this is fine (and arguably preferable, since a key-set failure
   is more informative than a value-level `KeyError` on a missing field), but
   the plan does not explicitly call out the ordering choice. Informational
   only; either order is acceptable.

3. `mode="json"` is technically unnecessary for a top-level-key comparison,
   since `model_dump()` and `model_dump(mode="json")` produce identical
   top-level keys (they differ only in value serialization, e.g. enum->str).
   Keeping `mode="json"` is harmless and is the more semantically faithful
   reference for "what the documented JSON sample should match," and it costs
   nothing. No change required; noted only so reviewers do not read it as a
   bug.

4. The plan does not restate that `SourcePackLintResult` uses
   `extra="forbid"`, which is what guarantees the key-set is stable and that
   the assertion is meaningful (no silent extras can appear). The design's
   Technical Approach section would be marginally stronger if it cited this,
   but it is not a blocker since the model file is listed as existing context
   and the assertion is correct as written.

## Verification Guidance

For the implementer:

- Run Task 1 Step 1 first and confirm the existing parity test passes before
  touching the file; this establishes the GREEN->GREEN baseline the plan
  promises.
- After adding the assertion, run
  `uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q`
  and confirm it still passes. If it fails, the failure message will show the
  symmetric key diff; per the plan, update `docs/source-pack-quality.md` only
  if a real runtime/docs key mismatch is confirmed, and treat any such update
  as an in-scope consequence explicitly permitted by the design's Out-of-scope
  caveat (lines 33-34).
- Run the full focused block in Task 2 Step 1
  (`pytest tests/test_source_pack_quality_docs.py`, `ruff check`, and
  `ruff format --check` on the touched file).
- Confirm no properties (`error_count`, `warning_count`, `info_count`, `ok`)
  leak into the documented sample or the assertion expectation; these are
  intentionally excluded by Pydantic and by the documented sample.
- Confirm `git status` after Task 1 shows only
  `tests/test_source_pack_quality_docs.py` modified (plus the untracked
  spec/plan/review artifacts) before proceeding to release gate.

For the reviewer of the next stage: re-run the focused test and ruff checks
independently, and verify the committed diff is the single two-line insertion
described in Task 1 Step 2 plus review artifacts.

## Verdict

Approve. The plan directly resolves Stage 176's Minor #3 follow-up with the
minimal, correct, bidirectional key-set guard; it preserves the documented
relative `path` value exception by keeping all existing value-level assertions;
it stays strictly within the test-only scope boundary with no runtime, docs
(unless the new test exposes a real mismatch), collector, availability,
demand-proof, ranking, coverage-verification, compliance-review, dependency, or
`uv.lock` changes; and its verification/review/release/commit/push steps match
the project's frozen-mirror and local-opencode review conventions. No critical
or important findings; the minor notes above are informational and do not block
implementation.
