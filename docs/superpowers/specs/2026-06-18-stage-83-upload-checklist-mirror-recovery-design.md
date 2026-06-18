# Stage 83 Upload Checklist Mirror Recovery Design

## Goal

Add a short GitHub upload checklist reminder that points contributors to the
mirror-lockfile recovery path before upload, so a locally mirror-rewritten
`uv.lock` is less likely to be missed during staging or publish prep.

## Scope

This is a docs/test-only node. It changes `docs/github-upload-checklist.md`,
the docs drift tests, and stage-local review artifacts only. It does not touch
runtime code, dependencies, CI, or lockfiles.

## Design

- Add a short recovery reminder to `docs/github-upload-checklist.md` near the
  existing public-lockfile and mirror checks, immediately after the current
  mirror-marker `rg ... uv.lock` block and before `Historical boundary checks`.
- The reminder should point to the sibling-relative
  `dependency-mirrors.md#recover-a-mirror-rewritten-lockfile` anchor and name
  the `Recover A Mirror-Rewritten Lockfile` section.
- Keep it short and operational: one or two sentences that tell contributors to
  restore a locally mirror-rewritten `uv.lock` before upload and use the linked
  recovery guidance. Do not duplicate the recovery commands already documented
  in `docs/dependency-mirrors.md`.
- Add a test in `tests/test_cli_docs.py` that pins the new checklist note, the
  section-name literal, and the sibling-relative anchor. The test should use
  whole-file substring presence because the reminder is new and short; do not
  scope it to the broad `## Before Upload` section.

## Non-Goals

- Do not edit `README.md`, `docs/dependency-mirrors.md`, or runtime code in
  this node unless a scoped test exposes a real mismatch.
- Do not modify `uv.lock` or dependency manifests.
- Do not add connector, scraper, platform API, ranking, or demand-proof
  behavior.

## Verification

- Focused docs test for the upload checklist reminder.
- Full `tests/test_cli_docs.py`.
- `ruff check` and `ruff format --check` for the changed test file.
- `git diff --check` for changed files.
- Full pytest, release hygiene, and public lock verification before commit.
