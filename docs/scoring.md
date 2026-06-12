# Scoring

Fashion Radar scores entities from local matched items. Scores are useful for
ranking signals inside your configured source set and imported local signals;
they are not rankings outside that local source set.

## Inputs

Scoring reads accepted rows from `item_entities` joined to `items`.

Each mention uses:

- `entity_name`
- `entity_type`
- `item_id`
- match `confidence`
- item `source_name`
- item `source_weight`
- item `collected_at`

Rows below `min_match_confidence` are ignored. Future-dated items relative to
`as_of` are ignored.

If multiple matches exist for the same `(entity_name, entity_type, item_id)`,
the highest-confidence match is used.

## Windows

Given `as_of`:

```text
current_start = as_of - current_window_days
baseline_start = current_start - baseline_window_days
```

Current window:

```text
current_start < collected_at <= as_of
```

Baseline window:

```text
baseline_start < collected_at <= current_start
```

Entities with no current-window mentions are omitted from ranked sections.

## Formula

For one entity:

```text
current_mentions = count(current-window distinct entity/item mentions)
baseline_mentions = count(baseline-window distinct entity/item mentions)
weighted_mention_sum = sum(source_weight * confidence for current mentions)
distinct_sources = count(unique source_name for current mentions)
current_rate = current_mentions / current_window_days
baseline_rate = baseline_mentions / baseline_window_days
growth_ratio = current_rate / baseline_rate, if baseline_rate > 0
```

Components:

```text
weighted_mention_component = weighted_mention_sum * weighted_mentions_7d
growth_component = max(0, growth_ratio - 1) * growth_bonus
source_diversity_component = max(0, distinct_sources - 1) * source_diversity_bonus
high_weight_component = high_weight_source_bonus
  if any current mention source_weight >= high_weight_source_threshold
  else 0
```

Final score:

```text
heat_score =
  weighted_mention_component
  + growth_component
  + source_diversity_component
  + high_weight_component
```

If there is no baseline rate, `growth_ratio` is `null` and the growth component
is `0`.

## Labels

Labels are assigned in this order:

1. `new`: stable first seen is within `new_entity_days` and current mentions are
   at least `new_min_mentions`.
2. `hot`: heat score is at least `hot_score_threshold` and distinct sources are
   at least `hot_min_distinct_sources`.
3. `rising`: baseline exists, current mentions are at least
   `rising_min_mentions`, and `growth_ratio >= rising_growth_ratio`.
4. `cooling`: baseline mentions are at least `cooling_min_baseline_mentions`
   and `growth_ratio <= cooling_growth_ratio`.
5. `stable`: current mentions are at least `stable_min_mentions`.
6. `stable`: final fallback.

The duplicate stable fallback is intentional in v0.1.0 behavior and documented
as a known quirk.

## Stable First Seen

`entity_first_seen` stores the earliest and latest accepted match timestamp for
each `(entity_name, entity_type)` using item `collected_at`.

Scoring prefers this stable first-seen timestamp for `new` labels. If the table
does not have a row, scoring falls back to the earliest retained item mention.
Keeping stable first-seen outside retained item history prevents old entities
from being mislabeled as new after old items are pruned.

## Candidate Signals

Candidate discovery uses the same `current_window_days`,
`baseline_window_days`, and `collected_at` window boundaries as entity scoring.
Instead of scoring configured entities, it reviews observed phrases in retained
local item titles and summaries from configured sources and imported local
signals.

Candidate labels use their own `candidate_discovery` thresholds in
`scoring.yaml`:

- `new_candidate` means the observed phrase has current-window mentions, no
  retained baseline mentions, and meets the configured mention/source floors.
- `rising_candidate` means the observed phrase has retained baseline mentions
  and meets the configured growth, mention, and source floors.
- `review` means the observed phrase meets the lower review floors but still
  needs review before being tracked.

`first_seen_at` for a candidate signal is based on retained local item history.
It can change after old items are pruned.

## Trend Deltas

Trend deltas reuse entity scoring and candidate discovery snapshots. They do not
introduce a new heat formula.

For trend deltas, `current_mentions` is the current comparison snapshot's
current-window count and `baseline_mentions` is the baseline comparison
snapshot's current-window count. Scoring's internal baseline-window counts are
exposed only as `current_internal_baseline_mentions` and
`baseline_internal_baseline_mentions`.

Existing signals are labeled `rising` or `cooling` only when score and mention
movement agree. Mixed-direction movement is `stable`. These labels are local
observed statuses for review, not market-wide popularity claims.

## Tuning

See `configs/scoring.example.yaml`.

- Increase `source_weight` on trusted sources in `sources.yaml` to make their
  mentions count more.
- Increase `min_match_confidence` to reduce low-confidence entity matches.
- Increase `source_diversity_bonus` to reward signals appearing across multiple
  sources.
- Increase `high_weight_source_threshold` or lower `high_weight_source_bonus`
  if a few high-weight sources dominate the report.

## Limits

- Scores only reflect configured sources and imported local signals.
- Candidate signals only reflect configured sources and imported local signals.
- Trend deltas only reflect configured sources and imported local signals.
- Candidate deltas are limited by configured candidate discovery thresholds.
- Counts use collected time, not necessarily publication time.
- Dashboard mention tabs show mention counts, while candidate signal views read
  the latest report JSON.
- There is no image/video or external engagement analysis in v0.1.0.
