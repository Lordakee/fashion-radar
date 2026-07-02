Review the Stage 267 implementation before commit and push.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-267-row-one-first-run-app-discovery-verification-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-267-row-one-first-run-app-discovery-verification-plan.md

Goal:
Expose ROW ONE `data/manifest.json` in preview output and verify the manifest
plus `row-one serve --dry-run` in first-run smoke.

Implementation summary:
- `row-one preview` keeps the existing `JSON:` line and adds `Manifest: <output>/data/manifest.json`.
- First-run smoke validates `data/manifest.json` against `data/edition.json`, including app path, site paths, counts, and readiness.
- First-run smoke runs `row-one serve --site-dir <site> --host 127.0.0.1 --port 8787 --dry-run` and asserts `Open: http://127.0.0.1:8787`.
- Docs and docs tests describe the manifest and serve dry-run verification path.

Review criteria:
- Preview keeps existing `JSON:` output and adds `Manifest:` without changing build behavior.
- First-run smoke validates manifest fields and counts against `edition.json`.
- First-run smoke verifies `row-one serve --dry-run` without starting a server.
- Deterministic first-run command sequence remains strictly ordered.
- No `row-one-app/v1` schema changes, provenance fields, collectors, scoring,
  scheduling, cleanup, deployment, image generation, LLM calls, or compliance-review features.
- Docs accurately describe the new verification surface.
- Review artifacts do not contain process chatter that would fail release hygiene.

Do not edit files. Return concise Critical / Important / Minor findings and a verdict.
