# Stage 98 Code Review

## Findings

**No Critical blockers.**

**No Important blockers.**

### Minor / Informational

**M1 (Informational) — Section marker uses substring, not line-anchored, matching.**
`_section` uses `assert marker in text` with `marker = "## Boundaries"`. This is a substring check rather than line-anchored. It is consistent with the lightweight pattern in sibling stages (90–97), and `## Boundaries` is the unique `##` heading in `docs/candidate-discovery.md`, so there is no false-positive risk today. Already acknowledged as acceptable in the plan review (M1). No change required.

**M2 (Informational) — `_section` does not anchor on a leading newline.**
`text.split("## Boundaries", 1)` would also split on `## Boundaries` appearing mid-line (e.g., inside a code fence). For this doc there is no such occurrence (verified by reading `docs/candidate-discovery.md` end-to-end), and the section is the trailing one so `.split("\n## ", 1)[0]` terminates correctly. Acceptable for a docs-only guard.

**M3 (Informational) — Shared vocabulary also pinned in `tests/test_cli_docs.py`.**
`configured sources and imported local signals` is also present in `tests/test_cli_docs.py` boundary phrase lists for other docs/sections. This is intentional shared project terminology guarding a *different* doc/section, not duplication. No change required.

## Review Questions

**1. Does the implementation match the Stage 98 plan and scope?**
Yes. `tests/test_candidate_discovery_docs.py:1-35` matches the planned test verbatim (`plan.md:121-159`). Git status shows only the 7 allowed untracked files: the test module, the spec, the plan, and the 4 review artifacts. No edits to `docs/candidate-discovery.md`, `src/`, schemas, `pyproject.toml`, `uv.lock`, CI workflows, or `tests/test_cli_docs.py`. No runtime candidate-discovery test changes.

**2. Are the docs assertions present, stable enough, and limited to the `## Boundaries` section?**
Yes. `_section(..., "Boundaries")` extracts only the `## Boundaries` block (`docs/candidate-discovery.md:128-133`); it does not normalize the whole document (compare the broader pattern in `tests/test_entity_pack_quality_docs.py`). All six asserted phrases were verified against the whitespace-collapsed, casefolded boundaries text — all resolve:
- `candidate discovery adds no collectors` ✓
- `no new source types` ✓
- `no external inference calls` ✓
- `no background network reads` ✓
- `configured sources and imported local signals` ✓
- `observed phrases that need review` ✓

The design (`design.md:75-76`) explicitly excludes candidate-window, pruning, imported-candidate, dashboard, demand-proof, platform-coverage, and report wording, so the scope is narrow and the guard will only fire on drift in the no-source-expansion paragraph.

**3. Is the new standalone test independent from broad CLI docs tests and runtime candidate discovery tests?**
Yes. Imports are stdlib-only (`from __future__ import annotations` and `from pathlib import Path`); no application modules, no SQLite, no config, no CLI invocation, no network, no file writes. `tests/test_cli_docs.py` only references `candidate-discovery.md` in `PATH_CONSISTENCY_DOCS` (line 51) and has no candidate-discovery *boundary* assertions — no overlap. Runtime candidate tests (`test_candidate_extraction.py`, `test_candidate_scoring.py`) are untouched and pass alongside the new test (20 passed).

**4. Are there any Critical or Important issues that must be fixed before final verification, commit, and push?**
No. Focused test passes (1 passed), adjacent candidate tests pass (20 passed), `ruff check` clean, `ruff format --check` clean, `git diff --check` clean.

## Verification Re-Run

```
uv --no-config run --frozen pytest tests/test_candidate_discovery_docs.py -q       → 1 passed
uv --no-config run --frozen pytest tests/test_candidate_extraction.py
  tests/test_candidate_scoring.py tests/test_candidate_discovery_docs.py -q         → 20 passed
uv --no-config run --frozen ruff check tests/test_candidate_discovery_docs.py       → All checks passed
uv --no-config run --frozen ruff format --check tests/test_candidate_discovery_docs.py
                                                                                   → 1 file already formatted
git diff --check                                                                   → clean
```

## Verdict

The implementation is acceptable. No Critical or Important blockers. Proceed to Task 4 (full release-gate verification, commit, push).
