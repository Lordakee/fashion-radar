# Stage 159 Code Review Prompt

Review the Stage 159 implementation for Fashion Radar.

Changed files:

- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `docs/superpowers/specs/2026-06-23-stage-159-review-artifact-hygiene-gate-design.md`
- `docs/superpowers/plans/2026-06-23-stage-159-review-artifact-hygiene-gate-plan.md`
- `docs/reviews/opencode-stage-159-plan-review-prompt.md`
- `docs/reviews/opencode-stage-159-plan-review.md`
- `docs/reviews/opencode-stage-159-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-159-plan-rereview.md`

Objective:

Add an automated release-hygiene guard for Stage 159+ completed opencode review
capture artifacts under `docs/reviews/`.

Implementation summary:

- `scripts/check_release_hygiene.py` now scans matching tracked and untracked
  Stage 159+ opencode review output files.
- Prompt files and Stage 158 or older review records are excluded.
- Numbered rereview files such as `opencode-stage-159-code-rereview-2.md` are
  included.
- The scanner flags empty output, ANSI escape sequences, tool-status lines,
  line-start opencode UI markers, and first-line process chatter.
- Inline arrow prose such as `pytest -q -> passed` remains allowed.

Focused verification already run:

- `uv --no-config run --frozen pytest tests/test_release_hygiene.py -q -k "review_artifact or review_capture"` -> 12 passed.
- `uv --no-config run --frozen pytest tests/test_release_hygiene.py -q` -> 82 passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .` -> passed.
- `uv --no-config run --frozen ruff check scripts/check_release_hygiene.py tests/test_release_hygiene.py` -> passed.
- `uv --no-config run --frozen ruff format --check scripts/check_release_hygiene.py tests/test_release_hygiene.py` -> passed.

Review questions:

1. Does the scanner correctly inspect only completed Stage 159+ opencode review
   output artifacts and ignore prompt files plus Stage 158 legacy files?
2. Are the blocked markers narrow enough to avoid likely false positives while
   catching live-capture/tool-output mistakes?
3. Do the tests prove tracked and untracked review artifacts are covered,
   including numbered rereviews and inline-arrow prose?
4. Does the change preserve product scope boundaries, with no runtime/social
   collection, scheduling, scraping, platform API, or compliance-review product
   behavior?
5. Are there any critical or important findings that must be fixed before
   commit?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
