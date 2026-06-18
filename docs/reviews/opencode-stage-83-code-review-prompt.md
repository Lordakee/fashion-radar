# Stage 83 Code Review Prompt

Review the Stage 83 changes in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Stage 83 should add a short GitHub upload checklist reminder that points to
the mirror-lockfile recovery section and add docs drift coverage for that
reminder.

## Intended Scope

Allowed changed files:

- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`
- Stage 83 spec/plan/review artifacts under `docs/superpowers/` and
  `docs/reviews/`

Out of scope:

- Runtime code under `src/`
- Dependency manifests
- `uv.lock`
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- CI behavior

## Requirements

- The checklist reminder must appear immediately after the mirror-marker
  `rg ... uv.lock` block and before `Historical boundary checks`.
- The reminder must be one or two sentences and only point to the recovery
  path; it must not duplicate recovery commands.
- The link must be sibling-relative:
  `[Recover A Mirror-Rewritten Lockfile](dependency-mirrors.md#recover-a-mirror-rewritten-lockfile)`.
- `tests/test_cli_docs.py` must include a dedicated drift test named
  `test_upload_checklist_mentions_mirror_lockfile_recovery`.
- The test must assert these whole-file substrings in `docs/github-upload-checklist.md`:
  - `Recover A Mirror-Rewritten Lockfile`
  - `dependency-mirrors.md#recover-a-mirror-rewritten-lockfile`
  - `If \`uv.lock\` was changed by mirror-backed local operations before upload`

## Review Instructions

Return findings first, ordered by severity. Classify each finding as Critical,
Important, or Minor. Include file and line references. If there are no
Critical or Important findings, say that explicitly.

Do not request broader product, compliance, scraping, social-platform, or
runtime changes; this node is docs/test-only.
