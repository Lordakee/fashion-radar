# Stage 204 Code Review Prompt

Review the Stage 204 code and documentation changes.

Goal: pin the optional public fashion source pack's offline composition
contract in tests and docs without changing the source pack itself.

Changed files:

- `tests/test_source_packs.py`
- `tests/test_config.py`
- `tests/test_source_packs_docs.py`
- `docs/source-packs.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-25-stage-204-public-source-pack-composition-contracts-plan.md`
- `docs/reviews/opencode-stage-204-plan-review-prompt.md`
- `docs/reviews/opencode-stage-204-plan-review.md`

Verification already run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py::test_source_packs_docs_list_public_rss_sources_in_pack_order -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_config.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
uv --no-config run --frozen ruff check tests/test_source_packs.py tests/test_config.py tests/test_source_packs_docs.py docs/source-packs.md docs/superpowers/plans/2026-06-25-stage-204-public-source-pack-composition-contracts-plan.md docs/reviews/opencode-stage-204-plan-review.md docs/reviews/opencode-stage-204-plan-review-prompt.md
uv --no-config run --frozen ruff format --check tests/test_source_packs.py tests/test_config.py tests/test_source_packs_docs.py
git diff --check
```

Important context:

- The RSS docs test was verified RED before `docs/source-packs.md` was updated.
- The exact YAML/config/lint contract tests codify existing intended state and
  may pass immediately by design.
- This stage must not add/remove/change sources, URLs, GDELT queries, tags,
  weights, dependency files, runtime collectors, source acquisition, social
  connectors, scraping, live liveness gates, demand proof, platform coverage
  verification, or compliance-review behavior.

Please review:

1. Do the tests correctly pin the current public pack composition and explicit
   fetch boundaries?
2. Is asserting exact 20-source composition and exact 10-entry RSS URL equality
   appropriate for this optional pack?
3. Does the raw YAML test correctly avoid Pydantic-default false confidence?
4. Are the new RSS docs inventory and docs-sync test consistent with the
   existing GDELT docs pattern?
5. Do docs and changelog accurately describe an offline contract rather than
   live source availability or demand proof?
6. Does the stage avoid dependency, source-content, connector, scraper,
   coverage, demand-proof, and compliance-review behavior changes?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
