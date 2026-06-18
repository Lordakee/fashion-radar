I'll review the Stage 109 plan. Let me read the relevant files in parallel.
Let me verify the adjacent test files referenced in the plan exist and check the project's test/verification conventions.
All 11 phrases match. Let me confirm no test name collision and no existing Quality Boundaries coverage.
Let me check the review artifact naming convention to confirm `opencode-*` prefix is established.
## Stage 109 Plan Review — Findings

**No Critical or Important blockers.** The plan is sound, well-scoped, and matches existing project conventions. Proceed to Task 2.

---

### Severity: None (Info / Verification)

**Q1 — Protects a real section without behavior/docs-text changes?** Yes. `## Quality Boundaries` exists at `docs/source-boundaries.md:333-349`. The plan modifies only `tests/test_source_boundaries_docs.py` and review artifacts; `docs/source-boundaries.md` is explicitly disallowed and untouched.

**Q2 — Phrases present and narrowly scoped?** Yes. I simulated the planned `_section` + `_normalized` logic against the live doc: all 11 phrases match after whitespace-collapse + casefold. The `_section("Quality Boundaries")` helper splits on `## Quality Boundaries` and terminates at the next `\n## ` (i.e. `## README Requirements`), so assertions cannot leak into or from adjacent sections. The heading is a unique h2 with no substring-collision risk.

**Q3 — Fits the existing test pattern?** Yes. The new `test_source_boundaries_docs_keep_quality_boundary` mirrors the three existing tests (`..._keep_storage_boundary`, `..._keep_readme_requirements_boundary`, `..._keep_output_boundary`) exactly: same helpers, same `for phrase in (...): assert phrase.casefold() in normalized` loop, consistent `keep_<section>_boundary` naming. No name collision. No new imports.

**Q4 — Avoids overlap with scoring/candidate/dashboard/report/runtime/archive?** Yes. It is a pure docs-text assertion over one section. No `src/`, no SQLite, no CLI invocation, no dashboard/report rendering, no archive/package-metadata touches. Confirmed via repo-wide grep: no `Quality Boundaries` references exist in `tests/` or `src/` outside this guard.

**Q5 — Verification sufficient?** Yes. Focused run on the target file, an adjacent bundle (`test_scoring_docs`, `test_candidate_discovery_docs`, `test_dashboard_docs`, `test_reports`, `test_cli_docs` — all verified present) to catch cross-cutting regressions, ruff check + format check + `git diff --check`, plus the full release gate (release hygiene, proxy-unset full pytest, ruff, `UV_NO_CONFIG=1 uv lock --check`, mirror-URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene + secret scan).

---

### Minor / Nits (non-blocking)

- **M1 (nit, consistency):** The short list-item phrases (`Source count.`, `Time window.`, etc.) are terse, but this matches the existing `..._keep_output_boundary` style and is exactly the desired drift-guard sensitivity. No change recommended.
- **M2 (nit, plan accuracy):** The File Map lists the spec and plan files as "Create," but they already exist (they are the artifacts under review). This is the standard self-describing plan format used in prior stages; no correction needed — just noting for the implementer.
- **Observation:** Review-artifact naming (`opencode-stage-109-{plan,code}-review{,-prompt}.md`) follows the established `opencode-stage-N-*` convention confirmed for stages 100–108.

---

### Strengths

- Reuses existing helpers verbatim — zero new test infrastructure.
- Scope boundaries in the plan/spec mirror the AGENTS.md constraints (no connectors, scraping, platform APIs, compliance features, etc.).
- Whitespace/case normalization is robust to the source doc's hard line-wraps (verified: phrases spanning line breaks like "...imported local\nsignals." match correctly).

**Verdict: Clear to implement.**
