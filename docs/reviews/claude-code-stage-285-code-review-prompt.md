# Stage 285 Code Review Request

Review the current uncommitted changes in `/home/ubuntu/fashion-radar` for Stage 285.

## Objective

Make ROW ONE organize information more clearly without adding collectors or a new broad data surface.

## Implemented Scope

- Added existing `why_it_matters` and `signal_context` fields to ROW ONE `contentCard` payloads and schema.
- These card fields now flow to `content_sections`, `daily_digest.blocks`, and `daily_digest.briefing_topics` through `_content_card_payload`.
- Added a static detail-page `detail-information-map` after article contents and before summary, derived only from existing `RowOneStory` fields.
- Updated tests and docs.
- Recorded that Claude Code plan review was blocked by local auth 401; opencode glm-5.2 reviewed and approved the revised plan.

## Constraints

No dependency, source collection, connector, social/community platform, browser automation, account/cookie, LLM, image generation, scoring, ranking, sorting, story ID, cleanup, scheduler, server, deployment, or contract-version changes.

## Changed Files

```text
README.md                              |   7 +-
docs/row-one.md                        |  21 +++-
schemas/row-one-app.schema.json        |   8 ++
src/fashion_radar/row_one/render.py    |   2 +
src/fashion_radar/row_one/templates.py | 169 +++++++++++++++++++++++++++++++++
tests/test_row_one_app_contract.py     |  20 ++++
tests/test_row_one_docs.py             |  22 +++++
tests/test_row_one_render.py           |  56 +++++++++++
8 files changed, 299 insertions(+), 6 deletions(-)
```

## Verification Already Run

```bash
UV_NO_CONFIG=1 uv --no-config run python -m json.tool schemas/row-one-app.schema.json >/dev/null
UV_NO_CONFIG=1 uv --no-config run pytest tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py -q
# 152 passed
UV_NO_CONFIG=1 uv --no-config run ruff check .
# All checks passed
UV_NO_CONFIG=1 uv --no-config run ruff format --check .
# 179 files already formatted
UV_NO_CONFIG=1 uv --no-config run pytest -q
# 1860 passed
UV_NO_CONFIG=1 uv --no-config lock --check
# Resolved 85 packages in 1ms
 git diff --check
 git diff --exit-code -- uv.lock pyproject.toml
```

## Review Request

Return APPROVED or NOT APPROVED. List only Critical/Important findings with file/line references. Focus on correctness, schema contract risk, escaping/XSS risk, tests, docs accuracy, and scope creep.
