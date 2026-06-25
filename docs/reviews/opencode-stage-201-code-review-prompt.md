# Stage 201 Code Review Prompt

Review the Stage 201 implementation in `/home/ubuntu/fashion-radar`.

Goal: normalize existing public RSS source URLs to current direct feed endpoints
so `source-liveness` and first-run collection avoid avoidable redirects or stale
feed paths.

This is a focused read-only review. Do not edit files. Do not run the full test
suite, package build, or live network checks. Inspect the current diff, tests,
docs, and verification evidence below.

Changed files:

- `CHANGELOG.md`
- `configs/source-packs/fashion-public.example.yaml`
- `configs/sources.example.yaml`
- `docs/source-packs.md`
- `src/fashion_radar/templates/configs/sources.example.yaml`
- `tests/test_config.py`
- `tests/test_source_packs_docs.py`
- `tests/test_stage1_hardening.py`
- Stage 201 plan/review artifacts

Implementation summary:

- Public source pack URLs were updated to direct RSS endpoints for Fashionista,
  Fashion Week Daily, The Industry Fashion, Highsnobiety, and WWD.
- Starter config URLs were updated for Fashionista and Fashion Week Daily.
- The packaged starter template was synchronized from
  `configs/sources.example.yaml` and verified with `cmp -s`.
- Tests now pin the canonical public-pack URLs, starter URL subset, source-pack
  docs availability wording, and root/package starter byte identity.
- Docs and changelog record this as direct RSS endpoint normalization, not new
  source acquisition or source expansion.

Verification already run:

- RED:
  `uv --no-config run --frozen pytest tests/test_config.py::test_public_fashion_source_pack_uses_direct_rss_endpoints tests/test_config.py::test_starter_source_configs_use_direct_rss_endpoints tests/test_stage1_hardening.py::test_root_and_packaged_source_configs_stay_byte_identical tests/test_source_packs_docs.py::test_source_packs_docs_record_stage_201_direct_endpoint_refresh -q`
  failed for the old RSS URL literals and missing Stage 201 docs wording, while
  the byte-identity guard passed.
- GREEN: the same command passed with `4 passed`.
- `cmp -s configs/sources.example.yaml src/fashion_radar/templates/configs/sources.example.yaml`
  passed.
- `uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict`
  passed with no findings.
- `uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json`
  reported `20` sources, `10` RSS, `10` GDELT, and no findings.
- Focused tests passed:
  `uv --no-config run --frozen pytest tests/test_config.py tests/test_stage1_hardening.py tests/test_source_packs.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_source_liveness.py -q`
  -> `76 passed`.
- Focused CLI source pack/liveness tests passed:
  `uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_pack_lint or source_liveness"`
  -> `17 passed, 302 deselected`.
- Advisory live `source-liveness` summary after URL updates:
  `live=11 degraded=0 empty=0 failed=9 errors=9`.
  The five Stage 201 RSS targets were all live:
  Fashionista `50`, Fashion Week Daily `20`, The Industry Fashion `20`,
  Highsnobiety `11`, WWD `10`. Remaining live failures are outside this RSS
  endpoint normalization scope and are not release gates.

Please check:

1. Exact canonical URL test coverage and whether the URL literals match the
   intended direct endpoints.
2. Public pack and starter/template alignment, including byte identity.
3. Docs and changelog accuracy, including point-in-time availability wording.
4. No runtime HTTP, source-liveness, collector, source-pack lint, scoring,
   matching, report, dashboard, dependency, lockfile, external/community, or
   imported command changes.
5. No source acquisition, ranking, demand proof, coverage proof, social
   connector, proxy-pool/rotation, scraping, browser automation, platform API,
   or compliance-review scope creep.
6. Whether the verification set is sufficient before release review.

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
