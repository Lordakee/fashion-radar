# Claude Code Stage 3 Code Re-Review Prompt

You are Claude Code re-reviewing Fashion Radar after fixes for Stage 3 code
review findings.

Repository: `/home/ubuntu/fashion-radar`

Original reviewed commit:

- `ac23386 feat: add stage 3 public collectors`

Fix commit:

- `6712300 fix: address stage 3 collector review findings`

Review range:

- `749f263..6712300`

Please specifically verify that the previous findings are resolved:

1. GDELT `seendate` parsing now supports the real `YYYYMMDDTHHMMSSZ` format and
   the fixture exercises that format.
2. Article extraction is wired into `collect_sources()` before item upsert,
   storing only a short snippet in `CollectedItem.summary` when extraction
   succeeds.
3. A run-scoped `RobotsPolicyChecker` is created for the default article
   extractor.
4. `skip_on_robots_failure` dead configuration was removed.
5. Robots unavailable and robots disallowed are distinguishable in code/tests.
6. Runner passes `started_at` into collectors and preserves non-zero durations
   from timing-aware collectors.
7. Expired unhealthy-source windows reset `consecutive_failures`.

Fresh local verification after the fix commit:

```text
.venv/bin/python -m pytest -q
84 passed in 1.32s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
46 files already formatted

uv lock --check
Resolved 84 packages in 2ms

uv sync --locked --dev --check
Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Would make no changes
```

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 4 plan review
- Approved after fixes
- Do not proceed
