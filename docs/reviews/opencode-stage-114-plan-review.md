I'll review the Stage 114 plan. Let me start by reading the review protocol and the key plan/design files in parallel.
Now let me read the test files and docs in parallel to verify the assertions and matcher behavior.
I have the full picture of the plan, design, sample, YAML, tests, and docs. Let me verify the matcher behavior and report/scoring thresholds to confirm the planned rows will actually surface Tory Burch / Pierced Mule / East-West Bags / Office Siren in the report and trend outputs.
Let me read the matcher implementation and locate the report module to confirm confidence/threshold behavior.
Let me confirm there are no tests pinning the docs match-example content, and verify the entity default `match_confidence` clears the 0.5 scoring threshold.
Found docs-content tests. I must verify none of them pin the docs match-example list as exhaustive (which would be a "concrete failing docs contract"). Let me check the watchlist-sample docs test and the two docs test modules.
I have completed a thorough static review of the Stage 114 plan against the actual source, tests, YAML, and docs. Here are my findings.

## Findings

**No Critical blockers. No Important blockers.** The plan is sound and can proceed to implementation.

### Minor / Informational

**M1 — Docs match-list reads as exhaustive but is non-exhaustive by contract (optional, out of scope).**
`docs/first-run.md:181-183` enumerates exactly the 10 original matches under "Expected local matches **include**". After Stage 114 the sample yields 14 matches. The word "include" keeps this contract-correct, and every docs-content test (`test_cli_docs.py:1028`, `test_entity_packs_docs.py`, `test_first_run_docs.py`) uses subset (`in text`) checks — none pin the list as exhaustive or require Tory Burch/East-West Bags/Office Siren to be absent. So docs may correctly stay unchanged. Flagging only because a reader could misread the explicit list as complete; an optional future tidy, not a Stage 114 requirement.

**I1 — "Processed N items" semantics confirmed.**
The `Processed 8 → 11 items` update (`test_watchlist_sample_workflow.py:139`) counts imported signal rows, not matched entities. 8→11 is consistent with adding 3 rows. No action needed.

## Review Question Answers

**Q1 — Do the planned rows exercise existing entities without alias/YAML changes? Yes.**
Verified against `configs/entity-packs/fashion-watchlist.example.yaml` and the matcher in `src/fashion_radar/extract/entities.py`:
- Row 1 contains `Tory Burch Pierced Mule` + `Pierced Mule` (aliases at YAML:162-163) and `Tory Burch` (brand alias YAML:66). The product has `parent_brand: Tory Burch`; since the text contains "Tory Burch", it is accepted via `REASON_PARENT_BRAND` (`entities.py:69-71`). The brand matches directly (multi-word alias, no gate).
- Row 2 contains `east-west bags` and `east west tote` (aliases YAML:188-190) — multi-word, accepted directly via `REASON_ACCEPTED` (`entities.py:76-77`; `_requires_context` only gates single-word/unsafe-common aliases).
- Row 3 contains `office siren` (alias YAML:228) — multi-word, accepted directly.

All four target entities surface with default `match_confidence = 1.0` (`models/entity.py:53`), above `min_match_confidence: 0.5`, so they enter scoring, report, and trends.

**Q2 — Is inserting before the final `Boho Revival` row sufficient? Yes.**
First-row assertion (`test_community_signal_import_contract.py:119`, `rows[0].url == ".../khaite-lotus-bag"`) and last-row assertion (`:123`, `rows[-1].title == "Boho Revival styling watchlist note"`) both remain valid. New rows slot between Mary Jane Shoes and Boho Revival; chronological timestamp order (14:00→14:15→14:30→14:45→15:00) and `collected_at > published_at` are preserved, so no lint warnings are introduced.

**Q3 — Are row-count and expected-entity test updates complete? Yes.**
The plan covers every pinned location:
- `test_community_signal_lint.py:23` `WATCHLIST_EXPECTED_ROWS 8→11`
- `test_community_signal_import_contract.py:21` constant `8→11` **and** `:118` hardcoded `assert len(rows) == 8→11`
- `test_entity_packs.py:150-161` matched_names += 4 entities (subset check)
- `test_watchlist_sample_workflow.py`: `valid_row_count==8→11` (`:81`), `Validated/Imported/Processed 8→11` (`:109,:128,:139`), `EXPECTED_REPORT_ENTITIES` += 4 (`:18-29`); this set feeds both the report subset assert (`:158`) and the trend subset assert (`:178`). Single-mention entities already appear in report/trends today (e.g., `Bella Hadid`), so the new 1-mention rows surface the same way.

**Q4 — Can docs safely remain unchanged? Yes.**
See M1: docs use "include" wording and all docs tests are subset checks. No concrete failing docs contract exists, so docs are correctly out of scope.

**Q5 — Are the focused verification commands sufficient? Yes.**
Task 3's focused pytest selection runs lint + import-contract + matcher + the **full** workflow (lint→pack-lint→dry-run→import→match→report→trends), which is exactly the surface this stage touches. Task 4 adds the two relevant CLI contract commands and ruff. Task 6 adds the complete release gate (full pytest, ruff, `uv lock --check`, mirror-URL scan, secret scan, `git diff --check`). Adequate for the scope.

## Additional Notes

- The plan correctly follows TDD discipline: Task 2 updates tests first and expects them to fail while the CSV still has 8 rows; Task 3 adds the rows and expects green.
- Scope constraints in the review prompt exactly match the design's Allowed/Out-of-scope lists. No disallowed file (YAML, runtime, docs, lockfile, CI) needs touching.
- The three new rows use valid `source_weight` values (1.1, 1.0, 1.0 — within schema `(0, 5]`), `Community Watchlist Sample` / `community` provenance, unique `example.com` URLs, and sanitized local-note language with no account/cookie/platform-scraping content — consistent with the project's free-first/local-first boundary in `AGENTS.md`.

**Recommendation: Approve the plan. Proceed to Task 2.**
