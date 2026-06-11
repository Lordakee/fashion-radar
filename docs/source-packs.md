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

It does not include Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Google
News RSS, Google Trends, Reddit, Pinterest, Playwright, login cookies,
account/session files, proxy pools, CAPTCHA bypass, paywall bypass, or private
data collection.

## Use A Pack

Copy the pack into your config directory as `sources.yaml`:

```bash
cp configs/source-packs/fashion-public.example.yaml configs/sources.yaml
uv run fashion-radar doctor
```

Then run:

```bash
uv run fashion-radar run --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
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
