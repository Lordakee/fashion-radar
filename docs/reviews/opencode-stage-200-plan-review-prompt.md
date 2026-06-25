# Stage 200 Plan Review Prompt

Review the Stage 200 implementation plan:

`docs/superpowers/plans/2026-06-25-stage-200-source-liveness-socks-proxy-compatibility-plan.md`

Context:

- Stage 199 added aggregate match evidence to reports and has been committed
  and pushed.
- The current v0.1.x review protocol prioritizes curated public-source coverage
  using source-liveness evidence and deterministic matching quality.
- In this workspace, `ALL_PROXY` and `all_proxy` are set to `socks5h://...`.
  The current locked environment has `httpx` but not `socksio`, so
  `FashionHttpClient(HttpSourceSettings(...))` fails at `httpx.Client`
  construction with an ImportError before source-liveness can probe feeds.
- Public source exploration found useful RSS endpoint recovery work, but that
  evidence path is weaker while source-liveness cannot run in SOCKS-proxy
  environments.

Please review:

1. Whether Stage 200 should prioritize SOCKS proxy compatibility before public
   RSS endpoint recovery or new source additions.
2. Whether changing the core dependency from `httpx>=0.28.1` to
   `httpx[socks]>=0.28.1` is the right fix, versus `trust_env=False`,
   per-source proxy config, source-liveness code changes, or deferring as
   environment-only.
3. Whether the proposed no-network `tests/test_http.py` constructor regression
   is a valid RED/GREEN test for the observed failure.
4. Whether the lockfile and mirror hygiene plan is sufficient, especially use of
   `UV_NO_CONFIG=1 uv lock`, narrow `uv.lock` review, and mirror-string scan.
5. Whether docs wording properly frames this as standard HTTP client
   compatibility with user/system proxy environment variables, not proxy pools,
   scraping, browser automation, source acquisition, platform coverage
   verification, ranking, or compliance-review behavior.
6. Whether the plan correctly avoids source packs, starter configs, scoring,
   matching, reports, social connectors, and external/community/imported command
   surfaces.
7. Whether verification and release-review steps are sufficient.

Return findings as:

- Critical: blockers that must be fixed before implementation.
- Important: issues that should be fixed before implementation.
- Minor: optional polish.

If there are no Critical or Important findings, say that clearly.
