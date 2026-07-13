# OpenCode Stage 387 Plan Revision Review

## Verdict
APPROVED

## Workflow Assessment
The Stage 387 plan-review workflow conforms to `AGENTS.md` and
`REVIEW_PROTOCOL.md`. Claude Code acted as the primary plan reviewer, running
pre-implementation with effort max, read-only plan mode, no session persistence,
and Read/Grep/Glob/LS/Bash tools. The recorded body at
`docs/reviews/claude-code-stage-387-plan-review.md` is one coherent, completed
record with a single APPROVED verdict, two residual risks stated and
dispositioned, and no live-capture stubs, tool-status lines, duplicated or
truncated text, or empty output. Plan Task 7 correctly routes the post-Claude
plan revision to OpenCode (GLM 5.2 max) acting on Claude's findings and its own
judgment, restricts OpenCode code/release review to the fallback-only case when
Claude Code is unavailable, and requires one concise credential-free completed
body per review record.

## Scope And Safety Assessment
Stage 387 remains generated-site-only and homepage-only. The builder consumes
only existing current-edition stories, already-loaded local article sidecars,
already-generated article page hrefs, and existing
`content_sections[*].items[*].references`; it emits saved-coverage counts as
facts without scoring, ranking, trend inference, or external calls, renders only
into the existing `index.html` between Daily Saved Text Takeaways and Daily Local
Saved Article Organizer, and is omitted unless at least two valid current-edition
saved local articles contribute. The plan's explicit non-goal list excludes JSON
artifacts, standalone pages, route families, app/runtime/manifest/schema fields,
new sidecars, source collection, fetching, scraping, matching, extraction,
scoring, ranking, LLM calls, connectors, scheduling, deployment, analytics,
personalization, recommendation, demand proof, coverage verification, and
compliance-review behavior, matching the `AGENTS.md` scope boundaries. The
contract denylist, no-artifact stems, and homepage-only sentinel in Task 5, plus
the docs boundary paragraph and stale-phrase tests in Task 6, enforce the
boundary at verification time. No new contract, artifact, route, collection,
extraction, scoring/ranking, external service, or prohibited product behavior is
introduced.

## Required Amendments
None.

## Residual Risks
None identified within the allowed review scope. Both of the Claude Code
review's residual risks are concretely closed in the plan: `_valid_article` now
explicitly rejects missing, unsafe, or story-ID-mismatched sidecars via
`article.story_id != story_id` on top of `safe_local_article_story_id(story_id)`,
and Task 1 Step 3 adds a focused mismatched-third-sidecar test alongside two
valid contributors. Task 4 Step 3 names `templates.py`'s existing
`_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` as the only accepted fragment
pattern for the safe-href helper, with explicit rejection of the paragraph regex
and all other fragments, and the builder's `_safe_article_page_href`
independently enforces a single path component equal to `<safe-story-id>.html`.
