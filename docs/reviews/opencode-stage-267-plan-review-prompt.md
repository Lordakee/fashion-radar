Review the Stage 267 plan before implementation.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-267-row-one-first-run-app-discovery-verification-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-267-row-one-first-run-app-discovery-verification-plan.md

Goal:
Expose ROW ONE `data/manifest.json` in preview output and verify the manifest
plus `row-one serve --dry-run` in first-run smoke.

Review criteria:
- Plan feasibility and correctness against current codebase.
- Whether tests are executable as written.
- Whether preview keeps existing `JSON:` output and adds `Manifest:` without changing build behavior.
- Whether first-run smoke validates manifest fields and counts against `edition.json`.
- Whether first-run smoke verifies `row-one serve --dry-run` without starting a server.
- Whether scope avoids `row-one-app/v1` schema changes, provenance fields, collectors, scoring, scheduling, cleanup, deployment, image generation, LLM calls, and compliance-review product features.
- Whether docs accurately describe the new verification surface.

Do not edit files. Return concise Critical / Important / Minor findings and a verdict.
