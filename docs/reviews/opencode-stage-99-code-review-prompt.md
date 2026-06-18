# Stage 99 Code Review Prompt

Review the Stage 99 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 99 adds `tests/test_manual_signal_import_docs.py`, a standalone docs drift
guard for the `## Privacy Boundary` section in `docs/manual-signal-import.md`.
It asserts that manual import docs prohibit private comments, account IDs,
cookies, author profiles, follower lists, images/videos, and other private or
sensitive material, and keep imported rows limited to conservative metadata that
the user is allowed to process and review locally.

## Files To Review

- `tests/test_manual_signal_import_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-99-manual-signal-import-privacy-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-99-plan-review-prompt.md`
- `docs/reviews/opencode-stage-99-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_manual_signal_import_docs.py`
- Stage 99 review artifacts

Disallowed changes:

- `docs/manual-signal-import.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime manual import tests
- data-retention, dashboard, architecture/source-boundary, source-pack,
  entity-pack, entity-pack-quality, candidate-discovery, or imported-candidate
  behavior

Do not propose adding privacy-compliance, audit, legal-review, runtime
validation, connector, platform collector, source acquisition, candidate review,
or dashboard/report behavior.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_manual_signal_import_docs.py -q
uv --no-config run --frozen pytest tests/test_manual_signal_import.py tests/test_manual_signal_import_docs.py -q
uv --no-config run --frozen ruff check tests/test_manual_signal_import_docs.py
uv --no-config run --frozen ruff format --check tests/test_manual_signal_import_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 99 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the manual
   signal import `## Privacy Boundary` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   manual import tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
