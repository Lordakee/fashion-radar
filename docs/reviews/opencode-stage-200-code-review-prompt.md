# Stage 200 Code Review Prompt

Review the Stage 200 implementation in `/home/ubuntu/fashion-radar`.

This is a focused read-only review. Do not edit files. Do not run the full test
suite, package build, sync commands, or live `source-liveness`; those are release
review responsibilities. Inspect the current diff, the lockfile, and the
targeted verification results listed below.

Goal: make `FashionHttpClient` and `source-liveness` usable in environments that
already set standard SOCKS proxy environment variables by declaring the HTTP
client's SOCKS transport helper in the core locked dependency graph.

Changed files:

- `pyproject.toml`
- `uv.lock`
- `tests/test_http.py`
- `tests/test_cli_docs.py`
- `docs/dependency-mirrors.md`
- `README.md`
- `CHANGELOG.md`
- Stage 200 plan/review artifacts

Implementation summary:

- `pyproject.toml` now depends on `httpx[socks]>=0.28.1`.
- `UV_NO_CONFIG=1 uv lock` added `socksio==1.0.0` and recorded the `httpx`
  `socks` extra; `httpx` stayed at `0.28.1`.
- `tests/test_http.py` adds a no-network constructor regression for both
  `ALL_PROXY` and `all_proxy` set to `socks5h://127.0.0.1:9`.
- Docs explain mirror/frozen-install behavior and source-liveness proxy-env
  compatibility while preserving the "no proxy pool" boundary.
- Advisory source-liveness no longer reports the previous missing-`socksio`
  ImportError; remaining failures are normal source/network fetch failures.

Verification already run:

- RED:
  `uv --no-config run --frozen pytest tests/test_http.py::test_http_client_constructs_with_socks_proxy_env -q`
  failed with missing `socksio` before dependency change.
- `UV_NO_CONFIG=1 uv lock --check` passed.
- `UV_NO_CONFIG=1 uv sync --locked --dev --check` passed.
- Mirror-string scan on `uv.lock` returned no matches for mirror/index
  strings.
- `uv --no-config run --frozen pytest tests/test_http.py -q` passed with
  `7 passed`.
- `ALL_PROXY=socks5h://127.0.0.1:9 all_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest tests/test_http.py -q`
  passed with `7 passed`.
- `uv --no-config run --frozen pytest tests/test_http.py tests/test_source_liveness.py -q`
  passed with `27 passed`.
- `ALL_PROXY=socks5h://127.0.0.1:9 all_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest tests/test_http.py tests/test_source_liveness.py -q`
  passed with `27 passed`.
- Docs tests:
  `tests/test_cli_docs.py::test_dependency_mirror_docs_explain_socks_helper_without_proxy_pool_scope`,
  `tests/test_cli_docs.py::test_dependency_mirror_docs_explain_lockfile_recovery`,
  `tests/test_project_brief_docs.py` passed.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_project_brief_docs.py tests/test_package_metadata.py -q`
  passed with `87 passed`.
- Targeted ruff and format checks passed for edited tests.
- Full test suite passed once after implementation:
  `uv --no-config run --frozen pytest tests/ -q` -> `1477 passed`.
- Advisory source-liveness run after installing `socksio` produced no
  missing-`socksio` ImportError. Remaining failures were source/network fetch
  failures and are not release gates.

Please check:

1. Dependency and lockfile diff scope: `httpx` remains stable, `socksio` is the
   only new package, no mirror URLs are committed.
2. The test is a valid no-network regression for the observed constructor-time
   ImportError and does not mask legitimate request failures.
3. The docs wording frames this as honoring standard user/system proxy
   environment variables, not proxy pools, scraping, browser automation, source
   acquisition, demand proof, ranking, coverage verification, social connector
   behavior, or compliance-review behavior.
4. The change does not alter source-liveness contracts, HTTP client code,
   source packs, starter configs, scoring, matching, reports, or
   external/community/imported commands.
5. The verification set is sufficient before release review.

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
