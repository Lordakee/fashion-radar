# Stage 165 Code Review Prompt

Review the Stage 165 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 165 Code Review
```

Objective:

Add direct unit coverage for the shared lint finding-count formatting helper
introduced in Stage 164.

Changed files:

- `tests/test_lint_formatting.py`
  - Adds direct `format_count_label(...)` coverage for zero, one, and plural
    counts.
  - Adds direct `format_finding_counts(...)` coverage for zero, singular,
    plural, and mixed severity counts.
- `docs/superpowers/specs/2026-06-23-stage-165-lint-formatting-helper-tests-design.md`
  - Records the Stage 165 scope and verification plan.
- `docs/superpowers/plans/2026-06-23-stage-165-lint-formatting-helper-tests-plan.md`
  - Records the task-by-task implementation plan.
- `docs/reviews/opencode-stage-165-plan-review-prompt.md`
- `docs/reviews/opencode-stage-165-plan-review.md`

Relevant unchanged production file:

- `src/fashion_radar/lint_formatting.py`

Scope boundaries:

- Direct helper unit tests only.
- No production code changes unless the tests expose a real mismatch.
- No renderer output changes.
- No CLI changes.
- No JSON output changes.
- No lint semantics, severity, sorting, or strict-mode changes.
- No docs output changes.
- No row-count grammar changes.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

Plan review history:

- `docs/reviews/opencode-stage-165-plan-review.md`
  - No critical findings.
  - No important findings.
  - Two minor findings only; neither blocks implementation.

Focused verification evidence:

- `uv --no-config run --frozen pytest tests/test_lint_formatting.py -q`
  - Result: 7 passed.
- `uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py -q -k "render_"`
  - Result: 14 passed, 114 deselected.
- `uv --no-config run --frozen ruff check tests/test_lint_formatting.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_lint_formatting.py`
  - Result: 1 file already formatted.

Review questions:

1. Does the implementation meet the Stage 165 objective?
2. Are the direct helper tests focused, readable, and sufficient for the helper
   contract?
3. Do the tests pin the intended `info` invariant without overfitting to caller
   renderers?
4. Did any production behavior or out-of-scope surface change?
5. Are the plan/review artifacts clean enough to keep?
6. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
