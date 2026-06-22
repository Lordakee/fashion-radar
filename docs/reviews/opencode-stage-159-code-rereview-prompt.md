# Stage 159 Code Rereview Prompt

Review the Stage 159 follow-up after the code review minor m1 was addressed.

Files to review:

- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `docs/superpowers/plans/2026-06-23-stage-159-review-artifact-hygiene-gate-plan.md`
- `docs/reviews/opencode-stage-159-code-review.md`

Follow-up changes:

- Added `test_stage_159_review_artifact_with_review_completed_prose_passes`.
- Narrowed `is_review_tool_status_line(...)` so `Review complete`,
  `Review complete.`, and `Review complete:` are tool-status lines, but
  ordinary prose such as `Review completed on 2026-06-23` is accepted.
- Cleaned `docs/reviews/opencode-stage-159-code-review.md` to contain one
  coherent review body with no live-capture chatter or tool logs.

Verification already run:

- `uv --no-config run --frozen pytest tests/test_release_hygiene.py::test_stage_159_review_artifact_with_review_completed_prose_passes -q` -> 1 passed.
- `uv --no-config run --frozen pytest tests/test_release_hygiene.py -q -k "review_artifact or review_capture"` -> 12 passed.
- `uv --no-config run --frozen pytest tests/test_release_hygiene.py -q` -> 82 passed.
- `uv --no-config run --frozen ruff check scripts/check_release_hygiene.py tests/test_release_hygiene.py` -> passed.
- `uv --no-config run --frozen ruff format --check scripts/check_release_hygiene.py tests/test_release_hygiene.py` -> passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .` -> passed after code-review artifact cleanup.

Review questions:

1. Does the m1 fix avoid the `Review completed` false positive without weakening
   intended tool-status detection?
2. Are the new test and implementation consistent with the Stage 159 scope?
3. Are the Stage 159 review artifacts clean enough for the new hygiene gate?
4. Are there any critical or important findings before release verification?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
