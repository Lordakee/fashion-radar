# Stage 166 Code Review Prompt

Review the Stage 166 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 166 Code Review
```

Objective:

Tighten the first-run smoke validator for `community-handoff-check-dir` JSON
output so stable nested payload drift is caught earlier.

Changed files:

- `scripts/check_first_run_smoke.py`
  - Extends `validate_community_handoff_check_dir(...)` with exact assertions
    for top-level findings, community-signal-lint identity/provenance details,
    candidate-preview metadata, and import-dry-run provenance counts.
- `tests/test_first_run_smoke.py`
  - Adds RED drift coverage for top-level findings, nested identity/path drift,
    nested source/platform count drift, lint field-count drift, and candidate-
    preview metadata drift.
- `docs/superpowers/specs/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-design.md`
- `docs/superpowers/plans/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-plan.md`
- `docs/reviews/opencode-stage-166-plan-review-prompt.md`
- `docs/reviews/opencode-stage-166-plan-review.md`

Scope boundaries:

- Local first-run smoke validator hardening only.
- No product code changes under `src/`.
- No exact assertions for nested `files` lists.
- No exact assertions for nested `findings` lists.
- No CLI changes.
- No JSON producer/model changes.
- No database, import, lint, candidate, workflow, dashboard, or report changes.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking,
  coverage verification, or compliance-review product features.

Plan review history:

- `docs/reviews/opencode-stage-166-plan-review.md`
  - No critical findings.
  - No important findings.
  - Two minor findings only, both non-blocking.

Focused verification evidence:

- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir"`
  - Result: 30 passed, 131 deselected.
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
  - Result: 2 files already formatted.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.

Review questions:

1. Does the implementation meet the Stage 166 objective?
2. Are the new drift tests focused and sufficient for the fields the validator
   now pins?
3. Did the validator stay narrow enough to avoid brittle schema-wide exactness?
4. Did any out-of-scope production behavior or nested list exactness slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
