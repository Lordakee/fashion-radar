# Stage 182 Release Review Prompt

Review Stage 182 for release readiness in `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 182 Release Review
```

Stage 182 summary:

- Extended first-run smoke's default artifact guard so it snapshots exactly the
  three repo-local generated config files when present:
  - `configs/sources.yaml`
  - `configs/entities.yaml`
  - `configs/scoring.yaml`
- Added `test_default_artifact_guard_detects_new_repo_config_files`.
- Kept scanning of `data/` and `reports/` unchanged.
- Did not scan the full `configs/` tree.
- Did not change smoke command order, validators, runtime CLI behavior,
  collectors, connectors, dependencies, lockfiles, source acquisition,
  scraping, platform APIs, monitoring, scheduling, ranking, demand proof,
  coverage verification, or compliance-review product behavior.

Review artifacts:

- `docs/reviews/opencode-stage-182-plan-review.md`
- `docs/reviews/opencode-stage-182-code-review.md`

Release gate already run:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - 1379 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Resolved 84 packages in 3ms.
- `git diff --check`
  - exit 0, no output.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - exit 1, no output, expected clean absence.
- `git config --get-all http.https://github.com/.extraheader`
  - exit 1, no output, expected clean absence.

Review questions:

1. Is Stage 182 in scope and ready to commit?
2. Are plan/code review artifacts complete and clean?
3. Is release verification sufficient for this smoke-helper hardening?
4. Did any runtime behavior outside the intended generated-config artifact guard
   drift in?
5. Are there any Critical or Important findings before commit and push?

Report findings under Critical, Important, and Minor. If acceptable, approve
commit and push.
