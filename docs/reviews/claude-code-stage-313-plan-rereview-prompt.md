# Claude Code Stage 313 Compact Plan Review Prompt

Review these two files only:

- `docs/superpowers/specs/2026-07-06-stage-313-row-one-saved-article-briefs-design.md`
- `docs/superpowers/plans/2026-07-06-stage-313-row-one-saved-article-briefs-plan.md`

Context: Fashion Radar ROW ONE Stage 313 should add a generated-site-only
homepage `Saved Article Briefs / 保存正文简报` section. It must use only existing
saved local article sidecars, show capped excerpts only, and must not change
`row-one-app/v7`, `data/edition.json`, `row-one-manifest/v1`,
`row-one-runtime/v1`, schemas, story IDs, detail routes, paragraph anchors, or
write a new JSON artifact. It must not add collection, scraping, scoring, LLM
calls, scheduling, social/community connectors, or compliance-review product
features.

Return only:

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

Use exact file/line references. If no Critical or Important findings exist,
say that clearly. Do not edit files.
