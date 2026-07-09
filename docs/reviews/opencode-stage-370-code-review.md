# opencode Stage 370 Code Review

Reviewer: opencode with `zhipuai-coding-plan/glm-5.2`

Scope: staged Stage 370 Daily Local Article Intelligence Brief changes.

## Resolved Findings

### Resolved Important

1. Metric scope could diverge when more than four eligible local articles existed.

   Location: `src/fashion_radar/row_one/daily_local_article_intelligence_brief.py`

   The first implementation capped `articles` to `DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES`
   only at return time, while `lanes`, `signal_count`, `evidence_count`, and `source_count` were
   computed from all eligible article briefs. The homepage could therefore show four cards while
   reporting signals and evidence from hidden cards.

   Resolution:

   - `article_cards` is now capped before computing included article briefs, lanes, signal count,
     evidence count, sources, and returned articles.
   - `tests/test_row_one_daily_local_article_intelligence_brief.py` now asserts the capped article
     scenario keeps shared-chip support, evidence count, and hidden-card labels aligned with the
     four displayed cards.

### Minor

1. The Stage 370 opening signal cap is higher than Stage 369's upstream opening-signal cap, so it is
   mostly defensive.
2. `brief.source_count` is still recalculated defensively by the template from rendered safe cards.

## Recheck

Commands:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_article_intelligence_brief.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_local_article_intelligence_brief"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/daily_local_article_intelligence_brief.py tests/test_row_one_daily_local_article_intelligence_brief.py
```

Result: all three focused checks passed after the fix.

No Critical issues remain from this review.
