# opencode Stage 332 Plan Review

**Verdict:** None — proceed to implementation.

No Critical, Important, or Minor plan issues remain after Claude Code's review.

## Findings

### Feasibility

`render.py` already builds `saved_article_content_organization`; `templates.py`
has keyword-only render signatures that can accept the new parameters
backward-compatibly; the existing direct test caller for
`render_saved_article_library_html()` remains compatible with the optional
argument.

### Safety

The validate-then-prefix order matches the existing saved-signal-index pattern,
while the planned configurable `href_prefix` is appropriate because the same
content-organization renderer serves both the homepage and the saved article
library page. The prefix is never passed into validation.

### Tests

The single-story `_signal_briefing_local_article()` fixture produces a non-None
saved signal index, so the ordering assertion can safely check that the saved
signal index appears before the content organization and source grid. The
integration test, direct renderer safety test, and docs sentinel provide enough
coverage and match recent Stage 327/328 testing patterns.

### Boundary

The plan does not add schema, sidecar, JSON contract, connector, crawler,
scheduler, extraction, ranking, LLM, or compliance-review behavior.

## Notes

Claude Code's Minor item about making the
`RowOneSavedArticleContentOrganization` import mandatory is reflected in Task 2
Step 2.

One non-blocking observation: `_saved_article_content_organization_section_html`
can return an unbounded tail on the library page because the next source section
is indented. This is harmless for the planned assertions, which use positive
checks and negative checks for strings absent from the rest of the page.
