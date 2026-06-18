I'll review the Stage 105 implementation. Let me start by examining the relevant files in parallel.
Now let me read the actual docs file and check the review artifacts and git status.
Now let me run the verification commands and check the source files referenced in the plan review.
Let me verify the sibling test pattern and confirm the scope boundaries by checking the actual scope of changes.
## Stage 105 Code Review

All verification passes: focused test `1 passed`, combined docs tests `60 passed`, ruff check/format clean, no whitespace errors, no tracked files modified (only the 7 Stage 105 untracked files exist).

### Findings

**No Critical blockers.**
**No Important blockers.**

#### Low / Nit (non-blocking)

- **L1 — Test body differs cosmetically from plan's literal snippet.** The plan (plan.md:172-175, 182-183) showed two phrases as two-line implicit string concatenations; the shipped file (`tests/test_trend_deltas_docs.py:32-33`) uses single-line literals for the shorter ones. Runtime behavior is identical (Python adjacent-literal concatenation), and the shipped form is what `ruff format` produces. No action needed.
- **L2 — Per-phrase `casefold()` differs from sibling convention.** Stage 105 uses `assert phrase.casefold() in normalized` (`tests/test_trend_deltas_docs.py:42`) while `tests/test_candidate_discovery_docs.py:35` uses pre-lowered phrases with `assert phrase in normalized`. Stage 105's form is intentional and more robust because its phrases legitimately contain capitals ("Entity…", "Scoring's…", "These statuses…"). Already acknowledged in the plan review (L1). No action.

### Verified facts supporting approval

- **All 10 asserted phrases are present in `docs/trend-deltas.md:45-65`** within `## What Is Compared`, after whitespace-collapse + casefold. I traced each phrase against the normalized section, including the line-wrapped ones (current/baseline mentions, internal baseline fields, rising/cooling/stable labels, market-wide rankings).
- **Section boundary is correct.** `_section` splits on `"## What Is Compared"` then cuts at the next `"\n## "`, terminating at `## Manual Signals` (`docs/trend-deltas.md:67`). None of the 10 phrases appear in adjacent `## Heat Movers`, `## CLI Usage`, `## Manual Signals`, or `## Dashboard` sections, so there is no cross-section overlap.
- **Heading rename trips loudly.** `assert marker in text` (`tests/test_trend_deltas_docs.py:19`) protects the heading itself, not just the body.
- **Stable against reflow.** `_normalized` collapses all whitespace via `" ".join(text.split())`, so future line-wrapping edits in the doc won't break the guard; only substantive wording changes will.
- **Independence confirmed.** The module imports only `pathlib` (`tests/test_trend_deltas_docs.py:3`), reads one local Markdown file, and has no CLI, SQLite, network, scoring, candidate-discovery, dashboard, or application-module dependencies. Pure docs text check.
- **Scope clean.** `git status` shows only the 7 Stage 105 untracked files (test + 4 review artifacts + spec + plan); no tracked modifications. `docs/trend-deltas.md`, `src/`, `scripts/`, `examples/`, configs, schemas, `uv.lock`, CI, and `tests/test_cli_docs.py` are untouched.
- **Convention match.** Test shape mirrors `tests/test_candidate_discovery_docs.py` exactly (same `ROOT`, `_normalized`, `_section`, read-helper, single test function with phrase loop).

### Answers to Review Questions

1. **Matches plan and scope?** Yes. Implementation matches plan Task 2 exactly (modulo ruff-format cosmetic differences in string literal layout). Scope is docs-test-only; all disallowed paths are untouched.
2. **Assertions present, stable, scoped to `## What Is Compared`?** Yes. All 10 phrases present, bounded to that one section, robust to whitespace reflow, and trip on heading rename or wording drift.
3. **Independent of CLI/scoring/candidate discovery/dashboard?** Yes. Stdlib-only, single doc read, no runtime/application imports or side effects.
4. **Critical/Important issues before commit/push?** None.

**Recommendation:** Proceed to Task 4 (full verification, commit, push). No fixes required.
