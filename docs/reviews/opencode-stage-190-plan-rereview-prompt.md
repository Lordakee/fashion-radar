# Stage 190 Plan Rereview Prompt

Re-review the revised Stage 190 source-liveness design and implementation plan
after the prior plan review reported one Critical and two Important findings.

Repository: `/home/ubuntu/fashion-radar`

Files to inspect:

- `docs/reviews/opencode-stage-190-plan-review.md`
- `docs/superpowers/specs/2026-06-24-stage-190-source-liveness-diagnostics-design.md`
- `docs/superpowers/plans/2026-06-24-stage-190-source-liveness-diagnostics-plan.md`
- `src/fashion_radar/collectors/rss.py`
- `src/fashion_radar/collectors/gdelt.py`
- `src/fashion_radar/utils/http.py`
- `src/fashion_radar/cli.py`
- `tests/test_cli.py`

Prior blockers to verify:

1. Critical: explicit `ruff format --check` commands must no longer include
   Markdown files.
2. Important: the plan must either support `http_status` through a real seam or
   remove the field and table column. The revised plan is expected to remove it.
3. Important: CLI tests must cover warning without strict, warning with strict,
   error output before exit, and invalid format not calling the builder.

Also check:

- The design defines report-level findings consistently with the plan.
- Skipped-source `elapsed_ms` is specified and tested as `0`.
- RSS/GDELT probe semantics remain scoped to read-only liveness and no live
  pytest network calls.
- The next implementation remains free of external/social/community handoff
  expansion.

Report findings under:

- Critical
- Important
- Minor

Critical or Important findings must block implementation. If the revised plan
is acceptable, say it is approved for implementation.

Start the response exactly with:

```text
# Stage 190 Plan Rereview
```

Do not include process chatter, command logs, ANSI output, or tool-status lines.
