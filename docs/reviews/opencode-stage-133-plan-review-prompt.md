Review the Stage 133 design and implementation plan before code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Route PR authors from `.github/pull_request_template.md` to the canonical
  `docs/github-upload-checklist.md` for conditional smoke/upload verification.
- Keep the PR template concise and avoid duplicating the full upload checklist.
- Keep the change docs/test-only.

Design:
- `docs/superpowers/specs/2026-06-21-stage-133-pr-template-upload-checklist-routing-design.md`

Plan:
- `docs/superpowers/plans/2026-06-21-stage-133-pr-template-upload-checklist-routing-plan.md`

Proposed implementation scope:
- `.github/pull_request_template.md`
- `tests/test_cli_docs.py`
- Stage 133 review artifacts only

Review focus:
1. Does the design address the PR-template upload-checklist routing gap without
   copying the full upload checklist into the PR template?
2. Is the planned RED test specific enough to prove the PR template
   `Verification` section links to `docs/github-upload-checklist.md` and ties
   that link to conditional smoke/upload verification?
3. Does the test avoid overfitting a single link spelling by using the
   existing positional `_assert_markdown_link_to_path(text, path)` helper?
4. Does the plan avoid CI changes, upload checklist content changes, package
   checker behavior changes, runtime product behavior changes, dependencies,
   `uv.lock`, README/CONTRIBUTING changes, release hygiene changes, connectors,
   scraping, browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?
5. Are the verification commands sufficient?

Return:
Start with `# Stage 133 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
