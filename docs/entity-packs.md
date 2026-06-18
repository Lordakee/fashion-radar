# Entity Packs

Entity packs are optional local configuration templates for `entities.yaml`.
They help users start from a broader watchlist without changing Fashion Radar's
runtime behavior.

The first optional pack is:

```text
configs/entity-packs/fashion-watchlist.example.yaml
```

It is a seed watchlist for designer brands, named bags and shoes, product
categories, designers, celebrity style signals, and style terms. It is not a
hot-list, ranking, current-hotness detector, platform-wide signal, or
market-wide demand proof.

## Lint The Pack

Check the pack before copying or editing it:

```bash
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
```

Use JSON output for scripts or CI:

```bash
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
```

Use `--strict` when a local edited pack should fail on advisory warnings as well
as errors. See [entity-pack-quality.md](entity-pack-quality.md) for finding
codes, matcher-rule notes, and limits.

## Use The Pack

Copy the pack into the config directory you want to use:

```bash
mkdir -p "$PWD/configs" "$PWD/data" "$PWD/reports"
cp configs/entity-packs/fashion-watchlist.example.yaml "$PWD/configs/entities.yaml"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

Use the same local config, data, and report directories in later commands so
Fashion Radar reads and writes one workspace instead of mixing repo-local config
with platform default user paths.

After your existing configured-source or local-signal pipeline has already
produced signals, run the normal local review commands:

```bash
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

The entity pack only changes local entity matching. It does not add sources,
source setup, collection workflows, platform or community ingestion, scraping,
social monitoring, current-hotness detection, or ranking semantics.

## Try The Optional Local Sample

Use the optional local sample when you want to exercise the broader
`fashion-watchlist` pack against checked-in synthetic community-signal rows.

```bash
tmp_watchlist="$(mktemp -d)"
AS_OF="2026-06-13T12:00:00Z"
mkdir -p "$tmp_watchlist/configs" "$tmp_watchlist/data" "$tmp_watchlist/reports"
cp configs/entity-packs/fashion-watchlist.example.yaml "$tmp_watchlist/configs/entities.yaml"
cp configs/scoring.example.yaml "$tmp_watchlist/configs/scoring.yaml"

uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
uv run fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample"
uv run fashion-radar import-signals examples/community-signals.watchlist.example.csv --format csv --source-name "Community Watchlist Sample" --imported-at "$AS_OF" --data-dir "$tmp_watchlist/data"
uv run fashion-radar match --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data"
uv run fashion-radar report --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --reports-dir "$tmp_watchlist/reports" --as-of "$AS_OF"
uv run fashion-radar trends --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --as-of "$AS_OF" --format json
```

The local sample rows are synthetic. They are not a hot-list, not a ranking,
not demand proof, and not platform coverage verification. The flow uses local
files only: no fetching URLs, no platform data collection, and no connectors.

## Edit The Pack

Treat the pack as a starting point:

- Remove brands, products, celebrities, or categories that are not useful for
  your research.
- Add aliases only when they are specific enough for the sources you review.
- Use `parent_brand` for named products where possible.
- Keep generic or common aliases narrow.
- Tune `initial_weight` conservatively. Weights are local scoring inputs, not
  confidence in external demand.

Existing matching uses context gates for product aliases with `parent_brand`,
single-word aliases, and aliases listed as unsafe/common by the application.
`context_terms` are not a universal phrase-level disambiguation system for every
multi-word category or trend alias. For other multi-word category or trend
aliases, use narrower aliases where possible.

Multi-word category aliases such as `Mary Janes` or `boat shoes` may match in a
retained fashion corpus without context gating. Remove or narrow them if they
are noisy for your source set.

Candidate discovery can still surface untracked phrases even when they are not
in the pack. Review those candidates before adding them to your entity config.

## Revert To The Starter

The default small starter config remains in:

```text
configs/entities.example.yaml
src/fashion_radar/templates/configs/entities.example.yaml
```

To return to the packaged starter in a local repo checkout:

```bash
mkdir -p "$PWD/configs" "$PWD/data" "$PWD/reports"
cp src/fashion_radar/templates/configs/entities.example.yaml "$PWD/configs/entities.yaml"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```
