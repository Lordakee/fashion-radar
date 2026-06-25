# Stage 200 Release Review Prompt

Review Stage 200 in `/home/ubuntu/fashion-radar` for release readiness.

This is a focused read-only release review. Do not edit files. Do not run the
full test suite, package build, sync commands, or live `source-liveness`; those
commands have already been run by the release owner. Inspect current status,
current diff, review artifacts, lockfile hygiene, and the verification evidence
below.

Stage goal: make `FashionHttpClient` and `source-liveness` usable in
environments that already set standard SOCKS proxy environment variables by
declaring `httpx[socks]>=0.28.1` in the core runtime dependency graph.

Expected included files:

- `CHANGELOG.md`
- `README.md`
- `docs/dependency-mirrors.md`
- `docs/reviews/opencode-stage-200-plan-review-prompt.md`
- `docs/reviews/opencode-stage-200-plan-review.md`
- `docs/reviews/opencode-stage-200-code-review-prompt.md`
- `docs/reviews/opencode-stage-200-code-review.md`
- `docs/reviews/opencode-stage-200-release-review-prompt.md`
- `docs/reviews/opencode-stage-200-release-review.md`
- `docs/superpowers/plans/2026-06-25-stage-200-source-liveness-socks-proxy-compatibility-plan.md`
- `pyproject.toml`
- `uv.lock`
- `tests/test_cli_docs.py`
- `tests/test_http.py`

Implementation summary:

- `pyproject.toml` changed `httpx>=0.28.1` to `httpx[socks]>=0.28.1`.
- `uv.lock` records the `httpx` `socks` extra and adds `socksio==1.0.0`.
- `tests/test_http.py` covers `FashionHttpClient(...)` construction with
  `ALL_PROXY` and `all_proxy` set to `socks5h://127.0.0.1:9`, without issuing a
  network request.
- Docs explain frozen mirror installs include the SOCKS transport helper and
  explicitly avoid proxy-pool/rotation scope.
- The Stage 200 plan was corrected after a review finding so
  `tests/test_cli_docs.py` appears in both file responsibilities and final
  staging guidance.

Verification evidence already run:

- `git diff --check` passed.
- `UV_NO_CONFIG=1 uv lock --check` passed.
- `rg -n "tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links" uv.lock`
  returned no matches.
- `UV_NO_CONFIG=1 uv sync --locked --dev --check` passed.
- `uv --no-config run --frozen ruff check .` passed.
- `uv --no-config run --frozen ruff format --check .` passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  passed.
- Package build and `scripts/check_package_archives.py` passed.
- `uv --no-config run --frozen pytest tests/ -q --tb=short` passed with
  `1477 passed`.
- Secret scan for `ghp_...` and `github_pat_...` outside lock/build/dist
  returned no matches.
- Stage 200 code review found no Critical or Important findings.

Please check:

1. All required Stage 200 artifacts are present, clean, and consistent.
2. The plan, docs, and tests match the implemented scope.
3. No release-blocking uncommitted/generated/secret/mirror hygiene risks remain.
4. The verification evidence is sufficient to commit and push.
5. The next-stage direction should remain public RSS endpoint liveness recovery,
   not social scraping/connectors, proxy pools, compliance-review features, or
   broad source expansion in this commit.

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
