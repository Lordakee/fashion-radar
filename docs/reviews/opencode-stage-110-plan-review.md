I'll review the Stage 110 plan. Let me start by reading the relevant files and the review protocol.
Let me verify the adjacent test files referenced in the verification commands actually exist, and confirm the section scoping behavior.
Let me simulate the exact section extraction and phrase matching to confirm the planned test would pass.
# Stage 110 Plan Review

## Findings (ordered by severity)

**Critical:** None.
**Important:** None.
**Minor / informational (non-blocking):**

- **M1 (nit, doc-only):** The design rationale says the guard "avoids generic fetch-policy bullets already covered more directly by runtime collector tests," but two asserted phrases (`Use source-specific rate limits where configured.` and `Record skipped URLs with reasons.`) are arguably on the generic side. This is a defensible judgment call (they pin boundary intent, not HTTP hygiene) and does not need changing — flagging only for transparency.
- **M2 (nit):** The deliberately-excluded numeric throttle (`near 1 request per second`) is the one sentence most likely to drift; the design explicitly justifies not freezing it. Reasonable, but worth noting that a future docs edit to that sentence will pass silently with no guard at all.

## Answers to review questions

1. **Protects real section without behavior/docs change?** Yes. `## Robots And Fetching` exists at `docs/source-boundaries.md:279`. The plan only adds a read-only pytest guard; allowed/disallowed lists correctly exclude `docs/source-boundaries.md`, `src/`, configs, `uv.lock`, and runtime tests (`tests/test_collectors_robots.py`, `tests/test_cli_docs.py`).

2. **Phrases present and narrowly scoped?** Yes. All 7 asserted phrases exist verbatim in the section (verified by simulation — all `OK`). The `_section` helper (`tests/test_source_boundaries_docs.py:17`) splits on `## Robots And Fetching` then on `\n## `, correctly stopping before `## Output Boundaries` (line 299). The `\n## ` delimiter does not false-match `###` subheadings.

3. **Fits existing test pattern?** Yes. The planned `test_source_boundaries_docs_keep_robots_and_fetching_boundary` reuses `_read_source_boundaries_doc`, `_normalized`, `_section`, and the `phrase.casefold() in normalized` loop identical to the 4 existing `*_boundary` tests. Naming convention matches.

4. **Avoids overlap with runtime/HTTP/GDELT/archive/runtime code?** Yes. `tests/test_collectors_robots.py` verifies `RobotsPolicyChecker` runtime behavior; the new test pins documentation wording only — complementary, not overlapping. Design doc (`...design.md:80-85`) explicitly addresses this. No runtime imports or execution.

5. **Verification commands sufficient?** Yes. Focused test, adjacent docs/runtime-reference tests (all 6 referenced files confirmed to exist), `ruff check` + `ruff format --check`, `git diff --check`, plus full release gate in Task 4.

Environment note observed during implementation: adjacent collector tests may
need `env -u ALL_PROXY -u all_proxy` in shells where SOCKS proxy variables are
set but `socksio` is unavailable. That is an environment issue, not a Stage 110
scope issue, and it matches the repository's existing full-pytest release-gate
pattern.

## Verdict

Plan is acceptable as written. No Critical or Important blockers — proceed to Task 2.
