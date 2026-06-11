# Stage 8 Candidate Discovery Design

## Goal

Add deterministic "Untracked Candidate Signals" so Fashion Radar can surface
observed phrases that may represent brands, designers, bags, shoes, products,
or style terms already present in locally collected RSS/GDELT items but not yet
configured as tracked entities.

This stage directly supports the user need to notice phrases that may warrant
human review for brands, bags, shoes, and designer labels while keeping the
project free, local-first, and safe for GitHub publication.

## Non-Goals

Stage 8 does not add any new source, collector, crawler, browser automation, or
external intelligence layer.

Out of scope:

- Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Pinterest, Reddit, Google
  Trends, Google News RSS, or static webpage monitoring.
- Scraping, crawler development, Playwright, browser profiles, login cookies,
  account/session files, proxy pools, CAPTCHA bypass, paywall bypass,
  fingerprint evasion, anti-bot bypass, or private data collection.
- Paid APIs, hosted SaaS dependencies, LLM calls, embeddings, vector databases,
  or image recognition.
- Automatic edits to `entities.yaml`.
- Claims that a candidate is globally trending, viral, or confirmed as a real
  brand/product.

## Recommended Approach

Use a no-schema derived analysis layer.

Candidate discovery will compute signals at report/CLI time from retained rows
in the existing SQLite `items` table plus existing accepted rows in
`item_entities`. It will not persist candidates in a new table in Stage 8.

This keeps the feature explainable and avoids migration risk. It also makes the
limitation honest: a candidate's `first_seen_at` is based on retained local item
history only. Unlike configured entities, candidate first-seen data is not
stable across retention pruning.

## Architecture

Create a focused package:

```text
src/fashion_radar/discovery/
  __init__.py
  candidates.py
```

`candidates.py` owns deterministic phrase extraction, known-entity filtering,
windowed metrics, labels, and representative item selection.

Reports will call candidate discovery while building `DailyReport`. The CLI
will expose a read-only `fashion-radar candidates` command. The dashboard will
read candidates from the latest generated JSON report instead of recomputing
them on refresh.

## Data Inputs

Candidate discovery uses these existing local fields:

- `items.id`
- `items.source_name`
- `items.source_type`
- `items.url`
- `items.title`
- `items.summary`
- `items.published_at`
- `items.source_weight`
- `items.collected_at`
- `item_entities.item_id`
- `item_entities.entity_name`
- `item_entities.alias`
- `item_entities.confidence`
- `item_entities.reason`

The feature uses `collected_at` for current and baseline windows, matching
existing heat scoring semantics.

## Candidate Extraction

Extraction is deterministic and uses only `title` plus `summary`.

The extractor will generate `CandidatePhrase` records with:

- `phrase`
- `normalized_key`
- `candidate_type`
- `contexts`

Candidate types are conservative:

- `brand_or_designer`
- `bag`
- `shoe`
- `product`
- `style_term`
- `unknown`

Rules:

- Normalize text with existing helpers from `fashion_radar.extract.text`.
- Prefer 2 to 5 word phrases.
- Extract proper-name spans such as `Sandy Liang`, `Le Teckel`, and
  `Tory Burch Pierced`.
- Extract product phrases anchored by fashion terms such as `bag`, `handbag`,
  `tote`, `clutch`, `shoe`, `sneaker`, `boot`, `loafer`, `flat`, `heel`,
  `sandal`, `pump`, and `mule`.
- Deduplicate candidates per item by `normalized_key`.
- Allow single-token candidates only if aggregate metrics meet stronger
  thresholds.
- Prefer explicit spans over noisy overlap. For `Sandy Liang Mary Jane flats`,
  emit `Sandy Liang` and `Mary Jane flats`, and do not emit the composite
  `Sandy Liang Mary Jane flats`. For `Le Teckel bag`, emit `Le Teckel bag`
  because the fashion anchor is part of the observed product phrase.
- Anchored phrases may include up to three adjacent non-anchor tokens before
  the anchor. If a longer anchored phrase starts with a separate two-word
  proper-name span and has a trailing anchored product phrase, split it into
  those two candidates instead of surfacing the full composite.

Filtering removes:

- Configured entity names and aliases from `entities.yaml` when available.
- Stored `item_entities` names and aliases where
  `item_entities.confidence >= scoring.min_match_confidence`. Discovery does
  not additionally require `reason == "accepted"` because the existing scoring
  path treats confidence as the accepted-match predicate.
- Source-name tokens.
- Generic fashion/media words.
- Days, months, seasons, years, broad cities, and generic event phrases such as
  `fashion week` and `spring collection`.

If a candidate phrase contains a configured or stored known entity key as a
complete token span, reject the full phrase rather than surfacing a composite
leak such as `the row margaux bag` or `margaux bag`.

Known-entity span checks normalize both candidate and known keys with
`normalize_alias_key()`, compare token sequences, treat possessive suffixes as
punctuation, and handle hyphens and ampersands through the same normalized token
path. Examples that must be rejected when their known keys are configured or
stored include `The Row's Margaux bag`, `The Row's Margaux`, `Tory
Burch-Pierced mule`, and `Proenza Schouler & Birkenstock sandal`.

If `entities.yaml` is missing in a direct report path, discovery falls back to
stored `item_entities` filtering. It must not break the existing `report`
command contract.

## Candidate Metrics

Candidate metrics mirror current/baseline scoring windows:

```text
current_start = as_of - scoring.current_window_days
baseline_start = current_start - scoring.baseline_window_days
current window: current_start < collected_at <= as_of
baseline window: baseline_start < collected_at <= current_start
```

Future-dated collected items are ignored.

Metrics:

- `score`
- `label`
- `current_mentions`
- `baseline_mentions`
- `distinct_sources`
- `growth_ratio`
- `first_seen_at`
- `candidate_type`
- `contexts`
- `representative_items`

Growth ratio follows the existing entity scoring convention and compares
window rates rather than raw counts:

```text
current_rate = current_mentions / scoring.current_window_days
baseline_rate = baseline_mentions / scoring.baseline_window_days
growth_ratio = current_rate / baseline_rate when baseline_mentions > 0
growth_ratio = None when baseline_mentions == 0
```

Counting rules:

- Count distinct `(candidate_key, item_id)` mentions.
- Use `source_weight` for weighted current mention score.
- Count distinct source names in the current window.
- Select representative items from current-window rows, newest first.

Score:

```text
weighted_current_mentions
+ source_diversity_bonus * max(0, distinct_sources - 1)
+ growth_bonus * max(0, growth_ratio - 1) when baseline mentions exist
```

Labels:

- `new_candidate`: `baseline_mentions == 0`,
  `current_mentions >= candidate_discovery.min_current_mentions`, and
  `distinct_sources >= candidate_discovery.min_distinct_sources`.
- `rising_candidate`: `baseline_mentions > 0`,
  `current_mentions >= candidate_discovery.min_current_mentions`,
  `distinct_sources >= candidate_discovery.min_distinct_sources`, and
  `growth_ratio >= candidate_discovery.rising_growth_ratio`.
- `review`: candidate meets the inclusion floor
  `current_mentions >= candidate_discovery.review_min_current_mentions` and
  `distinct_sources >= candidate_discovery.review_min_distinct_sources`, but
  does not meet the `new_candidate` or `rising_candidate` contracts.

The inclusion floor for output is the `review_*` threshold pair. The
`min_current_mentions` and `min_distinct_sources` fields are label thresholds
for `new_candidate` and `rising_candidate`.

Sort order is deterministic:

```text
-score, -current_mentions, -distinct_sources, phrase
```

## Settings

Add a small optional `candidate_discovery` block to `scoring.yaml` and
`ScoringConfig`.

Defaults:

```yaml
candidate_discovery:
  enabled: true
  max_candidates: 20
  representative_items_per_candidate: 3
  min_current_mentions: 2
  min_distinct_sources: 1
  rising_growth_ratio: 1.5
  review_min_current_mentions: 2
  review_min_distinct_sources: 1
  min_single_token_mentions: 2
  min_single_token_distinct_sources: 2
  max_phrase_words: 5
  max_phrase_chars: 80
```

Keeping the settings in `scoring.yaml` is acceptable because candidate discovery
uses the same current/baseline windows and source-weight concepts as heat
scoring. Existing scoring configs remain valid because the block is optional.

## Report Output

Extend `DailyReport` with:

```python
candidates: list[CandidateReport] = Field(default_factory=list)
```

The Markdown report gets:

```text
## Untracked Candidate Signals
```

Report wording must use "candidate signal", "observed phrase", "needs review",
and "from configured sources". It must not use "viral", "confirmed brand", or
"market-wide trend".

Public `contexts` values must be short controlled labels such as
`proper_name_span` or `fashion_anchor`. They must not contain raw source text,
aliases, matcher reasons, snippets, or serialized internal extraction state.

JSON output must avoid internal DB fields including `content_hash`,
`normalized_url`, raw matcher reasons, raw aliases, and internal context
serialization.

## CLI Output

Add a read-only command:

```bash
fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of 2026-06-12T00:00:00Z --limit 20 --format table
fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of 2026-06-12T00:00:00Z --limit 20 --format json
```

The command reads local SQLite and config, prints candidates, and does not write
reports or mutate `entities.yaml`.

The command must check whether `fashion-radar.sqlite` exists before creating an
engine. For an existing database it must use a read-only SQLite URI or an
equivalent explicitly non-mutating connection, inspect schema compatibility
without calling `initialize_schema()`, and fail with a user-facing error instead
of creating tables, writing `schema_metadata`, or running migrations.

## Dashboard Output

Add a "Candidate Signals" dashboard tab.

To preserve dashboard read-only behavior, the tab reads candidate rows from the
latest generated JSON report in `reports_dir`. It does not collect, match,
write a report, call the network, or recompute phrase extraction on page load.

The UI should show report date or staleness so users know the dashboard reflects
the latest report file, not necessarily the newest DB row. The dashboard helper
selects the latest report by the `fashion-radar-YYYY-MM-DD.json` filename
contract used by `report_output_paths()`, and must return report metadata even
when the latest report has zero candidate rows. If the latest JSON report is
malformed, the helper must return empty rows plus clear error metadata so the
Streamlit app can render a message instead of crashing.

## Safety And Language

Candidate discovery is a local signal detector, not a truth engine. Every output
must be framed as a candidate requiring human review.

This stage must preserve these boundaries:

- No new collectors.
- No social scraping.
- No private data.
- No external paid dependency.
- No LLM dependency.
- No automatic config mutation.

## Verification

Required verification before Stage 8 commit:

- Focused tests for extraction, metrics, reports, CLI, dashboard helpers, and
  config defaults.
- Full `pytest`.
- `ruff check .`.
- `ruff format --check .`.
- `uv lock --check`.
- `uv sync --locked --dev --check`.
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`.
- Wheel/sdist build.
- Installed-wheel CLI/resource smoke.
- Dashboard extra import smoke.
- CodeGraph status.
- Claude Code code review with `--effort max`.
