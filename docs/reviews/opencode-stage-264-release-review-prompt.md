Review the current uncommitted Stage 264 release candidate in /home/ubuntu/fashion-radar.

Scope:
- ROW ONE daily readiness summary derived from RowOneEdition.
- ROW ONE homepage status strip.
- `fashion-radar row-one preview` CLI.
- first-run smoke coverage for ROW ONE help/schedule/preview.
- package archive guardrails for ROW ONE docs/source.
- docs for readiness and preview.

Constraints:
- Do not change files.
- Verify no `row-one-app/v1` JSON contract drift.
- Verify no source collection, scoring/ranking, scheduling semantic, scraping, connector, or compliance-review feature scope was added.
- Focus on release blockers, correctness risks, missing tests, package/archive issues, and docs/CLI inconsistencies.
- Return a concise review with Critical / Important / Minor findings and a verdict.
