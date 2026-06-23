# Stage 171 Plan Review Prompt

Review the Stage 171 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 171 Plan Review

Objective:

Fix singular count-label wording in human-readable `community-handoff-check-dir`
summary lines.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-171-community-handoff-check-count-label-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-171-community-handoff-check-count-label-grammar-plan.md`
- `src/fashion_radar/community_handoff_check.py`
- `tests/test_community_handoff_check.py`
- `tests/test_cli.py`

Scope boundaries:

- Human-readable `community-handoff-check-dir` renderer summary count labels
  only.
- In scope labels:
  - Lint summary `file/files`.
  - Lint summary `import-ready row/import-ready rows`.
  - Candidate preview `candidate/candidates`.
  - Candidate preview `row/rows`.
  - Import dry-run `valid file/valid files`.
  - Import dry-run `row/rows`.
- Preserve the Stage 167 singular error-count behavior.
- No changes to `check_community_handoff_directory(...)`.
- No changes to lint, candidate preview, or manual import dry-run logic.
- No changes to structured models, JSON output, CLI options, command flow,
  checks, strict-mode behavior, warnings, finding messages, or exit codes.
- No changes to historical stage design/plan/review artifacts that quote old
  output as prior context.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Planned implementation:

1. Extend the existing renderer test in `tests/test_community_handoff_check.py`
   by using `model_copy(...)` to force synthetic one-count state for lint,
   candidate preview, and import dry-run nested results.
2. Assert exact rendered lines:
   - `Lint: 1 file, 1/1 import-ready row, 1 error`
   - `Candidate preview: 1 candidate from 1 row`
   - `Import dry-run: 1/1 valid file, 1 row, 1 error`
3. Run the focused test before implementation and confirm it fails on hard-coded
   plural labels.
4. Update only `render_community_handoff_directory_check_table(...)` to use the
   already-imported `format_count_label(...)` helper for the in-scope labels.
5. Run focused tests/checks, code review, full release gate, release review,
   commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Is extending the existing renderer test the right RED strategy?
4. Are the planned `format_count_label(...)` calls correct for the slash-prefixed
   phrases (`1/1 import-ready row`, `1/1 valid file`)?
5. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
