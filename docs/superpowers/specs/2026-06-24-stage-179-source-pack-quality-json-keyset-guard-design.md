# Stage 179 Source-Pack Quality JSON Key-Set Guard Design

## Objective

Add a focused regression guard that ensures the documented source-pack quality
JSON sample exposes the same top-level keys as the runtime
`SourcePackLintResult` payload.

## Background

Stage 176 synchronized `docs/source-pack-quality.md` with the current lint
output. Its code review noted one optional follow-up: the JSON parity test
asserts stable field values, but it does not assert the complete top-level key
set. If a future runtime field is added to `SourcePackLintResult`, the current
test could keep passing while the docs sample omits the new field.

## Scope

In scope:

- Add one key-set assertion to the existing docs-test guard in
  `tests/test_source_pack_quality_docs.py`.
- Compare the documented JSON sample's top-level keys with the runtime
  `SourcePackLintResult.model_dump(mode="json")` keys.
- Preserve the existing documented-path exception: docs use the relative source
  pack path, while the runtime result built from `PUBLIC_SOURCE_PACK` stores the
  absolute path.
- Add Stage 179 plan/review artifacts.

Out of scope:

- Runtime behavior changes.
- Changes to `docs/source-pack-quality.md`, unless the key-set test exposes a
  real documented/runtime mismatch.
- Source-pack lint model changes, source config changes, collector/source
  acquisition, availability checks, demand proof, ranking, coverage
  verification features, compliance-review product features, dependency
  changes, and `uv.lock`.

## Technical Approach

Enhance the existing
`test_source_pack_quality_json_sample_matches_public_pack_lint_output` test. It
already loads the documented JSON sample and runtime lint result, so add:

```python
runtime_payload = result.model_dump(mode="json")
assert set(payload) == set(runtime_payload)
```

The existing value-level test stays in place and continues to assert the
relative `path` value and the stable counts/maps. Do not compare the full
payload dictionaries, because the docs intentionally use the relative source
pack path while the runtime result built from `PUBLIC_SOURCE_PACK` stores the
absolute path.

## Acceptance Criteria

- The source-pack quality JSON parity test compares documented JSON top-level
  keys with runtime
  `SourcePackLintResult.model_dump(mode="json")` keys.
- Existing value-level JSON assertions remain unchanged, including the
  documented relative path assertion.
- Focused source-pack quality docs tests pass.
- `ruff check` and `ruff format --check` pass for the touched test file.
- Full release gate remains clean before commit.
