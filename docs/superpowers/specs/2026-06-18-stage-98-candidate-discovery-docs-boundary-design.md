# Stage 98 Candidate Discovery Docs Boundary Design

## Goal

Add a standalone docs drift guard for the `## Boundaries` section in
`docs/candidate-discovery.md` so future edits keep candidate discovery framed as
a local review aid, not a source-expansion or background-network feature.

## Scope

Stage 98 is docs-test-only. It creates one focused pytest module that reads the
existing Markdown file and asserts stable normalized phrases from the
`## Boundaries` section.

Allowed changes:

- `tests/test_candidate_discovery_docs.py`
- Stage 98 spec, plan, and review artifacts

Out of scope:

- Runtime candidate discovery behavior
- CLI behavior
- report or dashboard rendering
- source configuration, collectors, adapters, schemas, dependencies, CI, or
  `uv.lock`
- retention/pruning semantics from the `## Windows` section
- imported/community candidate workflow sections

## Boundary Phrases

The guard should extract only the `## Boundaries` section and assert these
phrases after whitespace collapse and case-folding:

- `candidate discovery adds no collectors`
- `no new source types`
- `no external inference calls`
- `no background network reads`
- `configured sources and imported local signals`
- `observed phrases that need review`

These phrases pin the no-source-expansion boundary without duplicating Stage 91
data-retention wording or imported/community candidate workflow coverage.

## Test Shape

Use the same lightweight pattern as the recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `docs/candidate-discovery.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a small phrase loop

The test must not import application modules, open SQLite, parse config, execute
the CLI, fetch network resources, or write files.

## Verification

Focused verification should cover the new docs guard, adjacent candidate tests,
ruff, formatting, and whitespace checks. Full verification before commit should
reuse the repository release gate: release hygiene, full pytest with proxy vars
unset, repo-wide ruff check and format check, lockfile check, mirror URL scan,
`uv.lock`/`pyproject.toml` diff guard, staged hygiene, and staged secret scan.

## Risks

The test is phrase-based, so legitimate copy edits to the boundary sentence may
need corresponding test updates. Section scoping keeps this acceptable because
the purpose is to detect semantic drift in a high-risk boundary paragraph.

The doc already has broader references in `tests/test_cli_docs.py`; this stage
adds a narrower guard for source-expansion boundaries only. It intentionally
does not assert candidate-window, pruning, imported-candidate, dashboard,
demand-proof, platform-coverage, or report wording.
