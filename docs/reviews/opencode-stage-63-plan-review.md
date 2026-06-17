# Opencode Stage 63 Plan Review

Model: `zhipuai-coding-plan/glm-5.2`
Variant: `max`

## Verdict

CHANGES REQUIRED

## Critical

None.

## Important

1. The unfiltered collection item count in the plan contradicts the
   two-rows-per-template implementation. `_template_items` returns two rows per
   adapter, so the unfiltered collection contains `7 * 2 = 14` items. The plan
   incorrectly asserted `len(collection.items) == 7` and
   `len(payload["items"]) == 7`.
2. The first-run smoke updates are under-specified. Adding
   `external-tool-template` after `external-tool-adapters` requires updating the
   fake `stdout_by_command`, the ordered captured-command list, and the
   hardcoded captured-command index assertions that follow the inserted command.

## Minor

- `csv_header` is derived from adapter field mappings, which is currently
  aligned with the community signal profile but order-dependent.
- The invalid `--as-of` path relies on dateutil parser errors subclassing
  `ValueError`; this is acceptable.
- Docs-drift tests require the new command and boundary language to appear in
  every listed doc, including `CHANGELOG.md`.

## Rationale

The design and contract are sound: `--format json` emits only
`{"items": [...]}`, CSV emits only the eight-field community signal header, and
metadata stays in the internal model/table output. The plan needs the two
Important inconsistencies fixed before implementation.
