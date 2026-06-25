# Stage 201 Release Review Prompt

Review Stage 201 in `/home/ubuntu/fashion-radar` for release readiness.

This is a focused read-only release review. Do not edit files. Do not run the
full test suite, package build, sync commands, or live `source-liveness`; those
commands have already been run by the release owner. Inspect current status,
current diff, review artifacts, and verification evidence below.

Stage goal: normalize existing public RSS source URLs to current direct feed
endpoints so `source-liveness` and first-run collection avoid avoidable
redirects or stale feed paths.

Expected included files:

- `CHANGELOG.md`
- `configs/source-packs/fashion-public.example.yaml`
- `configs/sources.example.yaml`
- `docs/source-packs.md`
- `docs/reviews/opencode-stage-201-plan-review-prompt.md`
- `docs/reviews/opencode-stage-201-plan-review.md`
- `docs/reviews/opencode-stage-201-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-201-plan-rereview.md`
- `docs/reviews/opencode-stage-201-code-review-prompt.md`
- `docs/reviews/opencode-stage-201-code-review.md`
- `docs/reviews/opencode-stage-201-release-review-prompt.md`
- `docs/reviews/opencode-stage-201-release-review.md`
- `docs/superpowers/plans/2026-06-25-stage-201-public-rss-endpoint-liveness-recovery-plan.md`
- `src/fashion_radar/templates/configs/sources.example.yaml`
- `tests/test_config.py`
- `tests/test_source_packs_docs.py`
- `tests/test_stage1_hardening.py`

Implementation summary:

- Public source pack URLs were updated to direct RSS endpoints for Fashionista,
  Fashion Week Daily, The Industry Fashion, Highsnobiety, and WWD.
- Starter config URLs were updated for Fashionista and Fashion Week Daily.
- The packaged starter template was synchronized from
  `configs/sources.example.yaml`; `cmp -s` passed.
- Tests pin the canonical public-pack URLs, starter URL subset, source-pack docs
  availability wording, and root/package starter byte identity.
- Docs and changelog record this as direct RSS endpoint normalization, not new
  source acquisition or source expansion.
- `pyproject.toml` and `uv.lock` are unchanged.

Review status:

- Plan review found one Important issue: preserve starter/template byte
  identity.
- Plan rereview approved the updated plan with no Critical or Important
  findings.
- Code review approved release review with no Critical or Important findings.

Verification evidence already run:

- RED tests failed for old RSS URL literals and missing Stage 201 docs wording,
  while the byte-identity guard passed.
- GREEN targeted tests passed with `4 passed`.
- `cmp -s configs/sources.example.yaml src/fashion_radar/templates/configs/sources.example.yaml`
  passed.
- `uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict`
  passed with no findings.
- Source-pack JSON lint reported `20` sources, `10` RSS, `10` GDELT, and no
  findings.
- Focused config/docs/source-liveness tests passed with `76 passed`.
- Focused CLI source pack/liveness tests passed with
  `17 passed, 302 deselected`.
- Advisory live `source-liveness` after URL updates reported:
  `live=11 degraded=0 empty=0 failed=9 errors=9`.
  The five Stage 201 RSS targets were all live:
  Fashionista `50`, Fashion Week Daily `20`, The Industry Fashion `20`,
  Highsnobiety `11`, WWD `10`. Remaining failures are outside this RSS endpoint
  normalization scope and are not release gates.
- `git diff --check` passed.
- `UV_NO_CONFIG=1 uv lock --check` passed.
- `git diff --name-only -- pyproject.toml uv.lock` returned no files.
- `UV_NO_CONFIG=1 uv sync --locked --dev --check` passed.
- `uv --no-config run --frozen ruff check .` passed.
- `uv --no-config run --frozen ruff format --check .` passed after formatting
  `tests/test_config.py`.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  passed.
- Package build and `scripts/check_package_archives.py` passed.
- `uv --no-config run --frozen pytest tests/ -q --tb=short` passed with
  `1481 passed`.
- Secret scan for `ghp_...` and `github_pat_...` outside lock/build/dist
  returned no matches.

Please check:

1. All required Stage 201 artifacts are present, clean, and consistent.
2. The final diff matches the Stage 201 scope and includes no unintended
   runtime/dependency/lockfile changes.
3. Public pack, starter config, and packaged template remain aligned.
4. Docs and changelog preserve point-in-time availability wording and scope
   boundaries.
5. No release-blocking uncommitted/generated/secret/mirror hygiene risks remain.
6. The verification evidence is sufficient to commit and push.
7. The next-stage direction should continue improving deterministic public
   source quality or matching/report utility without social scraping/connectors,
   proxy pools, source acquisition, ranking proof, coverage proof, or
   compliance-review features.

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
