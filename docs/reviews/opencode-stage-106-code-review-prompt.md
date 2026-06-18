# Stage 106 Code Review Prompt

Review the Stage 106 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 106 adds `tests/test_source_boundaries_docs.py`, a standalone docs drift
guard for the `## Storage Boundaries` section in `docs/source-boundaries.md`.
It asserts that source-boundary storage guidance keeps explicit wording about
conservative local storage, source metadata and local provenance, avoiding full
article text/media/comment redistribution by default, preserving source
attribution, and skipping known paywalled extraction unless permitted metadata is
provided.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-106-source-boundaries-storage-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-106-source-boundaries-storage-docs-plan.md`
- `docs/reviews/opencode-stage-106-plan-review-prompt.md`
- `docs/reviews/opencode-stage-106-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 106 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- collector, robots/fetching, storage schema, dashboard, report, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_architecture_boundary_docs.py tests/test_cli_docs.py tests/test_package_archives.py -q
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 106 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/source-boundaries.md` `## Storage Boundaries` section?
3. Is the new standalone test independent from robots/fetching, output wording,
   README requirements, architecture source-boundary docs, package archive
   checks, and runtime collector/storage behavior?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
