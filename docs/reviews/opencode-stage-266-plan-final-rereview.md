## Stage 266 Plan Final Re-Review

### Previously-reported blockers — status
- **I3-recur (docs assertion case mismatch, line 651): FIXED.** Needle now has `.lower()` applied, matching the pattern used on lines 643, 645–647. The dictated `github-upload-checklist.md` wording satisfies it.
- **C1, I1, I2, M1, M2 (from first review): remain FIXED.** Re-confirmed: Task 3 assertions match the `_edition()` fixture's escaped values (`&lt;signals&gt;`, `&#x27;`, `&quot;`); timestamp regex at line 340 is `^\\d{4}-…`; `app_contract.path` drift uses `"was expected"` (line 148); `build_row_one_manifest_payload(edition, app_payload=None)` reuses the render's payload (lines 194–198, 240); README bullet is pinned verbatim (lines 717–719).

### Critical
None.

### Important
None.

### Minor
- **m1** — Lines 648–650 (`"docs/row-one.md" in readme`, `"ROW ONE local static site" in readme`, `"data/manifest.json" in checklist`) use exact-case matches without `.lower()`, unlike the rest of the test. They pass because the dictated Step 5 wording contains those exact substrings, but they're stylistically inconsistent and slightly more fragile. Not a blocker.
- **m2** — `_meta_description`'s 180-char truncation/ellipsis branch is never exercised by the fixtures (carried over, not a blocker).
- **m3** — Lead story is intentionally also kept in the section grid (top story appears twice); acknowledged in the design.

### Verified correct (no blockers)
- Scope is strictly sidecar manifest + presentation/docs. `row-one-app/v1` (`data/edition.json` + `schemas/row-one-app.schema.json`) untouched; no change to collection/matching/scoring/ranking/scheduling/server/cleanup/image-gen/LLM/compliance-review.
- Manifest is small, strict (`additionalProperties: false`, `const` paths/versions, `enum` readiness), non-duplicative, and its drift matrix maps to correct jsonschema messages.
- TDD steps are internally consistent: each "Expected: FAIL" precedes implementation and each "Expected: PASS" follows it; the one-line docs fix makes Step 6 genuinely green.
- CLI flags in the first-run doc (`--config-dir/--data-dir/--reports-dir/--output-dir/--as-of/--latest-only/--dry-run-serve-url`) match the real `row-one` CLI.

### Verdict
**Approved — proceed to implementation.** No Critical or Important blockers remain. The plan is executable end-to-end to a green suite as written.
