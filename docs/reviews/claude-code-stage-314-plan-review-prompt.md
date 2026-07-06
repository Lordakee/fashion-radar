# Claude Code Stage 314 Plan Review Prompt

You are reviewing the Stage 314 plan for `/home/ubuntu/fashion-radar`.

Use read-only review. Do not edit files.

Required command settings for this project:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-314-plan-review-prompt.md)"
```

Review:

- `docs/superpowers/specs/2026-07-06-stage-314-row-one-local-article-observability-design.md`
- `docs/superpowers/plans/2026-07-06-stage-314-row-one-local-article-observability-plan.md`
- Relevant existing implementation in:
  - `src/fashion_radar/row_one/articles.py`
  - `src/fashion_radar/workflows.py`
  - `src/fashion_radar/row_one/render.py`
  - `src/fashion_radar/cli.py`
  - `src/fashion_radar/row_one/status_integrity.py`
  - `tests/test_row_one_cli.py`
  - `tests/test_workflows.py`

Check:

- The objective matches the user need: prove whether local saved article bodies are actually present in the generated ROW ONE site.
- The scope stays observability-only and does not add compliance-review product features, social/community connector defaults, source collection behavior, scoring, LLM calls, new app contracts, schemas, or generated JSON artifacts.
- The proposed `site_metrics.py` approach is technically reasonable and does not conflict with existing status integrity validation.
- The CLI/status JSON fields are appropriate as ops/status output and do not drift `row-one-app/v7`, runtime, or manifest contracts.
- The tests are strong enough to prove sidecars, detail local article sections, and homepage saved article modules when deterministic local article extraction succeeds.
- The implementation plan is feasible and does not rely on network access.

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
