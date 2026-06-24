# Stage 187 Release Review Prompt

Review the Stage 187 release state for `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 187 Release Review
```

Files to review:

- `tests/test_external_tool_contract_parity.py`
- `docs/superpowers/specs/2026-06-24-stage-187-community-adapter-catalog-exact-table-design.md`
- `docs/superpowers/plans/2026-06-24-stage-187-community-adapter-catalog-exact-table-plan.md`
- `docs/reviews/opencode-stage-187-plan-review.md`
- `docs/reviews/opencode-stage-187-code-review.md`

Verification already completed:

- `uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q`
- `uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q -k "adapter_catalog or community_signal_docs"`
- `uv --no-config run --frozen ruff check tests/test_external_tool_contract_parity.py`
- `uv --no-config run --frozen ruff format --check tests/test_external_tool_contract_parity.py`
- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q` passed with 1389 tests.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .` passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .` passed.
- `uv --no-config run --frozen ruff check .` passed.
- `uv --no-config run --frozen ruff format --check .` passed.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check` passed.
- `git diff --check` passed.
- `rg -n 'ghp_[A-Za-z0-9]+' .` returned no matches.
- `git config --get-all http.https://github.com/.extraheader` returned no persisted extraheader.

Review questions:

1. Does the final state satisfy the Stage 187 objective: exact adapter-catalog
   parity in both community docs, with no stale extra rows or row-order drift
   slipping through?
2. Are the code and review artifacts clean and internally consistent, with the
   temporary stale-row RED mutation fully removed from the working tree?
3. Is the change scope still limited to the intended test-only hardening plus
   staged review/spec/plan artifacts?
4. Does the final state avoid source acquisition, scraping, browser automation,
   platform APIs, dependency changes, package changes, scheduling, ranking,
   demand proof, platform coverage verification, and compliance-review product
   behavior?

Report findings under Critical, Important, and Minor. Critical or Important
findings must include exact file/line references and concrete fixes. If the
state is acceptable, say it is approved for the full release gate and commit.
