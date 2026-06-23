# Stage 167 Plan Review Prompt

Review the Stage 167 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 167 Plan Review
```

Objective:

Fix singular `1 error` wording in the human-readable
`community-handoff-check-dir` table for lint and import dry-run summaries.

Read these files:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-167-community-handoff-check-error-label-design.md`
- `docs/superpowers/plans/2026-06-23-stage-167-community-handoff-check-error-label-plan.md`
- `src/fashion_radar/community_handoff_check.py`
- `src/fashion_radar/lint_formatting.py`
- `tests/test_community_handoff_check.py`
- `tests/test_lint_formatting.py`

Review questions:

1. Is Stage 167 correctly scoped to human-readable
   `community-handoff-check-dir` table error-count wording?
2. Does the RED test isolate renderer grammar without coupling to malformed CSV
   internals?
3. Is reusing `format_count_label(...)` appropriate and safe here?
4. Does the plan avoid changing JSON, models, CLI flow, readiness semantics,
   row/file/candidate wording, and `manual_signals.py`?
5. Are verification, code-review, release-review, release-hygiene, commit, and
   push steps complete enough?
6. Are there any critical or important findings before implementation?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
