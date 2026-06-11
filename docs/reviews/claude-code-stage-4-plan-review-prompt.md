# Claude Code Stage 4 Plan Review Prompt

You are Claude Code reviewing the Stage 4 plan for Fashion Radar before any
Stage 4 implementation starts.

Repository: `/home/ubuntu/fashion-radar`

Current state:

- Stage 1 skeleton/config/models completed.
- Stage 2 SQLite storage/entity matcher completed.
- Stage 3 RSS/GDELT public collectors, HTTP/robots/article helpers, serial
  runner, schema v1->v2 migration, collector run status, and source health
  completed.
- Stage 3 code re-review result:
  `docs/reviews/claude-code-stage-3-code-rereview.md`
  says "Approved for Stage 4 plan review".

Stage 4 goal:

- Compute deterministic daily entity metrics and heat scores.
- Generate Markdown and JSON daily reports from stored item/entity/source-health
  data.
- Preserve source attribution and avoid reproducing full article text.

Proposed Stage 4 files:

```text
src/fashion_radar/scoring.py
src/fashion_radar/reports.py
templates/daily_report.md.j2
tests/test_scoring.py
tests/test_reports.py
```

Existing config/model/storage context:

- `configs/scoring.example.yaml` and `ScoringSettings` currently define:
  - `weighted_mentions_7d`
  - `growth_bonus`
  - `source_diversity_bonus`
  - `high_weight_source_bonus`
  - `new_entity_days`
- `items` table stores:
  - source name/type
  - url/normalized_url
  - title
  - published_at
  - summary
  - content hash
- `item_entities` table stores:
  - item id
  - entity name/type
  - matched alias
  - confidence
  - reason
  - context terms
- `collector_runs` and `source_health` tables store source status for report
  transparency.

Proposed Stage 4 implementation method:

1. Use TDD with fixtures seeded into SQLite temp DBs.
2. Add query helpers/repository methods only as needed for scoring/report reads.
3. Keep scoring deterministic and transparent; no LLM summaries.
4. Compute a daily metrics structure by entity:
   - mention count in current 24h window
   - weighted mention count using source weight from config
   - 7-day count or available-history count
   - previous comparable window count
   - growth ratio or delta
   - source diversity count
   - representative item snippets with source name, URL, publication time,
     title, and short summary only
5. Compute heat labels:
   - `new`
   - `rising`
   - `hot`
   - `stable`
   - `cooling`
6. Generate Markdown and JSON reports from the same deterministic report model.
7. Include source health and recent failed/skipped collector runs in reports.
8. Do not add pandas or Streamlit yet; those stay for Stage 5 dashboard unless a
   Stage 4 report implementation genuinely needs pandas.

Proposed Stage 4 tests:

- Weighted mention counting respects source weights.
- Entity metrics aggregate item/entity matches by date window.
- Heat labels distinguish weak-new, rising, hot/stable high-volume, and cooling
  entities.
- Reports are deterministic from fixture DB rows.
- Markdown report includes rising brands, rising products, celebrity mentions,
  representative item attribution, and source health.
- JSON report has the same core data as Markdown.
- Reports do not include full article text and use stored short summaries only.
- Empty database produces a useful empty report, not a crash.

Please review:

1. Is this Stage 4 plan safe to execute after the current Stage 3 implementation?
2. Are scoring windows and heat label inputs specific enough to avoid arbitrary
   or misleading rankings?
3. Are additional schema/repository changes needed before scoring/reporting?
4. Are report content boundaries conservative enough?
5. Are tests sufficient for deterministic scoring/report output?
6. Should any Stage 4 scope be deferred to Stage 5?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 4 implementation
- Approved after fixes
- Do not proceed
