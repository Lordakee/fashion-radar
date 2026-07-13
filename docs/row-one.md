# ROW ONE

ROW ONE is the local daily fashion-news site generated from Fashion Radar output.
It turns existing daily report data into a static editorial website with a
homepage, detail pages, bilingual UI controls, JSON data, and a small local
server for testing.

## Quick Start

Run the single local daily refresh command, then preview or serve the ROW ONE
site:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar row-one refresh --as-of "$AS_OF" --output-dir reports/row-one/site
uv run fashion-radar row-one preview --as-of "$AS_OF" --latest-only --dry-run-serve-url
uv run fashion-radar row-one status --site-dir reports/row-one/site --json
uv run fashion-radar row-one ops-check --site-dir reports/row-one/site --host 0.0.0.0 --port 8787 --json
uv run fashion-radar row-one local-ops --time 04:00 --host 0.0.0.0 --port 8787
uv run fashion-radar row-one install-local --dry-run --time 04:00 --host 0.0.0.0 --port 8787
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 127.0.0.1 --port 8787
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 0.0.0.0 --port 8787
uv run fashion-radar row-one schedule --time 04:00
```

Use `127.0.0.1` for local-only testing. Use `0.0.0.0` only when you explicitly
want IP:port local-network serving on your LAN. Open `http://<LAN-IP>:8787`,
not `http://0.0.0.0:8787`, from another device. The local server has no
authentication layer.

## Boundary

ROW ONE is a local static site generator built from existing Fashion Radar daily
report data. It is presentation-only: it does not collect sources, does not run
entity matching, does not persist new scoring artifacts, does not call
translation services, does not call LLMs, does not add paid APIs, and does not
deploy or publish the site. It reuses the existing daily report and scoring
logic to construct the local display model. It provides no demand proof and no
platform coverage verification.

The bilingual UI uses deterministic labels and fallback text. It does not claim
to translate source articles. Open Design imagery is optional and not required
for tests.

## Editorial Synthesis

ROW ONE adds deterministic editorial synthesis to each generated story. The
synthesis explains the local signal, the report context behind it, and a reader
path for scanning the story. It is generated only from retained local report and
item fields such as section, label, mention counts, growth ratio, first-seen
timing, source name, local item title, and retained item metadata.

This is not translation, not LLM generation, not new scoring, and not demand
proof. It does not infer domestic/international market grouping unless explicit
source metadata is added in a future stage.

## Reader Orientation

ROW ONE includes a deterministic reader orientation layer for the generated
static site. The homepage renders edition contents with section jump links and
current story counts. Story cards include lightweight story-card metadata such
as section, source, date, evidence count, `why_it_matters`, and
`signal_context`. Detail pages include a back to section link and a Detail
Information Map built from existing story fields so readers can understand the
story context without leaving the generated page.

The top-level `data/edition.json` field `edition_brief` adds a deterministic
daily overview for clients and the homepage. It summarizes the read-first story,
active sections, briefing topics, follow-up path blocks, story counts, and safe
evidence counts before readers drill into cards or detail pages. It is derived
from existing ROW ONE story, content section, digest block, briefing topic,
route, and safe evidence-count data. `edition_brief.summary_points` now includes
read-first orientation, active-section coverage, explicit topic-mix counts
across brands, products, designers, and people, and positive heat-watch cues
when local raw mention deltas are available.
The edition brief is presentation-only organization, not a new collection,
matching, ranking, or scoring layer.

This remains presentation-only. Reader orientation does not change ranking,
scoring, story IDs, source collection, source acquisition, or publishing.

## Editorial Web Experience

ROW ONE renders a professional static website presentation for editorial review.
The homepage edition rail, article contents, evidence trail, and retained source
row labels help readers scan the generated site while staying within the
existing local data model. This editorial web experience uses existing
row-one-app/v7 content organization and adds homepage briefing topics: the ROW
ONE homepage renders the first four `daily_digest.briefing_topics` from the same
app payload written to `data/edition.json` as a presentation-only briefing topic
index with organized topic groups, topic labels, `story_ids`, `cards`, evidence
link counts, and links to existing detail pages. It remains not a flat link
list, does not scrape HTML, does not infer people from sections or tags, does
not change matching, ranking, scoring, story IDs, and does not add source
collection or prove demand.
It does not add acquisition, deployment, or automation expansion.

The homepage briefing path renders a compact briefing path from
`daily_digest.blocks`, using `key_takeaways` and `signals_to_watch` to show what
to read next after the lead story. It does not duplicate `read_first`, links
only to existing detail pages, does not add source collection, and does not
change matching, ranking, scoring, or story IDs.

The homepage renders the same `edition_brief` object before `signal_synthesis`,
the lead story, briefing topics, briefing path, and story rails. This makes the
generated site open with a daily overview while staying on the same app payload
as clients.

## Display/Media Readiness

Every app story includes a `display` object with `variant`, `accent`, and
`image`. `display.image` is `null` until a safe image path is available. Safe
image sources are safe `assets/...` image paths generated for the site or safe
http(s) URLs.

Generated pages render a typographic fallback visual when no image is present.
OpenDesign is the local image-generation integration name. OpenDesign imagery is
optional and not required for tests. Open Design imagery is optional and not
required for tests.

## App JSON Contract

`data/edition.json` is the row-one-app/v7 app-facing contract for clients that
need to render the latest ROW ONE edition without scraping HTML. The payload is
validated by `schemas/row-one-app.schema.json` and includes localized edition
summary text, section counts (`story_count`), section anchors, story detail
hrefs (`detail_href` and `href`), published dates, evidence counts
(`evidence_count`), and sanitized URLs.

The active app version is `row-one-app/v7`. Its content organization surface
adds `edition_brief`, `signal_synthesis`, `content_sections`, `detail_sections`,
`evidence_summary`, and `daily_digest` so app clients render a daily overview,
local observed signal synthesis, section rails, and a daily briefing from the
JSON payload instead of reconstructing them from page markup. `edition_brief`
is always present in `row-one-app/v7`; empty editions keep `edition_brief`
present, lead fields are `null`, counts are zero, links may be empty, and summary
text falls back to a no-stories-yet message. `signal_synthesis` is also always
present in `row-one-app/v7`; empty or no-reference editions keep
`signal_synthesis.groups` empty and use the no-signals-yet dek. `content_sections`
describes homepage rails with section labels, anchors, counts, and story
references. App cards in `content_sections`, `daily_digest.blocks`, and
`daily_digest.briefing_topics` include the existing `why_it_matters` and
`signal_context` story synthesis fields, so clients can render organized story
cards without opening the full story object first. `detail_sections` describes
detail-page rails, including the current story context and adjacent section
navigation. `evidence_summary` gives compact evidence-link counts and readiness
metadata for client badges. `daily_digest`
is the app-facing Today's Briefing surface: `read_first` selects the first story
to open, `key_takeaways` summarizes the first story from each non-empty section,
and `signals_to_watch` lists only positive local raw mention deltas. Together
these fields let app clients render section rails without scraping HTML and
app clients can render a daily briefing without scraping HTML. It does not add
source collection, does not change matching, ranking, scoring, sorting, or
story IDs, and does not prove demand.

`signal_synthesis` is a top-level `data/edition.json` field derived from
`daily_digest.briefing_topics` and reshapes existing topic data into
brand/product/designer/person summaries. It carries local observed text and the
fixed "Local observed signals; review required." boundary so app clients can
show what needs review without inventing market claims. It uses existing local
heat deltas, safe evidence counts, `story_ids`, and safe detail hrefs; it does
not add collection, source acquisition, external enrichment, LLM generation,
image generation, matching changes, ranking changes, scoring changes, sorting
changes, story ID changes, or deployment behavior.

`signal_synthesis.groups[].signals[].story_refs` is an app-facing information
organization index for inline signal support. Each `story_refs` item carries
compact supporting story references inline, derived from the same briefing topic
source story data that produced the signal group, so app clients can show which
existing ROW ONE stories support a local observed signal without opening a
separate lookup first. It is not a compliance review feature and does not change
collection, matching, ranking, scoring, sorting, or story IDs.
`schemas/row-one-app.schema.json` validates this field structurally; `row-one status`
and the first-run smoke also validate that each story ref mirrors the referenced
top-level story and keeps `story_refs[].story_id` aligned with `story_ids`.

The detail page renders a Detail Information Map derived from existing ROW ONE
story data: section, source, date, story type, tags, heat delta, evidence count,
and links only to existing detail-page anchors. This does not change collection,
matching, scoring, ranking, or story IDs.

`story_directory` is the app-facing route index for existing ROW ONE stories.
It gives app clients a route lookup surface derived only from the stories already
present in the edition payload, so clients can open story detail routes without
scraping HTML. It does not collect sources, does not change matching, scoring,
sorting, or story IDs, and does not introduce a separate story discovery layer.

`daily_digest.briefing_topics` is the app-ready briefing organization surface
for showing organized topic groups instead of a flat list of links. Each topic
contains stable topic labels, localized title text, `story_ids`, app-ready
`cards`, evidence counts, heat-delta summary fields, and source references
derived from explicit ROW ONE story references. Topic order is supplied by the
payload; stories inside each topic keep the generated ROW ONE story order.
Empty editions keep `briefing_topics: []`. The topic layer is not a link list,
does not infer people from sections, tags, headlines, source names, or URLs,
does not add source collection, does not prove demand, and does not change
matching, ranking, scoring, story IDs, cleanup, server, or schedule behavior.

Unsafe external URLs are written as `null`. Missing story publication timestamps
are represented as `null` in both `published_at` and `published_date`. The
`evidence_count` value counts only safe clickable evidence URLs; evidence entries
with unsafe or missing URLs remain present with `url: null` and `href: null`.
The schema pins UTC timestamp and date string shapes; generated values come from
ROW ONE's normalized datetime output.
The contract is generated from the existing ROW ONE edition model only; it does
not collect sources, run platform integrations, call LLMs, generate images,
deploy the site, or change matching, ranking, scoring, story IDs, cleanup,
server, or schedule behavior.

## App Discovery Manifest

`data/manifest.json` is the `row-one-manifest/v1` app discovery manifest. It is
validated by `schemas/row-one-manifest.schema.json` and points clients to
`data/edition.json`, the `row-one-app/v7` edition payload, and stable generated
site paths such as `index.html`, `assets/`, and `details/`.

The manifest contains only discovery metadata, counts, readiness status, and
capabilities. It does not duplicate story arrays, section arrays, absolute
host/port URLs, LAN preview URLs, local machine paths, source collection output,
or deployment state.

## Runtime Status

`data/runtime.json` is the row-one-runtime/v1 runtime metadata file for local
operations and smoke checks. It records the generated site runtime surface:
site path metadata, `data/edition.json`, `data/manifest.json`, the fixed local
serve port `8787`, default local serve host `127.0.0.1`, daily refresh time `04:00`,
latest readiness status, counts, and generated timestamp. It is local
operational metadata only and is not a deployment record.

`row-one status` reads the generated ROW ONE site directory and prints the
runtime status without rebuilding the site or starting a server. It performs a
lightweight runtime contract check: the generated site marker must be present,
`data/runtime.json`, `data/edition.json`, and `data/manifest.json` must exist
as JSON objects, runtime paths must match the fixed local contract, and the key
generated timestamps, counts, and readiness fields must agree across runtime,
manifest, and edition payloads. It is intended for first-run smoke checks and
operator preflight checks before serving
`http://127.0.0.1:8787` or `http://<LAN-IP>:8787`.

`row-one status --json` keeps the nested `runtime` and `manifest` payloads
intact and adds an additive CLI projection for app and operations preflight
checks. The top-level JSON exposes `counts`, `readiness`, `refresh_time`,
`local_url`, `lan_url_hint`, `index_path`, `edition_path`, `manifest_path`, and
`runtime_path` for direct consumption. It also exposes structured `site`,
`serve`, `contracts`, and `refresh` objects projected from the validated
runtime, manifest, and app payloads. These fields are CLI status output only;
they do not add fields to `row-one-runtime/v1`, `row-one-manifest/v1`, or
`row-one-app/v7`.

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

## Ops Check

`row-one ops-check` is a read-only local ROW ONE operations diagnostic. It
inspects generated site file presence, runtime freshness, local HTTP/port
readiness, access URLs, and the expected user systemd filenames under the
selected unit directory. It can print human-readable output or `--json` output
for local operator dashboards.

When the site is ready and all three canonical filenames are present, it reports
`site_ready_scheduler_unverified` and a systemd status of
`unit_files_present`. This is filename evidence only: it does not prove unit
contents, drop-ins, enablement, activity, or a successful future refresh. Missing
canonical filenames yield `attention` only when runtime evidence is otherwise
healthy. Incomplete or invalid runtime evidence can still yield `unknown`, even
when canonical filenames are missing.

It does not start servers, install or enable systemd units, call `systemctl` or
`loginctl`, kill processes, refresh or rebuild the site, write files or artifacts, change
`row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, source
collection, fetching, extraction, scoring, ranking, LLM, connectors, deployment
automation, market grouping, domestic/international classification, or
compliance-review behavior. Use `row-one status --json` as the script-facing
preflight surface; runtime metadata is local operational metadata only and is
not a deployment record. Fashion Radar does not invoke `systemctl` or `loginctl`.
After `status` has validated the generated site, the first-run smoke checks ROW
ONE serve dry-run URLs, then starts a temporary local HTTP server, fetches
through that temporary local HTTP server, and terminates it without leaving a
long-running process.

The canonical first-run local serving boundary is fixed IP:port `127.0.0.1:8787`
for local-only testing. Use `0.0.0.0:8787` only for explicit LAN serving, and
open `http://<LAN-IP>:8787` from other devices. Daily local refresh examples use
`04:00`.

## Daily Readiness And Preview

ROW ONE adds a deterministic daily readiness and preview layer for the generated
site. The homepage renders a Latest Edition status strip directly under the
masthead so a reader can see the generated timestamp, edition date, Stories,
Evidence links, Empty sections, and a simple readiness label.

The readiness labels are deliberately narrow:

- `ready`: at least one local story exists in the generated edition.
- `empty`: the site rendered successfully, but the current edition has no
  stories yet.

`row-one preview` builds the same static site as `row-one build` and prints the
site path, `data/edition.json` path, `data/manifest.json` output path, story
count, section count, evidence link count, empty sections, generated timestamp,
and readiness label. Preview prints the manifest path so app clients and smoke
checks can verify the Manifest: `data/manifest.json` output without scraping
HTML. Use
`row-one preview --dry-run-serve-url` to also print the same local URL message
used by `row-one serve --dry-run` without starting a long-running server.
The CLI preview uses compact English status labels for terminal output; the
homepage Latest Edition status strip renders bilingual English/Chinese labels.

This is a display/readiness surface only. It does not change the
`row-one-app/v7` JSON contract, source collection, matching, scoring, ranking,
or scheduling semantics.

The homepage also renders a lead story presentation block and the index/detail
HTML include deterministic SEO/social metadata derived from existing edition and
story summaries.

## Generated Files

`row-one build` writes a static site under the selected output directory:

- `index.html`
- `details/`
- `articles/index.html` when the current edition has publishable saved local
  articles for the daily saved article library
- `articles/<story-id>.html` first-class local article pages when the current
  edition has publishable saved local articles
- `assets/row-one.css`
- `assets/row-one.js`
- `data/edition.json`
- `data/manifest.json`
- `data/runtime.json`
- `data/local-intelligence.json` when homepage Daily Local Intelligence sections
  are available from current saved local article bodies
- `data/articles/<story-id>.json` when ROW ONE local article sections are
  enabled for a source and article extraction or stored-summary fallback succeeds
- `.row-one-site` marker

ROW ONE detail pages can render a local article section before the editorial
analysis. This is generated only from sources that explicitly set
`row_one_article.enabled: true` in `sources.yaml`; the default is off. The
generated section is capped by `row_one_article.max_chars`, respects the same
source HTTP timeout, robots, and paywalled-domain settings used for extraction,
falls back to already collected local source summaries when extraction is
unavailable, and is written only to the generated static site under
`data/articles/` plus the matching detail page. It is not stored in SQLite, not
added to the daily report JSON, and not added to `data/edition.json`.
Saved sidecar JSON and detail pages carry local article body provenance in
`body_source`: `extracted` marks usable extracted article text,
`summary_fallback` marks a publishable ROW ONE local article body generated
from the story summary/editorial fallback when extraction was skipped, failed,
or unusable, and `skipped` marks no publishable saved body. This is sidecar/data detail-page
provenance only; it does not change `data/edition.json`, does not change
`row-one-runtime/v1`, and does not add compliance-review behavior.
The homepage keeps local article bodies out of `data/edition.json`; when
`data/local-intelligence.json` is present, cards link back to generated detail
pages and exact `#local-article-paragraph-N` anchors.
Content sections use source-backed reference excerpts when a matched entity,
designer, person, bag, shoe, or product appears in a saved local paragraph;
otherwise they retain the deterministic reference metadata fallback.
The `takeaways` content section prefers saved paragraphs with explicit brand,
designer, person, bag, shoe, or product matches, while retaining the first saved
paragraphs as the deterministic fallback when no signal paragraph is present.
Detail pages render a local article map for structured saved articles, and
paragraph target highlight styling makes in-page paragraph jumps visibly land
on the referenced saved text.
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
Stage 387 adds a generated-site-only Daily Local Brand, Product & People Signal Digest section on the ROW ONE homepage in `index.html`; it reuses current-edition ROW ONE stories, current-edition saved local article sidecars, existing generated local article page routes, saved content-section items, references, and local article content-section anchors to organize factual brand, product, and people coverage without changing app-facing contracts; it does not create `data/daily-local-brand-product-people-signal-digest.json`, does not create `daily-local-brand-product-people-signal-digest.html`, does not create new article-source sidecars or route families, does not alter `articles/index.html`, `articles/<story-id>.html`, detail pages, `data/edition.json`, `data/manifest.json`, or `data/runtime.json`, does not publish full article bodies on the homepage, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
Stage 386 adds a generated-site-only Daily Saved Text Takeaways section on the ROW ONE homepage in `index.html`; it reuses current-edition ROW ONE stories, current-edition saved local article sidecars, existing generated local article page routes, saved paragraphs, content sections, and local article anchors to show short capped saved-text snippets grouped for reading without changing app-facing contracts; it does not create `data/daily-local-saved-text-takeaways.json`, does not create `data/daily-saved-text-takeaways.json`, does not create `daily-local-saved-text-takeaways.html`, does not create `daily-saved-text-takeaways.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, detail pages, `data/edition.json`, `data/manifest.json`, or `data/runtime.json`, does not publish full article bodies on the homepage, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
Stage 385 adds a generated-site-only Daily Local Synthesis Evidence Trail inside the existing Daily Local Synthesis Brief cards on the ROW ONE homepage in `index.html`; it reuses current-edition ROW ONE stories, current-edition saved local article sidecars, existing generated local article page routes, and Stage 382 synthesis anchors to point readers from each homepage synthesis card to concrete saved-article content-section or paragraph anchors without changing app-facing contracts; it does not create `data/daily-local-synthesis-evidence-trail.json`, does not create `data/local-synthesis-evidence-trail.json`, does not create `data/daily-synthesis-evidence-trail.json`, does not create `daily-local-synthesis-evidence-trail.html`, does not create `local-synthesis-evidence-trail.html`, does not create `daily-synthesis-evidence-trail.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, detail pages, `data/edition.json`, `data/manifest.json`, or `data/runtime.json`, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
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
Stage 384 hardens the generated-site-only Daily Local Synthesis Brief presentation on the ROW ONE homepage by omitting blank thesis paragraphs, tightening the existing homepage-only renderer sentinel, and adding long-text wrapping for synthesis card titles, source chips, and saved-article route labels; it reuses the Stage 383 homepage section, current render model, existing CSS, and existing generated local article page routes while adding presentation-focused regression coverage without changing app-facing contracts; it does not create `data/daily-local-synthesis-quality.json`, does not create `data/daily-synthesis-quality.json`, does not create `daily-local-synthesis-quality.html`, does not create `daily-synthesis-quality.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
Stage 383 adds generated-site-only Daily Local Synthesis Brief copy on the ROW ONE homepage inside `index.html` after the existing Daily Local Article Intelligence Brief and before the Daily Local Saved Article Organizer; it reuses current-edition ROW ONE stories, current-edition saved local article sidecars, existing generated local article page routes, and Stage 382 article-page synthesis fields to give readers a compact homepage-only cross-article synthesis without changing app-facing contracts; it does not create `data/daily-local-synthesis-brief.json`, does not create `data/local-synthesis-brief.json`, does not create `data/daily-synthesis-brief.json`, does not create `daily-local-synthesis-brief.html`, does not create `local-synthesis-brief.html`, does not create `daily-synthesis-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
Stage 382 adds generated-site-only Local Article Synthesis Brief copy inside `articles/<story-id>.html` after the existing Local Article Intelligence Brief and before the saved local article body; it reuses existing ROW ONE story fields, current-edition saved local article sidecars, existing brief sections, existing content-section text, existing saved paragraphs, existing generated local article page routes, and existing safe same-page content-section and paragraph anchors to give readers a compact narrative so-what interpretation without changing app-facing contracts; it does not create `data/local-article-synthesis-brief.json`, does not create `data/saved-local-article-synthesis-brief.json`, does not create `data/article-synthesis-brief.json`, does not create `local-article-synthesis-brief.html`, does not create `saved-local-article-synthesis-brief.html`, does not create `article-synthesis-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
Stage 381 adds generated-site only Saved Local Article Related-Read Connection Brief copy inside the existing related saved local reads section on `articles/<story-id>.html`; it reuses Stage 377/378/380 related-read cards, lanes, reasons, source names, shared reference chips, evidence bridge row counts, generated local article page routes, and existing safe renderable-card filters to explain why the next local reads connect without changing app-facing contracts; it does not create `data/saved-local-article-related-read-connection-brief.json`, does not create `data/local-article-related-read-connection-brief.json`, does not create `data/related-read-connection-brief.json`, does not create `saved-local-article-related-read-connection-brief.html`, does not create `local-article-related-read-connection-brief.html`, does not create `related-read-connection-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full related articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
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
Stage 310 adds a generated-site saved text reader on story detail pages. ROW ONE
lists saved local paragraphs as numbered reader segments that link to the
existing `#local-article-paragraph-N` anchors before the existing saved text.
This is a detail-page saved text reader only; it does not change
`row-one-app/v7`, does not change `data/edition.json`, uses existing `data/articles/<story-id>.json` sidecars, does not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change detail routes, does not change paragraph anchors, does not change schemas, does not add source collection, and does not add scoring.
Stage 309 adds newsroom digest polish: ROW ONE clusters duplicate saved
local-article cards in `data/local-intelligence.json` for the homepage
`strongest_reads` and `heat_movers` digest sections, evidence paragraph links
use reader-facing copy, and detail pages show compact local article provenance
from existing source/extraction/published/count fields. This is presentation
and sidecar organization only; it does not change `row-one-app/v7`, does not
change `data/edition.json`, does not change `row-one-manifest/v1`, and does
not change `row-one-runtime/v1`. It does not add source collection, does not
add scoring, and does not change collection, matching, story IDs, detail
routes, paragraph anchors, or schemas.

The latest-only cleanup has two local presentation surfaces.
`row-one build --latest-only` and `row-one preview --latest-only` remove only
known ROW ONE generated children: `index.html`, `.row-one-site`, `details/`,
`assets/`, `data/`, and `articles/`. They do not delete unrelated files in the
output directory. If an existing directory has generated-looking children but
no `.row-one-site` marker, cleanup refuses to continue so user files are not
silently removed.

`row-one refresh` is latest-only for the local ROW ONE presentation path: after
writing the current dated report and rebuilding the site, it prunes older
generated report artifacts in the selected `--reports-dir` that match
`fashion-radar-YYYY-MM-DD.md`, `fashion-radar-YYYY-MM-DD.json`, and
`fashion-radar-YYYY-MM-DD.html`. It keeps the current refresh date's report
artifacts. Report artifact pruning remains separate from SQLite item retention:
after the current site and reports are generated, `row-one refresh` runs default
1-day retention for SQLite `items` and `item_entities` unless
`--skip-data-retention` is passed. Use `--retention-days N` to keep longer local
SQLite item history. The SQLite retention step does not prune `collector_runs`,
does not prune `source_health`, does not prune `entity_first_seen`, does not
prune config files, does not prune generated site files, and does not change ROW
ONE contracts, detail routes, or schemas. Nonmatching digest and note files such
as `latest.md`, `latest.json`, `report-index.json`,
`fashion-radar-YYYY-MM-DD.eml`, and local notes are left untouched.

## Commands

- `row-one build`: builds the static ROW ONE site from existing local Fashion
  Radar report/state data. Important flags: `--as-of`, `--output-dir`, and
  `--latest-only`.
- `row-one refresh`: runs the single local daily refresh command for ROW ONE by
  refreshing the daily report data and generated site in one command. Important
  flags: `--as-of`, `--reports-dir`, `--output-dir`, `--retention-days`, and
  `--skip-data-retention`; latest-only site cleanup is built in, older generated
  dated report artifacts in `--reports-dir` are pruned after the current report
  is written, and default 1-day SQLite item retention runs after the current
  site and reports are generated. A non-skipped SQLite retention failure returns
  a nonzero exit status after report and site output is written.
- `row-one preview`: builds the static ROW ONE site and prints daily readiness
  details. Important flags: `--as-of`, `--output-dir`, `--latest-only`,
  `--host`, `--port`, and `--dry-run-serve-url`.
- `row-one status`: reads a generated ROW ONE site directory and prints runtime
  status from `data/runtime.json` without rebuilding or serving the site.
  Important flags: `--site-dir`. Use `row-one status --json` as the
  script-facing preflight surface before serving.
- `row-one ops-check`: runs a read-only local operations diagnostic for site
  freshness, server/port readiness, access URLs, and user systemd unit-file
  filename presence. Important flags: `--site-dir`, `--host`, `--port`,
  `--unit-dir`, `--as-of`, and `--json`. Its positive filename-only result is
  `site_ready_scheduler_unverified` with `unit_files_present`; it does not start
  servers, install systemd units, refresh or rebuild the site, write files, or
  change ROW ONE contracts.
- `row-one local-ops`: prints a ROW ONE local daily ops runbook for 04:00
  refresh, fixed IP:port serving, preview, `row-one status --json` preflight,
  source checkout commands, and cron snippets. It prints snippets only and does
  not install timers, build the site, start the server, or mutate files.
- `row-one install-local`: renders or writes user-level systemd units for the
  local ROW ONE daily site. With `--dry-run`, it prints the refresh service,
  refresh timer, serve service, and enable commands without writing files.
  Without `--dry-run`, it writes `row-one-refresh.service`,
  `row-one-refresh.timer`, and `row-one-serve.service` to the selected
  `--unit-dir` (default: `~/.config/systemd/user`). Existing unit files are not
  overwritten unless `--force` is passed.
- `row-one serve`: serves a generated site directory. Important flags:
  `--site-dir`, `--host`, `--port`, and `--dry-run`.
- `row-one schedule`: prints examples for 04:00 local scheduling without
  installing timers. Important flags: `--mode`, `--host`, and `--port`.

## Scheduling

ROW ONE scheduled refresh runs the single refresh command.
`fashion-radar row-one refresh` is the single local daily refresh command for
ROW ONE: it refreshes the daily report data and rebuilds the site in one local
operation. It also runs default 1-day SQLite item retention after the current
site and reports are generated. Use `--retention-days` for longer local history
or `--skip-data-retention` when a scheduled refresh must leave item history
untouched. The 1-day retention default is disk-friendly for test deployments, but
it reduces multi-day item history available to future scoring window comparisons
and heat scores. Schedule output includes the 04:00 command, `--output-dir`,
and serving guidance, but it prints snippets only. A non-skipped SQLite retention
failure returns a nonzero exit status after report and site output is written.

Use:

```bash
uv run fashion-radar row-one schedule --mode systemd --time 04:00 --host 0.0.0.0 --port 8787
uv run fashion-radar row-one local-ops --time 04:00 --host 0.0.0.0 --port 8787
uv run fashion-radar row-one install-local --dry-run --time 04:00 --host 0.0.0.0 --port 8787
```

`row-one schedule` and `row-one local-ops` print snippets only; they do not
install cron jobs or systemd timers. `row-one local-ops` also prints fixed
IP:port serving guidance, including `Open from LAN: http://<LAN-IP>:8787`, the
manual preview/serve commands for the latest-only local ROW ONE site, and a
copyable source-checkout command group:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cd /path/to/fashion-radar
uv run fashion-radar row-one refresh --config-dir configs --data-dir data --reports-dir reports --output-dir reports/row-one/site --as-of "$AS_OF"
uv run fashion-radar row-one preview --config-dir configs --data-dir data --reports-dir reports --output-dir reports/row-one/site --as-of "$AS_OF" --latest-only --host 0.0.0.0 --port 8787 --dry-run-serve-url
uv run fashion-radar row-one status --site-dir reports/row-one/site --json
uv run fashion-radar row-one ops-check --site-dir reports/row-one/site --host 0.0.0.0 --port 8787 --json
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 0.0.0.0 --port 8787
```

The source checkout commands include a `row-one status --json` preflight so app
and operations scripts can validate the generated site before serving it.
The copyable source-checkout command group includes
`uv run fashion-radar row-one refresh`, `uv run fashion-radar row-one preview`,
`uv run fashion-radar row-one status --site-dir reports/row-one/site --json`,
`uv run fashion-radar row-one ops-check --site-dir reports/row-one/site --host 0.0.0.0 --port 8787 --json`,
and `uv run fashion-radar row-one serve`.

`row-one install-local --dry-run` prints the complete user systemd unit files and
the enable commands. After reviewing the output, run the same command without
`--dry-run` to write the unit files. The generated units include a user-systemd
`PATH` entry for `%h/.local/bin` and `%h/.cargo/bin` so `uv` can be found in
common user installs. If this is a fresh install, generate the site once before
starting the serve unit:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar row-one refresh --as-of "$AS_OF" --output-dir reports/row-one/site
```

`row-one schedule --mode systemd` and `row-one install-local` use the same
canonical user-unit names: `row-one-refresh.service`,
`row-one-refresh.timer`, and `row-one-serve.service`. Fashion Radar does not
invoke `systemctl` or `loginctl`. Unattended user-systemd operation requires
manual lingering verification. Check it with `loginctl show-user "$USER" -p
Linger`; enabling lingering can require an authorized operator under host policy.

After writing the units, make the local user-systemd activation decision manually:

```bash
loginctl show-user "$USER" -p Linger
loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now row-one-refresh.timer
systemctl --user enable --now row-one-serve.service
systemctl --user status row-one-refresh.timer row-one-serve.service
```

The generated timer runs the single ROW ONE refresh command at the selected local
time (default `04:00`). The generated serve service keeps the selected
`--output-dir` available on the fixed `--host` and `--port`.
