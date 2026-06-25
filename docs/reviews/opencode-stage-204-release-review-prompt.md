# Stage 204 Release Review Prompt

Review Stage 204 final release readiness.

Goal: release a test/docs-only source-pack contract stage that pins the
optional public fashion source pack's offline composition: 20 enabled sources,
10 RSS feeds, 10 bounded GDELT lanes, and RSS article extraction disabled by
default.

Changed files expected in this stage:

- `tests/test_source_packs.py`
- `tests/test_config.py`
- `tests/test_source_packs_docs.py`
- `docs/source-packs.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-25-stage-204-public-source-pack-composition-contracts-plan.md`
- `docs/reviews/opencode-stage-204-plan-review-prompt.md`
- `docs/reviews/opencode-stage-204-plan-review.md`
- `docs/reviews/opencode-stage-204-code-review-prompt.md`
- `docs/reviews/opencode-stage-204-code-review.md`
- `docs/reviews/opencode-stage-204-release-review-prompt.md`

Verification already run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py::test_source_packs_docs_list_public_rss_sources_in_pack_order -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_config.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
uv --no-config run --frozen ruff check tests/test_source_packs.py tests/test_config.py tests/test_source_packs_docs.py docs/source-packs.md CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-204-public-source-pack-composition-contracts-plan.md docs/reviews/opencode-stage-204-plan-review.md docs/reviews/opencode-stage-204-plan-review-prompt.md docs/reviews/opencode-stage-204-code-review.md docs/reviews/opencode-stage-204-code-review-prompt.md
uv --no-config run --frozen ruff format --check tests/test_source_packs.py tests/test_config.py tests/test_source_packs_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
```

Important results:

- Full pytest collected 1495 tests and passed.
- Full ruff check and format check passed.
- Source-pack strict lint reports 20 total, 20 enabled, 0 disabled,
  `gdelt=10`, `rss=10`, and no findings.
- `uv.lock` and `pyproject.toml` have no diff.

Please review:

1. Are the implementation, tests, docs, changelog, and review artifacts ready to
   commit and push?
2. Does release hygiene pass on the current working tree, including all Stage
   204 review artifacts?
3. Is the verification set sufficient for a test/docs-only source-pack
   contract stage?
4. Does the stage avoid live network checks, source additions/removals/URL
   changes/query changes, connectors, scraping, source acquisition, demand
   proof, platform coverage verification, dependency changes, and
   compliance-review behavior?
5. Is the current git status limited to expected Stage 204 files?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
