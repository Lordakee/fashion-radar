# Stage 198 Code Review

## Verification re-run (independent)

| Check | Result |
|---|---|
| Core 4-file test set | `15 passed` |
| Extended 13-item suite | `158 passed` |
| **Full test suite** | **`1471 passed`** |
| `entity-pack-lint` JSON | `entity_count=32`, 0 errors, 16 warnings, 71 info; first finding = pre-existing `context_terms_no_effect` for `Boat Shoes` |
| `community-signal-lint` | `row_count=13`, `valid_row_count=13`, no findings |
| `uv lock --check` | 84 packages, clean |
| `uv.lock` / `pyproject.toml` diff | none |
| mirror scan in `uv.lock` | no matches |
| secrets scan on new CSV rows | none (all `example.com`) |
| `src/` changes | **none** (pure data/test/docs) |

## Answers to review questions

**1. Are the new aliases/context terms technically safe under matcher semantics? — Yes.**

Verified against `src/fashion_radar/extract/entities.py:28-115` and `text.py:48-64`:
- `Savette`/`Aeyde` use `safe_single_word: true` + `reason`, matching the established pattern (Khaite, Toteme, Alaia, Loewe, Jacquemus, Zendaya). Both are coined, non-dictionary tokens absent from `UNSAFE_COMMON_ALIASES` (`settings.py:13-24`), so no `safe_common_alias` warning fires. Trailing `(?!\w)` prevents plurals/compounds matching.
- Product aliases (`Savette Symmetry`, `Symmetry Bag`, `Aeyde Uma`, `Uma Mary Jane`) are all routed through the parent-brand/context gate (`entities.py:69-74`). `safe_single_word` is correctly a no-op here because the product branch short-circuits first.
- **No collision** between product alias `Uma Mary Jane` and category `Mary Jane Shoes`: the matcher matches whole literal phrases with word boundaries (`text.py:59-64`); normalized alias keys are distinct; no shared token index exists. The duplicate guard is exact-key only (`settings.py:60-70`), which is the correct/safe design here.

**2. Do tests cover intended behavior without brittle/impossible assertions? — Yes.**
- The bare-shorthand test (`test_entity_packs.py:120-132`) asserts `decisions == []`. This is correct and *not* over-strong: "The symmetry of the geometry was noted." contains no literal phrase `symmetry bag` or `savette symmetry`, so the matcher records no decision at all (`entities.py:41-42` skips). The assertion faithfully captures real semantics.
- Count assertions use `>=` (e.g. `>= 32`, `>= 12`, `>= 8`) — forward-compatible, not brittle.
- The new `--limit 50` on the trends command (`test_watchlist_sample_workflow.py:180-181`) is justified: `EXPECTED_REPORT_ENTITIES` now has 18 members while the trends default is 20 (`cli.py:1516`); a 32-entity pack can emit >20 deltas, so explicit headroom keeps the subset assertion stable. Reasonable and explicit.
- `WATCHLIST_EXPECTED_ROWS = 13` is exact, appropriate for a fixed sample file.

**3. Are docs/changelog synchronized with runtime lint? — Yes.** Every figure in `docs/entity-pack-quality.md` (entity_count, alias_count, type_counts, tag_counts, category_tag_counts, gate-classification counts, findings 0/16/71) matches live `entity-pack-lint` output exactly. Changelog boundary statement is accurate.

**4. Are scope boundaries preserved? — Yes.** No `src/` changes; no boundary terms (source/rss/atom/gdelt/collect/scrape/crawl/connector/login/cookie/token/session/proxy/monitor/schedul) in any diff; no dependency/lockfile change; new CSV rows are synthetic `example.com`; no ranking/demand-proof/coverage/compliance features. Starter config and packaged template untouched.

**5. Critical/Important issues? — None.**

## Verdict: **APPROVED**

- **Critical findings:** none.
- **Important findings:** none.
- **Minor findings:**
  - (m1, informational) The trends test now passes `--limit 50` to keep an 18-member subset assertion above the default-20 delta cap. This is correct and explicit, but the test's guarantee that all expected names appear in deltas is now mildly coupled to available headroom. Not a defect; no action required.
  - (m2, informational) `context_terms_no_effect` warning for `Boat Shoes` remains the first lint finding — pre-existing, out of scope for this stage, correctly left alone.
- **Concrete fixes required before release review:** none.

The implementation is a clean, pattern-consistent data expansion with deterministic guards, accurate regenerated docs, and intact scope boundaries. Ready for release review.
