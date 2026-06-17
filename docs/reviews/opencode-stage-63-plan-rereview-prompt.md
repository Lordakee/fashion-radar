You are rereviewing the Stage 63 implementation plan for fashion-radar.

Model requirement: zhipuai-coding-plan/glm-5.2.
Variant requirement: max.

Repository: /home/ubuntu/fashion-radar

Files to review:
- docs/superpowers/specs/2026-06-17-stage-63-external-tool-template-design.md
- docs/superpowers/plans/2026-06-17-stage-63-external-tool-template-plan.md
- docs/reviews/opencode-stage-63-plan-review.md

Previous review verdict: CHANGES REQUIRED.

Previous Important findings to verify:
1. Unfiltered collection count must be 14 because there are seven adapters and
   `_template_items` returns two rows per adapter. The plan must not assert 7
   items for the unfiltered JSON/collection.
2. First-run smoke edits must explicitly cover:
   - adding `"external-tool-template"` to the fake `stdout_by_command` map,
   - adding the command tuple after `external-tool-adapters`,
   - shifting later hardcoded captured-command index assertions by one.

Stage 63 intended contract:
- `external-tool-template --format json` emits only importable
  `{"items": [...]}` JSON.
- CSV/JSON rows contain only community signal fields.
- Metadata stays in the internal model/table output.
- The command is stdout-only and print-only.
- No platform collection, connectors, scraping, browser automation, platform
  APIs, account/session/cookie behavior, media downloads, directory/file reads,
  file writes, import execution, SQLite, scheduling, monitoring, demand proof,
  ranking, coverage verification, or compliance-review product feature.

Please return exactly:
- Verdict: APPROVED FOR STAGE 63 IMPLEMENTATION or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.
