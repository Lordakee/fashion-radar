# Stage 198 Plan Review (Rereview)

**Verdict: APPROVED**

This is a rereview. The plan under review is the **revised** version that already incorporates the fixes from the first review recorded in `docs/reviews/opencode-stage-198-plan-review.md` (C1, I1, I2 — all confirmed resolved below). No new Critical or Important blockers remain.

---

## Prior Findings — Resolution Verification

- **C1 (blocking matcher tests) — FIXED.** The old rejection-test shape is gone. The plan now adds a *separate* test, `test_fashion_watchlist_matcher_does_not_register_bare_new_product_shorthands` (Task 1 Step 2), asserting `decisions == []`. Verified against `entities.py:41`: for `"The symmetry of the geometry was noted."` no alias of `Savette Symmetry Bag` (`Savette Symmetry`, `Symmetry Bag`) matches the text, and for `"Uma joined the dinner list."` no alias of `Aeyde Uma Mary Jane` (`Aeyde Uma`, `Uma Mary Jane`) matches. Test passes vacuously pre-implementation and correctly post-implementation; it fails if anyone later adds bare `Symmetry`/`Uma` aliases. Valid guard.

- **I1 (plan-review artifacts never created) — FIXED.** Task 0 now creates `opencode-stage-198-plan-review-prompt.md` and writes the completed review into `opencode-stage-198-plan-review.md` before the `git add` in Task 5 Step 5.

- **I2 (self-referential context_terms bypassing the parent gate) — FIXED.** `bag` was dropped from `Savette Symmetry Bag` (now `[savette, handbag, top handle]`) and `mary jane` was dropped from `Aeyde Uma Mary Jane` (now `[aeyde, shoe, footwear]`). Verified: the short aliases (`Symmetry Bag`, `Uma Mary Jane`) no longer embed any of their own tokens as context terms, so `REASON_MISSING_CONTEXT` is now reachable (for example, a generic symmetry-bag sentence with no Savette, handbag, or top-handle wording is rejected). `savette`/`aeyde` retained as context terms is correct because they equal the parent brand, identical to the existing product pattern (`alaia`, `loewe`, etc.) and do not weaken precision.

---

## Critical Findings
None.

## Important Findings
None.

## Minor Findings

- **m1. Review-output capture can retain process narration.** Earlier raw capture included reviewer process preamble before the structured review. Task 0/4/5 save raw `opencode run` output via `cp "$tmp_review"`. If regenerated output again includes narration, the Task 5 Step 4 hygiene scan flags it. The gate exists and catches it, but the plan only says to inspect any match before staging. Suggest hardening: instruct the review prompt to emit only the structured review, or filter preamble between capture and save. Non-blocking.

- **m2. Exact-fit thresholds have zero headroom.** Task 1 Step 1 sets `>= 32` / `>= 12` / `>= 8` against exact post-stage counts (current: 28 / 10 / 6; verified correct). Consistent with the coverage-pinning intent; any future in-stage entity removal would require updating these floors.

- **m3. Focused test runs omit one constant-dependent test.** Task 1 Step 7 / Task 4 Step 3 do not include `test_import_signals_dry_run_validates_watchlist_sample_without_artifacts`, which keys off `WATCHLIST_EXPECTED_ROWS`. It is covered by the constant update (`11 to 13`) and will run in the full pytest gate (Task 5 Step 1). Optional to add for earlier signal.

- **m4. Docs regeneration stability — verified.** Confirmed via `_sort_findings` (`entity_packs.py:645`) and `_alias_findings` that the 4 new entities add **no new errors/warnings** (brands: `safe_single_word_alias` INFO only; products: parent-gated, no `ungated_alias_with_context_terms`/`self_context_term`). The first finding remains `context_terms_no_effect` / `Boat Shoes` (no warning sorts before it; only `blank_*` codes precede it alphabetically and none fire). New counts: aliases increase from `45` to `51`, `safe_aliases` from `7` to `9`, and `product_parent_gated_aliases` from `12` to `16`. `test_entity_pack_quality_*` will pass if output is copied faithfully.

- **m5. Prose edits are boundary-safe.** Verified `test_entity_packs_docs.py` and `test_cli_docs.py:1436-1499`: no checked phrase is altered by the `docs/entity-packs.md` intro/sample-prose edits ("broader watchlist", boundary phrases, "checked-in synthetic community-signal rows" all retained).

---

## Answers to the Review Questions

1. **Closes a real gap without surface expansion?** Yes. Improves collect-match-report matching coverage via the *optional* watchlist pack and synthetic sample only. Starter config, packaged template, source packs, community/imported commands, and external-tool surfaces untouched. No sources/scraping/connectors/platform APIs/ranking/demand-proof/coverage-verification/compliance features.
2. **Four entities reasonable/precise?** Yes. `Savette`/`Aeyde` are distinctive emerging brand names, consistent with the `Khaite`/`Toteme`/`Alaia` `safe_single_word` pattern. Both products use `parent_brand` + narrowed `context_terms`.
3. **Parent-brand/context guarding; bare aliases avoided?** Yes (post-I2). `Symmetry Bag`/`Uma Mary Jane` no longer self-satisfy context; bare `Symmetry`/`Uma` deliberately excluded and regression-guarded.
4. **Tests sufficient?** Yes (post-C1): presence + type mix + name list, parent-brand membership in the brand set, existing broad-alias rejection, new bare-shorthand non-registration, parent-brand acceptance, sample matched names, workflow row counts (lint/import/match `11` to `13`), contract counts plus last-row title, docs table+JSON parity, and boundary tests.
5. **`docs/entity-pack-quality.md` regenerated, not hardcoded?** Yes. Task 3 Step 2 runs `entity-pack-lint` (text + JSON) and replaces counts/table/first-warning from live output; m4 confirms the first warning is stable.
6. **Dependency/lockfile/mirror + review-artifact hygiene preserved?** Yes — `uv --no-config run --frozen`, `UV_NO_CONFIG=1 uv lock --check`, uv.lock mirror-URL scan, `check_release_hygiene.py`, secret scan, review-artifact rg. (m1: harden preamble stripping.)
7. **Critical/Important fixes required?** None. All three prior blockers (C1/I1/I2) are resolved in this revision; no new ones introduced.

---

## Concrete Fixes Required Before Implementation
None blocking. Optional hardening (m1): make the review-capture step proactively exclude process narration rather than relying solely on the post-hoc hygiene grep.

The plan is implementable as written.
