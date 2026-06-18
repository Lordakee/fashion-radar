# Stage 112 Code Review Prompt

Review the Stage 112 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 112 adds one concise README public non-goals paragraph aligned with
`docs/PROJECT_BRIEF.md` `## Non-Goals For MVP`, then extends
`tests/test_project_brief_docs.py` with a narrow README/project-brief parity
guard.

## Files To Review

- `README.md`
- `tests/test_project_brief_docs.py`
- `docs/superpowers/specs/2026-06-19-stage-112-readme-project-brief-parity-design.md`
- `docs/superpowers/plans/2026-06-19-stage-112-readme-project-brief-parity-plan.md`
- `docs/reviews/opencode-stage-112-plan-review-prompt.md`
- `docs/reviews/opencode-stage-112-plan-review.md`
- `docs/reviews/opencode-stage-112-code-review-prompt.md`

## Scope Constraints

Allowed changes:

- `README.md`
- `tests/test_project_brief_docs.py`
- Stage 112 review artifacts

Disallowed changes:

- `docs/PROJECT_BRIEF.md`
- `docs/source-boundaries.md`
- `docs/dashboard.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- `tests/test_source_boundaries_docs.py`
- runtime behavior, CLI behavior, collectors, source acquisition, connector
  behavior, scraping, browser automation, platform APIs, monitoring,
  scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_project_brief_docs.py -q
uv --no-config run --frozen pytest tests/test_project_brief_docs.py tests/test_cli_docs.py tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen ruff check tests/test_project_brief_docs.py
uv --no-config run --frozen ruff format --check tests/test_project_brief_docs.py
git diff --check
```

## Review Questions

1. Does the README paragraph accurately reflect the project brief MVP non-goals
   without changing product behavior?
2. Does the parity guard prove README coverage while staying narrow and
   maintainable?
3. Does the implementation avoid overlap or conflict with existing README,
   source-boundaries, and CLI docs guards?
4. Are there any Critical or Important issues to fix before commit?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
