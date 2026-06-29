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

The expanded public pack keeps the RSS entries conservative, adds public RSS
feeds for runway/editorial, business/luxury fashion, red-carpet celebrity
style, and bag/accessory product signals, and keeps bounded GDELT lanes for
runway and fashion week, designer-brand momentum, retail and resale, footwear,
handbags and accessories, creative-director moves, and beauty/fashion crossover
signals inside the configured source set.

Current composition:

- 20 enabled sources.
- 10 RSS feeds followed by 10 GDELT query lanes.
- RSS article extraction disabled by default for every RSS source.
- GDELT lanes explicitly bounded to a 24-hour lookback, 100 max records, and
  one request per second.

It does not include Google News RSS, Google Trends, account-based source access,
browser automation, access-control bypasses, paywall bypass, or private data
collection.

## RSS Feeds

The RSS entries are listed in pack order:

- `Fashionista`: general fashion media and industry news.
- `Fashion Week Daily`: fashion media and celebrity style.
- `FashionUnited`: fashion industry and retail news.
- `The Industry Fashion`: brand and industry news.
- `Highsnobiety`: streetwear and culture signals.
- `WWD`: trade media and industry news.
- `Vogue`: runway, fashion week, and celebrity style.
- `Business of Fashion`: trade, luxury, retail, and emerging-designer coverage.
- `Red Carpet Fashion Awards`: celebrity red-carpet styling.
- `PurseBlog`: bags, handbags, accessories, and luxury product signals.

## Self-Hosted RSSHub

RSSHub is a mature, MIT-licensed, community-maintained feed generator that turns
sites and platforms without native feeds into RSS/Atom. Self-hosting it lets you
broaden Fashion Radar coverage of official sites and news without fragile
per-site scraping. Fashion Radar already supports `type: rsshub` sources
(collected by the same RSS collector).

Run a local RSSHub instance with Docker (pin a release tag in production rather
than relying on `latest`):

```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub:latest
```

Then add a Fashion Radar source pointing at a local RSSHub route:

```yaml
- name: "Example Site via RSSHub"
  type: rsshub
  url: "http://localhost:1200/example/site"
```

Users remain responsible for respecting each upstream site's terms and robots
rules. RSSHub routes are community-maintained and may break when upstream sites
change. RSSHub-sourced signals are local observed signals only; they provide no
demand proof and no platform coverage verification.

## HTML And Sitemap Sources

For sites that publish article pages but no feed, use `type: html` with one or
more seed URLs (requires the optional `article` extra for trafilatura
extraction):

```yaml
- name: "Brand X Newsroom"
  type: html
  url: "https://brandx.example/news"
  article: { enabled: true, respect_robots_txt: true, max_summary_chars: 500 }

- name: "Designer Y Press"
  type: html
  seed_urls:
    - "https://designery.example/press"
    - "https://designery.example/collections"
```

For large sites that publish a sitemap, use `type: sitemap` with the sitemap or
site-root URL; article URLs are discovered and extracted through the same
robots-respecting path (bounded per run):

```yaml
- name: "Fashion News Daily"
  type: sitemap
  url: "https://fashionnewsdaily.example/sitemap.xml"
```

HTML and sitemap sources respect robots.txt and configured paywalled-domain
skips, do not crawl or follow links, and provide no demand proof and no
platform coverage verification.

## Xiaohongshu (Opt-In)

Xiaohongshu (小红书) acquisition is opt-in and use-at-your-own-risk. Fashion
Radar reads notes from an external `xiaohongshu-mcp` server (which you install,
run, and log into separately) over its local MCP HTTP endpoint; it does not
handle login or store cookies itself.

```yaml
- name: "Xiaohongshu: The Row"
  type: xiaohongshu
  query: "The Row handbag"
  xiaohongshu:
    endpoint: "http://localhost:18060/mcp"
    max_notes_per_run: 20
```

Users are responsible for respecting Xiaohongshu's terms. Signals are local
observed only; they provide no demand proof and no platform coverage
verification.

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
  "source_count": 20,
  "enabled_count": 20,
  "disabled_count": 0,
  "type_counts": {
    "gdelt": 10,
    "rss": 10
  },
  "tag_counts": {
    "accessories": 2,
    "bags": 1,
    "beauty": 1,
    "brand_news": 2,
    "celebrity_style": 4,
    "creative_directors": 1,
    "culture": 1,
    "designer_brands": 2,
    "emerging_designers": 2,
    "executive_moves": 1,
    "fashion_media": 4,
    "fashion_week": 2,
    "footwear": 1,
    "gdelt": 10,
    "handbags": 1,
    "industry_news": 6,
    "luxury": 4,
    "products": 2,
    "red_carpet": 1,
    "resale": 1,
    "retail": 3,
    "runway": 2,
    "shoes": 2,
    "streetwear": 2,
    "trade_media": 2
  },
  "findings": []
}
```

See [source-pack-quality.md](source-pack-quality.md) for finding codes,
severity meanings, and tag/weight tuning guidance.

## Check Source Liveness

After the local YAML lint is clean, run a bounded live diagnostic when you want
to know whether the configured public RSS/RSSHub feed URLs and GDELT query lanes
are reachable today:

```bash
uv run fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml
uv run fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml --format json
```

`source-liveness` prints table or JSON diagnostics only. It does not collect
items, store rows, score entities, write reports, open SQLite, fetch article
pages, or prove demand or coverage.

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

Original RSS endpoints were checked during Stage 7 planning on 2026-06-12.
Vogue, Business of Fashion, Red Carpet Fashion Awards, and PurseBlog RSS
endpoints were checked during Stage 197 planning on 2026-06-25. Fashionista,
Fashion Week Daily, The Industry Fashion, Highsnobiety, and WWD direct RSS
endpoints were normalized during Stage 201 planning on 2026-06-25. RSS
availability can change without notice. If a source fails, disable it or
replace it with a feed you have verified.

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

The GDELT entries are broad starter queries grouped into these current lanes:

- `GDELT Luxury Fashion`: luxury/designer fashion and fashion week signals.
- `GDELT Celebrity Style`: celebrity style and red carpet looks.
- `GDELT Bags Shoes Products`: designer bags, handbags, sneakers, ballet flats,
  and loafers.
- `GDELT Emerging Designers`: emerging and independent designers plus LVMH Prize
  and ANDAM fashion signals.
- `GDELT Runway Fashion Week`: runway shows, fashion week schedules, and
  collection coverage.
- `GDELT Designer Brand Momentum`: designer brands, quiet luxury, heritage
  fashion houses, and independent fashion labels.
- `GDELT Retail Resale Fashion`: fashion retail, luxury retail, resale
  marketplaces, and consignment signals.
- `GDELT Footwear Sneakers`: sneakers, footwear, loafers, ballet flats, and
  boots.
- `GDELT Creative Director Moves`: creative director, artistic director, and
  leadership moves at fashion houses and luxury brands.
- `GDELT Beauty Fashion Crossover`: beauty, fragrance, makeup, and skincare
  signals tied to fashion brands, designers, and luxury.

Tune the query strings, `max_records`, and source weights for your own research
needs. Scores only reflect the configured source set.
