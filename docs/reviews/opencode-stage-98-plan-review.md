# Stage 98 Plan Review

## Findings

**No Critical blockers.**

**No Important blockers.**

### Minor / Informational

**M1 (Informational) — Section marker uses substring, not line-anchored, matching.**
`tests/test_candidate_discovery_docs.py` `_section` helper uses
`assert marker in text` with `marker = "## Boundaries"`. This is a substring
check rather than the line-anchored match used by `_markdown_section_exact_heading`
in `tests/test_cli_docs.py:409`. It is consistent with the lightweight pattern in
sibling stages (90–97) and the `## Boundaries` heading is unique in
`docs/candidate-discovery.md`, so it is acceptable. No change required.

**M2 (Informational) — Shared vocabulary phrase also pinned elsewhere.**
`configured sources and imported local signals` is also in
`HEAT_MOVERS_REQUIRED_BOUNDARY_PHRASES` (`tests/test_cli_docs.py:110`) and
`IMPORTED_REVIEW_WORKFLOW_REQUIRED_PHRASES` (`tests/test_cli_docs.py:149`). This
is intentional shared project terminology guarding a *different* doc/section, not
duplication. Each test pins its own markdown. No change required.

**M3 (Informational) — `## Boundaries` is the trailing section.**
`.split("\n## ", 1)[0]` terminates correctly because `## Boundaries` is the last
`##` section in the doc. A future `## ` section appended after it would still be
excluded correctly; a `### ` subsection would be included but is harmless for
these phrases.

## Review Questions

**1. Does the plan protect a real candidate-discovery docs boundary without
changing product behavior?**
Yes. The `## Boundaries` section (`docs/candidate-discovery.md:128-133`) is the
canonical no-source-expansion statement. The stage is docs-test-only: no `src/`,
schemas, CI, dependency, or `uv.lock` changes, and `docs/candidate-discovery.md`
itself is explicitly disallowed from edits. No runtime behavior changes.

**2. Are the planned phrases present and scoped narrowly enough to
`## Boundaries`?**
Yes. All six phrases were verified against the whitespace-collapsed, casefolded
`## Boundaries` section text — all resolve. The `_section` helper extracts only
that section. The design (`...design.md:75-76`) explicitly excludes
candidate-window, pruning, imported-candidate, dashboard, demand-proof,
platform-coverage, and report wording, so the scope is narrow.

**3. Does the plan avoid overlap with recent docs-boundary stages?**
Yes. Target file (`docs/candidate-discovery.md`) and target section
(`## Boundaries`) are distinct from Stage 91 (`data-retention.md`), 94
(`dashboard.md`), 95 (architecture/source-boundaries), 96 (`entity-packs.md`),
and 97 (`entity-pack-quality.md`). `tests/test_cli_docs.py` currently has no
candidate-discovery *boundary* assertions — `candidate-discovery.md` appears only
in `PATH_CONSISTENCY_DOCS` (`tests/test_cli_docs.py:51`). No overlap.

**4. Are the verification commands sufficient for a docs-only guard?**
Yes. Focused test, adjacent candidate tests (`test_candidate_extraction.py`,
`test_candidate_scoring.py` — both exist), `ruff check`, `ruff format --check`,
`git diff --check`, plus the full release gate (release hygiene, full pytest with
`ALL_PROXY` unset, repo-wide ruff, `uv lock --check`, mirror-URL scan,
`uv.lock`/`pyproject.toml` diff guard, staged hygiene, staged secret scan). This
matches Stage 97 and the repository release gate.

## Verdict

The plan is acceptable. No Critical or Important blockers. Proceed to Task 2.
