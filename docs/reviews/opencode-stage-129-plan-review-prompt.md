Review the Stage 129 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `.github/pull_request_template.md` packaging verification guidance with
  CI/upload-checklist temp build and package archive checker commands.
- Keep the change docs/test-only.

Design:
- `docs/superpowers/specs/2026-06-20-stage-129-pr-template-package-smoke-parity-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-129-pr-template-package-smoke-parity-plan.md`

Proposed implementation scope:
- `.github/pull_request_template.md`
- `tests/test_cli_docs.py`
- Stage 129 review artifacts only

Review focus:
1. Does the design address the PR template package smoke drift without changing
   CI, package checker behavior, or runtime behavior?
2. Is the planned focused docs test specific enough to catch missing temp-build and
   package archive checker commands in the PR template?
3. Does the plan update the canonical GitHub verification surface test so the
   PR template is included for the package archive checker and temp build
   commands?
4. Does the plan avoid duplicating the full upload checklist inside the PR
   template?
5. Does the scope avoid runtime product behavior, package checker behavior, CI
   behavior, dependencies, lockfile, connectors, scraping, browser automation,
   platform API, monitoring, scheduling, source acquisition, demand proof,
   ranking, coverage verification, and compliance/audit product behavior?
6. Are the verification commands sufficient?

Return:
Start with `# Stage 129 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
