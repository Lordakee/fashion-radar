I'll review the Stage 111 plan. Let me read the relevant files in parallel.
Now let me read the adjacent test files to understand existing patterns and check for overlaps.
I have reviewed all files. Here are my findings.

## Stage 111 Plan Review — Findings

**Verdict: No Critical or Important blockers.** The plan is sound, well-scoped, and ready to implement. All 5 planned phrases are verifiably present in `docs/dashboard.md`, the test fits the existing pattern, and the scope correctly avoids all disallowed surfaces.

### Findings

**Critical:** None.

**Important:** None.

**Minor / Observations:**

1. **Style inconsistency (cosmetic, non-blocking).** The three existing tests in `tests/test_dashboard_docs.py:17-54` write phrases in lowercase and assert `assert phrase in normalized`. The new test (plan Task 2) follows the `tests/test_scoring_docs.py:37` convention of mixed-case phrases with `assert phrase.casefold() in normalized`. Both are functionally identical because `normalized` is already casefolded. The mixed-case form is arguably more readable. Acceptable as-is, but if you want strict intra-file consistency, write the phrases lowercase and drop `.casefold()`. Not worth blocking on.

2. **Mild phrase redundancy (intentional, acceptable).** Phrase 3 (`Reads candidate signals from the latest report JSON when that file is available.` — pinned from the Behavior list, `docs/dashboard.md:36-37`) and phrase 4 (`The Candidate Signals tab reads the latest generated report JSON.` — pinned from Current Tabs, `docs/dashboard.md:92`) cover the same concept in two sections. This is reasonable broader coverage of two distinct sentences, not duplication.

### Phrase Verification (all confirmed present after `" ".join(text.split()).casefold()`)

| # | Phrase | Source in `docs/dashboard.md` |
|---|--------|-------------------------------|
| 1 | `Invalid or missing trend config shows a concise dashboard warning without creating the data directory or database.` | lines 44-45 |
| 2 | `If the local database has not been initialized or has no retained items, the tab shows an empty-state message without creating the data directory or database.` | lines 82-84 |
| 3 | `Reads candidate signals from the latest report JSON when that file is available.` | lines 36-37 |
| 4 | `The Candidate Signals tab reads the latest generated report JSON.` | line 92 |
| 5 | `If the latest report was generated before the latest collection, local import, or matching run, the tab may be stale until a new report is written.` | lines 94-96 |

List markers (`- `) do not interfere since each phrase is a substring of the normalized stream.

### Answers To Review Questions

1. **Protects wording without behavior/docs-text changes?** Yes. Only `tests/test_dashboard_docs.py` is modified; `docs/dashboard.md`, `src/`, `scripts/`, configs, etc. are explicitly disallowed. No runtime impact.

2. **Phrases present and suitable for the whole-doc normalized pattern?** Yes — all 5 verified above (table). Each is a clean substring of the normalized full document. No section helper is needed; the spec correctly says to avoid adding one absent real ambiguity.

3. **Fits the existing dashboard docs test pattern?** Yes. Reuses `_read_dashboard_doc()` and `_normalized()`, mirrors the phrase-loop + whole-doc assertion of the 3 existing tests, adds no imports, touches no application modules / SQLite / Streamlit / files. Consistent with the spec's test-shape constraints.

4. **Avoids overlap?** Yes. `tests/test_scoring_docs.py` pins `docs/scoring.md` "Limits"; `tests/test_candidate_discovery_docs.py` pins `docs/candidate-discovery.md` "Boundaries"; `tests/test_dashboard.py` is runtime. The new test pins only `docs/dashboard.md` sentences not already covered by the existing dashboard docs tests (existing trend test covers lines 38-43 "readonly"; new test covers the distinct lines 44-45 "invalid config warning"). No phrase collision, no runtime/doc-scope overlap.

5. **Verification commands sufficient?** Yes. Task 2 runs the focused test, an adjacent set (`test_dashboard_docs.py`, `test_dashboard.py`, `test_scoring_docs.py`, `tests/test_candidate_discovery_docs.py`, `test_reports.py`, `tests/test_cli_docs.py`) with proxy vars unset, plus `ruff check`, `ruff format --check`, and `git diff --check`. Task 4 runs the full release gate (release hygiene, full pytest with proxy unset, ruff repo-wide, `UV_NO_CONFIG=1 uv lock --check`, mirror-URL scan, `uv.lock`/`pyproject.toml` diff guard, staged secret scan). The `uv --no-config run --frozen` form is consistent with the mirror-avoidance guidance in `AGENTS.md`.

**Recommendation:** Proceed to Task 2. The Minor style note (`.casefold()` form) can be normalized either way; do not let it block.
