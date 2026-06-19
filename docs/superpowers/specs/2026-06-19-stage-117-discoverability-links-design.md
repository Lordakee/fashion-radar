# Stage 117 Discoverability Links Design

## Goal

Make the checked-in community tool directory preflight examples easier to find
from the summary docs that already explain local external/community tool handoff
paths.

## Reviewer Context

This design is for Claude Code / local opencode review before implementation.
Use local review with:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-117-plan-review-prompt.md)" > docs/reviews/opencode-stage-117-plan-review.md
```

## Background

Stage 116 already added the exact checked-in directory preflight commands:

- `examples/community-tool-handoff-directory.example/README.md`
- `docs/community-signal-import.md#external-tool-export-directory-examples`

That stage also added tests that pin the actual CSV/JSON readiness/workflow
commands. Stage 117 should not duplicate those command blocks again. Instead it
should improve discoverability from the summary docs that users are most likely
to open first:

- `README.md`
- `docs/cli-reference.md`
- `docs/first-run.md`
- `docs/github-upload-checklist.md`

This keeps the change docs/tests-only and avoids runtime or schema changes.

## Decision

Add short discoverability pointers in the summary docs that point users to the
existing checked-in example README and the already-pinned command block in
`docs/community-signal-import.md`.

Use the following stable concepts:

- checked-in directory examples
- `examples/community-tool-handoff-directory.example/README.md`
- `external-tool-readiness`
- `external-tool-workflow`
- `generic_community_export`
- `External Community Tool`
- `docs/community-signal-import.md#external-tool-export-directory-examples`

Do not add new runtime behavior. Do not duplicate the exact CSV/JSON command
block in summary docs if a pointer is enough.

## In Scope

- Add discoverability pointers in `README.md`, `docs/cli-reference.md`,
  `docs/first-run.md`, and `docs/github-upload-checklist.md`.
- Add docs drift tests in `tests/test_cli_docs.py` that prove the summary docs
  point to the Stage 116 preflight examples.
- Add Stage 117 review artifacts.

## Out of Scope

- No runtime behavior changes.
- No changes to `src/`.
- No schema changes.
- No dependency or lockfile changes.
- No CI workflow changes.
- No collectors, source packs, entity packs, dashboard, scoring, reports, or
  import-behavior changes.
- No compliance/audit/legal-review product feature.
- No new command blocks beyond what already exists in Stage 116.

## Expected User-Facing Behavior

After implementation, a user reading the summary docs should be able to move
from the high-level local import guidance to the concrete checked-in directory
example and the exact readiness/workflow preflight commands.

The docs should make it obvious that:

- the checked-in directory examples exist,
- they have local `external-tool-readiness` and `external-tool-workflow`
  preflight commands,
- the commands are for `generic_community_export`,
- and the concrete command block lives in
  `docs/community-signal-import.md#external-tool-export-directory-examples`.

## Acceptance Criteria

- `README.md` includes a discoverability pointer from the directory example
  summary block to the checked-in example README or the community import docs.
- `docs/cli-reference.md` includes a discoverability pointer from the local
  import/community handoff section to the checked-in example README or the
  `docs/community-signal-import.md` section.
- `docs/first-run.md` includes a short pointer from the directory handoff
  walkthrough to the checked-in example README and/or the community import docs.
- `docs/github-upload-checklist.md` includes a docs-check item or linked pointer
  that makes the checked-in preflight examples discoverable.
- `tests/test_cli_docs.py` asserts those pointers are present in the relevant
  sections without re-parsing the Stage 116 command blocks.
- All tests, lint, formatting, and release gates remain green.
