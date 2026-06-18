Let me empirically verify the test passes and confirm the section scope behavior, since this directly supports review questions Q1, Q2, and Q6.
# Stage 108 Plan Review

Reviewed the design, plan, `docs/source-boundaries.md`, and the working-tree test. Empirically confirmed: focused test passes (3 passed), `test_source_boundaries_docs_keep_output_boundary` is defined exactly once, ruff + format clean, all 10 phrases present in the `## Output Boundaries` section.

## Findings

**Critical:** None.

**Important:** None.

**Minor / Nitpick:**

1. **Prose vs. Task 2 wording drift.** The design doc (`...design.md:13,62`) and the plan's Architecture/File Map (`...plan.md:11,34`) describe the change as *"appends/appending one focused pytest test,"* while Task 2 (`...plan.md:145-152`) correctly says the body is already in the working tree, *"Do not append it a second time"* and *"exactly this new test body once."* The descriptive prose describes the net diff vs. HEAD (which is an append), so it is not wrong, but an agent that skims only the header prose could append again and create a duplicate definition. Low risk because Task 2 is explicit; still, recommend aligning the design/plan prose to note the working-tree-pre-stage state (e.g., "the test body is already present in the working tree; this stage verifies and commits it").

2. **Section scope includes the Heat Movers subsection.** `_section("Output Boundaries")` extracts from `## Output Boundaries` up to the next `## ` heading, which includes the `### Heat Movers` paragraph (`docs/source-boundaries.md:326-331`). None of the 10 asserted phrases appear there today, so there is no false positive, and the design's Risks section (`...design.md:79-84`) explicitly avoids heat-mover/trend/scoring/candidate phrases. Acceptable and consistent with the existing two tests — noting only so a future editor understands the extraction boundary.

## Answers To Review Questions

1. **Protects a real section without behavior/docs-text changes?** Yes. `## Output Boundaries` exists (`docs/source-boundaries.md:299-323`) with all asserted phrases. The stage only adds a docs test; no `docs/source-boundaries.md`, `src/`, `scripts/`, or runtime changes.
2. **Phrases present and narrowly scoped?** Yes. All 10 phrases verified present in the section; the `_section` helper limits extraction to the `Output Boundaries` block. (See Minor 2 re: the included `### Heat Movers` sub-block — no leakage today.)
3. **Fits existing pattern?** Yes. `tests/test_source_boundaries_docs.py:66-85` mirrors the existing storage/readme tests exactly: same `_section`/`_read_source_boundaries_doc`/`_normalized` helpers and the same `phrase.casefold() in normalized` loop.
4. **Avoids overlap?** Yes. Docs-only, imports only `pathlib`, no app modules, no SQLite/network/CLI. Asserted phrases are output-wording specific; heat-mover, trend-delta, scoring, and candidate phrases are intentionally left to their own guards per the design Risks section.
5. **Verification sufficient?** Yes. Task 2 runs the focused test, adjacent docs tests (all four referenced files exist), ruff check + format + `git diff --check`; Task 4 runs the full release gate (hygiene, full pytest with proxy unset, repo-wide ruff, lockfile check, mirror-URL scan, `uv.lock`/`pyproject.toml` diff guard, staged secret scan).
6. **Should Task 2 say "verify once" not "append"?** It already does — `...plan.md:145-152` explicitly states the body is already present, *"Do not append it a second time,"* and *"exactly this new test body once."* That wording is correct and sufficient given the current working tree. Only the header prose in the design and plan still uses "append" (see Minor 1).

**Conclusion:** No Critical or Important blockers. The plan is sound, correctly handles the working-tree-pre-stage state in Task 2, and the candidate test already passes clean. Safe to proceed to Task 2 verification and Task 3.
