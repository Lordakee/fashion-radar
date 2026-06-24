# Stage 188 Release Review Prompt

Review the Stage 188 implementation for `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

# Stage 188 Release Review

Files to review:

- `tests/test_collectors_runner.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `docs/architecture.md`
- `docs/REVIEW_PROTOCOL.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-design.md`
- `docs/superpowers/plans/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-plan.md`
- `docs/reviews/opencode-stage-188-plan-review.md`
- `docs/reviews/opencode-stage-188-code-review.md`

Full release gate evidence:

- `ALL_PROXY=socks5h://127.0.0.1:9 ... uv --no-config run --frozen pytest -q`: 1390 passed
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`: passed
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`: passed
- `uv --no-config run --frozen ruff check .`: All checks passed
- `uv --no-config run --frozen ruff format --check .`: 144 files already formatted
- `env -u UV_DEFAULT_INDEX ... uv lock --check`: Resolved 84 packages
- `git diff --check`: clean
- `rg -n 'ghp_[A-Za-z0-9]+' .`: no matches
- `git config --get-all http.https://github.com/.extraheader`: no output

Review questions:

1. Does the test-only isolation fix correctly resolve the proxy-sensitive
   collector/workflow test failures without changing runtime behavior?
2. Are the roadmap/documentation corrections aligned with the full-project
   review findings and appropriately scoped?
3. Is the change set limited to tests and docs only, with no `src/` runtime
   changes, dependency changes, lockfile changes, or new CLI behavior?
4. Does the release gate evidence confirm the fix is complete and the suite
   passes under a synthetic proxy environment?
5. Are there any remaining issues that should block commit and push?

Report findings under Critical, Important, and Minor. If acceptable, approve
for commit and push.
