# opencode Stage 312 Plan Review Prompt

You are the fallback plan reviewer for `/home/ubuntu/fashion-radar` on branch
`main`. Claude Code returned a server-side 524 timeout before producing a plan
review verdict, so this fallback review is required by `docs/REVIEW_PROTOCOL.md`.

Review the pasted Stage 312 design and implementation plan only. Do not run
tools and do not inspect additional files. Keep the review concise.

## Stage Goal

Add a generated-site homepage Saved Article Coverage section that summarizes the
current ROW ONE edition's locally saved article corpus.

## Intended Architecture

- Add an internal dataclass builder module:
  `src/fashion_radar/row_one/saved_article_coverage.py`
- Build coverage from existing `edition` and `local_articles_by_story_id`.
- Pass coverage from `render_row_one_site()` to `render_index_html()`.
- Render static homepage HTML/CSS only.
- Do not write a new JSON artifact.
- Do not change app-facing Pydantic models or JSON contracts.

## Boundaries

This stage must not:

- change `row-one-app/v7`
- change `data/edition.json`
- change `row-one-manifest/v1`
- change `row-one-runtime/v1`
- change schemas, story IDs, detail routes, or paragraph anchors
- add source collection, scraping, browser automation, platform APIs, scheduling, scoring, LLM calls, translation services, compliance-review features, or social/community connectors
- commit generated `reports/row-one/site/**` output or `uv.lock` changes

## Reviewer Tasks

1. Check whether the plan is technically feasible and consistent with the current codebase.
2. Check whether the plan is too broad, under-specified, or likely to violate the stated boundaries.
3. Check whether the proposed tests are strong enough.
4. Report Critical and Important findings first.
5. Include Minor findings only if they are worth fixing before implementation.
6. If there are no Critical or Important findings, say so explicitly.
7. Keep the whole response under 120 lines.
