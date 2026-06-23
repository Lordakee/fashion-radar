# Stage 170 Plan Review Prompt

Review the Stage 170 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 170 Plan Review

Objective:

Fix singular `1 row` wording in human-readable `community-signal-lint-dir`
per-file lines.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-170-community-signal-directory-file-row-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-170-community-signal-directory-file-row-grammar-plan.md`
- `src/fashion_radar/community_signals.py`
- `tests/test_community_signal_lint.py`
- `docs/community-signal-quality.md`

Scope boundaries:

- Human-readable `community-signal-lint-dir` per-file row-count wording only.
- No changes to `lint_community_signal_directory(...)`.
- No changes to `lint_community_signal_file(...)`.
- No changes to structured models, JSON output, CLI command flow, field counts,
  source counts, platform counts, finding ordering, finding messages, or
  finding-count grammar.
- No changes to top-level summary lines such as `Rows: ... total, ...
  import-ready`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Planned implementation:

1. Tighten the existing renderer test in `tests/test_community_signal_lint.py`
   so the synthetic one-row per-file line must start with
   `- exports/signals.csv: 1 row, 0 import-ready, `.
2. Run the focused test before implementation and confirm it fails because the
   renderer currently emits `1 rows`.
3. Import `format_count_label(...)` alongside `format_finding_counts(...)` in
   `src/fashion_radar/community_signals.py`.
4. Use `format_count_label(file.row_count, 'row', 'rows')` only for the
   per-file `row_count` phrase in
   `render_community_signal_directory_lint_table(...)`.
5. Update the matching example line in `docs/community-signal-quality.md` from
   `1 rows` to `1 row`.
6. Run focused tests/checks, code review, full release gate, release review,
   commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Is the existing renderer test the right place to add the `1 row` assertion?
4. Is `format_count_label(...)` the correct helper to reuse for this per-file
   row-count phrase?
5. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
