# ROW ONE Daily Site Design

## Goal

Build the first ROW ONE website layer on top of Fashion Radar: a local, professional
fashion-news site that turns collected fashion signals into an organized daily edition
with bilingual UI, detail pages, a local static server, and latest-edition cleanup.

## User Requirements

- Site name and app name: **ROW ONE**.
- Run locally first; deployment is not part of this stage.
- Later remote access should work through an IP address and port.
- The daily refresh target is 04:00 local machine time.
- The site must feel like a fashion publication, not an engineering dashboard.
- It should show domestic and international fashion news.
- It should support Chinese and English switching.
- Readers can click from the homepage into detail pages.
- Each daily run saves the current edition locally.
- The next daily refresh removes the prior ROW ONE edition artifacts to avoid disk growth.
- Generated imagery may use the local Open Design installation. The site must still work
  without image generation.

## Chosen Approach

Add a static ROW ONE edition generator inside the existing Python package. The generator
will consume the existing Fashion Radar report model plus recent collected items, organize
them into editorial sections, and render static HTML/CSS/JSON files. A lightweight stdlib
HTTP server command will serve the generated directory on `127.0.0.1:<port>` by default
and supports explicit `0.0.0.0:<port>` binding for local-network testing.

This is the safest first stage because it reuses the existing collect -> match -> score ->
report pipeline and avoids adding a web framework, database migration, JavaScript build
system, paid API, or platform connector.

## Architecture

```text
Configured public sources / local imports
  -> existing Fashion Radar collect / match / report
  -> ROW ONE edition builder
  -> static site renderer
  -> generated site directory
  -> stdlib local HTTP server on IP:port
```

### Components

- `fashion_radar.row_one.models`: typed edition, section, story, link, and language-copy
  models. These are presentation models only and do not alter the existing report models.
- `fashion_radar.row_one.edition`: converts `DailyReport` and recent collected items into
  editorial sections:
  - `Top Stories / 今日重点`
  - `Brand Moves / 品牌动态`
  - `Celebrity Style / 明星穿搭`
  - `Hot Products / 热门包鞋单品`
  - `Rising Radar / 上升雷达`
- `fashion_radar.row_one.render`: writes `index.html`, `details/*.html`,
  `assets/row-one.css`, `assets/row-one.js`, and `data/edition.json`.
- `fashion_radar.row_one.server`: serves a generated site directory with
  `http.server.ThreadingHTTPServer`.
- `fashion_radar.workflows`: adds a small workflow wrapper that builds the existing daily
  report and then renders ROW ONE output.
- `fashion_radar.cli`: adds `row-one build`, `row-one serve`, and `row-one schedule`
  commands.

### Bilingual Behavior

The first stage provides bilingual UI chrome and deterministic bilingual editorial labels.
Story titles preserve the original source title. Short summaries use existing safe snippets
and deterministic templates in both languages when possible. When a source item only has one
language, ROW ONE still emits non-empty Chinese and English fields by pairing the source text
with deterministic context labels such as "Original source summary" and "来源摘要". This avoids
pretending to translate while keeping the language toggle useful. A future enrichment stage can
add optional local or API-backed translation/summarization behind explicit configuration.

### Visual Direction

ROW ONE should look like a restrained fashion media product:

- monochrome editorial base with off-white paper, black typography, and a muted oxblood
  accent;
- large masthead, dense but readable story hierarchy, and strong image slots;
- no card-heavy admin dashboard styling;
- no external CDN assets;
- CSS-only responsive layout for mobile and desktop;
- optional Open Design-generated hero image can be dropped into the generated assets, but
  tests and default rendering must not require image generation.

### Daily Refresh And Cleanup

`row-one build --latest-only` removes only known ROW ONE generated children before writing the
new edition: `index.html`, `.row-one-site`, `details/`, `assets/`, and `data/`. It does not
delete the entire user-supplied output directory and leaves unrelated files in place. This
cleanup applies to ROW ONE site artifacts, not necessarily the existing Fashion Radar SQLite
database. The database retention remains configurable because trend and heat movement
calculations need a short baseline window. The default test path keeps disk usage small by
writing one current static site and allowing existing `clean` commands to prune raw metadata
separately.

### Scheduling

`row-one schedule --time 04:00` prints cron and systemd examples that first run the existing
Fashion Radar collection/report workflow and then call `row-one build --latest-only` against
the refreshed local data. The command mirrors the existing scheduling approach and does not
install timers or modify the host automatically.

### Error Handling

- Empty reports render a professional empty-state edition.
- Missing source URLs render non-clickable story detail pages instead of broken links.
- Unsafe URLs are omitted from HTML links.
- Detail page paths use a bounded ASCII slug plus a stable short hash so duplicate
  headlines do not collide and non-Latin titles do not create unsafe filenames.
- `latest-only` cleanup is scoped to known ROW ONE generated children inside the configured
  output directory.
- The server refuses to serve a missing directory with a clear CLI error.

### Testing

- Unit tests cover section assignment, bilingual copy, safe URL handling, detail slug
  stability, latest-only cleanup, and server URL formatting.
- CLI tests cover build, serve argument validation, and schedule output shape.
- Snapshot-style assertions cover key HTML strings without relying on pixel tests.

## Out Of Scope For This Stage

- No new social-platform scraping, connector execution, cookie handling, or browser automation.
- No paid API requirement.
- No login-based platform access by default.
- No permanent historical ROW ONE edition archive.
- No production deployment automation.
- No compliance-review product feature.
- No LLM translation or summarization dependency in the default path.

## Success Criteria

- A user can run one command to generate a ROW ONE static site from local Fashion Radar data.
- The generated homepage has bilingual controls and links into detail pages.
- A user can run one command to serve it on an IP-addressable port.
- A user can print 04:00 cron/systemd examples.
- Running with latest-only cleanup replaces only known generated ROW ONE children
  and preserves unrelated files in the output directory.
- Tests and lint pass without requiring Open Design, image API keys, paid APIs, or platform
  credentials.
