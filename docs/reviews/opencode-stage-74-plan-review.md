# Stage 74 Plan Review

Reviewed:

- `docs/superpowers/specs/2026-06-18-stage-74-adapter-registry-parity-design.md`
- `docs/superpowers/plans/2026-06-18-stage-74-adapter-registry-parity-plan.md`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_adapters.py`
- `src/fashion_radar/community_signal_profile.py`
- `scripts/check_first_run_smoke.py`

## Verdict

Approved for implementation. No Critical or Important findings.

## Critical

None.

## Important

None.

## Minor

1. The plan over-lists `boundaries` as a drift point. Adapter-level and
   registry-level boundaries in the fixture already match the runtime registry,
   so no boundary edit is needed.

2. The plan does not explicitly call out the required-flag drift for
   `summary`, `source_name`, and `platform`. Runtime required fields are derived
   from `COMMUNITY_SIGNAL_REQUIRED_FIELDS = ["url", "title", "published_at"]`,
   while the Stage 73 fixture still marked those three optional fields as
   required. The red-state parity test will catch this, so it is not blocking.

## Review Answers

1. **Safe and useful after Stage 73?** Yes. The parity test completes the same
   pattern already present for template, workflow, and readiness fixtures, and
   it does not weaken the independent smoke validator.

2. **Anticipates drift correctly?** Mostly yes. The real current drift is in
   adapter `description`, `upstream_tool_examples`, and `field_mappings` notes
   and required flags. Boundaries already match.

3. **Avoids runtime/external-platform changes?** Yes. The planned change is
   confined to `tests/test_first_run_smoke.py`. The runtime registry builder is
   a pure metadata/model builder over deterministic inputs; it does not fetch,
   scrape, execute adapters, read SQLite, or call external platforms.

4. **Critical/Important issues before implementation?** None.

## Supporting Notes

- `external_tool_adapters_payload()` should remain a hand-built static fixture.
  Do not replace it with a direct call to `build_external_tool_adapter_registry`,
  because that would remove the fixture's independent smoke-contract value.
- Put the new parity test next to the existing external-tool template/workflow
  readiness parity tests.
- Use `model_dump_json()` plus `json.loads(...)`, matching the nearby fixture
  parity pattern and preserving JSON serialization fidelity.
