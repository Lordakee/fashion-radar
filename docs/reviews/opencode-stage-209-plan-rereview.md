## Stage 209 Plan Rereview

**Verdict: I-1 is resolved. No Critical findings. One new Important finding. One carried Minor.**

### Critical
None.

### Important

**I-2. Task 3, Step 4 docs-guard test is broken as written and will fail.**

Three verifiable defects in the provided snippet:

- **(a) `NameError`.** `_normalized(...)` does not exist in `tests/test_cli_docs.py`. That file's helpers are `_normalized_doc_text(path: Path)` (`tests/test_cli_docs.py:397`) and `_normalized_text(text: str)` (`tests/test_cli_docs.py:401`). The new test errors at runtime, so Task 3 Step 6 (`pytest tests/test_cli_docs.py`) fails before any assertion evaluates.
- **(b) Case mismatch.** `_normalized_text` preserves case (`" ".join(text.split())`), but the test asserts lowercase `"daily brief" in normalized` while the docs use "Daily Brief". The established convention in this file is `_normalized_text(...).casefold()` (e.g. `tests/test_cli_docs.py:619,636,668,852,880`). Without `.casefold()` the assertion fails.
- **(c) Phrase coherence gap.** The guard asserts both `"candidate score-component cues"` and `"mentions, growth, and source diversity"` in all three docs, but the wording guidance in Steps 1–3 doesn't yield those contiguous phrases in each doc: README only produces "score-component cues"; CLI and architecture lack "mentions, growth, and source diversity".

Fix: use `_normalized_doc_text(path).casefold()`, and reconcile Steps 1–3 wording so each doc literally contains the asserted phrases (or relax the guard to match the wording actually requested).

### Minor

**M-2 (carried).** Task 2 Step 2 still re-inlines the entire base summary string verbatim. Acceptable, but couples this stage to base wording. (Optional.)

### I-1 resolution — RESOLVED

Verified against actual code:
- `## Daily Brief` / `## Top Signals` exist at `src/fashion_radar/templates/daily_report.md:7,11`.
- `### Candidate Signals Needing Review` / `### Source Caveats` render via `f"### {section.title}"` at `src/fashion_radar/reports.py:171` (titles set at `reports.py:222,225`).
- The only pre-existing `Score components:` renderings (`reports.py:627,713`) live in the full `## Untracked Candidate Signals` / tracked-entity sections, which the new outer slice (`split("## Daily Brief",1)[1].split("## Top Signals",1)[0]`) excludes — so the assertion can no longer be satisfied by the full report.
- The brief candidate summary today (`reports.py:288-293`) has no `Score components:`, so the sliced assertion is genuinely RED and only turns GREEN after the helper append. Component values `mentions 2.00; growth 0.00; sources 1.00` are already pinned for this exact Fashionista+WWD fixture at `tests/test_reports.py:907`.

The optional docs-guard trap (M-1) is also correctly avoided by not extending `DAILY_BRIEF_REQUIRED_PHRASES`.
