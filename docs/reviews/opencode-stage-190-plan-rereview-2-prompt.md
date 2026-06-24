# Stage 190 Plan Rereview 2 Prompt

You are reviewing the Stage 190 source-liveness design and implementation plan
after a subagent audit found integration edge cases.

Please inspect:

- `docs/superpowers/specs/2026-06-24-stage-190-source-liveness-diagnostics-design.md`
- `docs/superpowers/plans/2026-06-24-stage-190-source-liveness-diagnostics-plan.md`
- `src/fashion_radar/models/source.py`
- `src/fashion_radar/settings.py`
- `src/fashion_radar/collectors/gdelt.py`
- `src/fashion_radar/utils/http.py`

Review questions:

1. Does the design now correctly scope skipped rows to schema-valid disabled
   sources while returning invalid config for invalid disabled sources?
2. Is the GDELT rate-limit wording technically accurate for the current
   per-source `FashionHttpClient` behavior?
3. Does the plan add enough TDD coverage for probe order, continuing after
   failures, and passing `gdelt_http_settings(source)` into the client factory?
4. Are there any remaining Critical or Important blockers before implementation?

Return Markdown starting with exactly:

`# Stage 190 Plan Rereview 2`

Use sections: Critical, Important, Minor, Verdict.
