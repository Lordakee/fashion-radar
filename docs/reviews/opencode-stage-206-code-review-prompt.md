# Stage 206 Code Review Prompt

Review the current working tree in `/home/ubuntu/fashion-radar` for Stage 206.

Goal: add a backward-compatible alias-level `requires_context` gate to
deterministic matching and apply it only to high-risk optional watchlist
category aliases so broad phrases such as `boat shoes`, `Mary Jane shoes`,
`east-west bag`, and `suede sneakers` require surrounding fashion context.

Baseline:

- `origin/main` / `HEAD`: `4af8179501e9992b4f780e5c5dc688988be39675`
- Stage 206 changes are currently uncommitted in the working tree.

Files changed:

- `src/fashion_radar/models/entity.py`
- `src/fashion_radar/extract/entities.py`
- `src/fashion_radar/settings.py`
- `src/fashion_radar/entity_packs.py`
- `configs/entity-packs/fashion-watchlist.example.yaml`
- `tests/test_models.py`
- `tests/test_matcher.py`
- `tests/test_config.py`
- `tests/test_entity_pack_lint.py`
- `tests/test_entity_packs.py`
- `tests/test_entity_packs_docs.py`
- `docs/entity-packs.md`
- `docs/entity-pack-quality.md`
- `CHANGELOG.md`
- Stage 206 plan/review artifacts under `docs/superpowers/plans/` and
  `docs/reviews/`

Review focus:

1. Matcher correctness: explicit alias `requires_context` should require
   matched entity `context_terms` for non-product aliases, run before
   `safe_single_word`, and leave product aliases with `parent_brand` on the
   existing parent-brand-or-context branch.
2. Config correctness: `requires_context: true` aliases should be rejected when
   their entity has no `context_terms`.
3. Linter correctness: explicit context aliases should be counted as
   `context_gated_aliases`; the safe alias + explicit context combination
   should classify as context-gated, not safe.
4. Optional watchlist scope: only the planned broad category aliases in
   `configs/entity-packs/fashion-watchlist.example.yaml` should be changed.
   Do not require changes to default starter config or `Sandy Liang` in this
   stage.
5. Tests: verify coverage for model defaults, matcher RED/GREEN behavior,
   safe/context precedence, product parent-brand precedence, config validation,
   linter classification, self-context warnings, watchlist false-positive
   rejection, sample workflow compatibility, and docs sample parity.
6. Docs/changelog: verify docs describe `requires_context: true`, the
   `entity-pack-lint` sample reflects current live output, and the changelog
   accurately states the scope.
7. Scope control: confirm there are no dependency/lockfile changes, no source
   acquisition changes, no scoring/report/dashboard changes, no social/platform
   connectors, no scraping/browser automation, no demand proof or platform
   coverage verification changes, and no compliance-review product features.
8. Review artifact hygiene: ensure committed review records should be coherent
   artifacts, not live-capture stubs or duplicated/truncated outputs.

Focused verification already run successfully before this review:

```text
uv --no-config run --frozen pytest tests/test_models.py tests/test_matcher.py tests/test_config.py tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_entity_packs_docs.py tests/test_entity_pack_quality_docs.py -q
# 99 passed

uv --no-config run --frozen fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
# 0 errors, 2 warnings, accepted_without_context_aliases=12, context_gated_aliases=14

uv --no-config run --frozen ruff check ...
# All checks passed

uv --no-config run --frozen ruff format --check ...
# 12 files already formatted

uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
# Resolved 85 packages

git diff --exit-code -- uv.lock pyproject.toml
# clean

git diff --check
# clean
```

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
