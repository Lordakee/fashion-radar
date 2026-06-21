# Stage 141 Plan Review

## Findings

**No blocking issues.**

## Verified Items

### Parity test builder args

- `test_imported_review_workflow_payload_matches_real_builder`: `config_dir=Path("configs")`, `data_dir=Path("data")`, `as_of="2026-06-13T12:00:00Z"`, and `source_name="Community Tool Export"` produce top-level fields that match `imported_review_workflow_payload()` exactly. The builder normalizes `as_of` to `"2026-06-13T12:00:00+00:00"` and uses defaults `lookback_days=current_days=baseline_days=7`, `step_count=7`.
- `test_community_handoff_workflow_payload_matches_real_builder`: `directory=Path("/tmp/export")`, `input_format="csv"`, `pattern="*.csv"`, plus `configs`/`data`/`as_of`/`source_name` match `community_handoff_workflow_payload()` top-level fields.

### JSON mode

`model_dump_json()` plus `json.loads()` matches existing parity test style in `tests/test_first_run_smoke.py`. Dict comparison is content-based, so field insertion order is irrelevant.

### Fixture metadata values

- Imported-review purposes and `suggested_effect` values in the design match `src/fashion_radar/imported_review_workflow.py` field-by-field.
- Community-handoff purposes in the design match `src/fashion_radar/community_handoff_workflow.py` field-by-field.

### Commands already match

Each `shlex.join(...)` output for both builders matches the fixture command strings, including quoting for `*.csv` and `Community Tool Export`. The parity gap is only missing nested metadata:

- Imported-review steps lack `order`, `purpose`, and `suggested_effect`.
- Community-handoff steps lack `order` and `purpose`.

### Runtime unchanged

The plan scope excludes runtime builder changes. `src/fashion_radar/imported_review_workflow.py` and `src/fashion_radar/community_handoff_workflow.py` remain untouched.

### RED/GREEN strategy

The proposed parity tests will fail before fixture enrichment because nested step metadata is missing. After adding exact metadata from the builders, dict equality should pass.

## Minor Observation

**Severity: low** - The two new imports should follow the file's existing sorted import style: `community_handoff_workflow` before `external_tool_adapters`, and `imported_review_workflow` after `external_tool_workflow`.

## Conclusion

Plan is approved to proceed to implementation.
