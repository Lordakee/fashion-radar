## Critical Findings

None.

## Important Findings

None.

## Minor Findings

1. **Clarify `platform_counts` filter scope in implementation.**
   The design implies `query_imported_signals()` platform counts should align with the same retained review row scope: manual-import rows within the requested window and any `source_name` / `unmatched_only` filters. The plan says "retained manual-import rows only," which is directionally correct but could be read as all retained manual rows regardless of the active review filters. Recommend implementing counts from the same `conditions` used for the review query, excluding null/blank platforms.

2. **Normalize `platform=None` explicitly before string coercion.**
   The plan's repository step mentions normalizing with `" ".join(str(value).split())` plus blank-to-None behavior. Implementation should ensure `None` remains `None` and is not converted to the literal string `"None"`.

3. **Migration test should cover idempotent missing-column guard.**
   The planned v4-to-v5 migration includes an `if "platform" not in existing_columns` guard. It would be useful for tests or review evidence to confirm the migration is safe if the column already exists while metadata still reports v4, though this is not required for approval.

## Verdict

The plan is acceptable to execute. It preserves sanitized local `platform` provenance through storage and review output while maintaining the stated boundaries: no heat-score changes, no platform-spread scoring, no source acquisition/connectors, and no private/raw field retention.

APPROVED FOR STAGE 37 LOCAL PLATFORM PROVENANCE
