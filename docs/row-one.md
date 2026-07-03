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

This remains presentation-only. Reader orientation does not change ranking,
scoring, story IDs, source collection, JSON contract semantics, or publishing.

## Editorial Web Experience

ROW ONE renders a professional static website presentation for editorial review.
The homepage edition rail, article contents, evidence trail, and retained source
row labels help readers scan the generated site while staying within the
existing local data model. This editorial web experience uses existing
row-one-app/v4 content organization and adds homepage briefing topics: the ROW
ONE homepage renders the first four `daily_digest.briefing_topics` from the same
app payload written to `data/edition.json` as a presentation-only briefing topic
index with organized topic groups, topic labels, `story_ids`, `cards`, evidence
link counts, and links to existing detail pages. It remains not a flat link
list, does not scrape HTML, does not infer people from sections or tags, does
not change data/edition.json contract semantics, does not change matching,
ranking, scoring, story IDs, and does not add source collection or prove demand.
It does not add acquisition, deployment, or automation expansion.

The homepage briefing path renders a compact briefing path from
`daily_digest.blocks`, using `key_takeaways` and `signals_to_watch` to show what
to read next after the lead story. It does not duplicate `read_first`, links
only to existing detail pages, does not add source collection, does not change
app JSON contract semantics, and does not change matching, ranking, scoring, or
story IDs.

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

`data/edition.json` is the row-one-app/v4 app-facing contract for clients that
need to render the latest ROW ONE edition without scraping HTML. The payload is
validated by `schemas/row-one-app.schema.json` and includes localized edition
summary text, section counts (`story_count`), section anchors, story detail
hrefs (`detail_href` and `href`), published dates, evidence counts
(`evidence_count`), and sanitized URLs.

The active app version is `row-one-app/v4`. Its content organization surface
adds `content_sections`, `detail_sections`, `evidence_summary`, and
`daily_digest` so app clients render section rails and a daily briefing from the
JSON payload instead of reconstructing them from page markup. `content_sections`
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
source collection and does not prove demand.

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
`data/edition.json`, the `row-one-app/v4` edition payload, and stable generated
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
`row-one-app/v4`.

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
`row-one-app/v4` JSON contract, source collection, matching, scoring, ranking,
or scheduling semantics.

The homepage also renders a lead story presentation block and the index/detail
HTML include deterministic SEO/social metadata derived from existing edition and
story summaries.

## Generated Files

`row-one build` writes a static site under the selected output directory:

- `index.html`
- `details/`
- `assets/row-one.css`
- `assets/row-one.js`
- `data/edition.json`
- `data/manifest.json`
- `data/runtime.json`
- `.row-one-site` marker

The latest-only cleanup has two local presentation surfaces.
`row-one build --latest-only` and `row-one preview --latest-only` remove only
known ROW ONE generated children: `index.html`, `.row-one-site`, `details/`,
`assets/`, and `data/`. They do not delete unrelated files in the output
directory. If an existing directory has generated-looking children but no
`.row-one-site` marker, cleanup refuses to continue so user files are not
silently removed.

`row-one refresh` is latest-only for the local ROW ONE presentation path: after
writing the current dated report and rebuilding the site, it prunes older
generated report artifacts in the selected `--reports-dir` that match
`fashion-radar-YYYY-MM-DD.md`, `fashion-radar-YYYY-MM-DD.json`, and
`fashion-radar-YYYY-MM-DD.html`. It keeps the current refresh date's report
artifacts and does not prune SQLite data, collected rows, matcher rows, source
config, connectors, or files outside the local reports/site output surfaces.
Nonmatching digest and note files such as `latest.md`, `latest.json`,
`report-index.json`, `fashion-radar-YYYY-MM-DD.eml`, and local notes are left
untouched.

## Commands

- `row-one build`: builds the static ROW ONE site from existing local Fashion
  Radar report/state data. Important flags: `--as-of`, `--output-dir`, and
  `--latest-only`.
- `row-one refresh`: runs the single local daily refresh command for ROW ONE by
  refreshing the daily report data and generated site in one command. Important
  flags: `--as-of`, `--reports-dir`, and `--output-dir`; latest-only site cleanup
  is built in, and older generated dated report artifacts in `--reports-dir` are
  pruned after the current report is written.
- `row-one preview`: builds the static ROW ONE site and prints daily readiness
  details. Important flags: `--as-of`, `--output-dir`, `--latest-only`,
  `--host`, `--port`, and `--dry-run-serve-url`.
- `row-one status`: reads a generated ROW ONE site directory and prints runtime
  status from `data/runtime.json` without rebuilding or serving the site.
  Important flags: `--site-dir`.
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
  installing timers.

## Scheduling

ROW ONE scheduled refresh runs the single refresh command.
`fashion-radar row-one refresh` is the single local daily refresh command for
ROW ONE: it refreshes the daily report data and rebuilds the site in one local
operation. Schedule output includes the 04:00 command, `--output-dir`, and
serving guidance, but it prints snippets only.

Use:

```bash
uv run fashion-radar row-one schedule --time 04:00
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
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 0.0.0.0 --port 8787
```

The source checkout commands include a `row-one status --json` preflight so app
and operations scripts can validate the generated site before serving it.
The copyable source-checkout command group includes
`uv run fashion-radar row-one refresh`, `uv run fashion-radar row-one preview`,
`uv run fashion-radar row-one status --site-dir reports/row-one/site --json`,
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

Then enable the timer and fixed local server with:

```bash
systemctl --user daemon-reload
systemctl --user enable --now row-one-refresh.timer
systemctl --user enable --now row-one-serve.service
```

The generated timer runs the single ROW ONE refresh command at the selected local
time (default `04:00`). The generated serve service keeps the selected
`--output-dir` available on the fixed `--host` and `--port`.
