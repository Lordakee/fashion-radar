# Stage 206 Code Review

## Verification Run Independently

OpenCode independently ran the Stage 206 verification checks during review:

- `1510 passed` for the full pytest suite.
- `ruff check` and `ruff format --check` passed.
- Release hygiene passed.
- `uv lock --check` resolved 85 packages cleanly.
- `uv.lock` / `pyproject.toml` diff and whitespace checks were clean.
- Live `entity-pack-lint` JSON/table output matched
  `docs/entity-pack-quality.md` samples exactly:
  - `0 errors, 2 warnings, 71 info`
  - `accepted_without_context_aliases=12`
  - `context_gated_aliases=14`
  - first finding: `context_terms_no_effect` on `Sandy Liang`

## Verdict

**No Critical findings. No Important findings.** The implementation is correct,
backward-compatible, and scope-clean. Approvable.

## Critical

None.

## Important

None.

## Focus-point Verification

1. **Matcher correctness**: `_evaluate_alias` places the
   `alias.requires_context` branch after the product-`parent_brand` branch and
   before the `safe_single_word` / `_requires_context` path. It requires
   matched `context_terms` and returns the right reasons. Products with
   `parent_brand` stay on the existing branch.
   `test_product_parent_brand_branch_precedes_alias_requires_context` pins this
   ordering.

2. **Config correctness**: `settings.py` rejects `requires_context: true`
   aliases lacking entity `context_terms`. Covered by both reject and accept
   tests.

3. **Linter correctness**: `_classify_alias_gate` checks
   `alias.requires_context` before `safe_single_word`, so the safe+context
   combination classifies as `CONTEXT_REQUIRED`; pinned by
   `test_explicit_context_alias_takes_precedence_over_safe_alias_lint`
   asserting `context_gated_aliases == 1`, `safe_aliases == 0`.

4. **Watchlist scope**: Only `Mary Jane Shoes`, `East-West Bags`,
   `Boat Shoes`, and `Suede Sneakers` aliases changed. `Sandy Liang`, starter
   configs, and `configs/entities.example.yaml` are untouched. Context terms
   were retuned so none are self-satisfied by the alias text.

5. **Tests**: Coverage spans model defaults, matcher RED/GREEN,
   safe/context precedence in matcher and lint, product parent-brand
   precedence, config validation, linter classification, self-context warning,
   watchlist false-positive rejection, sample-workflow compatibility, and docs
   sample parity. The sample CSV already contains `runway footwear` /
   `handbag styling`, so the gated entities still match.

6. **Docs/changelog**: `requires_context: true` is documented in both docs;
   quality-doc samples are regenerated to current live output and verified by
   the parity tests; changelog scope statement is accurate.

7. **Scope control**: No dependency/lockfile changes; no source acquisition,
   scoring, report, dashboard, DB, connector, scraping, demand-proof,
   coverage-verification, or compliance-review changes.

8. **Review artifact hygiene**: `opencode-stage-206-plan-review.md` and
   `opencode-stage-206-plan-rereview.md` are coherent, single-verdict
   artifacts with genuine review content; no stubs, truncation, duplication,
   or tool-status lines.

## Minor

1. `_alias_requires_context(...)` retains `alias.requires_context or`,
   unreachable from its only caller since `_classify_alias_gate` early-returns
   on that flag. Harmless defensive code; a pure future cleanup.

2. The config-validation check applies to all entity types, including `PRODUCT`
   with `parent_brand` where the matcher never consults `requires_context`.
   Mildly conservative; no current or planned config is affected since the field
   is only applied to `category` aliases.

Both minor notes were already documented in the plan rereview audit trail; no
action is required for this stage.
