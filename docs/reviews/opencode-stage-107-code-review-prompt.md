# Stage 107 Code Review Prompt

Review the Stage 107 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 107 appends a second docs drift guard to
`tests/test_source_boundaries_docs.py`, scoped to the
`## README Requirements` section in `docs/source-boundaries.md`. It asserts that
public README boundary obligations remain explicit about no full
social-platform coverage, user responsibility for source/robots/API terms,
avoiding account-based default collection, manual import as a local input path
rather than a platform connector, and community handoff check directory reports
as local-only readiness reports.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-107-source-boundaries-readme-requirements-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-107-source-boundaries-readme-requirements-docs-plan.md`
- `docs/reviews/opencode-stage-107-plan-review-prompt.md`
- `docs/reviews/opencode-stage-107-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 107 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `README.md`
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

1. Does the implementation match the Stage 107 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/source-boundaries.md` `## README Requirements` section?
3. Is appending to `tests/test_source_boundaries_docs.py` clean and consistent
   with the Stage 106 helper pattern?
4. Is the new guard independent from full README parity, CLI broad boundary
   checks, architecture source-boundary docs, robots/fetching, package archive
   checks, and runtime collector/storage behavior?
5. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
