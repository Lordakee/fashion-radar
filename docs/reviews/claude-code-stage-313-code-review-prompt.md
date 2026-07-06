# Claude Code Stage 313 Code Review Prompt

You are reviewing Stage 313 implementation in `/home/ubuntu/fashion-radar`.

Use read-only review. Do not edit files.

Required command settings for this project:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-313-code-review-prompt.md)"
```

## Scope

Stage 313 implements ROW ONE homepage `Saved Article Briefs / 保存正文简报`.

Review these files:

- `docs/superpowers/specs/2026-07-06-stage-313-row-one-saved-article-briefs-design.md`
- `docs/superpowers/plans/2026-07-06-stage-313-row-one-saved-article-briefs-plan.md`
- `src/fashion_radar/row_one/detail_routes.py`
- `src/fashion_radar/row_one/saved_article_briefs.py`
- `src/fashion_radar/row_one/saved_article_coverage.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_briefs.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

## Requirements To Check

- Generated-site-only homepage section; no app contract, manifest, runtime, schema, story id, detail route, paragraph anchor, collection, scraping, scoring, LLM, scheduling, image, or social/community connector changes.
- Builder uses only current-edition `data/articles/<story-id>.json` sidecars supplied through `local_articles_by_story_id`.
- Builder filters unsafe story IDs, invalid detail paths, blank sidecars, non-edition sidecars, and mismatched `article.story_id`.
- `article_count` counts all publishable saved articles, while rendered cards are capped at four.
- Lead excerpt prefers first nonblank `takeaways` item body and falls back to first nonblank saved paragraph with aligned `paragraphs_zh` when available.
- People/brands chips come from `entities`; product chips come from `product_signals`; both are deduped and capped.
- Template renders after Saved Article Coverage and before the lead story.
- Template validates only `details/<story>.html#local-article-digest`, omits invalid cards, escapes all dynamic text, does not emit external article URLs, and caps homepage excerpts without mutating source sidecars.
- Existing Saved Article Coverage behavior does not regress after route-helper refactor.
- Docs describe the Stage 313 boundary accurately and do not imply new JSON artifacts or connector/compliance features.

## Verified Locally Before Review

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_briefs.py tests/test_row_one_render.py tests/test_row_one_docs.py -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`
- `UV_NO_CONFIG=1 uv lock --check`
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py`
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only`
- `UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json`

## Output Format

Return:

```markdown
## Critical
- ...

## Important
- ...

## Minor
- ...

## Verdict
...
```

Only include actionable findings. If there are no findings in a severity, say `No findings.`
