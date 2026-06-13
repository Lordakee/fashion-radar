# Candidate Discovery

Candidate discovery surfaces untracked candidate signals from retained local
items collected from configured sources or imported from local user-provided
signal files. Each candidate signal is an observed phrase from item titles or
short summaries, and it needs review before a user decides whether to track it
as an entity.

Candidate discovery does not validate observed phrases as entities. It only
helps a reviewer notice repeated or changing phrases from configured sources and
imported local signals.

## Inputs

Candidate discovery reads existing local SQLite state:

- `items.title`
- `items.summary`
- `items.source_name`
- `items.collected_at`
- accepted tracked-entity matches in `item_entities`
- configured entity names and aliases when an entity config is available

Configured and already matched tracked entities are filtered so they do not
reappear as untracked candidate signals.

## Windows

Candidate metrics use the same current and baseline window shape as entity
scoring:

```text
current_start = as_of - current_window_days
baseline_start = current_start - baseline_window_days
```

Both windows use `items.collected_at`, not publication time. Current-window
mentions count retained items where:

```text
current_start < collected_at <= as_of
```

Baseline mentions count retained items where:

```text
baseline_start < collected_at <= current_start
```

`first_seen_at` is the earliest retained local `collected_at` value for the
observed phrase. Because it is based on retained history, it can change after
old local items are pruned.

## Labels

Candidate labels are review aids:

- `new_candidate`: the observed phrase appears in the current window, has no
  retained baseline mentions, and meets the configured mention/source floors.
- `rising_candidate`: the observed phrase has retained baseline mentions and
  meets the configured growth, mention, and source floors.
- `review`: the observed phrase meets the lower review floors but does not meet
  the `new_candidate` or `rising_candidate` label rules.

All labels remain candidate signals from configured sources and imported local
signals and need review.

## CLI

Print candidate signals as a table:

```bash
uv run fashion-radar candidates --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Print the same review data as JSON:

```bash
uv run fashion-radar candidates --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

Review imported manual candidate signals only:

```bash
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export" --format json
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --phrase "Le Teckel bag"
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --phrase "Le Teckel bag" --source-name "Community Tool Export" --format json
```

The command reads local config and local SQLite state. It is intended for review
and should not mutate source, entity, scoring, or report files.
After local imports, `imported-signals` can inspect retained `manual_import`
rows before candidate discovery. `imported-candidates` is the local read-only
imported-only view of observed candidate phrases from retained `manual_import`
rows. These phrases need review and are not verified entities, demand proof, or
platform coverage.
`imported-candidate-evidence` is the phrase-scoped local read-only view of the
retained `manual_import` rows behind one observed candidate phrase.

## Reports And Dashboard

Daily JSON and Markdown reports may include an untracked candidate signal
section. Representative items keep source attribution so a reviewer can inspect
where an observed phrase appeared from configured sources and imported local
signals.

The dashboard reads candidate signals from the latest report JSON. That view can
be stale until a new report is generated, and it does not recompute candidate
signals from SQLite on refresh.

## Boundaries

Candidate discovery adds no collectors, no new source types, no external
inference calls, and no background network reads. It uses retained local items
from configured sources and imported local signals and keeps outputs framed as
observed phrases that need review.
