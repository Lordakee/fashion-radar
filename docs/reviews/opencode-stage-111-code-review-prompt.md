# Stage 111 Code Review Prompt

Review the Stage 111 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 111 appends a docs drift guard to `tests/test_dashboard_docs.py`, scoped
to warning, empty-state, and stale-report wording in `docs/dashboard.md`. It
asserts that dashboard docs keep local-state warning expectations and Candidate
Signals latest-report/staleness expectations explicit.

## Files To Review

- `tests/test_dashboard_docs.py`
- `docs/superpowers/specs/2026-06-19-stage-111-dashboard-warning-staleness-docs-design.md`
- `docs/superpowers/plans/2026-06-19-stage-111-dashboard-warning-staleness-docs-plan.md`
- `docs/reviews/opencode-stage-111-plan-review-prompt.md`
- `docs/reviews/opencode-stage-111-plan-review.md`
- `docs/reviews/opencode-stage-111-code-review-prompt.md`

## Scope Constraints

Allowed changes:

- `tests/test_dashboard_docs.py`
- Stage 111 review artifacts

Disallowed changes:

- `docs/dashboard.md`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_dashboard.py`
- `tests/test_scoring_docs.py`
- `tests/test_candidate_discovery_docs.py`
- dashboard runtime behavior, Streamlit rendering, SQLite queries, report
  loading, candidate extraction, scoring, source collection, dashboard tab
  routing, CLI behavior, source acquisition, connectors, scraping, browser
  automation, platform APIs, monitoring, scheduling, ranking, demand proof,
  coverage verification, account/cookie/session/proxy/CAPTCHA/paywall behavior,
  or compliance/audit/legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_dashboard_docs.py -q
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_dashboard_docs.py tests/test_dashboard.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py tests/test_reports.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_dashboard_docs.py
uv --no-config run --frozen ruff format --check tests/test_dashboard_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 111 plan and remain scoped to a
   docs-only drift guard?
2. Are the asserted phrases appropriate for `docs/dashboard.md`, given existing
   overlap with scoring docs, candidate-discovery docs, reports, and dashboard
   runtime tests?
3. Does the implementation fit the existing `tests/test_dashboard_docs.py`
   pattern cleanly?
4. Are there any Critical or Important issues to fix before commit?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
