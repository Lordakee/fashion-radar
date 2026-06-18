# Stage 81 External Import Doc Test Tightening Design

## Goal

Tighten the Stage 80 documentation drift tests so the external tool import
boundary language is verified inside the actual Stage 80 README and CLI
reference guidance, not only somewhere in the full document.

## Scope

This is a docs-test quality node. It changes tests and stage-local review
artifacts only. It does not change runtime code, public documentation wording,
dependencies, lockfiles, source collection behavior, connectors, scraping,
platform APIs, ranking, or demand proof.

## Current Problem

The Stage 80 README and CLI reference tests confirm unique route anchors in the
right places, but some boundary phrases are checked against the normalized full
document. Because those phrases also appear in older text, future edits could
delete the new section's boundary sentence while the test still passes.

## Design

- Keep the Stage 80 README heading and CLI section boundaries unchanged.
- In the README test, extract the exact `### External Tool Import Path`
  Markdown section with a heading-aware helper that stops at the next heading
  of the same or higher level. Assert all route terms and all boundary terms
  within that extracted section. Do not split on `external-tool-readiness`
  because that command appears inside the route string before the boundary
  sentence.
- In the CLI reference test, continue extracting text under
  `## Local Import And Community Handoff` before `Print adapter registry
  examples:`. Assert boundary terms against the normalized extracted section,
  not the normalized full document.
- Keep the existing community import roadmap test as-is because it already
  scopes phase and command assertions to the roadmap section and the roadmap
  itself contains the full boundary sentence.

## Non-Goals

- Do not add new CLI behavior.
- Do not edit source files under `src/`.
- Do not edit README or CLI reference prose unless a scoped test reveals a real
  mismatch.
- Do not touch `uv.lock`; the local mirror rewrite remains unstaged.

## Verification

- Run the tightened focused docs tests.
- Run all `tests/test_cli_docs.py`.
- Run `ruff check` and `ruff format --check` on `tests/test_cli_docs.py`.
- Run `git diff --check` for changed files.
- Run the repository's release hygiene and full pytest/ruff checks before
  commit.
