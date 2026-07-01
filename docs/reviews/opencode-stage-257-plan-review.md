# Stage 257 Plan Review

**Reviewer:** opencode (GLM 5.2 max) — fallback per `docs/REVIEW_PROTOCOL.md`
(Claude Code plan review timed out twice; see
`docs/reviews/claude-code-stage-257-plan-review.md`).

## Verdict: ACCEPTABLE WITH REQUIRED CHANGES

The plan is sound in direction and correctly scoped (no connectors/scraping/deps). It correctly identifies the two real gaps. But the central correctness defect in the current diff is under-specified in step 3, and two promised coverage items (package, docs) need to be made explicit before implementation.

Claude Code concerns to incorporate: **none** (review was unavailable; no body captured).

---

## Required plan changes before implementation

### CRITICAL — recent-item windowing must be concretely specified (plan step 3)

The plan's Architecture/step 3 say to scope recent items to `as_of - scoring.current_window_days < collected_at <= as_of`, but the **current uncommitted** `write_daily_report_files()` diff (`src/fashion_radar/workflows.py:70-86`) selects the latest 50 items by `collected_at desc` with **no date bound at all** — items newer than `as_of` and items far outside the window both leak in. This is the core correctness defect and must be fixed, mirroring the existing pattern in `src/fashion_radar/reports.py:455-497` (`_representative_items`).

Step 3 should explicitly require:
1. Compute `window_start = as_of_utc - timedelta(days=scoring.current_window_days)`.
2. Add a WHERE clause `window_start < items_table.c.collected_at <= as_of_utc`.
3. Add `items_table.c.collected_at` to the SELECT list so the `ORDER BY collected_at.desc()` is self-contained and consistent with `_representative_items`.

The plan's step-2 integration tests already assert the bounds ("Excludes items newer than `as_of`", "Excludes items outside `scoring.current_window_days`"), so the tests will currently **fail** against the diff until step 3 lands — confirm the plan ships them together.

### IMPORTANT — package/archive expectation must be concrete (plan step 4)

The plan promises "package-checked" coverage and "mention the pack in ... package/archive expectations," but `tests/test_package_archives.py:51-90` (`SDIST_FILES`) only lists `configs/entity-packs/fashion-watchlist.example.yaml`. If the real sdist build globs `configs/entity-packs/*.example.yaml`, the synthetic fixture will silently diverge. Step 4 should explicitly require:
- Add `configs/entity-packs/buyer-brands.example.yaml` to `SDIST_FILES` in `tests/test_package_archives.py` (parallel to the watchlist entry), and
- Confirm via `uv build --sdist` (or the existing packaging path) that the real archive includes it.

This keeps "package-checked" honest and stays within the package-gap scope.

### IMPORTANT — docs edit must preserve existing boundary assertions (plan step 4)

"Mention the pack in entity-pack docs" risks regressing `tests/test_entity_packs_docs.py` and `tests/test_entity_packs.py:252-255` (`test_entity_pack_docs_do_not_introduce_collect_workflow` asserts `"fashion-radar collect" not in text`). Step 4 should explicitly require the buyer-brands mention in `docs/entity-packs.md` to reuse the existing "optional local configuration template" framing and keep all current boundary phrases intact. Flag this as a test-gate, not a free-text edit.

---

## Optional nits

- **Inline imports / style:** the current diff puts `from sqlalchemy import select` and `from fashion_radar.db.schema import items` inside the function body (`workflows.py:72-74`); hoist to top-level to match the file's convention. Also `str(item.get("url", ""))` coerces a NULL url to the literal `"None"` before `_safe_url` rejects it — prefer `item.get("url") or ""` (`html_report.py:185`).
- **Lint expectation for buyer-brands:** the pack will likely emit lint *warnings* (e.g. `ungated_alias_with_context_terms` for multi-word aliases on entities that also define `context_terms`) but zero *errors*. The new lint test should assert `result.error_count == 0`, not `result.ok is True`, to avoid over-constraining. (I scanned every alias: each single-word/common alias is either `safe_single_word`+reason or guarded by entity-level `context_terms`, so it should clear `EntityConfig.validate_aliases`.)
- **Shared truncation helper:** `_render_recent_items` (`html_report.py:188`) duplicates the `[:N] + "..."` pattern from `_render_representative_items` (`reports.py`-adjacent); a tiny helper would reduce drift. Low priority.
- **Lock the contract:** add an assertion that the HTML section heading is exactly `Latest Collected News` so the public-facing label is pinned.

No dependency/`uv.lock`/scope-boundary issues found.
