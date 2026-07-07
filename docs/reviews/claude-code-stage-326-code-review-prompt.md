You are Claude Code reviewing Stage 326 for /home/ubuntu/fashion-radar.

Use maximum reasoning. Review the current uncommitted working tree against the Stage 326 spec and plan. Do not edit files.

## What Was Implemented

Stage 326 adds a generated-site only ROW ONE daily saved article library:

- New render-only builder: src/fashion_radar/row_one/saved_article_library.py
- Generated optional page: articles/index.html, written only when current edition has publishable saved local articles
- Homepage entry point: saved-article-library-entry between saved article coverage and saved article briefs
- Latest-only cleanup now removes top-level articles/ generated HTML
- Docs and workflow boundaries ensure no app/runtime/manifest/schema/JSON-artifact/source/fetching/scoring/LLM/connector/scheduling/deployment/compliance behavior changes

## Requirements / Plan

- Spec: docs/superpowers/specs/2026-07-07-stage-326-row-one-daily-saved-article-library-design.md
- Plan: docs/superpowers/plans/2026-07-07-stage-326-row-one-daily-saved-article-library-plan.md
- Plan review: Claude Code plan review timed out without usable output; opencode fallback review is saved at docs/reviews/opencode-stage-326-plan-review.md and rereview at docs/reviews/opencode-stage-326-plan-rereview.md. Critical/Important were closed before implementation.

## Required Boundaries

- Do not change row-one-app/v7.
- Do not change data/edition.json.
- Do not add saved_article_library, daily_saved_article_library, article_library, or related keys to app/runtime/manifest JSON.
- Do not scan output_dir, data/articles/*.json, or persisted sidecar files to build the library.
- Do not change row-one-manifest/v1.
- Do not change row-one-runtime/v1.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not add source collection, fetching, extraction, scoring, ranking, matching, LLM calls, translation calls, image generation, connectors, scheduling, deployment behavior, or compliance-review product features.
- Do not add dependencies.

## Diff To Review

The changes are uncommitted. Inspect with:

- `git status --short`
- `git diff --stat`
- `git diff -- src/fashion_radar/row_one/saved_article_library.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py README.md docs/row-one.md docs/superpowers/specs/2026-07-07-stage-326-row-one-daily-saved-article-library-design.md docs/superpowers/plans/2026-07-07-stage-326-row-one-daily-saved-article-library-plan.md`

## Verification Already Run

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py -q` -> 6 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py tests/test_row_one_render.py -q` -> 158 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q` -> 60 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q` -> 218 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q` -> 2163 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .` -> passed
- `UV_NO_CONFIG=1 uv lock --check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py` -> passed
- `git diff --check` -> passed
- `git grep -n -E 'ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' -- . ':!docs/reviews/*'` -> no hits

## What To Check

- Builder filters only current edition + in-memory local_articles_by_story_id.
- No stale data/articles sidecar reads.
- Safe route validation and ../ detail links from articles/index.html.
- Escaping in homepage entry and library page.
- latest_only cleanup safety with articles/ marker guard.
- JSON contract stability and docs wording.
- CSS/design quality within existing ROW ONE static style.
- Test coverage quality and meaningful boundary tests.

## Output Format

### Strengths

### Issues

#### Critical (Must Fix)

#### Important (Should Fix)

#### Minor (Nice to Have)

For each issue, include file:line, what is wrong, why it matters, and how to fix.

### Recommendations

### Assessment

Ready to merge? Yes | No | With fixes

Base SHA: bcd64d4a64a0cd26dc455d72d126f16fc9248e5e
