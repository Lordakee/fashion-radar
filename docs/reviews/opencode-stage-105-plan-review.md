I'll review the Stage 105 plan. Let me first read the relevant files and the review protocol.
Let me verify the existing test patterns and confirm the planned files don't already exist.
Let me compare the planned test shape against an existing similar docs guard to confirm convention match, and check the existing review record state.
I've reviewed the spec, plan, target doc, and verified the planned test against existing conventions and the live source. Here are my findings.

---

# Stage 105 Plan Review

## Findings

**No Critical blockers.**
**No Important blockers.**

### Low / Nit (non-blocking)

- **L1 — Phrase-case assertion differs from nearest sibling (consistency note only).** The planned guard uses `assert phrase.casefold() in normalized` (plan line 185), whereas the closest sibling `tests/test_candidate_discovery_docs.py:35` uses `assert phrase in normalized` and relies on pre-lowercased phrases. The Stage 105 form is *more* robust because the Stage 105 phrases legitimately contain capitals ("Entity…", "Scoring's…", "These statuses…"). No change needed; flagging only so reviewers don't read it as an inconsistency bug.
- **L2 — `## What Is Compared` heading itself is not pinned.** `_section` asserts `"## What Is Compared"` is present (`tests/test_trend_deltas_docs.py` plan line 159), so a heading rename would fail loudly — that is the intended drift trip. Acceptable. Just noting the guard protects heading + body via two mechanisms.

### Verified facts supporting approval

- **All 10 planned phrases are present in `docs/trend-deltas.md` within `## What Is Compared` (lines 45–65)** after the plan's whitespace-collapse + casefold normalization. I traced each phrase against the normalized section text, including the line-wrapped ones (`current_mentions…`, `baseline_mentions…`, `Scoring's internal baseline-window…`, `Existing signals…`, `These statuses…`).
- **The documented contract is real, not aspirational.** The internal fields named in the guard exist in source: `current_internal_baseline_mentions` / `baseline_internal_baseline_mentions` at `src/fashion_radar/models/trend.py:40-41` and `src/fashion_radar/trends.py:221-224`. So the guard pins docs to shipped behavior.
- **Section extraction is correctly bounded.** `_section` splits on `"## What Is Compared"` then cuts at the next `"\n## "`, terminating at `"## Manual Signals"` (line 67). None of the 10 phrases appear in the adjacent `## Heat Movers`, `## CLI Usage`, `## Manual Signals`, or `## Dashboard` sections, so there is no cross-section overlap.
- **Test shape matches repo convention exactly** (same `ROOT`, `_normalized`, `_section`, read-helper structure as `tests/test_candidate_discovery_docs.py`).
- **`tests/test_trend_deltas_docs.py` does not yet exist** (clean Create); no name collision in `tests/`.

## Answers to Review Questions

1. **Protects a real boundary without changing product behavior?** Yes. The guard is read-only on `docs/trend-deltas.md`, adds no runtime/scoring/source behavior, and the asserted fields/statuses match `src/fashion_radar/models/trend.py` and `src/fashion_radar/trends.py`.
2. **Phrases present and scoped narrowly enough?** Yes. All 10 are present and uniquely within `## What Is Compared`; `_section` isolates that one section.
3. **Overlap avoided?** Yes. Deliberately excludes `## CLI Usage`, `## Manual Signals`, `## Dashboard`, `## Heat Movers`, scoring implementation, and candidate discovery runtime logic. The only candidate-discovery touch is the *documentation* of snapshot reuse + `candidate_discovery` config thresholding, which is in-scope for the comparison boundary.
4. **Verification sufficient for a docs-only guard?** Yes. Focused run, adjacent `test_cli_docs.py` run, `ruff check`/`format --check`, `git diff --check` (Task 2); full gate adds release hygiene, full `pytest` with proxy unset, repo-wide ruff, `UV_NO_CONFIG=1 uv lock --check`, mirror-URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and staged secret scan (Task 4).

**Recommendation:** Proceed to Task 2. No fixes required before implementation.
