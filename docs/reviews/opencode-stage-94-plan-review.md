I'll review the Stage 94 design and plan. Let me start by reading all the relevant files in parallel.
Let me verify one critical concern by searching for the specific phrase in the doc:
# Stage 94 Plan Review Findings

## Critical

### C1. Test asserts a phrase that does not exist in `docs/dashboard.md`

**Location:** `docs/superpowers/plans/2026-06-18-stage-94-dashboard-docs-boundary-plan.md:79`

The planned `test_dashboard_docs_keep_trend_readonly_boundary` asserts:

```python
"do not initialize schema, migrate a database, create trend tables",
```

This phrase is **not present** in `docs/dashboard.md`. The only related text is at `docs/dashboard.md:42-43`:

> "Trend reads verify schema read-only and do not initialize, migrate, or write trend tables."

`rg` confirms no occurrence of `initialize schema`, `migrate a database`, or `create trend tables` anywhere in the doc. Since the scope forbids modifying `docs/dashboard.md`, this assertion will fail at implementation time.

The design (`docs/superpowers/specs/2026-06-18-stage-94-dashboard-docs-boundary-design.md:36-39`) only requires pinning the existing "trend reads verifying schema read-only and not initializing, migrating, or writing trend tables" boundary — which the plan already covers with two valid phrases on plan lines 77-78. The third phrase on line 79 is not required by the design and is not in the doc.

**Fix:** Remove line 79 (`"do not initialize schema, migrate a database, create trend tables",`) from the planned test. Do not add the phrase to the doc (that would violate scope).

---

## No Other Critical Or Important Blockers

## Review Question Answers

**1. Are the proposed docs assertions present in current `docs/dashboard.md`?**
All 17 phrases pass **except** C1 above. Verified each against `docs/dashboard.md`:
- L3-4: "optional Streamlit app for inspecting local Fashion Radar state" ✓
- L28: "Reads local SQLite/report state" ✓
- L30-33: collect/match/generate/network boundaries ✓
- L38-39: "Computes the Trend Deltas tab from existing local SQLite state … not from external services" ✓
- L42-43: "Trend reads verify schema read-only and do not initialize, migrate, or write trend tables" ✓
- L27: "Defaults to \`127.0.0.1:8501\`" ✓
- L60: "has no authentication layer" / "intended for local use" ✓
- L62: "Do not bind \`--host 0.0.0.0\`" ✓
- L55-56: "no scraping, no browser automation, no platform APIs … no account or cookie work" ✓

**2. Are the phrases stable enough and not overly broad?**
Yes. Phrases are sentence-specific boundary statements. Backtick literals (`\`127.0.0.1:8501\``, `\`--host 0.0.0.0\``) are preserved through `_normalized` (which only splits whitespace + casefolds), so matching is exact. "intended for local use" is mildly broad but unique within this doc.

**3. Is the scope safely test-only and independent from Stages 91, 92, 93?**
Yes. Plan only creates `tests/test_dashboard_docs.py` + review artifacts under `docs/reviews/`. Imports limited to `pathlib.Path` (satisfies design line 43-44: no Streamlit/dashboard/app/SQLite imports). No reference to or dependency on other stages. Does not touch `tests/test_cli_docs.py`, `tests/test_dashboard.py`, `src/`, schemas, `uv.lock`, CI, or `docs/dashboard.md`.

**4. Are the verification commands sufficient?**
Yes. Task 3 runs focused new test + combined dashboard/docs run + Ruff check/format. Task 4 runs full pytest, Ruff, lockfile check, hygiene script, and staged-file guards. Matches AGENTS.md lockfile patterns (`UV_NO_CONFIG=1 uv lock --check`, mirror-leak `rg`).

**5. Critical/Important blockers before implementation?**
One Critical: **C1**. Fix by removing the extra invalid phrase. After that fix, no Critical or Important blockers remain.

---

## Minor Notes (Non-blocking)

- Plan Task 1/3 invoke `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` while `AGENTS.md` suggests `claude --effort max`. This matches the tool actually running this review, so it is consistent in practice.
- The design concept #4 ("Trend Deltas using existing local SQLite state **and local config**") is pinned without the "local config" fragment; the doc's "and local scoring config" wording is not asserted. Acceptable — the boundary essential ("existing local SQLite state" + "not from external services") is covered.
