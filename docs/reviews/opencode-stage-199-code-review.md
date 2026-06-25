# Stage 199 Code Review

## Verdict

Approved. No Critical or Important blockers were found.

The Stage 199 implementation is additive, scoped to aggregate report evidence,
and does not expand collection, source packs, social connectors, ranking,
platform coverage verification, demand proof, external-tool behavior, or
compliance-review product behavior.

## Critical Findings

None.

## Important Findings

None.

## Verification Reviewed

- `tests/test_reports.py`
- `tests/test_cli.py::test_report_command_writes_markdown_and_json`
- `tests/test_first_run_smoke.py::test_validate_report_requires_expected_first_run_entity_sections`
- `scripts/check_first_run_smoke.py --repo-root .`
- Targeted `ruff check` and `ruff format --check`
- Full `tests/` suite

## Review Notes

1. `EntityMatchEvidence` is an additive Pydantic model with `extra="forbid"`,
   stable field order, default zero/null values, and a defaulted
   `EntityReport.match_evidence` field.
2. `_match_evidence(...)` uses existing `item_entities` joined to `items`,
   filters by `entity_name`, `entity_type`, confidence threshold, and the
   current report window, then deduplicates by entity/item using highest
   confidence and lexicographically smallest reason on ties.
3. Reason bucketing matches the approved contract:
   `accepted`, `context`, `parent_brand`, `safe_alias`, and an `other` bucket
   for unknown accepted reasons.
4. Confidence statistics are rounded in the helper before model construction
   and Markdown rendering uses the stable two-decimal range form, including
   single-match `1.00-1.00 avg 1.00` output.
5. JSON and Markdown reports expose only aggregate counts and confidence
   statistics. Raw aliases, context terms, item ids, normalized URLs, raw
   reasons, and per-row matcher explanations remain internal.
6. CLI and first-run smoke coverage validate the new report contract without
   requiring exact product/category evidence counts beyond the guaranteed
   first-run `The Row` match.
7. Documentation and changelog wording correctly frame match evidence as local
   report-derived evidence, not demand proof, popularity ranking, source-set
   completeness, platform coverage verification, or connector expansion.

## Minor Follow-Up Notes

- `_match_evidence(...)` follows the existing report pattern of issuing
  per-entity queries. Future batching may be useful if report size grows, but
  this is not a blocker for Stage 199.
- Smoke validation pins count fields and the 9-key evidence shape. Future
  tightening could add explicit float-or-null checks for the three confidence
  fields if first-run report fixtures need stricter schema validation.
