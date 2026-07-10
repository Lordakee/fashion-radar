# Fashion Radar

Fashion Radar is a free-first, local-first fashion intelligence tool for daily
tracking of fashion signals across allowed public sources. It collects RSS or
RSSHub-compatible feeds and GDELT metadata, matches configurable brands,
designers, celebrities, products, categories, and trends, then writes local
Markdown, JSON, and companion HTML reports and a read-only dashboard. It can
also surface candidate signals as observed phrases from configured sources and
imported local signals that need review before being tracked.

The MVP is built for personal research and editorial monitoring. It is not a
full social-listening service, and its heat scores are local metrics based only
on the sources you configure and local signals you import.

## Start Here

For first-run onboarding, start with [docs/first-run.md](docs/first-run.md).
The Manual repo-local sample is the recommended first-time path when you want
inspectable output, local SQLite state, dated reports, and dashboard data.
For a source-checkout first run, follow [docs/first-run.md](docs/first-run.md)
and then inspect the same sample in the ROW ONE local static site. The
source-checkout smoke covers the ROW ONE manifest and serve dry-run path.
The first-run smoke now performs a local HTTP serve fetch, not just
`serve --dry-run`, so it also exercises the generated local routes over HTTP.

Use Automated source-checkout smoke or Installed-wheel smoke as verification
paths when you need disposable source-tree or package checks. They are not the
main exploratory path.

Entity packs are an optional local matching layer. Copy one after `init` and
before `match`/`report` when you want a broader local watchlist; see
[docs/entity-packs.md](docs/entity-packs.md).

- [ROW ONE local static site](docs/row-one.md)

All onboarding paths are local-first. This does not add live platform
collection, does not add social connectors, and does not prove demand, rank
brands, or verify platform coverage.

## What It Does

- Collects public RSS/Atom, RSSHub-compatible, and GDELT Doc API signals, plus configured HTML seed pages and sitemap-discovered article URLs via trafilatura (optional `article` extra), respecting robots.txt and paywalled-domain skips.
- Imports local user-provided CSV/JSON signal files that you are authorized to
  process.
- Preserves optional imported `platform` labels as local provenance in SQLite
  and imported-row review output only.
- Lints local community signal CSV/JSON files against the handoff contract
  before import, without fetching URLs or importing rows.
- Supports a documented local CSV/JSON handoff path for user-provided
  external/community exports, with validation and review commands. This handoff
  surface is supported as-is and frozen for v0.1.x.
- Reviews retained `manual_import` rows already stored in local SQLite without
  importing, collecting, matching, scoring, or writing reports.
- Reviews privacy-safe imported-only entity evidence for one matched entity
  from retained local rows without scraping, browser automation, platform APIs,
  or account or cookie behavior.
- Stores conservative metadata in a local SQLite database.
- Matches entities with deterministic alias and context rules.
- Computes transparent heat scores over current and baseline windows.
- Surfaces untracked candidate signals as observed phrases from configured
  sources and imported local signals that need review.
- Compares local observed entity and candidate signal deltas between scoring
  snapshots.
- Explains local observed trend deltas with a read-only `trend-explanations`
  sidecar over configured sources and imported local signals. The explanation
  output needs review, provides no demand proof, and provides no platform
  coverage verification.
- Generates daily Markdown, JSON, and companion HTML reports with source attribution plus a
  Daily Brief Heat Narrative for local observed tracked signals, candidate
  phrases that need review, and source caveats from configured sources and
  imported local signals. It provides no demand proof and no platform coverage
  verification.
- Generates the optional ROW ONE local static site from existing daily report
  data for editorial review, with no new data acquisition, no demand proof, and
  no platform coverage verification. The active app JSON payload is
  `row-one-app/v7`; `edition_brief`, `signal_synthesis`, `content_sections`,
  `detail_sections`, `evidence_summary`, `daily_digest`, and `story_directory`
  let app clients render a daily overview, local observed signal synthesis,
  section rails, a daily briefing, and route lookups from local JSON without
  scraping HTML. The generated experience is a
  professional static website with an edition rail and article contents for
  local editorial review. ROW ONE content cards also include `why_it_matters`
  and `signal_context`, and generated detail pages can render a Detail
  Information Map from existing story fields.
- Can package optional local digest artifacts such as latest report copies, a
  report index, and a local `.eml` handoff file.
- Provides an optional local Streamlit dashboard for read-only inspection.

## What It Does Not Do

Fashion Radar v0.1.0 does not include broad platform collection, account-based
source access, access-control bypasses, private data collection, or hidden
platform workarounds. Google News is not part of the default source set.
Manual signal import is a local input path, not a platform connector or source
acquisition guide.
Stored imported `platform` labels are local provenance metadata only; they are
not scraping, crawling, social connectors, source acquisition, platform
coverage, or demand proof.

The public MVP non-goals stay aligned with the project brief: no paid API
requirement, no account pool, no proxy pool, no high-frequency scraping, no
automated posting, no private user data collection, no full-platform
Instagram, TikTok, X, or Xiaohongshu coverage claim, and no login-cookie,
proxy-pool, CAPTCHA-bypass, or paywall-bypass behavior by default; login-based
social-platform collection is opt-in and use-at-your-own-risk (Phase 2 adds
Xiaohongshu).

ROW ONE is a local static site built from existing daily report data. It adds
no new data acquisition, no scraping, no platform APIs, no paid APIs, no
translation service, no deployment automation, no demand proof, and no platform
coverage verification. Its active app contract is `row-one-app/v7`, with
`edition_brief`, `signal_synthesis`, `content_sections`, `detail_sections`,
`evidence_summary`, and `daily_digest` so app clients can render a daily
overview, brand/product/designer/person signal summaries, section rails, and a
daily briefing without scraping HTML. `edition_brief` is derived from existing
ROW ONE stories, content sections, digest blocks/topics, route data, and safe
evidence counts; it is not a collection or ranking layer. `daily_digest.briefing_topics`
lets clients render an organized app-ready briefing instead of a flat list of links. `briefing_topics`
is presentation organization over existing ROW ONE stories; it does not add
source collection, ranking changes, demand proof, platform coverage
verification, or external enrichment. The ROW ONE homepage can render
the first four daily_digest.briefing_topics from the same data/edition.json
payload, while app clients still use data/edition.json without scraping HTML. See
[docs/row-one.md](docs/row-one.md).
`signal_synthesis` reshapes `daily_digest.briefing_topics` into local observed
brand/product/designer/person signal summaries with review required boundaries;
it is not demand proof, platform heat, collection, ranking, or external
enrichment. When saved local article bodies are available, ROW ONE also renders
a homepage Daily Local Intelligence section from those local sidecars. It
groups strongest reads, brand watch, product watch, and heat movers from the
saved article paragraphs and structured references. Daily cards include
compact content segments from the saved local article sections so readers can
scan organized source-backed takeaways, entity context, and product signals
without leaving the generated site. Homepage Daily Local Intelligence cards
include local saved-text and paragraph drilldown links so readers can jump from
organized takeaways into anchored saved local paragraphs. Generated detail pages link content-section
paragraph badges to anchored saved local paragraphs when the referenced
paragraph is available, and ROW ONE writes the optional
generated artifact `data/local-intelligence.json` next to the static site data.
Detail-page reference cards can include saved-source paragraph excerpts for
matched brands, designers, people, bags, shoes, and products while keeping
paragraph badges linked to the local article body. Structured local articles
also include a detail-page local article map so readers can jump between the
brief, organized content cards, and saved text. Local article takeaways
prioritize source-backed signal paragraphs with explicit brand, designer,
person, bag, shoe, or product matches before falling back to the first saved
paragraphs.
ROW ONE saved sidecar JSON and generated detail pages also expose local article
body provenance through `body_source`: `extracted` means the saved body came
from usable extracted article text, `summary_fallback` means ROW ONE generated
a publishable local article body from the story summary/editorial fallback when
extraction was skipped, failed, or unusable, and `skipped` means no publishable
saved body was written. This sidecar/data detail-page provenance does not change
`data/edition.json`, does not change `row-one-runtime/v1`, and does not add
compliance-review behavior.
Stage 311 adds a generated-site saved text digest on ROW ONE detail pages:
existing saved local paragraphs and existing organized sidecar sections are
presented as scan-first cards for read-first context, people/brands, products,
and source structure. This is a detail-page saved text digest only; it does not
change `row-one-app/v7`, does not change `data/edition.json`, uses existing `data/articles/<story-id>.json` sidecars, does not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change detail routes, does not change paragraph anchors, does not change schemas, does not add source collection, does not add scoring, and does not add llm calls.
Stage 312 adds homepage saved article coverage for ROW ONE: existing saved
local article sidecars are summarized as a homepage coverage strip with saved
article counts, saved paragraph counts, source counts, source chips, and a read
queue linking into local detail-page digests. This is homepage saved article
coverage only; it uses existing `data/articles/<story-id>.json` sidecars, does not change `row-one-app/v7`, does not change `data/edition.json`, does not
change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not write a new json artifact, does not change detail routes, does not change
paragraph anchors, does not change schemas, does not add source collection,
does not add scoring, and does not add llm calls.
Stage 313 adds homepage saved article briefs for ROW ONE: existing saved local
article sidecars are surfaced as capped homepage brief cards with a lead saved
text excerpt, people/brands chips, product chips, source context, and links
into local detail-page digests. This is homepage saved article briefs only; it
uses existing `data/articles/<story-id>.json` sidecars, does not change
`row-one-app/v7`, does not change `data/edition.json`, does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not write a
new json artifact, does not change detail routes, does not change paragraph
anchors, does not change schemas, does not add source collection, does not add
scoring, and does not add llm calls.
Stage 314 adds local article observability for ROW ONE: build, preview,
refresh, and `row-one status --json` report saved local articles and saved local
paragraphs from valid generated `data/articles/<story-id>.json` sidecars.
Build, preview, and refresh report the current render's local article metrics;
`row-one status --json` reports the sidecars present on disk. The saved local
paragraph count is the nonblank saved body indicator; full article body
extraction requires sources with `row_one_article.enabled: true` and the
optional article extraction dependency. This does not change `row-one-app/v7`,
does not write a new json artifact, does not add source collection, does not add
scoring, and does not add llm calls. Use `--latest-only` when you want a status
sidecar count that reflects only the current generated site.
Stage 315 adds ROW ONE article readiness diagnostics: `row-one article-readiness`
checks the selected `sources.yaml`, the generated ROW ONE site, saved local
article sidecars, saved local paragraphs, and current story source coverage
without collecting sources, fetching article pages, mutating SQLite, changing
`row-one-app/v7`, or writing a new generated JSON artifact. It does not change
`row-one-app/v7`, does not write a new generated JSON artifact, does not add
source collection, does not fetch article pages, does not add scoring, and does
not add llm calls. Use it when `row-one build` reports zero saved local
articles; older platformdirs config directories may still contain source packs
without `row_one_article.enabled: true`, while the current starter config can
produce saved local article sidecars when matching stories exist.
Stage 316 adds local article content organization to the generated ROW ONE
homepage. It is generated-site only and organizes existing
`data/articles/<story-id>.json` sidecars, existing saved local paragraphs, and
existing `content_sections` into scan-first groups. It does not change
`row-one-app/v7`, does not change `data/edition.json`, does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change
detail routes, does not change paragraph anchors, does not change schemas, does
not write a new json artifact, does not add source collection, does not fetch
article pages, does not add scoring, does not add llm calls, does not add
connectors, and is not a compliance review feature.

Stage 317 adds detail saved paragraph previews to generated ROW ONE detail
pages. It is generated-site only and turns existing
`data/articles/<story-id>.json` sidecars, existing saved local paragraphs, and
existing `content_sections` into compact paragraph previews that link to
existing paragraph anchors. It does not change `row-one-app/v7`, does not change
`data/edition.json`, does not change `row-one-manifest/v1`, does not change
`row-one-runtime/v1`, does not change detail routes, does not change paragraph
anchors, does not change schemas, does not write a new json artifact, does not
add source collection, does not fetch article pages, does not add scoring, does
not add llm calls, does not add connectors, and is not a compliance review
feature.

Stage 318 adds detail continue reading to generated ROW ONE detail pages. It is
generated-site only and selects up to three next reads from the same daily
edition, preferring same-section stories before filling from other sections and
linking only through validated detail routes. It does not change
`row-one-app/v7`, does not change `data/edition.json`, does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change
schemas, does not write a new json artifact, does not add source collection,
does not fetch article pages, does not add scoring, does not add llm calls, does
not add connectors, and is not a compliance review feature.
Stage 319 adds detail signal briefing to generated ROW ONE detail pages. It is
generated-site only and organizes the existing story summary, signal context,
safe evidence count, existing story references, and existing saved local article
sections into a compact Signal Briefing panel before the detail summary. It uses
existing `data/articles/<story-id>.json` sidecars when present and links only to
existing paragraph anchors. It does not change `row-one-app/v7`, does not change
`data/edition.json`, does not change `row-one-manifest/v1`, does not change
`row-one-runtime/v1`, does not change detail routes, does not change paragraph
anchors, does not change schemas, does not write a new json artifact, does not
add source collection, does not fetch article pages, does not add scoring, does
not add llm calls, does not add connectors, and is not a compliance review
feature.
Stage 320 adds homepage Daily Edit to generated ROW ONE index pages. It is
generated-site only and turns the existing `edition_brief`,
existing `signal_synthesis`, existing `daily_digest.briefing_topics`, existing
`daily_digest.blocks`, and existing story directory payload into a scan-first
editorial briefing with safe internal detail links. It does not change
`row-one-app/v7`, does not change `data/edition.json`, does not add `daily_edit`,
does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change
schemas, does not write a new json artifact, does not add source collection,
does not fetch article pages, does not add scoring, does not add llm calls, does
not add connectors, and is not a compliance review feature.
Stage 380 adds generated-site only Saved Local Article Related-Read Evidence Bridge rows inside existing related saved local read cards on `articles/<story-id>.html`; it reuses Stage 377/378 related-read cards and lanes, current-edition saved local article sidecars, existing shared reference keys, existing item-level paragraph indices, generated local article page routes, and existing paragraph anchors to show a compact current-paragraph to next-read-paragraph evidence bridge without changing app-facing contracts; it does not create `data/saved-local-article-related-read-evidence-bridge.json`, does not create `data/local-article-related-read-evidence-bridge.json`, does not create `data/related-read-evidence-bridge.json`, does not create `saved-local-article-related-read-evidence-bridge.html`, does not create `local-article-related-read-evidence-bridge.html`, does not create `related-read-evidence-bridge.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full related articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
Stage 379 adds generated-site only Saved Local Article Cross-Surface Organization Trail links inside the existing Saved Article Local Reading Companion on `articles/<story-id>.html`; it reuses existing saved article library groups, existing saved article content organization groups, generated local article page routes, existing article library cards, and existing saved article library organization groups to link each local article back to its Filed In / 内容归档 context; it does not create `data/saved-local-article-cross-surface-organization-trail.json`, does not create `data/local-article-cross-surface-organization-trail.json`, does not create `data/cross-surface-organization-trail.json`, does not create `saved-local-article-cross-surface-organization-trail.html`, does not create `local-article-cross-surface-organization-trail.html`, does not create `cross-surface-organization-trail.html`, does not create source shelf links, does not create new article-source sidecars, does not create new route families, does not alter `details/<story-id>.html`, does not publish full articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 378 adds generated-site only Saved Local Article Related Read Lanes inside the existing post-body Saved Local Article Related Reads section on `articles/<story-id>.html`; it reuses the Stage 377 same-site related-read cards, existing card reasons, existing source labels, existing reference chips, generated local article page routes, and existing paragraph anchors to organize next reads by shared signal, same ROW ONE section, and same source while preserving the current flat-card fallback; it does not create `data/saved-local-article-related-read-lanes.json`, does not create `data/local-article-related-read-lanes.json`, does not create `data/related-read-lanes.json`, does not create `saved-local-article-related-read-lanes.html`, does not create `local-article-related-read-lanes.html`, does not create `related-read-lanes.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full related articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 377 adds generated-site only Saved Local Article Related Reads inside `articles/<story-id>.html` after the saved local article body; it reuses current-edition stories, current-edition saved local article sidecars, content-section references, generated local article page routes, existing paragraph anchors, and existing local reading companion related-item hrefs to show post-body same-site next reads while excluding articles already recommended by the pre-body companion; it does not create `data/saved-local-article-related-reads.json`, does not create `data/local-article-related-reads.json`, does not create `data/related-reads.json`, does not create `saved-local-article-related-reads.html`, does not create `local-article-related-reads.html`, does not create `related-reads.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full related articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

Stage 376 adds generated-site only Daily Local News Timeline inside `index.html` between Daily Local Theme Summary Strip and Daily Local Article Intelligence Brief; it reuses current-edition stories, current-edition saved local article sidecars, generated local article page routes, existing saved local paragraphs, and existing paragraph anchors to show today's saved local fashion stories in publication-time order with short same-site excerpts without changing app-facing contracts; it does not create `data/daily-local-news-timeline.json`, does not create `data/local-news-timeline.json`, does not create `data/news-timeline.json`, does not create `daily-local-news-timeline.html`, does not create `local-news-timeline.html`, does not create `news-timeline.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 375 adds read-only generated-site Local Article Content Health to `row-one status` and `row-one ops-check`; it reuses current generated `data/articles/*.json` saved local article sidecars, existing `articles/<story-id>.html` pages, existing local article section anchors, existing saved local article body container anchors, existing saved paragraph anchors, and existing local content-section anchors to verify that already-saved local article bodies are rendered inside same-site article pages without changing app-facing contracts; it adds CLI-only content-health status payload fields, but it does not create `data/local-article-content-health.json`, does not create `data/article-content-health.json`, does not create `data/content-health.json`, does not create `local-article-content-health.html`, does not create `article-content-health.html`, does not create `content-health.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, `articles/<story-id>.html`, or detail page rendering, does not publish full articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 374 adds read-only generated-site Saved Local Article Route Health to `row-one status` and `row-one ops-check`; it reuses current generated `data/articles/*.json` saved local article sidecars, current validated story ids, existing `index.html`, existing `articles/index.html`, and existing `articles/<story-id>.html` routes to verify that already-saved local article bodies are reachable through same-site generated article pages without changing app-facing contracts; it adds CLI-only route-health status payload fields, but it does not create `data/local-article-route-health.json`, does not create `data/article-route-health.json`, does not create `data/route-health.json`, does not create `local-article-route-health.html`, does not create `article-route-health.html`, does not create `route-health.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, `articles/<story-id>.html`, or detail page rendering, does not publish full articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 373 adds generated-site only Local Article Body Section Markers inside the saved body of `articles/<story-id>.html`; it reuses current-edition saved local article sidecars, existing saved local paragraphs, existing local article content sections, existing content-section item bodies, existing item labels, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to insert compact section-start markers before the first rendered saved paragraph filed under each existing content section without changing app-facing contracts; it does not create `data/local-article-body-section-markers.json`, does not create `data/article-body-section-markers.json`, does not create `data/body-section-markers.json`, does not create `local-article-body-section-markers.html`, does not create `article-body-section-markers.html`, does not create `body-section-markers.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 372 adds generated-site only Daily Local Reading Itinerary inside `index.html` between the Daily Local Saved Article Organizer and Saved Article Content Organization; it reuses current-edition stories, current-edition saved local article sidecars, generated local article page routes, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing content-section item bodies, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to arrange today's saved articles into a short Start Here, Skim Next, and Evidence Trail reading sequence with article-backed excerpts, reason labels, and same-site reader anchors without changing app-facing contracts; it does not create `data/daily-local-reading-itinerary.json`, does not create `data/local-reading-itinerary.json`, does not create `data/reading-itinerary.json`, does not create `daily-local-reading-itinerary.html`, does not create `local-reading-itinerary.html`, does not create `reading-itinerary.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 371 adds generated-site only Daily Local Saved Article Organizer inside `index.html` between the Daily Local Article Intelligence Brief and Saved Article Content Organization; it reuses current-edition stories, current-edition saved local article sidecars, generated local article page routes, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing content-section item bodies, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to organize today's saved articles into short homepage editorial lanes with article-backed excerpts, reference chips, and same-site reader anchors without changing app-facing contracts; it does not create `data/daily-local-saved-article-organizer.json`, does not create `data/local-saved-article-organizer.json`, does not create `data/saved-article-organizer.json`, does not create `daily-local-saved-article-organizer.html`, does not create `local-saved-article-organizer.html`, does not create `saved-article-organizer.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 370 adds generated-site only Daily Local Article Intelligence Brief inside `index.html` between the Daily Local Theme Summary Strip and Saved Article Content Organization; it reuses current-edition stories, current-edition saved local article sidecars, Stage 369 local article intelligence briefs, generated local article page routes, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to summarize today's saved articles into a homepage opening read, entity lanes, article cards, and same-site reader routes without changing app-facing contracts; it does not create `data/daily-local-article-intelligence-brief.json`, does not create `data/local-article-intelligence-brief.json`, does not create `data/article-intelligence-brief.json`, does not create `daily-local-article-intelligence-brief.html`, does not create `local-article-intelligence-brief.html`, does not create `article-intelligence-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 369 adds generated-site only Local Article Intelligence Brief inside `articles/<story-id>.html` between the Local Article Body Organizer and the saved local article body; it reuses current-edition saved local article sidecars, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to summarize each saved article body into an opening signal, entity lanes, paragraph evidence trail, and local reader route without changing app-facing contracts; it does not create `data/local-article-intelligence-brief.json`, does not create `data/article-intelligence-brief.json`, does not create `data/intelligence-brief.json`, does not create `local-article-intelligence-brief.html`, does not create `article-intelligence-brief.html`, does not create `intelligence-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 368 adds generated-site only Local Article Body Organizer inside `articles/<story-id>.html` between the Local Article Content Segment Deck and the saved local article body, after Saved Article Key Signals in the current template order; it reuses current-edition saved local article sidecars, existing saved local paragraphs, existing local article content sections, existing item-level content-section paragraph indices, existing content-section anchors, and existing paragraph anchors to summarize each saved article body into filed section rows, an unfiled paragraph queue, and a read-first paragraph route without changing app-facing contracts; it does not create `data/local-article-body-organizer.json`, does not create `data/article-body-organizer.json`, does not create `data/body-organizer.json`, does not create `local-article-body-organizer.html`, does not create `article-body-organizer.html`, does not create `body-organizer.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 367 adds generated-site only Saved Article Filing Inbox inside `articles/index.html`; it reuses current-edition saved local article sidecars, existing local article page routes, existing saved local paragraphs, existing item-level content-section paragraph indices, existing body-source labels, and existing paragraph anchors to aggregate unfiled saved paragraphs across the article library without changing app-facing contracts; it does not create `data/saved-article-filing-inbox.json`, does not create `data/article-filing-inbox.json`, does not create `data/filing-inbox.json`, does not create `saved-article-filing-inbox.html`, does not create `article-filing-inbox.html`, does not create `filing-inbox.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 366 adds generated-site only Local Article Body Filing Cues inside the saved body paragraphs of `articles/<story-id>.html` pages; it reuses current-edition saved local article sidecars, existing saved local paragraphs, existing local article content sections, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to mark each rendered saved paragraph as filed under existing organization or unfiled saved text without changing app-facing contracts; it does not create `data/local-article-body-filing-cues.json`, does not create `data/article-body-filing-cues.json`, does not create `data/body-filing-cues.json`, does not create `data/paragraph-filing-cues.json`, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.
Stage 365 adds generated-site only Local Article Content Segment Deck inside `articles/<story-id>.html` pages after Saved Article Key Signals and before the saved local article body; it reuses current-edition saved local article sidecars, existing local article content sections, existing content-section anchors, existing paragraph anchors, existing item references, and existing body-source labels to turn already-saved local text into compact content segment cards without changing app-facing contracts; it does not create `data/local-article-content-segment-deck.json`, does not create `data/article-content-segment-deck.json`, does not create `data/content-segment-deck.json`, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Stage 364 adds generated-site only Daily Local Theme Summary Strip as a homepage-only section inside `index.html` after Daily Local Coverage Map and before Saved Article Content Organization; it reuses current-edition stories, existing saved local article content organization groups and cards, group titles, group deks, card leads, existing card references, already-saved local article paragraphs, generated local article page routes, and existing local article content-section and paragraph anchors to summarize saved local text by theme without changing app-facing contracts; it does not create `data/daily-local-theme-summary-strip.json`, does not create `data/local-theme-summary-strip.json`, does not create `data/theme-summary-strip.json`, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Stage 363 adds generated-site only Daily Local Coverage Map as a homepage-only section inside `index.html` after Daily Local Source Desk and before Saved Article Content Organization; it reuses current-edition stories, existing saved local article content organization groups and cards, already-saved local article paragraphs, existing source names, existing card references, generated local article page routes, and existing local article content-section and paragraph anchors to cross-tab saved local article sources against editorial organization buckets without changing app-facing contracts; it does not create `data/daily-local-coverage-map.json`, does not create `data/local-coverage-map.json`, does not create `data/coverage-map.json`, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Stage 362 adds generated-site only Daily Local Source Desk as a homepage-only section inside `index.html` after Daily Local Article Reading Brief and before Saved Article Content Organization; it reuses current-edition stories, already-saved local article paragraphs, existing local article brief sections, existing local article content sections, existing body-source labels, existing source names, existing story references, generated local article page routes, and existing paragraph anchors to organize saved local text into compact source-watch, local-context, and source-route lanes without changing app-facing contracts; it does not create `data/daily-local-source-desk.json`, does not create `data/local-source-desk.json`, does not create `data/source-desk.json`, does not create new route families, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Stage 361 adds generated-site only Daily Local Article Reading Brief as a homepage-only section inside `index.html` after Daily Local Article Capsules and before Saved Article Content Organization; it reuses current-edition stories, already-saved local article paragraphs, existing local article brief sections, existing local article content sections, existing body-source labels, existing story references, generated local article page routes, and existing paragraph anchors to organize saved local text into compact read-first, brand-watch, and product-watch lanes without changing app-facing contracts; it does not create `data/daily-local-article-reading-brief.json`, does not create `data/daily-local-reading-brief.json`, does not create `data/article-reading-brief.json`, does not create new route families, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Stage 360 adds generated-site only Daily Local Article Capsules as a homepage-only section inside `index.html` after Daily Local Heat Signals and before Saved Article Content Organization; it reuses current-edition stories, already-saved local article paragraphs, existing body-source labels, existing story references, generated local article page routes, and existing paragraph anchors to turn saved local text into compact readable article cards without changing app-facing contracts; it does not create `data/daily-local-article-capsules.json`, does not create `data/daily-local-capsules.json`, does not create `data/article-capsules.json`, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Stage 359 adds generated-site only Daily Local Heat Signals as a homepage-only section inside `index.html` after Daily Local Signal Momentum and before Saved Article Content Organization; it reuses existing `daily_digest.briefing_topics` heat fields, `source_refs`, saved local article availability, and generated local article page routes to focus this MVP on brands and products, including bag/shoe subtype badges from existing source references; it shows current-edition positive heat only, not historical trend deltas, and does not change app contracts, schemas, JSON artifacts, fetching, scoring, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Stage 358 adds generated-site only Daily Local Signal Momentum as a homepage-only section inside `index.html` after Daily Local Key Signals Digest and before Saved Article Content Organization; it reuses Stage 350 Saved Article Daily Signal Leaderboard data to show current-edition support counts only, not historical trend deltas, without changing app-facing contracts; it does not create `data/daily-local-signal-momentum.json`, does not create `data/daily-local-momentum.json`, does not create `data/signal-momentum.json`, and does not change app contracts, schemas, JSON artifacts, fetching, scoring, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Stage 357 adds generated-site only Daily Local Key Signals Digest as a homepage-only section inside `index.html` after Saved Article Briefs and before Saved Article Content Organization; it reuses Stage 356 Saved Article Key Signals from already-saved current-edition local articles and links only to local article pages and anchors to summarize daily Why It Matters, Brands, Products, People, and Themes signals without changing app-facing contracts; it does not create `data/daily-local-key-signals-digest.json`, does not create `data/local-key-signals-digest.json`, does not create `data/daily-key-signals.json`, does not create or modify article-source sidecars, does not create new route families, does not add outbound article URLs as primary navigation, does not alter article detail pages, `articles/index.html`, saved article payloads, app payloads, row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, runtime, manifest, sidecar artifacts, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

Stage 356 adds generated-site only Saved Article Key Signals inside `articles/<story-id>.html` pages after the Stage 355 local section binder and before the saved local article body; it reuses current-edition saved local article sidecars, existing local article brief sections, `RowOneStory.why_it_matters` only as a Why It Matters fallback, existing reference buckets, existing content section titles and item labels, existing paragraph anchors, and existing content-section anchors to turn already-saved local text into compact Why It Matters, Brands, Products, People, and Themes signals without changing app-facing contracts; it does not create `data/saved-article-key-signals.json`, does not create `data/article-key-signals.json`, does not create `data/local-article-key-signals.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not alter Stage 319 detail Signal Briefing, Stage 349 Saved Article Signal Facets, Stage 350 Saved Article Daily Signal Leaderboard, `articles/index.html`, the homepage, or generated data payloads, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

Stage 355 adds generated-site only Saved Article Local Section Binder inside `articles/<story-id>.html` pages; it reuses current-edition saved local article sidecars, existing local article page routes, existing safe detail digest and content-section anchors, existing paragraph anchors, existing body-source labels, saved paragraph counts, organized section counts, references, and evidence counts to bind organized local sections back to already-saved local text without changing app-facing contracts; it does not create `data/saved-article-local-section-binder.json`, does not create `data/article-local-section-binder.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 354 adds generated-site only Saved Article Local Reading Companion inside `articles/<story-id>.html` pages; it reuses current-edition saved local article sidecars, existing local article page routes, existing safe detail digest and content-section anchors, existing paragraph anchors, existing body-source labels, saved paragraph counts, organized section counts, references, and evidence counts to help readers move through already-saved local text without changing app-facing contracts; it does not create `data/saved-article-local-reading-companion.json`, does not create `data/article-local-reading-companion.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 353 adds generated-site only Saved Article Read Next Clusters inside `articles/index.html`; it reuses existing saved article library entries, existing saved article content organization groups, existing local article page hrefs, existing safe detail digest and content-section anchors, existing body-source labels, local leads, references, saved paragraph counts, organized section counts, and evidence counts to organize what to read next without changing app-facing contracts; it does not create `data/saved-article-read-next-clusters.json`, does not create `data/article-read-next-clusters.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 352 adds generated-site only Saved Article Reading Queue inside `articles/index.html`; it reuses existing saved article library entries, existing local article page hrefs, existing safe detail digest anchors, existing body-source labels, saved paragraph counts, and organized section counts to provide a compact local reading sequence without changing app-facing contracts; it does not create `data/saved-article-reading-queue.json`, does not create `data/article-reading-queue.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

Stage 351 adds generated-site only Saved Article Organization Jump Index inside `articles/index.html`; it reuses existing local saved article content organization, existing source routes, existing signal facets, existing daily signal leaderboard data, and existing same-page saved article anchors to provide compact navigation across local saved article surfaces without changing app-facing contracts; it does not create `data/saved-article-organization-jump-index.json`, does not create `data/local-article-organization.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

Stage 350 adds generated-site only Saved Article Daily Signal Leaderboard inside `articles/index.html`; it reuses existing Stage 349 saved article signal facet rows, existing safe local article digest anchors, and existing source names to aggregate brand, product, and theme chips into capped daily support-count rollups without changing app-facing contracts; it does not create `data/saved-article-daily-signal-leaderboard.json`, does not create `data/article-chip-leaderboard.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

Stage 349 adds generated-site only Saved Article Signal Facets inside `articles/index.html`; it reuses the existing saved article library entries, existing saved article content organization cards, existing safe local article page routes, existing safe card detail-path anchors, and existing reference labels to show article-level brand, product, and theme chips without changing app-facing contracts; it does not create `data/saved-article-signal-facets.json`, does not create `data/article-signal-facets.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

Stage 348 adds generated-site only Saved Article Source Routes inside `articles/index.html`; it reuses the existing saved article library source groups, existing saved article source brief rows, existing safe local article page routes, existing safe card detail-path anchors, and existing local article page allowlist to show source-group reading routes without changing app-facing contracts; it does not create `data/saved-article-source-routes.json`, does not create `data/article-source-routes.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.

Stage 347 adds a generated-site only Saved Article Source Brief inside `articles/index.html`; it reuses the existing saved article library source groups, existing saved article content organization cards, existing safe card detail-path anchors, existing local article page allowlist, and existing body-guide excerpt logic to show up to two concise source-contribution bullets per source without changing app-facing contracts; it does not create `data/saved-article-source-brief.json`, does not create `data/article-source-brief.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 346 adds a generated-site only Saved Article Body Guide inside `articles/index.html`; it reuses the existing saved article library cards, existing saved article content organization cards, existing safe card detail-path anchors, existing paragraph evidence anchors, and existing per-card organized snippet slot to show up to two concise body-guide bullets without changing app-facing contracts; it does not create `data/saved-article-body-guide.json`, does not create `data/article-body-guide.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 345 adds a generated-site only Saved Article Daily Summary inside `articles/index.html`; it reuses existing saved article content organization groups, existing organization coverage rows, existing safe card detail-path anchors, existing card references, and existing paragraph indices to summarize the daily saved article library without changing app-facing contracts; it does not create `data/saved-article-daily-summary.json`, does not create `data/daily-saved-article-summary.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 344 adds a generated-site only Saved Article Organization Coverage Matrix inside `articles/index.html`; it reuses existing saved article content organization groups, existing safe card detail-path anchors, existing card references, and existing paragraph indices to show article-by-article organization coverage across groups without changing app-facing contracts; it does not create `data/saved-article-organization-coverage.json`, does not create `data/organization-coverage-matrix.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 343 adds generated-site only Saved Article Content Organization group summaries inside `articles/index.html`; it reuses existing saved article content organization groups, existing organization cards, existing card detail-path anchors, existing card references, and existing paragraph indices to show per-group saved-card counts, saved-article counts, source counts, evidence paragraph counts, and capped reference chips before each group grid without changing app-facing contracts; it does not create `data/saved-article-content-organization-summary.json`, does not create `data/content-organization-group-summary.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 342 adds generated-site only saved paragraph context cues for ROW ONE local article pages; it reuses current-edition saved local article sidecars, existing local article rendering sections, existing content-section paragraph indices, existing detail-page `#local-article-content-section-N` anchors, existing `#local-article-paragraph-N` anchors, and existing `articles/<story-id>.html` pages to show which organized section or item cites each saved paragraph without changing app-facing contracts; it does not create `data/saved-paragraph-context-cues.json`, does not create `data/local-article-paragraph-contexts.json`, does not create new article-source sidecars, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 341 adds generated-site only local article reading improvements for ROW ONE first-class local article pages; it reuses current-edition saved local article sidecars, existing local article rendering sections, existing saved article library routes, existing detail-page `#local-article-*` anchors, and existing `articles/<story-id>.html` pages to improve how readers scan already-saved local text without changing the app-facing contracts; it does not create `data/local-article-reading-improvements.json`, does not create new article-source sidecars, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
Stage 340 adds saved local article paragraph quality gating for ROW ONE: it filters high-confidence extraction boilerplate from saved local article paragraphs before sidecar and HTML rendering while preserving short valid fashion-news paragraphs, existing summary_fallback/no_publishable_paragraphs fallback behavior, paragraph anchors, paragraphs_zh alignment, content-section paragraph indices, existing saved article library links, and first-class local article pages; it does not create `data/saved-article-paragraph-quality-gate.json`, does not remove saved local articles with publishable paragraphs, does not publish full articles on the library index, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 339 adds generated-site only first-class local article pages at `articles/<story-id>.html`; it reuses current-edition saved local article sidecars, existing local article rendering sections, safe story-id article routes, existing saved article library routes, and existing detail-page `#local-article-*` anchors so `articles/index.html` can make the local article page the primary local reading action while existing detail anchors continue to work; it does not remove detail-page local article sections or anchors, does not add outbound article URLs as primary navigation, does not write `data/local-article-pages.json` or `data/saved-article-pages.json`, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 338 adds generated-site only Saved Article Paragraph Evidence Board inside `articles/index.html`; it reuses existing saved local article sidecars, existing saved local paragraphs, existing saved article content organization paragraph indices, existing saved article library routes, and existing detail-page `#local-article-content-section-N` and `#local-article-paragraph-N` anchors to show capped local paragraph evidence excerpts behind saved article sections; it does not publish full articles on the library index, does not add outbound article URLs in the evidence board, does not write `data/saved-article-evidence-board.json`, does not add LLM-generated summaries, does not add extraction, ranking, trend scoring, or heat ranking, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 337 adds generated-site only Saved Article Reference Atlas inside `articles/index.html`; it reuses existing saved local article sidecars, existing saved article content organization references, and existing detail-page `#local-article-content-section-N` and `#local-article-paragraph-N` anchors to group saved local references by brands, people, products, and source context; it does not publish full articles on the library index, does not add outbound article URLs in the atlas, does not write `data/saved-article-reference-atlas.json`, does not add LLM-generated summaries, does not add trend scoring or heat ranking, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 336 adds generated-site only Saved Article Theme Digest inside `articles/index.html`; it reuses existing saved local article sidecars, existing saved local paragraphs, existing saved article content organization, and existing detail-page `#local-article-content-section-N` and `#local-article-paragraph-N` anchors to summarize recurring themes from already-saved local text; it does not publish full articles on the library index, does not add LLM-generated summaries, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 335 adds generated-site only Saved Article Reading Paths inside `articles/index.html`; it reuses existing saved article library cards, existing saved article content organization leads, existing detail-page content-section anchors, and existing paragraph anchors to show capped read-first paths through already-saved local text; it does not publish full articles on the library index, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 334 adds generated-site only organized local excerpts to saved article library cards inside `articles/index.html`; it reuses existing saved article content organization leads and existing detail-page content-section and paragraph anchors to show capped per-card read-first snippets from already-saved local text; it does not publish full articles on the library index, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 333 adds a generated-site only saved article library text-source map inside `articles/index.html`; it reuses existing saved local article `body_source` values to show included-library counts and per-card text source chips for extracted article text, ROW ONE summary fallback, and skipped saved bodies; it does not expose fallback reasons, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 332 adds generated-site only saved article content groups inside `articles/index.html`; it reuses existing saved local article sidecars and existing `content_sections` to organize the current edition's saved local articles by read-first, people/brands, products, and source structure, with links back to existing detail-page content-section and paragraph anchors; it does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 331 documents local article body provenance for ROW ONE saved sidecar JSON and generated detail pages: `body_source` distinguishes `extracted`, `summary_fallback`, and `skipped`; `summary_fallback` means ROW ONE generated a publishable local article body from the story summary/editorial fallback when extraction was skipped, failed, or unusable. This is a sidecar/data detail-page provenance signal only; it does not change `data/edition.json`, does not change `row-one-runtime/v1`, and does not add compliance-review behavior. The row one summary fallback label is provenance for locally generated saved bodies, not a claim that saved paragraphs are extracted article text.
Stage 329 adds `row-one ops-check` as a read-only local ROW ONE ops diagnostic for site freshness, server/port readiness, access URLs, and user systemd unit-file presence; it does not start servers, install or enable systemd units, kill processes, refresh or rebuild the site, write files, change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, extraction, scoring, ranking, LLM, connector, deployment automation, market grouping, domestic/international classification, or compliance-review behavior.
Stage 328 adds generated-site only evidence excerpts to the existing ROW ONE Saved Signal Index inside `articles/index.html`; it shows capped snippets from existing saved local article item bodies or saved paragraphs and links back into existing detail-page local article anchors; it does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
Stage 327 adds a generated-site only ROW ONE Saved Signal Index inside
`articles/index.html`; it organizes the current edition's saved local article
references by signal and links back into existing detail-page local article
anchors; it does not change row-one-app/v7, row-one-manifest/v1,
row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching,
matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment,
or compliance-review behavior.
Stage 326 adds a generated-site only ROW ONE daily saved article library at
`articles/index.html`; it organizes the current edition's saved local articles
by source and links back into existing detail-page local article anchors; it
does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1,
schemas, JSON artifacts, source collection, fetching, scoring, LLM, connector,
scheduling, deployment, or compliance-review behavior.
Stage 324 adds Paragraph Evidence Index to generated ROW ONE detail pages. It is
generated-site only and turns existing `RowOneLocalArticle.content_sections`
items with existing `paragraph_indices`, existing `references`, existing
`#local-article-paragraph-N` anchors, and existing
`#local-article-content-section-N` anchors into a compact saved paragraph
evidence index with safe internal links. It does not change `row-one-app/v7`,
does not change `data/edition.json`, does not change `row-one-manifest/v1`,
does not change `row-one-runtime/v1`, does not add
`local_article_paragraph_evidence`, does not add `paragraph_evidence_index`,
does not change schemas, does not write a new JSON artifact, does not add source
collection, does not fetch article pages, does not add extraction, does not add
scoring, does not add ranking, does not add LLM calls, does not add translation
calls, does not add image generation, does not add connectors, does not add
scheduling, does not add deployment behavior, and does not add
compliance-review product features.
Stage 323 adds Local-First Reading to generated ROW ONE pages. It is
generated-site only and turns existing `data/articles/<story-id>.json`
sidecars, existing saved local paragraphs, existing `#local-article`, and
existing `#local-article-paragraph-N` anchors into saved article
content-organization cards with a read saved article path and safe internal
links. It does not change `row-one-app/v7`, does not change `data/edition.json`,
does not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`,
does not add `local_first_read`, does not add `local_read_path`, does not add
`saved_article_cta`, does not add `evidence_paragraph_trail`, does not change
schemas, does not write a new json artifact, does not add source collection,
does not fetch article pages, does not add scoring, does not add llm calls,
does not add connectors, and is not a compliance review feature.
Stage 322 adds Editorial Source Trail to the existing homepage Editorial Brief
cards. It is generated-site only and turns existing saved local article source
names, existing saved article titles, existing brief sections, existing content
sections, existing `data/articles/<story-id>.json` sidecars, and existing
paragraph/content-section anchors into compact bilingual provenance chips with
safe internal links. It does not change `row-one-app/v7`, does not change
`data/edition.json`, does not add `editorial_source_trail`, does not add
`source_trail`, does not change `row-one-manifest/v1`, does not change
`row-one-runtime/v1`, does not change schemas, does not write a new json
artifact, does not add source collection, does not fetch article pages, does not
add scoring, does not add llm calls, does not add connectors, and is not a
compliance review feature.
Stage 321 adds homepage Editorial Brief to generated ROW ONE index pages. It is
generated-site only and turns existing story summaries, existing story signal
context, existing saved local article brief sections, existing
`data/articles/<story-id>.json` sidecars, and existing paragraph anchors into a
short bilingual Editorial Brief / 编辑正文 section with safe internal detail and
paragraph links. It does not change `row-one-app/v7`, does not change
`data/edition.json`, does not add `editorial_brief`, does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change
schemas, does not write a new json artifact, does not add source collection,
does not fetch article pages, does not add scoring, does not add llm calls, does
not add connectors, and is not a compliance review feature.
Stage 310 adds a generated-site saved text reader on ROW ONE detail pages:
saved local paragraphs are listed as numbered in-page reader segments that link
to the existing paragraph anchors before the existing saved text. This is a
detail-page saved text reader only; it does not change `row-one-app/v7`,
does not change `data/edition.json`, uses existing `data/articles/<story-id>.json` sidecars, does not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change detail routes, does not change paragraph anchors, does not change schemas, does not add source collection, and does not add scoring.
ROW ONE also applies newsroom digest polish to saved local articles: it
clusters duplicate saved local-article cards in the homepage digest, evidence
paragraph links point into saved local paragraphs with reader-facing copy, and
detail pages show compact local article provenance. This does not change
`row-one-app/v7`, does not change `data/edition.json`, and does not add source
collection/scoring. It does not change `row-one-manifest/v1`, does not change
`row-one-runtime/v1`, does not change detail routes, does not change paragraph
anchors, and does not change schemas.
`row-one-app/v7 remains stable`: this local-intelligence artifact is separate
from `data/edition.json`, so app clients pinned to the existing app payload do
not need to accept a new top-level field.
`signal_synthesis.groups[].signals[].story_refs` is an app-facing information
organization index that carries compact supporting story references inline,
derived from the same briefing topic source story data. It is not a compliance
review feature and does not change collection, matching, ranking, scoring,
sorting, or story IDs.
`schemas/row-one-app.schema.json` validates this field structurally; `row-one status`
and the first-run smoke also validate that each story ref mirrors the referenced
top-level story and keeps `story_refs[].story_id` aligned with `story_ids`.
App clients can render section rails and a daily briefing from `data/edition.json`
without scraping HTML.
`story_directory` is an app-facing route index derived only from existing ROW
ONE stories. It helps app clients resolve story routes from local JSON without
HTML scraping, and it does not change collection, matching, scoring, sorting,
story IDs, or source acquisition.
The ROW ONE homepage briefing path reuses `daily_digest.blocks` as a compact
reading path, links to existing detail pages, and is not a new data layer.
The content-card explanation fields and Detail Information Map are presentation
surfaces derived from existing ROW ONE stories; they do not change collection,
matching, scoring, ranking, story IDs, sorting, or source acquisition.
For local app/ops preflight, `row-one status --json` provides additive top-level
fields such as counts, readiness, refresh_time, local_url, lan_url_hint, and
edition_path while preserving the nested runtime and manifest payloads.
`row-one status --json` is the script-facing preflight surface. Stage 308 site
integrity/preflight validates an already generated ROW ONE site before serving;
it is read-only and does not rebuild, write files, start a server, collect
sources, call external services, deploy, or alter ranking/scoring/story IDs. It
validates `.row-one-site`, `index.html`, fixed JSON paths, core assets, current
detail routes, local image asset existence, article sidecars,
local-intelligence detail paths, and paragraph anchors. This has no schema/app
contract change: the additive status fields are CLI output only and do not add
fields to `row-one-runtime/v1`, `row-one-manifest/v1`, or `row-one-app/v7`.
`data/edition.json` remains `row-one-app/v7`, `data/manifest.json` remains
`row-one-manifest/v1`, and `data/runtime.json` remains `row-one-runtime/v1`.

The external tool handoff templates are sanitized CSV/JSON local file handoff
templates for user-controlled external/community tools:
[examples/community-tool-handoff.example.csv](examples/community-tool-handoff.example.csv)
and
[examples/community-tool-handoff.example.json](examples/community-tool-handoff.example.json).
This is not platform collection and does not add connectors, scraping, browser
automation, platform APIs, monitoring, scheduling, source acquisition, demand
proof, ranking, or coverage verification.

The external community tool export directory examples are sanitized CSV/JSON
local export directory examples for user-controlled external/community tools:
[examples/community-tool-handoff-directory.example/README.md](examples/community-tool-handoff-directory.example/README.md),
[examples/community-tool-handoff-directory.example/csv/community-tool-a.csv](examples/community-tool-handoff-directory.example/csv/community-tool-a.csv),
[examples/community-tool-handoff-directory.example/csv/community-tool-b.csv](examples/community-tool-handoff-directory.example/csv/community-tool-b.csv),
[examples/community-tool-handoff-directory.example/json/community-tool-a.json](examples/community-tool-handoff-directory.example/json/community-tool-a.json),
and
[examples/community-tool-handoff-directory.example/json/community-tool-b.json](examples/community-tool-handoff-directory.example/json/community-tool-b.json).
The example README includes `external-tool-readiness` and
`external-tool-workflow` preflight examples for the checked-in
`generic_community_export` CSV and JSON directories, and the concrete command
block lives in
[docs/community-signal-import.md#external-tool-export-directory-examples](docs/community-signal-import.md#external-tool-export-directory-examples).
`community-signal-profile --format json` and
`community-handoff-manifest --format json` expose these same checked-in
directory layout pointers as `directory_example_paths` for local/external tool
discovery, while `example_paths` stays limited to single-file examples.
The checked-in `csv/` and `json/` directories are separate non-recursive
examples for one input format and one matched filename pattern per run. They
are not platform collection and do not add connectors, scraping, browser
automation, platform APIs, monitoring, scheduling, source acquisition, demand
proof, ranking, or coverage verification.

`external-tool-adapters` is a local, print-only external social/community tool
adapter registry and local producer-discovery registry for user-controlled
external/community tools that need sanitized CSV/JSON local file handoff
targets. It prints metadata and copyable local handoff commands only. Each
adapter command list includes `external-tool-readiness` as an optional local
read-only preflight command, while `external-tool-adapters` itself remains
print-only and does not run readiness or perform PATH lookup. It is not
platform collection and has no connectors, no scraping, no browser automation,
no platform APIs, no monitoring, no scheduling, no source acquisition, no
demand proof, no ranking, and no coverage verification.

Known adapter ids:

| Adapter id | Display/source name | Platform label | Format | Pattern |
| --- | --- | --- | --- | --- |
| `rednote_mcp` | Rednote MCP Export | `rednote` | `json` | `*.json` |
| `xiaohongshu_crawler` | Xiaohongshu Crawler Export | `xiaohongshu` | `csv` | `*.csv` |
| `instaloader` | Instaloader Export | `instagram` | `json` | `*.json` |
| `tiktok_api` | TikTok-Api Export | `tiktok` | `json` | `*.json` |
| `yt_dlp` | yt-dlp Metadata Export | `media` | `json` | `*.json` |
| `x_search_export` | X Search Export | `x` | `csv` | `*.csv` |
| `xpoz_mcp` | XPOZ MCP Export | `community` | `json` | `*.json` |
| `generic_community_export` | Generic Community Export | `community` | `csv` | `*.csv` |

The Display/source name column reflects the current registry `display_name` and
`suggested_source_name` values, which are identical for these adapters.

The Platform label column reflects `suggested_platform_labels` as advisory local
provenance label guidance for the optional handoff `platform` field. These
labels are local provenance suggestions only: they are not a schema enum, not a
linter restriction, not platform coverage, and not demand proof.

`external-tool-template` is a local, print-only command that prints
adapter-specific template rows for user-controlled external/community tools
that need sanitized CSV/JSON local file handoff examples. JSON and CSV output
contain importable community handoff rows only; table output may include local
metadata, field mappings, and copyable commands. The JSON/CSV handoff rows
remain importable row output only, while table/model guidance can include the
same adapter recommended command list. It is not platform collection and has
no connectors, no scraping, no browser automation, no platform APIs, no
monitoring, no scheduling, no source acquisition, no demand proof, no ranking,
and no coverage verification.

`external-tool-workflow` is a local, print-only command that prints workflow
metadata for user-controlled external/community tools that need a
producer-facing wrapper around existing local commands before writing sanitized
CSV/JSON local file handoff rows. JSON output is workflow metadata, not
importable handoff rows; table output may include local metadata and copyable
commands. The printed steps include `check_external_tool_readiness`, an
optional preflight command that points to `external-tool-readiness` for local
command availability guidance before sanitized handoff rows are prepared. It
does not inspect directories, read handoff files, import rows, open SQLite, or
create artifacts. It is not platform collection and has no connectors, no
scraping, no browser automation, no platform APIs, no monitoring, no
scheduling, no source acquisition, no demand proof, no ranking, and no
coverage verification.

```bash
uv run fashion-radar external-tool-workflow --adapter instaloader --format table
uv run fashion-radar external-tool-workflow --adapter instaloader --format json
```

### External Tool Import Path

When a user-controlled external export directory already contains sanitized
CSV/JSON rows, use [docs/community-signal-import.md](docs/community-signal-import.md)
for the local handoff route. The path is:
`external-tool-adapters -> external-tool-readiness -> external-tool-workflow ->
community-signal-lint-dir -> community-candidates-dir ->
community-handoff-check-dir -> import-signals-dir -> imported-review-workflow`.

Fashion Radar treats this as a sanitized CSV/JSON local file handoff from a
user-controlled external export directory. It does not run upstream tools, does
not search platforms, does not scrape, does not call platform APIs, does not add
connectors, does not prove demand, does not rank brands, and does not verify
platform coverage.

`external-tool-readiness` provides external tool readiness guidance and is local
read-only, not print-only, because it checks command availability only with
local PATH lookup (`shutil.which`) for known free external/community tools such
as Rednote MCP, Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp, X/search
exports, and XPOZ MCP / Social Data API exports created outside Fashion Radar.
It prints readiness guidance, mirror-friendly install hints, and Fashion Radar
next-step handoff commands for user-controlled external/community tools
producing sanitized CSV/JSON local file handoff rows.
It does not install dependencies automatically, does not run
adapters, does not run upstream tools, does not inspect directories, does not
read handoff files, import rows, open or write SQLite, or create
config/data/report/dashboard/workflow/handoff artifacts. It is not a
scraper/connector and has no scraping, no browser automation, no platform APIs,
no account/session/cookie/token behavior, no monitoring, no scheduling, no
source acquisition, no demand proof, no ranking, no coverage verification, and
no compliance-review product feature.

```bash
uv run fashion-radar external-tool-readiness --adapter instaloader
uv run fashion-radar external-tool-readiness --adapter rednote_mcp --format json
```

Future non-core connectors, if ever added, must be explicit opt-ins with clear
risk labels. They are not required for the core workflow.

## Current Roadmap Focus

Near-term v0.1.x work is focused on the core pipeline: using source-liveness
evidence to broaden curated public-source coverage and improving deterministic
matching quality. Further report summary or explanation refinements should stay
optional, local, and post-core. No new external-tool, community-handoff, or
imported-review surface area is planned unless a release-blocking defect
requires maintenance.

## Quickstart

For a source checkout, install dependencies with uv:

```bash
uv sync --locked --dev
```

For users in mainland China or slower networks, use a mirror only as a local
install aid:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
```

Do not regenerate or commit `uv.lock` from a mirror-backed lock operation. The
public lockfile should remain usable from the default PyPI registry. See
[docs/dependency-mirrors.md](docs/dependency-mirrors.md).

Package readiness is checked separately before upload by building and smoking a
local wheel from this checkout; that check does not publish to PyPI. See
[docs/github-upload-checklist.md](docs/github-upload-checklist.md).

For first-run onboarding, see [docs/first-run.md](docs/first-run.md). Choose
the path that matches what you need:

- Source checkout smoke: verify the working tree with temporary paths.
- Manual repo-local sample output/dashboard: create local sample configs,
  SQLite state, and dated reports you can inspect in the dashboard.
- Installed-wheel release smoke: build a local wheel and smoke the installed
  package path before upload; this does not publish to PyPI.
- Reset repo-local sample output: remove generated sample runtime files after
  reviewing any local config edits.

Run Quickstart commands from the repository root after `cd /path/to/fashion-radar`.

Create starter config, initialize the repo-local SQLite schema, and check the
same repo-local workspace:

```bash
uv run fashion-radar init --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
uv run fashion-radar migrate-db --data-dir "$PWD/data"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

`doctor` reports database schema status read-only. `migrate-db` only performs
local schema initialization or upgrades; it does not collect, import, match,
score, report, monitor, watch, schedule, or touch external platforms.

### Manual Repo-Local Sample Flow

Use the checked-in community signal example when you want a deterministic
first run that produces local output without live source collection. This
manual flow writes to the repo-local `data/` and `reports/` directories shown
in the commands. Run the prerequisite `init`, `migrate-db`, and `doctor` block
above first so the same repo-local paths are initialized and checked.

```bash
AS_OF="2026-06-13T12:00:00Z"

uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$AS_OF"
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
uv run fashion-radar trend-explanations --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
test -s reports/fashion-radar-2026-06-13.md
test -s reports/fashion-radar-2026-06-13.json
test -s reports/fashion-radar-2026-06-13.html
```

Expected repo-local artifacts include `configs/sources.yaml`,
`configs/entities.yaml`, `configs/scoring.yaml`,
`data/fashion-radar.sqlite`, `reports/fashion-radar-2026-06-13.md`, and
`reports/fashion-radar-2026-06-13.json`, plus the companion
`reports/fashion-radar-2026-06-13.html`. The deterministic sample is expected
to produce matched report and trend signals for `The Row`, `The Row Margaux`,
and `Ballet Flats`. To inspect the generated sample report, run the dashboard
with the same path flags and open
`http://127.0.0.1:8501`.

### Automated First-Run Smoke

In a source checkout, the automated local sample smoke uses temporary config, data,
report, and export directories, then verifies generated report artifacts there.
It should not create files under repo `data/` or `reports/`:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Source checkout mode prepends the checkout `src/` directory so it exercises the
working tree. Use it to check local source edits. The installed wheel smoke
builds and installs the local wheel, then runs the same sample path with the
wheel Python environment and `--installed`; use it to check release packaging:

```bash
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Both modes print `First-run sample smoke passed.` on success and create
temporary dated reports such as `fashion-radar-2026-06-13.md`,
`fashion-radar-2026-06-13.json`, and `fashion-radar-2026-06-13.html` inside
their temporary report directories.
The automated smoke validates that sample rows import as community signals,
match the starter entities `The Row`, `The Row Margaux`, and `Ballet Flats`,
appear in the dated report, produce matching entity trend deltas, and keep
untracked candidates empty under starter config.
The automated first-run smoke also validates local external-tool JSON
contracts: `external-tool-adapters --format json` across all eight adapters,
plus the `external-tool-template --adapter rednote_mcp --format json`,
`external-tool-workflow --adapter rednote_mcp --format json`, and
`external-tool-readiness --adapter rednote_mcp --format json` outputs generated
with the `rednote_mcp` adapter. These are command-output contract checks only;
they do not run adapters or upstream external/community tools, do not call
platform APIs, and do not perform source acquisition.
Temporary smokes do not leave dashboard-inspectable repo-local reports; use the
manual repo-local sample flow when you want dashboard output under
`reports/`.

This path does not run live collection, scraping, platform automation,
monitoring, scheduling, or external services. Candidate and trend JSON outputs
are local sample content checks from the checked example rows and current
starter config.

### Optional Expanded Watchlist Sample

Use this optional local sample when you want to see the broader
`fashion-watchlist` entity pack match designer brands, named products,
categories, designers, celebrity style, and trend terms against checked-in
synthetic local rows. It is separate from the default first-run smoke and does
not change generated starter configs.

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

Expected local matches include `Khaite`, `Khaite Lotus Bag`, `Loewe`,
`Loewe Puzzle Bag`, `Jonathan Anderson`, `Bella Hadid`, `Alaia Le Teckel`,
`Miu Miu Arcadie`, `Mary Jane Shoes`, and `Boho Revival`.

The optional local sample does not fetch URLs, does not collect platform data,
does not prove demand, does not rank brands, does not verify platform coverage,
and does not add connectors.

Run the daily workflow step by step:

```bash
uv run fashion-radar collect --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Optionally import local user-provided signals before matching:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export" --data-dir "$PWD/data"
```

External community tools can target the local community signal contract:

The external tool handoff template examples are sanitized CSV/JSON local file
handoff templates for user-controlled external/community tools, not platform
collection. Use
[examples/community-tool-handoff.example.csv](examples/community-tool-handoff.example.csv)
or
[examples/community-tool-handoff.example.json](examples/community-tool-handoff.example.json)
as local template shapes before running the same lint, preview,
`review_handoff_readiness`, dry-run, import, and review commands below.

```bash
AS_OF="2026-06-13T12:00:00Z"
tmp_run="$(mktemp -d)"
mkdir -p "$tmp_run/exports"
cp examples/community-signals.example.csv "$tmp_run/exports/community-signals.csv"
uv run fashion-radar community-signal-profile --format json
uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar community-handoff-manifest "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar community-handoff-workflow "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar external-tool-adapters --format table
uv run fashion-radar external-tool-adapters --format json
uv run fashion-radar external-tool-template --adapter instaloader --format table
uv run fashion-radar external-tool-template --adapter instaloader --format json
uv run fashion-radar external-tool-template --adapter instaloader --format csv
uv run fashion-radar external-tool-workflow --adapter instaloader --format table
uv run fashion-radar external-tool-workflow --adapter instaloader --format json
uv run fashion-radar external-tool-readiness --adapter instaloader
uv run fashion-radar external-tool-readiness --adapter rednote_mcp --format json
uv run fashion-radar community-signal-lint-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar community-handoff-check-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
```

Inspect retained imported rows and matched-entity evidence after import:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data" --format json
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$AS_OF"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$AS_OF" --format json
uv run fashion-radar imported-entity-evidence --data-dir "$PWD/data" --as-of "$AS_OF" --entity-name "The Row" --entity-type brand
uv run fashion-radar imported-entity-evidence --data-dir "$PWD/data" --as-of "$AS_OF" --entity-name "The Row" --entity-type brand --source-name "Community Tool Export" --format json
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF"
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --phrase "Le Teckel bag"
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --phrase "Le Teckel bag" --source-name "Community Tool Export" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --unmatched-only
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --format json
```

`imported-review-workflow` is local and does not execute commands. It prints a
copyable review sequence for existing local commands after manual signal
import. The workflow includes `review_imported_entity_evidence` after entity
deltas, then a read-only imported-candidates step for candidate phrase review,
and still ends with the final read-only heat-movers step for local observed
heat movement from configured sources and imported local signals. Those review
outputs need review and provide no demand proof and no platform coverage
verification.

`imported-entity-evidence` is local read-only and imported-only. It opens an
existing SQLite database in read-only mode and shows retained local rows whose
`manual_import` stored matched entity equals the requested entity. Output is a
privacy-safe drilldown: it includes only review metadata plus `window`, `id`,
`source_name`, `title`, `url`, `published_at`, and `collected_at`; it omits
summaries, candidate contexts, match internals, import file paths, normalized
keys, and platform labels. It does no scraping, no browser automation, no
platform APIs, and no account or cookie work.

`imported-candidates` is local and read-only. It surfaces observed candidate
phrases from retained `manual_import` rows only. These phrases need review and
are not verified entities, demand proof, or platform coverage.

`imported-candidate-evidence` is local and read-only. It shows retained
`manual_import` rows whose extracted candidate phrases match one requested
phrase. Evidence rows are review aids and are not verified entities, demand
proof, or platform coverage.

`community-candidates` is local and read-only. It previews aggregate candidate
phrase metrics from one supplied community signal CSV/JSON file before import.
It does not store rows, open SQLite, fetch URLs, print the supplied input file
path, or expose row URLs, row titles, summaries, raw text, normalized keys,
candidate contexts, or representative item details. The output is not proof of demand, not platform coverage, and not source ranking.

`community-candidates-dir` is local and read-only. It previews aggregate
candidate phrase metrics from matched regular CSV/JSON handoff files directly
under one supplied directory before import. It does not recurse, import rows,
open SQLite, fetch URLs, print the supplied directory path, expose matched file
paths, expose matched file names, or expose row URLs, row titles, summaries,
raw text, normalized keys, candidate contexts, raw validation findings,
account/private fields, or representative item details. The output is not proof
of demand, not platform coverage, and not source ranking.

`community-handoff-manifest` is local and print-only. It prints a
producer-facing manifest for a supplied directory without reading it. The
manifest describes the directory, matched file pattern, suggested handoff
filename, `community-signal-profile`/schema/example pointers,
`directory_example_paths`, embedded producer profile fields and rules, a
storage note, and the local workflow commands used by
`community-handoff-workflow`. If an external tool saves the manifest, keep it
outside the matched export directory or use a filename excluded by the handoff
`--pattern`, especially for JSON export directories using `--pattern "*.json"`.

`community-handoff-workflow` is local and print-only. It prints the ordered
local sequence `lint_handoff_directory`, `preview_candidate_phrases`,
`review_handoff_readiness`, `dry_run_directory_import`,
`import_directory_signals`, and `print_post_import_review` for a supplied
directory. The `review_handoff_readiness` step prints the
`community-handoff-check-dir` local-only handoff readiness report before
importing rows. The workflow does not execute commands, read the supplied
directory, validate files, import rows, open or write SQLite, fetch URLs, log
in, download media, automate browsers, scrape, monitor, watch folders, schedule
work, add source/platform connectors, prove demand, verify platform coverage,
rank sources, write reports, update dashboards, generate configs, or generate
entity files. It intentionally prints the supplied directory/config/data paths
inside copyable local commands; this differs from aggregate candidate preview
output, which suppresses paths and row details.

`community-handoff-check-dir` is a local-only handoff readiness report for
user-controlled community signal directories. It reads only matched local
regular files and local config. It does not import rows, uses no SQLite,
creates no config/data/report/dashboard/digest artifacts, and has no fetch URLs/login/platform
APIs/download media/browser automation/scrape/crawl/monitor/watch/schedule/connectors/source
acquisition/demand proof/ranking/coverage verification/entity generation/compliance/policy/
authorization/safety-review features.

`external-tool-adapters` is local and print-only. It prints the external
social/community tool adapter registry as a local producer-discovery registry
for user-controlled external/community tools that want sanitized CSV/JSON local
file handoff rows. It can print table or JSON metadata and copyable local
handoff commands. Each adapter command list includes `external-tool-readiness`
as an optional local read-only preflight command, while
`external-tool-adapters` itself remains print-only and does not run readiness
or perform PATH lookup. It does not run adapters, inspect directories, read
handoff files, validate files, import rows, open SQLite, create artifacts, or
perform platform collection. It has no connectors, no scraping, no browser
automation, no platform APIs, no monitoring, no scheduling, no source
acquisition, no demand proof, no ranking, and no coverage verification.

`external-tool-template` is local and print-only. It prints adapter-specific
template rows for user-controlled external/community tools that want sanitized
CSV/JSON local file handoff examples. It can print importable JSON, importable
CSV, or a table with local metadata and copyable local commands. The JSON/CSV
handoff rows remain importable row output only, while table/model guidance can
include the same adapter recommended command list. It does not write files,
run adapters, inspect directories, read handoff files, validate files, import
rows, open SQLite, create artifacts, or perform platform collection. It has no
connectors, no scraping, no browser automation, no platform APIs, no
monitoring, no scheduling, no source acquisition, no demand proof, no ranking,
and no coverage verification.

`external-tool-readiness` provides external tool readiness guidance as local
read-only command availability only. It uses local PATH lookup (`shutil.which`)
to report whether the known command for a free external/community tool appears
available, then prints mirror-friendly install guidance and next-step Fashion
Radar handoff commands for sanitized CSV/JSON local file handoff rows. It does
not install dependencies, run
adapters, run upstream tools, inspect directories, read handoff files, import
rows, open or write SQLite, or create config/data/report/dashboard/workflow/
handoff artifacts. It is not platform collection and has no connectors, no
scraping, no browser automation, no platform APIs, no account/session/cookie/
token behavior, no monitoring, no scheduling, no source acquisition, no demand
proof, no ranking, no coverage verification, and no compliance-review product
feature.

Review untracked candidate signals from configured sources and imported local
signals:

```bash
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Compare local observed trend deltas without writing to the database:

```bash
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Trend deltas are read-only local comparisons. They do not prove demand outside
your configured source set.

Explain the same local observed trend deltas without changing the `trends` or
`heat-movers` contracts:

```bash
uv run fashion-radar trend-explanations --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

`trend-explanations` derives deterministic explanations from configured
sources and imported local signals only. The output needs review, provides no
demand proof, and provides no platform coverage verification.

Generated reports include a Daily Brief Heat Narrative that summarizes local
observed report content from configured sources and imported local signals:
tracked signals, candidate phrases, and source caveats. Candidate summaries can
include candidate score-component cues for mentions, growth, and source
diversity. The Daily Brief needs review. It provides no demand proof and no
platform coverage verification.

### Heat Movers

The `heat-movers` command is a local observed heat movement view over one
configured source set. It reviews configured sources and imported local
signals, and the output needs review. It is local observed heat movement only,
with no demand proof and no platform coverage verification.

```bash
uv run fashion-radar heat-movers --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Or run the workflow serially:

```bash
uv run fashion-radar run --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Build and serve the optional ROW ONE local static site from existing daily
report data:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar row-one refresh --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --output-dir reports/row-one/site --as-of "$AS_OF"
uv run fashion-radar row-one preview --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --output-dir reports/row-one/site --as-of "$AS_OF" --latest-only --dry-run-serve-url
uv run fashion-radar row-one status --site-dir reports/row-one/site --json
uv run fashion-radar row-one ops-check --site-dir reports/row-one/site --host 0.0.0.0 --port 8787 --json
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 127.0.0.1 --port 8787
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 0.0.0.0 --port 8787
uv run fashion-radar row-one schedule --time 04:00
uv run fashion-radar row-one local-ops --time 04:00 --host 0.0.0.0 --port 8787
```

ROW ONE supports IP:port local-network serving when you explicitly bind
`--host 0.0.0.0`; open `http://<LAN-IP>:8787`, not `http://0.0.0.0:8787`,
from another device. The local ROW ONE server has no authentication layer.
Open Design imagery is optional and not required for tests.
`row-one refresh` is the single local daily refresh command for ROW ONE: it
refreshes the daily report data and generated site in one command. After the
current site and reports are generated, it keeps generated dated report artifacts
latest-only in the selected `--reports-dir`, pruning older
`fashion-radar-YYYY-MM-DD.{md,json,html}` files, then runs SQLite item retention.
The SQLite retention uses a default 1-day retention window for `items` and
`item_entities` so test deployments stay disk-friendly. Use `--retention-days N`
when you need longer local item history, or `--skip-data-retention` to opt out
for a refresh. A 1-day SQLite item retention window reduces the multi-day local
history available to future scoring window comparisons and heat scores, so raise
`--retention-days` when you are tuning scoring or comparing heat over multiple
days. The retention step does not prune `collector_runs`, does not prune
`source_health`, does not prune `entity_first_seen`, does not prune config files,
and does not prune generated site files. It also does not change ROW ONE
contracts, detail routes, or schemas; report artifact pruning remains separate
from SQLite item retention.
`row-one local-ops` prints a local daily ops runbook for 04:00 refresh, preview,
fixed IP:port serving, LAN access, cron snippets, latest-only cleanup, and a
copyable source-checkout command group with its own `AS_OF`, `cd`, and
`row-one status --json` preflight. The group includes
`uv run fashion-radar row-one refresh`,
`uv run fashion-radar row-one preview`, `uv run fashion-radar row-one status --site-dir reports/row-one/site --json`,
and `uv run fashion-radar row-one serve`. It prints snippets only and does not
install timers, build the site, start the server, or mutate files.
`row-one ops-check` is a read-only local ROW ONE ops diagnostic for site
freshness, server/port readiness, access URLs, and user systemd unit-file
presence. It inspects local files and local HTTP/port readiness only; it does
not start servers, install or enable systemd units, kill processes, refresh or
rebuild the site, write files or artifacts, or change ROW ONE contracts,
schemas, collection, fetching, extraction, scoring, ranking, LLM, connector,
deployment automation, market grouping, domestic/international classification,
or compliance-review behavior. Its `ready` status requires generated site
files, fresh runtime metadata, a local server already serving ROW ONE, and
expected user systemd unit files; missing units keep the result in `attention`.
Use `row-one status --json` as the
script-facing preflight; ROW ONE runtime metadata remains local operational
metadata only, not a deployment record.
The first-run smoke now performs a local HTTP serve fetch, not just
`serve --dry-run`, after the same status preflight path is covered.

Package local digest artifacts after a report or serial run:

```bash
uv run fashion-radar run --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --digest-latest copy --digest-index --digest-summary
```

Digest artifacts are local files only. Fashion Radar does not send email,
webhooks, or push notifications.

Print a daily scheduling example:

```bash
uv run fashion-radar schedule-example --mode cron --project-dir "$PWD"
```

By default, config/data/report directories use platform-specific user
directories. To keep everything inside a local workspace while experimenting:

```bash
export FASHION_RADAR_CONFIG_DIR="$PWD/configs"
export FASHION_RADAR_DATA_DIR="$PWD/data"
export FASHION_RADAR_REPORTS_DIR="$PWD/reports"
```

Generated SQLite databases and reports are ignored by git.

## Dashboard

The dashboard is optional:

```bash
uv sync --locked --dev --extra dashboard
uv run fashion-radar dashboard --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --host 127.0.0.1 --port 8501
```

Run the manual repo-local sample flow first when you want the dashboard to open
against a freshly generated sample report in the same `reports` directory.

Mirror install:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --extra dashboard
uv run fashion-radar dashboard
```

The dashboard defaults to `127.0.0.1:8501`, is read-only, and does not collect,
match, or fetch network data on page import or refresh. It shows local
mention-count summaries, reads candidate signals from the latest report JSON,
and can show a `Trend Deltas` tab computed from local SQLite state with the
configured scoring window. This local read does not create trend tables or write
database state. Candidate signals may be stale until a new report is generated.
Trend explanations remain a CLI-only read-only sidecar over configured sources
and imported local signals; they provide no demand proof and no platform
coverage verification.

ROW ONE is separate from the Streamlit dashboard. It is a local static site and
server generated from existing daily report data, not a dashboard tab.

There is no authentication layer. Do not bind `--host 0.0.0.0` or any non-local
address on an untrusted network unless you understand that the dashboard may be
reachable by other machines.

See [docs/dashboard.md](docs/dashboard.md).

## Configuration

Starter files live in [configs](configs) and are also packaged for
`fashion-radar init`:

- `sources.example.yaml` defines a compact RSS/GDELT fashion starter set with
  source weights, HTTP settings, article extraction settings, and source-health
  circuit-breaker behavior. It includes starter lanes for industry news,
  celebrity style, designer/luxury, emerging designers, fashion week, bags, and
  shoes.
- `entities.example.yaml` defines brands, designers, celebrities, products,
  categories, and trends. Single-word/common aliases may need context terms
  unless explicitly marked safe with a reason; ordinary multi-word aliases can
  match without context under current matcher rules.
- `scoring.example.yaml` defines scoring windows, label thresholds, confidence
  filtering, source diversity bonuses, high-weight source bonuses, and optional
  candidate discovery thresholds.

Broader optional public-source starter packs live in
[configs/source-packs](configs/source-packs). See
[docs/source-packs.md](docs/source-packs.md). For sites without native feeds,
self-host [RSSHub](docs/source-packs.md#self-hosted-rsshub) and add
`type: rsshub` sources pointing at your local instance.

Optional entity watchlist packs live in [configs/entity-packs](configs/entity-packs).
See [docs/entity-packs.md](docs/entity-packs.md).

Check a source pack before copying or editing it:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
```

Check whether configured public RSS/RSSHub feeds and GDELT lanes are reachable
today without collecting or writing artifacts:

```bash
uv run fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml
```

In proxy-configured environments, refresh from the committed lockfile/frozen
install so the HTTP client's SOCKS transport helper is present. Fashion Radar
does not manage proxy pools or rotate proxies; it only uses the standard
environment observed by the HTTP client.

Check an entity pack before copying or editing it:

```bash
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
```

Check a community signal handoff file before import:

```bash
uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
```

Check a directory of community signal handoff files before choosing files to dry
run or import:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar community-handoff-manifest ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar community-handoff-workflow ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-handoff-check-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
```

The linters are local and read-only. They do not collect sources, fetch live
feeds or URLs, run matching/scoring, open SQLite, import rows, or create
config/data/report artifacts.

`import-signals-dir --dry-run` is also local and read-only. It validates matched
regular files directly under one local directory through the same importer model
as `import-signals --dry-run`; it does not recurse, open SQLite, import rows, or
create config/data/report artifacts.

`import-signals-dir` without `--dry-run` imports the same matched local files
only after every matched file validates. Validation failures import nothing and
do not create the data directory or SQLite database.

`community-handoff-manifest` can print a directory producer manifest before
workflow or directory validation. It is local and print-only; it describes the
target directory, file pattern, suggested filename, producer contract/profile
pointers, `directory_example_paths`, storage note, and workflow commands
without reading the supplied directory or creating artifacts.

`community-handoff-workflow` can print the same directory handoff order before
you run any step: `lint_handoff_directory`, `preview_candidate_phrases`,
`review_handoff_readiness`, `dry_run_directory_import`,
`import_directory_signals`, and `print_post_import_review`. The
`review_handoff_readiness` step prints the `community-handoff-check-dir`
local-only handoff readiness report before importing rows. It prints copyable
commands only; it does not execute commands, read the supplied directory,
validate files, import rows, open or write SQLite, fetch URLs, log in, download
media, automate browsers, scrape, monitor, watch folders, schedule work, add
source/platform connectors, prove demand, verify platform coverage, rank
sources, write reports, update dashboards, generate configs, or generate entity
files.

`community-handoff-check-dir` can print one local-only handoff readiness report
before import. It reads only matched local regular files and local config. It
does not import rows, uses no SQLite, creates no config/data/report/dashboard/digest artifacts,
and has no fetch URLs/login/platform APIs/download media/browser automation/scrape/crawl/
monitor/watch/schedule/connectors/source acquisition/demand proof/ranking/coverage verification/
entity generation/compliance/policy/authorization/safety-review features.

`imported-signals` is local and read-only. It opens an existing SQLite database
in read-only mode and returns retained rows where `source_type` is
`manual_import`, including stored `platform` labels when present; it does not
import rows, fetch URLs, run matching/scoring, generate reports, monitor
folders, infer platform coverage, or create dashboard/report artifacts.

`imported-signals-summary` is local and read-only. It opens an existing SQLite
database in read-only mode and groups retained `manual_import` rows by stored
`source_name` and local `platform` provenance labels where present, showing row
counts and item-level stored match presence without exposing row titles, URLs,
summaries, import file paths, or match details. `source_name` and `platform` are
stored local provenance labels, not statements about anything outside the local
database.

`imported-entity-deltas` is local and read-only. It compares stored matched
entities on retained `manual_import` rows across collected-at windows and
prints aggregate entity counts only.

`imported-entity-evidence` is local read-only and imported-only. It opens an
existing SQLite database in read-only mode and shows retained local rows whose
`manual_import` stored matched entity equals the requested entity. Output is a
privacy-safe drilldown with review metadata plus `window`, `id`, `source_name`,
`title`, `url`, `published_at`, and `collected_at`; it omits summaries,
candidate contexts, match internals, import file paths, normalized keys, and
platform labels. It does not import rows, fetch URLs, run entity matching,
write scores, generate reports, monitor folders, scrape, automate browsers, use
platform APIs, or perform account or cookie work.

`imported-candidates` is local and read-only. It opens an existing SQLite
database in read-only mode and computes review-oriented candidate signals from
retained `manual_import` rows only; it does not import rows, fetch URLs, run
entity matching, write scores, generate reports, monitor folders, or create
dashboard/report artifacts.

`imported-candidate-evidence` is local and read-only. It opens an existing
SQLite database in read-only mode and shows phrase-scoped retained
`manual_import` evidence rows. It does not import rows, run entity matching,
write scores, generate reports, monitor folders, or create dashboard/report
artifacts.

## Reports And Storage

The local database defaults to `fashion-radar.sqlite` under the configured data
directory. Use `uv run fashion-radar migrate-db --data-dir "$PWD/data"` when
you want to initialize or upgrade that local SQLite schema explicitly. Reports
are written as:

```text
fashion-radar-YYYY-MM-DD.md
fashion-radar-YYYY-MM-DD.json
fashion-radar-YYYY-MM-DD.html
```

Reports contain source attribution, links, snippets/metadata, matched entities,
candidate signals from configured sources and imported local signals, and score
components. They should be reviewed before being shared publicly.

Optional local digest artifacts can make daily output easier to find:

```text
latest.md
latest.json
report-index.json
fashion-radar-YYYY-MM-DD.eml
```

See [docs/daily-digest.md](docs/daily-digest.md).

Use cleanup when you want to prune old collected items:

ROW ONE report artifact pruning remains separate from SQLite item retention.
`row-one refresh` may prune older generated dated report files for the local
presentation path after the current report and site are generated, then runs
default 1-day SQLite item retention with the same cleanup semantics as
`clean-old-data`. Use `--retention-days N` for a longer ROW ONE local history or
`--skip-data-retention` to opt out for a refresh. `clean-old-data` remains the
standalone/manual cleanup command for pruning old collected SQLite rows outside
the ROW ONE refresh path.

To reset the deterministic repo-local sample, see
[docs/first-run.md#reset-the-repo-local-sample](docs/first-run.md#reset-the-repo-local-sample).
`clean-old-data` is retention pruning for old collected items and matcher rows;
it is not a full reset of generated configs, reports, or the sample database.

```bash
uv run fashion-radar clean-old-data --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30 --dry-run
uv run fashion-radar clean-old-data --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30
```

See [docs/data-retention.md](docs/data-retention.md).

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/first-run.md](docs/first-run.md)
- [docs/cli-reference.md](docs/cli-reference.md)
- [docs/source-boundaries.md](docs/source-boundaries.md)
- [docs/dependency-mirrors.md](docs/dependency-mirrors.md)
- [docs/scoring.md](docs/scoring.md)
- [docs/candidate-discovery.md](docs/candidate-discovery.md)
- [docs/trend-deltas.md](docs/trend-deltas.md)
- [docs/daily-digest.md](docs/daily-digest.md)
- [docs/manual-signal-import.md](docs/manual-signal-import.md)
- [docs/community-signal-import.md](docs/community-signal-import.md)
- [docs/community-signal-quality.md](docs/community-signal-quality.md)
- [docs/entity-packs.md](docs/entity-packs.md)
- [docs/entity-pack-quality.md](docs/entity-pack-quality.md)
- [docs/data-retention.md](docs/data-retention.md)
- [docs/dashboard.md](docs/dashboard.md)
- [docs/scheduling.md](docs/scheduling.md)
- [docs/source-packs.md](docs/source-packs.md)
- [docs/source-pack-quality.md](docs/source-pack-quality.md)
- [docs/github-upload-checklist.md](docs/github-upload-checklist.md)
- [docs/REVIEW_PROTOCOL.md](docs/REVIEW_PROTOCOL.md)

## Development

```bash
uv sync --locked --dev
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest
```

For PR/release verification, use [CONTRIBUTING.md](CONTRIBUTING.md) or
[docs/github-upload-checklist.md](docs/github-upload-checklist.md); public
lockfile checks should use `UV_NO_CONFIG=1`.

For agent-run verification, prefer `uv --no-config run --frozen ...` so
user-level mirror config cannot rewrite `uv.lock`; keep mirror-backed commands
as frozen mirror install commands, not test or lockfile regeneration commands.

Optional article text extraction uses the `article` extra:

```bash
uv sync --locked --dev --extra article
```

The core RSS/GDELT workflow does not require this extra. If `trafilatura` is not
installed, article extraction returns a conservative skipped result instead of
attempting a fallback page collector.

## GitHub Publishing Boundary

This repository can be prepared for GitHub locally, but the user controls remote
creation, pushing, PyPI publishing, and artifact uploads. Do not upload local
SQLite databases, generated reports, browser state, account/session artifacts,
secrets, build artifacts, or CodeGraph database files.
