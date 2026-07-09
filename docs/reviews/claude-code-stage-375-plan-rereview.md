## opencode I-1 — Empty-paragraph sidecars treated as non-targets:✅ Resolved

The spec now applies anchor expectations exclusively to renderable sidecars. Architecture section (lines 83–87):

> "Content health evaluates renderable sidecars only: a sidecar must have at least one non-empty saved paragraph… Empty-paragraph sidecars therefore do not create local article content expectations; if no renderable sidecars exist, content health returns `not_applicable`."

Anchor Semantics (lines 127–131) repeats this explicitly. Plan Task 3 Step 2 (lines 271–279) gives the implementation rule. The problematic test `test_content_health_requires_content_section_anchors_for_skipped_articles_when_sections_exist` has been removed from Task 2's required test names and replaced by `test_content_health_ignores_empty_paragraph_sidecars_without_anchor_expectations` and `test_validate_content_health_accepts_not_applicable`. Both directly assert the corrected behavior.

---

## opencode I-2 — Shared HTML id helper exposes both `parse_html_ids` and `html_ids`: ✅ Resolved

The spec now specifies both signatures (Architecture section, lines 89–93):

> "The shared anchor helper should expose both `parse_html_ids(html: str) -> set[str]` for existing cached validation paths and `html_ids(path: Path) -> set[str]` as a path-reading convenience for generated-site diagnostics."

Plan Task 3 Step 1 specifies both functions with correct signatures. Plan Task 5 Step 1 explicitly says to use `parse_html_ids(...)` with `status_integrity`'s existing `html_cache`, preserving the cached-string path and avoiding the repeated-file-read regression that the original plan would have caused.

---

## Remaining Findings

### Critical

None.

### Important

None.

### Minor

**m-A — Product Shape prose does not account for the all-empty-paragraph `not_applicable` case.**
Lines 38–39 say `not_applicable` only when "no saved local article sidecars exist." Architecture says `not_applicable` also when all discovered sidecars are empty-paragraph (no renderable sidecars). A site with one empty-paragraph sidecar on disk would read as `not_applicable` per the architecture, but `missing` per the Product Shape prose. The architecture and implementation guidance are unambiguous; this is a cosmetic inconsistency in the spec's summary section that could confuse a reader auditing the expected behavior. Fix by updating Product Shape to say "When no renderable saved local article sidecars exist, the health status is `not_applicable`."

**m-B — `test_content_health_ignores_empty_paragraph_sidecars_without_anchor_expectations` has no fixture or assertion sketch.**
Every other required test in Task 2 has a concrete fixture and key assertion. This test is directly derivable from the spec (the empty-paragraph sidecar asserts zero counts and all empty tuples across all four missing-anchor fields), but the asymmetry could cause a worker to underspecify it. Informational; spec is clear enough to derive correctly.

**m-C — ops-check `article_count` can diverge from route health `article_count`; undocumented.**
This is opencode's original m-3, still unaddressed. Route health counts safe sidecar stems without parsing JSON; content health parses to read `paragraphs`/`content_sections` and skips malformed files. A sidecar that is a safe stem but has a malformed body is counted by route health and silently excluded by content health. Both payloads expose `article_count` but they measure different things. No note in the spec warns the reader. Low operational risk (the CLI pays distinction is correct), but worth one sentence in the Architecture section.

**m-D — Parallel-worker import dependency is not explicitly sequenced for workers B and C.**
Plan lines 52–59 describe parallel workers but do not explicitly say B and C cannot reach GREEN until Worker A's module exists. The task numbering (3→ 5 → 7) enforces the sequence correctly; the prose could still mislead a controller into running A, B, and C concurrently expecting independent GREEN gates. This is opencode's original m-5, partially addressed (the note about B/C sharing `cli.py` is there) but the A→B/C import dependency is still implicit.

---

**Net verdict:** Both opencode Important findings are resolved and no new Critical or Important issues are present. The spec and plan are clear for implementation.
