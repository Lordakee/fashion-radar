# Source Packs

Source packs are example YAML files that help users start with public fashion
signals. They are not endorsements, subscriptions, or availability guarantees.
Users remain responsible for source terms, RSSHub route terms, robots rules, and
local laws.

## Public Fashion Pack

The starter pack lives at:

```text
configs/source-packs/fashion-public.example.yaml
```

It uses only existing v0.1.0 source types:

- `rss`
- `gdelt`

The expanded public pack keeps the RSS entries conservative and adds bounded
GDELT lanes for runway and fashion week, designer-brand momentum, retail and
resale, footwear, handbags and accessories, creative-director moves, and
beauty/fashion crossover signals inside the configured source set.

It does not include Google News RSS, Google Trends, account-based source access,
browser automation, access-control bypasses, paywall bypass, or private data
collection.

## Check Pack Quality

Before copying or editing a pack, run the local linter:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
```

JSON output is available for scripts and CI:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

Example JSON shape:

```json
{
  "path": "configs/source-packs/fashion-public.example.yaml",
  "source_count": 16,
  "enabled_count": 16,
  "disabled_count": 0,
  "type_counts": {
    "gdelt": 10,
    "rss": 6
  },
  "tag_counts": {
    "industry_news": 5,
    "gdelt": 10
  },
  "findings": []
}
```

See [source-pack-quality.md](source-pack-quality.md) for finding codes,
severity meanings, and tag/weight tuning guidance.

## Use A Pack

Copy the pack into your config directory as `sources.yaml`:

```bash
mkdir -p "$PWD/configs" "$PWD/data" "$PWD/reports"
cp configs/source-packs/fashion-public.example.yaml "$PWD/configs/sources.yaml"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

Then run:

```bash
uv run fashion-radar run --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

## Source Availability

The RSS endpoints in the public pack were checked during Stage 7 planning on
2026-06-12. RSS availability can change without notice. If a source fails,
disable it or replace it with a feed you have verified.

## Article Extraction

RSS article extraction is disabled by default in the public pack:

```yaml
article:
  enabled: false
```

This keeps the pack conservative and avoids unnecessary article-page fetching.
You can opt into article extraction per source after reviewing source terms and
robots behavior.

## GDELT Queries

The GDELT entries are broad starter queries for:

- luxury/designer fashion
- celebrity style/red carpet
- bags/shoes/products
- emerging designers

Tune the query strings, `max_records`, and source weights for your own research
needs. Scores only reflect the configured source set.
