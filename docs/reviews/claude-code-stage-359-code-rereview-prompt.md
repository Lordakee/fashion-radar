You are re-reviewing /home/ubuntu/fashion-radar Stage 359 after code-review fixes.

Context:
- Initial review found:
  1. Potential local_articles_by_story_id None crash path.
  2. Sorting by capped displayed story rows instead of total qualifying local article count.
  3. Potential subtype substring issue.
  4. Missing tests for strict heat gate edge cases.
- A parallel reviewer also found:
  5. Safe but mismatched article href mapping could link story A to story B.

Current intended behavior:
- Add homepage-only generated-site section "Daily Local Heat Signals".
- Use existing app_payload["daily_digest"]["briefing_topics"] only.
- Keep only brand/product topics.
- Strict positive-int heat gate; bool/string/float/zero/None must not count.
- Require usable saved local article paragraphs and a generated local article page href.
- Require article href filename stem to match the source story_id.
- Link to articles/<story-id>.html#local-article-digest.
- Sort by positive_heat_delta_sum desc, max_heat_delta desc, total qualifying local article count desc, evidence_count desc, title.
- Display at most 6 topics and 2 story rows per topic.
- Do not add app payload fields, schemas, artifacts, source fetching, LLM, connectors, scheduling, analytics, personalization, recommendations, or compliance-review functionality.

Please review the current uncommitted diff from HEAD, focusing specifically on whether the prior issues are fixed and whether the fixes introduced regressions.

Return findings by severity with file:line references. If there are no blocking issues, say so and list residual risks.
