# Stage 189 Release Review Prompt

Review the Stage 189 release state before commit and push. Evaluate the current
working tree, including uncommitted changes intended for this commit. Do not
treat "not committed yet" as a blocking finding.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:

- Broaden release-hygiene review-capture checks to non-stage opencode review
  records and timeout-stub staged records.
- Clean the full-project review artifact.
- Replace the Stage 188 code-review timeout stub with completed review output,
  fix the duplicate workflow proxy-test finding, and add Stage 188 follow-up
  rereviews.
- Keep this as a prerequisite review-gate maintenance node; the next product
  node should be source-liveness diagnostics.

Inspect:

- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `tests/test_workflows.py`
- `docs/REVIEW_PROTOCOL.md`
- `CHANGELOG.md`
- `docs/reviews/opencode-full-project-review.md`
- `docs/reviews/opencode-stage-188-plan-review.md`
- `docs/reviews/opencode-stage-188-code-review.md`
- `docs/reviews/opencode-stage-188-code-rereview.md`
- `docs/reviews/opencode-stage-188-release-review.md`
- `docs/reviews/opencode-stage-188-release-rereview.md`
- `docs/superpowers/specs/2026-06-24-stage-189-review-capture-hygiene-coverage-design.md`
- `docs/superpowers/plans/2026-06-24-stage-189-review-capture-hygiene-coverage-plan.md`
- `docs/reviews/opencode-stage-189-plan-review.md`
- `docs/reviews/opencode-stage-189-plan-rereview.md`
- `docs/reviews/opencode-stage-189-code-review.md`
- `docs/reviews/opencode-stage-189-code-rereview.md`

Verified commands already run by Codex:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 HTTPS_PROXY=socks5h://127.0.0.1:9 HTTP_PROXY=socks5h://127.0.0.1:9 http_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest -q
# 1393 passed

uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
# passed

uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# passed

uv --no-config run --frozen ruff check .
# passed

uv --no-config run --frozen ruff format --check .
# 144 files already formatted

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
# resolved 84 packages

git diff --check
# clean

rg -n 'ghp_[A-Za-z0-9]+' .
# no matches

git config --get-all http.https://github.com/.extraheader
# no output
```

Questions:

1. Does the Stage 189 implementation satisfy the design and plan?
2. Are all prior Stage 189 plan/code review Critical and Important findings
   closed?
3. Are the Stage 188 follow-up review records sufficient to close the stale
   timeout-stub and duplicate-test issues?
4. Is the release gate evidence sufficient and fresh?
5. Are there any remaining Critical or Important blockers to commit and push?

Report:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A verdict stating whether Stage 189 is approved for commit and push.

Start the response exactly with:

```text
# Stage 189 Release Review
```

Do not include process chatter, command logs, ANSI output, or tool-status lines.
