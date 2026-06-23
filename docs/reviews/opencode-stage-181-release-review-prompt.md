# Stage 181 Release Review Prompt

Review Stage 181 for release readiness in `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 181 Release Review
```

Stage 181 summary:

- Added a runtime-derived docs parity guard in
  `tests/test_external_tool_contract_parity.py` so both community docs must
  list the current external social/community tool adapter catalog.
- Added the current `Known adapter ids` table to:
  - `docs/community-signal-import.md`
  - `docs/community-signal-quality.md`
- Kept the change docs/test-only. No runtime adapter, CLI, connector, scraping,
  browser automation, platform API, monitoring, scheduling, source acquisition,
  demand proof, ranking, coverage verification, compliance-review product,
  dependency, or lockfile behavior should be present.

Review artifacts:

- `docs/reviews/opencode-stage-181-plan-review.md`
- `docs/reviews/opencode-stage-181-code-review.md`
- `docs/reviews/opencode-stage-181-code-rereview.md`

Release gate already run:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - 1378 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Resolved 84 packages in 1ms.
- `git diff --check`
  - exit 0, no output.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - exit 1, no output, expected clean absence.
- `git config --get-all http.https://github.com/.extraheader`
  - exit 1, no output, expected clean absence.

Review questions:

1. Is Stage 181 in scope and ready to commit?
2. Are the plan/code/rereview artifacts complete, clean, and consistent with
   local opencode review workflow?
3. Is release verification sufficient for a docs/test-only community adapter
   catalog parity node?
4. Did any runtime, connector, source acquisition, scraping, platform API,
   ranking, compliance-review, dependency, lockfile, package, source-pack,
   entity-pack, first-run smoke, or release hygiene behavior drift in?
5. Are there any Critical or Important findings before commit and push?

Report findings under Critical, Important, and Minor. If acceptable, approve
commit and push.
