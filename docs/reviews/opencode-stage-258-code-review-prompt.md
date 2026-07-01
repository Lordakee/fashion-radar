Review the Stage 258 code changes for Fashion Radar as the local opencode
fallback reviewer.

Repository: /home/ubuntu/fashion-radar
Model route: zhipuai-coding-plan/glm-5.2 --variant max
Base/current commit: ca60fe7bc48d4ccc38008d7bf81a959760b15c07
Worktree changes are unstaged.

Read:
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/superpowers/plans/2026-07-01-stage-258-html-report-artifact-hygiene-parity-plan.md
- docs/reviews/claude-code-stage-258-code-review.md
- docs/reviews/opencode-stage-258-plan-review.md
- git diff -- README.md docs/first-run.md docs/data-retention.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_data_retention_docs.py

What was implemented:
- `scripts/check_first_run_smoke.py` now derives and asserts the generated HTML
  report path alongside Markdown and JSON.
- `tests/test_first_run_smoke.py` covers HTML path parity, artifact guard
  created/changed/deleted HTML files, and the deterministic fake first-run flow
  writing the HTML report.
- README, first-run docs, data-retention docs, and docs guard tests now include
  generated HTML report artifacts where appropriate.

Verification already run:
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_data_retention_docs.py -q`
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_data_retention_docs.py`
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_data_retention_docs.py`
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- `git diff --check`

Check:
- Plan alignment and scope control.
- Missing consumers of `report_paths()`.
- Docs guard specificity for the README smoke sentence and reset command.
- Whether daily digest is correctly left out of scope.
- Any Critical or Important correctness issues that must be fixed before commit.

Return:
- Verdict.
- Strengths.
- Critical issues, if any.
- Important issues, if any.
- Minor issues, if any.
- Assessment: ready to merge yes/no/with fixes.
