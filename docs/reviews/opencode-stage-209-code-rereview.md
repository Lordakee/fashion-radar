## Stage 209 Code Rereview — Findings

**Verification (all green):** 4 focused tests passed; broader suites 107 passed; full suite **1517 passed**; `ruff check` passed; `ruff format --check` clean.

**Critical:** None.
**Important:** None.
**Minor:** None.

**The prior Minor is resolved.** `test_daily_report_includes_stable_daily_brief_json_shape` (test_reports.py:329-331) now asserts only shape/contract properties — `"Score components:"` cue presence and `high-weight` absence — without pinning numbers. Exact values were correctly hoisted into the dedicated `test_daily_brief_candidate_summary_includes_existing_score_components`, which owns its explicit component inputs.

**No new blockers:** `sections[1]` candidate indexing is sound (verified against the section-order assertion at test_reports.py:309-313 and `kind == "candidate_phrase"` at :321); the markdown render test's exact-value pin is legitimate (it's an integration test building a real report, not a stable-shape test); only `reports.py` changed in source; and all docs/CHANGELOG retain the demand-proof/coverage boundary language with additions scoped strictly to cue phrasing.
