# Stage 315 ROW ONE Article Readiness Design

## Goal

Make ROW ONE local article-body generation diagnosable from the normal local
deployment path, so a user can understand why `row-one build` reports zero
saved local articles and what configuration change will make daily builds
produce `data/articles/<story-id>.json` sidecars.

## Current Evidence

Stage 314 made the local article sidecar count visible. A repo-config build can
already produce local article sidecars:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-06T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
```

This produced 17 stories, 17 saved local articles, and 136 saved local
paragraphs on the current local data. The same command without `--config-dir
configs` read the user's platformdirs config at
`~/.config/fashion-radar/sources.yaml`, an older public pack that lacks
`row_one_article.enabled: true`, so it produced zero local articles.

The implementation should not silently overwrite user config. The right product
surface is a deterministic diagnostic command plus docs that explain how to run
with the current starter config or update an older local config.

## Architecture

Add a pure ROW ONE article-readiness analyzer that reads local config and an
optional generated ROW ONE site. It must not collect sources, fetch article
pages, call LLMs, start servers, write config files, or mutate SQLite. The CLI
will expose it as `fashion-radar row-one article-readiness`, with text output
for operators and optional JSON output for agents/app integrations.

The analyzer has three inputs:

- `sources`: the loaded `SourceDefinition` list from `sources.yaml`.
- optional `edition_payload`: the existing `data/edition.json` payload from a
  generated ROW ONE site.
- optional local-article metrics from Stage 314, computed from `data/articles`.

It emits:

- source counts: total enabled sources and `row_one_article.enabled` sources.
- site metrics: saved local articles and saved local paragraphs when a site is
  available.
- story-source coverage: how many current stories have a source that is eligible
  for ROW ONE article generation.
- guidance lines that are deterministic and local-only.

## Approaches Considered

### Recommended: Readiness Command Only

Add `row-one article-readiness` as a non-mutating diagnostic command. This is
safe for existing users, works on old configs, and gives future agents a stable
machine-readable way to tell whether local article generation is configured.

### More Aggressive: Auto-Patch User Config

Automatically add `row_one_article.enabled: true` to old local `sources.yaml`.
This would make the user's default build work sooner, but it risks overwriting
custom source choices and introduces a config migration surface that needs
backup/merge UX. It is not the right first step.

### Too Broad: New Extractor or Source Collection Changes

Changing article extraction logic or source collection is unnecessary for the
observed problem. The current extractor plus fallback already generates sidecars
when sources are article-enabled. This stage should not add scraping,
platform connectors, scoring, or LLM behavior.

## Functional Requirements

1. `fashion-radar row-one article-readiness` loads `sources.yaml` from the
   selected `--config-dir`.
2. The command prints:
   - `ROW ONE article readiness`
   - `Config: <config-dir>`
   - `Site: <site-dir>`
   - `Sources: <enabled>/<total> enabled`
   - `ROW ONE article-enabled sources: <count>`
   - `Saved local articles: <count>`
   - `Saved local paragraphs: <count>`
   - `Story source coverage: <eligible>/<story_count> eligible`
   - a recommendation when zero current stories are eligible.
3. `--json` prints a machine-readable payload and does not mix text lines into
   stdout.
4. Missing generated site files do not fail the command; they report zero site
   story/source coverage and include guidance to run `row-one build` or
   `row-one refresh`.
5. Existing Stage 314 status metrics are reused; no new generated JSON artifact
   is written.
6. The command is read-only: no network, no collection, no extraction, no file
   mutation, no SQLite mutation.
7. Documentation explains the default-config gotcha: a repo-config build can
   have article-enabled sources while an older platformdirs config may not.
8. `row-one install-local` and `row-one local-ops` docs mention
   `row-one article-readiness` as the preflight command before relying on daily
   04:00 refresh.
9. First-run docs clarify that deterministic smoke uses empty live sources and
   does not require nonzero saved article sidecars.

## Non-Goals

- No automatic config migration.
- No source collection or article fetching.
- No changes to `data/edition.json`, `data/manifest.json`, or
  `data/runtime.json`.
- No new app contract version.
- No social/community connector activation.
- No compliance-review feature.
- No OpenDesign/image generation changes.

## Data Model

Add `src/fashion_radar/row_one/article_readiness.py` with frozen dataclasses:

```python
@dataclass(frozen=True)
class RowOneArticleReadinessSourceSummary:
    total_sources: int
    enabled_sources: int
    article_enabled_sources: int

@dataclass(frozen=True)
class RowOneArticleReadinessStoryCoverage:
    story_count: int
    eligible_story_count: int
    missing_source_count: int
    disabled_source_count: int

@dataclass(frozen=True)
class RowOneArticleReadiness:
    source_summary: RowOneArticleReadinessSourceSummary
    story_coverage: RowOneArticleReadinessStoryCoverage
    local_article_metrics: RowOneLocalArticleSiteMetrics
    recommendations: tuple[str, ...]
```

The analyzer should match stories to sources using the same source-name first
rule as `row_one/articles.py`: if a story's `source_name` equals a source name,
that source controls eligibility. This relies on the existing
`row-one-app/v7` generated `stories[].source_name` field; missing or invalid
story source names should be counted as missing source coverage instead of
failing the command. If no exact source name matches, the analyzer should mirror
the local article producer's non-network host fallback by comparing the story
`source_url` hostname with enabled source `url` and `seed_urls` hostnames, then
count the matched story as eligible or disabled based on that source's
`row_one_article.enabled` setting.

## Testing

Focused tests should cover:

- An old public-pack-style source config with `article.enabled: false` and no
  `row_one_article` blocks reports zero article-enabled sources.
- A generated site whose stories come from those sources reports zero eligible
  stories and prints a recommendation.
- The current starter config reports at least one article-enabled source.
- Story coverage counts a story as eligible when its `source_name` differs from
  the configured source name but its safe `source_url` hostname matches an
  article-enabled source URL.
- Story coverage counts a story as disabled, not missing, when its safe
  `source_url` hostname matches an enabled source whose `row_one_article.enabled`
  setting is false.
- JSON output contains only JSON and includes `local_articles`,
  `source_summary`, `story_coverage`, and `recommendations`.
- The command does not require a generated site.
- Docs describe the readiness preflight and the default-config gotcha.
- First-run docs describe the no-live-source smoke boundary and point live ROW
  ONE users to `row-one article-readiness`.

## Verification

Required commands for the implementation node:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_article_readiness.py \
  tests/test_row_one_cli.py \
  tests/test_row_one_docs.py \
  tests/test_first_run_docs.py \
  tests/test_config.py -q

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
```

The final manual smoke should include:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one article-readiness \
  --config-dir configs \
  --site-dir reports/row-one/site
```

and:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one article-readiness \
  --config-dir "$HOME/.config/fashion-radar" \
  --site-dir reports/row-one/site
```

The second command may report zero eligible stories on older local config; that
is acceptable if it prints the deterministic recommendation.

## Self-Review

- No placeholders remain.
- Scope is a single diagnostic feature, not a config migration or extractor
  rewrite.
- The design directly addresses the observed default-config mismatch.
- The feature is additive and does not change generated ROW ONE contracts.
