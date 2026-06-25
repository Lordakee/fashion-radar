# Stage 198 Release Review

## Verdict

**APPROVED.** No Critical or Important findings remain. The stage is a clean, pattern-consistent data/test/docs expansion confined to the optional watchlist pack and its synthetic sample, with intact scope boundaries and all release gates green.

## Critical findings

None.

## Important findings

None.

## Minor findings

- **(m1, informational — the formatting fix is acceptable.)** The `tests/test_review_protocol_docs.py` change is purely mechanical `ruff format` line reflow: two `assert` expressions and one dict literal were reflowed, with no string, logic, or assertion-content change. It is required to satisfy the `ruff format --check .` release gate (which otherwise fails on pre-existing drift), and bundling it here with a transparent note in the plan/expected-file list is preferable to bypassing the gate. Prefer fixing drift in a dedicated commit next time to keep stage scope tight, but this does not block release.
- **(m2, informational)** The two new CSV sample rows carry `version=1.1` while prior rows are `1.0`. No test or lint constrains per-row version uniformity, and using 1.1 for newly added rows is a reasonable convention. No action required.
- **(m3, informational, pre-existing)** The first lint warning remains `context_terms_no_effect` for `Boat Shoes`; correctly left out of scope for this stage.

## Verification notes

All gates re-run independently from a clean frozen environment:

| Check | Result |
|---|---|
| `git diff --check` | clean |
| `git diff --exit-code -- uv.lock pyproject.toml` | clean (src + both starter configs also unchanged) |
| `UV_NO_CONFIG=1 uv lock --check` | 84 packages |
| mirror-URL scan in `uv.lock` | no matches |
| `UV_NO_CONFIG=1 uv sync --locked --dev --check` | passes |
| `ruff check .` / `ruff format --check .` | pass (148 files formatted) |
| `entity-pack-lint` live JSON vs `docs/entity-pack-quality.md` | exact match: entity_count=32, alias_count=51, types brand=12/category=5/celebrity=2/designer=2/product=8/trend=3, safe_aliases=9, product_parent_gated_aliases=16, accepted_without_context=22, context_gated=4, findings 0 errors / 16 warnings / 71 info |
| New-entity lint impact | **0 new warnings** — all 16 warnings are pre-existing entities; new brands emit only `safe_single_word_alias` info, new products are parent-gated with no `ungated_alias_with_context_terms`/self-context findings |
| `check_release_hygiene.py` | passed |
| `check_first_run_smoke.py` | passed |
| `uv build` + `check_package_archives.py` | passed |
| `pytest tests/ -q` | **1471 passed** |

Matcher semantics confirmed against `src/fashion_radar/extract/entities.py:63-87` and `entity_packs.py:286-359`:
- `Savette`/`Aeyde` are coined, non-dictionary tokens absent from `UNSAFE_COMMON_ALIASES`; `safe_single_word + reason` is correct, with `(?!\w)` preventing plural/compound bleed.
- Both products route through the parent-brand/context gate (`entities.py:69-74`). Bare `Symmetry`/`Uma` are deliberately excluded and regression-guarded by `test_fashion_watchlist_matcher_does_not_register_bare_new_product_shorthands`, which correctly asserts `decisions == []` (no alias phrase is present in the probe text).
- Post-I2, `Symmetry Bag`/`Uma Mary Jane` no longer embed their own context tokens, so `REASON_MISSING_CONTEXT` is reachable; `savette`/`aeyde` retained as context equals the parent brand — identical to the established `Alaia`/`Loewe` product pattern and does not weaken precision.
- No `product_alias_matches_parent_brand` collision (alias keys `savette symmetry`/`symmetry bag`/`aeyde uma`/`uma mary jane` are distinct from parent keys `savette`/`aeyde`).

Scope boundaries preserved: `src/` untouched; both starter configs untouched; no source/RSS/Atom/GDELT collection, no social/connector/scrape/crawl/browser/login/cookie/session/proxy behavior, no ranking/hotness/demand-proof/coverage-verification, and no compliance-review product feature in any diff. New CSV rows are synthetic `example.com`. Review artifacts (plan prompt/review, code prompt/review, release prompt) are complete, non-stub, and free of tool-status chatter; the stage plan is 645 lines.

## Release decision

**Release is approved.** The changed-file scope — including the mechanical `tests/test_review_protocol_docs.py` formatting fix (m1) — is acceptable. Commit/push may proceed.
