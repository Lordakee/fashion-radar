Review the Stage 131 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `CONTRIBUTING.md` and `.github/pull_request_template.md` verification
  sections with the local release hygiene and source-checkout first-run smoke
  commands already required by CI and the upload checklist.
- Keep the change docs/test-only.

Design:
- `docs/superpowers/specs/2026-06-21-stage-131-verification-surface-parity-design.md`

Plan:
- `docs/superpowers/plans/2026-06-21-stage-131-verification-surface-parity-plan.md`

Proposed implementation scope:
- `tests/test_cli_docs.py`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- Stage 131 review artifacts only

Review focus:
1. Does the design address the contributor-facing verification drift without
   changing CI, package behavior, or runtime behavior?
2. Is the planned focused docs test specific enough to catch missing release
   hygiene and source-checkout first-run smoke commands in both contributor
   verification sections?
3. Does the plan update the canonical verification-surface test for the same
   commands while keeping README/first-run/package-smoke scope intact?
4. Does the plan avoid package archive behavior changes, README development
   block expansion, dependency/lockfile/CI/runtime product changes, connectors,
   scraping, browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?
5. Are the verification commands sufficient?

Return:
Start with `# Stage 131 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
