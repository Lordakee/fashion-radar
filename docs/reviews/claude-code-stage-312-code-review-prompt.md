# Claude Code Stage 312 Code Review Prompt

You are the primary local Claude Code reviewer for Fashion Radar Stage 312.
Use maximum reasoning. Review the current uncommitted working tree in
`/home/ubuntu/fashion-radar`.

## Stage Goal

Add a generated-site-only ROW ONE homepage `Saved Article Coverage / 保存正文覆盖`
section that summarizes the current edition's locally saved article corpus.

## Required Boundaries

- Use existing `data/articles/<story-id>.json` sidecars only.
- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not write a new JSON artifact.
- Do not change schemas, story IDs, detail routes, or paragraph anchors.
- Do not add source collection, scraping, scoring, LLM calls, scheduling,
  platform/social/community connectors, or compliance-review product features.

## Expected Implementation

- New internal builder:
  - `src/fashion_radar/row_one/saved_article_coverage.py`
  - Counts current-edition publishable local articles only.
  - Requires `safe_local_article_story_id(story.id)`.
  - Requires at least one nonblank saved paragraph.
  - Corpus metrics count all publishable articles.
  - Homepage read queue is capped to four cards in edition order.
  - Source chips preserve first-seen source order.
- Renderer wiring:
  - `render_row_one_site()` builds coverage from `edition` and
    `local_articles_by_story_id`.
  - `render_index_html()` renders the section after Daily Local Intelligence and
    before lead story.
  - Card hrefs must only render safe `details/<story>.html#local-article-digest`
    links.
- Docs/tests:
  - README and `docs/row-one.md` document the Stage 312 boundary.
  - Tests cover builder counts/filtering/order, homepage rendering, omission,
    escaping, bad coverage href filtering, CSS selectors, and docs boundary.

## Changed Files To Inspect

- `README.md`
- `docs/row-one.md`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `src/fashion_radar/row_one/saved_article_coverage.py`
- `tests/test_row_one_docs.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_saved_article_coverage.py`

## Verification Already Run

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_coverage.py tests/test_row_one_render.py tests/test_row_one_docs.py -q`
  - `129 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`
  - passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`
  - passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`
  - `2060 passed`
- `UV_NO_CONFIG=1 uv lock --check`
  - passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py`
  - passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only`
  - passed, wrote 18 stories
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json`
  - `ok: true`

## Review Instructions

Return findings first, ordered by severity:

- Critical: correctness, security, contract drift, generated artifact/schema
  regression, unsafe links, data loss, or failing required behavior.
- Important: likely bugs, brittle tests that miss boundary regressions, or
  meaningful maintainability issues that should be fixed before commit.
- Minor: polish or low-risk improvements.

For each finding, include exact file and line references. If no Critical or
Important findings exist, say that clearly and mention residual risk/test gaps.
