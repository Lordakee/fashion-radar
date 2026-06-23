# Stage 163 Plan Review Prompt

Review the Stage 163 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 163 Plan Review
```

Objective:

Make `scripts/check_package_archives.py` return deterministic checker errors,
not tracebacks, when wheel `.dist-info/METADATA` or
`.dist-info/entry_points.txt` contains invalid UTF-8 bytes.

Read these files:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-163-package-archive-invalid-utf8-design.md`
- `docs/superpowers/plans/2026-06-23-stage-163-package-archive-invalid-utf8-plan.md`
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`

Review questions:

1. Is Stage 163 correctly scoped to invalid UTF-8 in wheel `METADATA` and
   `entry_points.txt` only?
2. Do the planned RED tests prove the current traceback behavior and the new
   deterministic checker errors?
3. Is catching `UnicodeDecodeError` in the two validators the narrowest
   appropriate implementation?
4. Are verification, code-review, release-review, release-hygiene, commit, and
   push steps complete enough?
5. Are there any critical or important findings before implementation?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
