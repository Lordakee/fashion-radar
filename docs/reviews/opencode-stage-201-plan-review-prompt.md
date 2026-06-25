# Stage 201 Plan Review Prompt

Review the Stage 201 implementation plan in
`docs/superpowers/plans/2026-06-25-stage-201-public-rss-endpoint-liveness-recovery-plan.md`.

Goal: normalize configured public RSS URLs to current direct feed endpoints so
`source-liveness` and first-run RSS collection avoid avoidable redirects or
stale feed paths.

Context:

- Stage 200 made the HTTP client constructible in environments with standard
  SOCKS proxy variables by declaring `httpx[socks]`.
- A short read-only probe on 2026-06-25 observed these current direct targets:
  - Fashionista:
    `https://fashionista.com/.rss/feed/28e21eb8-20ac-4617-a448-e845081591ca.xml`
  - Fashion Week Daily: `https://fashionweekdaily.com/feed/`
  - The Industry Fashion: `https://www.theindustry.fashion/feed/`
  - Highsnobiety: `https://www.highsnobiety.com/feeds/rss`
  - WWD: `https://wwd.com/feed/`
- The plan is intentionally config/docs/test only.
- Live network checks are advisory only; deterministic tests are the release
  gate.

Please review:

1. Is direct RSS endpoint normalization the right next stage after Stage 200 for
   the `collect -> match -> report` pipeline?
2. Should the scope include both `configs/source-packs/fashion-public.example.yaml`
   and the overlapping starter config/template URLs in
   `configs/sources.example.yaml` and
   `src/fashion_radar/templates/configs/sources.example.yaml`?
3. Are the planned RED tests in `tests/test_config.py` and
   `tests/test_source_packs_docs.py` sufficient and appropriately
   deterministic?
4. Are advisory live probes and `source-liveness` correctly kept out of hard
   release gates?
5. Does the plan avoid runtime code, dependency, source acquisition, ranking,
   coverage proof, social connector, proxy-pool, and compliance-review scope
   creep?
6. Is the release verification set sufficient, especially given that
   `pyproject.toml` and `uv.lock` should remain unchanged?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
