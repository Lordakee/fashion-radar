# Stage 99 Manual Signal Import Privacy Docs Boundary Design

## Goal

Add a standalone docs drift guard for the `## Privacy Boundary` section in
`docs/manual-signal-import.md` so future edits keep manual imports limited to
conservative local metadata and away from private or sensitive material.

## Scope

Stage 99 is docs-test-only. It creates one focused pytest module that reads the
existing Markdown file, extracts the `## Privacy Boundary` section, normalizes
whitespace and case, and asserts privacy/material boundary phrases.

Allowed changes:

- `tests/test_manual_signal_import_docs.py`
- Stage 99 spec, plan, and review artifacts

Out of scope:

- Runtime manual import behavior
- CLI behavior
- parser, importer, SQLite, report, dashboard, trend, or candidate behavior
- source configuration, collectors, adapters, schemas, dependencies, CI, or
  `uv.lock`
- `docs/manual-signal-import.md` source text
- architecture/source-boundary claims already covered by earlier stages

## Boundary Phrases

The guard should extract only `## Privacy Boundary` and assert these phrases
after whitespace collapse and case-folding:

- `do not import private comments`
- `account ids`
- `cookies`
- `author profiles`
- `follower lists`
- `images, videos`
- `private or sensitive material`
- `keep imported rows limited to conservative metadata`
- `allowed to process and review locally`

These phrases pin the privacy-sensitive import material boundary without
expanding the stage into manual import workflow, candidate review, dashboard,
source acquisition, connector, or platform-collector semantics.

## Test Shape

Use the same lightweight pattern as the recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `docs/manual-signal-import.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a focused phrase loop

The test must not import application modules, open SQLite, parse CSV/JSON, run
the CLI, fetch network resources, or write files.

## Verification

Focused verification should cover the new docs guard, the existing manual signal
import tests, ruff, formatting, and whitespace checks. Full verification before
commit should reuse the repository release gate: release hygiene, full pytest
with proxy vars unset, repo-wide ruff check and format check, lockfile check,
mirror URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and
staged secret scan.

## Risks

The test is phrase-based, so harmless copy edits to the privacy paragraph may
need corresponding test updates. That is acceptable because the section is short
and intentionally high-signal.

Some terms such as `cookies` and `follower lists` appear in broader project
boundary language. Section scoping keeps the guard specific to manual signal
import privacy, and the test intentionally does not pin the final sentence about
manual import being a local input path rather than a connector or platform
collector.
