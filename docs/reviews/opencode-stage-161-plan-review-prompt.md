# Stage 161 Plan Review Prompt

Review the Stage 161 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 161 Plan Review
```

Objective:

Show deterministic source tag counts in the default human table output from
`fashion-radar source-pack-lint`.

Read these files:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-161-source-pack-lint-tag-counts-design.md`
- `docs/superpowers/plans/2026-06-23-stage-161-source-pack-lint-tag-counts-plan.md`
- `src/fashion_radar/source_packs.py`
- `tests/test_source_packs.py`
- `tests/test_cli.py`
- `docs/source-pack-quality.md`

Review questions:

1. Is Stage 161 a narrow, valid next step after Stage 160?
2. Do the planned RED tests prove that the human table and CLI output currently
   lack a `Tags:` line?
3. Is it correct to reuse existing `tag_counts` and `_format_counts(...)` in
   `render_source_pack_lint_table(...)`?
4. Does the docs update preserve local/read-only and non-data boundaries?
5. Are verification, code-review, release-review, release-hygiene, commit, and
   push steps complete enough?
6. Are there any critical or important findings before implementation?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
