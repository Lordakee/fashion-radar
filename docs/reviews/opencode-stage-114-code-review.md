I'll review the Stage 114 implementation. Let me start by reading the key files in parallel.
Let me read the remaining review files and the entity pack YAML to verify the entities exist.
I have all the data needed. Let me verify there are no other references to the watchlist sample or row-count assertions that might have been missed, and confirm the matcher behavior for the new rows.
I have verified the implementation against the CSV, YAML entity pack, all four test files, and cross-referenced other references to the watchlist sample across the repo. Here is my review.

---

## Stage 114 Code Review

**No Critical blockers. No Important blockers.** The implementation is correct, safe, and consistent with the design and plan. It can proceed to the release gate (Task 6).

### Findings (Minor / Informational only)

**M1 — `assert len(rows) == 11` uses a literal where a sibling line uses the constant (informational).**
`tests/test_community_signal_import_contract.py:118` hardcodes `11` while `:21` defines `WATCHLIST_EXPECTED_ROWS = 11` and `:299` uses the constant. This matches the plan's explicit instruction (Task 2 pins the literal) and is consistent with the file's existing style for the default example (`:55`, `:81`, `:106` all use `== 2` literals). No action required; flagging only for future tidiness.

**I1 — `docs/first-run.md` match list reads as exhaustive but is contract-non-exhaustive (already known, out of scope).**
Already raised as M1 in the plan review. The "include" wording and subset-style docs tests keep this contract-correct, so docs correctly remain unchanged per the design. No Stage 114 action.

**I2 — Full release gate not yet executed (by design).**
The verification run covers the four in-scope test files, ruff, and the two relevant CLI contract commands. The full pytest release gate, `uv lock --check`, mirror-URL scan, and secret scan are Task 6 (after code review). Not a code-review blocker.

### Review-Focus Answers

**1. Are the added rows safe synthetic local-sample rows? Yes.**
All three new rows (`community-signals.watchlist.example.csv:9-11`) use `https://example.com/` URLs (IANA-reserved), `Community Watchlist Sample` source, `community` platform, sanitized local-note summaries with no usernames, account names, raw comments, cookies, or platform-scraping claims. `source_weight` values (1.1, 1.0, 1.0) are within the schema's `(0, 5]` bound. `collected_at` is strictly after `published_at` for each row, and timestamps stay monotonically ordered across the whole file (14:00 → 14:15 → 14:30 → 14:45 → 15:00), so no new lint warnings are introduced.

**2. Do they exercise existing entities without YAML/runtime changes? Yes.**
Verified against `configs/entity-packs/fashion-watchlist.example.yaml` (unchanged, 230 lines):
- Row 9 contains `Tory Burch Pierced Mule`, `Pierced Mule` (YAML:162-163) and `Tory Burch` (YAML:66) — product accepts via `parent_brand: Tory Burch`; brand matches directly as a multi-word alias.
- Row 10 contains `east-west bags` and `east west tote` (YAML:189-190) — multi-word aliases, accepted directly.
- Row 11 contains `office siren` (YAML:228) — multi-word alias, accepted directly.

No entity YAML, matcher, importer, report, trend, dashboard, CLI, or schema file was modified.

**3. Are all row-count and expected-match tests updated consistently? Yes.**
Repo-wide grep confirms every pinned watchlist row count and output string is updated, and no other test pins these values:
- `tests/test_community_signal_lint.py:23,79-82` — `WATCHLIST_EXPECTED_ROWS = 11` and four dependent asserts.
- `tests/test_community_signal_import_contract.py:21,118,299` — constant, `len(rows) == 11`, and `Validated {WATCHLIST_EXPECTED_ROWS}`.
- `tests/test_entity_packs.py:150-165` — all four new entities added to the matched-names subset check.
- `tests/test_watchlist_sample_workflow.py:18-33,85,113,132,143,162,181` — `EXPECTED_REPORT_ENTITIES` extended and `valid_row_count`, `Validated/Imported/Processed 11` strings updated; the entity set feeds both the report and trend subset asserts.

Other references (`tests/test_cli_docs.py`, `tests/test_package_archives.py`, `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py`) reference only the *path* or the *default* sample's "Validated 2" output — none pin the watchlist row count.

**4. Does Boho Revival remain the final row? Yes.**
`community-signals.watchlist.example.csv:12` is still the `boho-revival` row. The three new rows are inserted at lines 9-11, between `mary-jane-shoes` (line 8) and `boho-revival` (line 12). First-row (`khaite-lotus-bag`) and last-row (`Boho Revival styling watchlist note`) assertions at `test_community_signal_import_contract.py:119,123` both still hold.

**5. Are there any release-blocking regressions or missing tests? No.**
The change is isolated to sample data plus the four pinning tests, all of which were updated in lockstep. The four in-scope test files, ruff check/format, and the two CLI contract commands (entity-pack-lint, community-signal-lint) were run clean per the verification block. No regression surface exists outside these files because no runtime/YAML/schema behavior changed. The remaining full-suite release gate is the next staged step (Task 6).

**Recommendation: Approve. Proceed to Task 6 (full release gate and commit).**
