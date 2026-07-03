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
uv run fashion-radar row-one local-ops --time 04:00 --host 0.0.0.0 --port 8787
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
as section, source, date, and evidence count. Detail pages include a back to
section link so readers can return to the relevant homepage section.

This remains presentation-only. Reader orientation does not change ranking,
scoring, story IDs, source collection, JSON contract semantics, or publishing.

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

`data/edition.json` is the row-one-app/v1 app-facing contract for clients that
need to render the latest ROW ONE edition without scraping HTML. The payload is
validated by `schemas/row-one-app.schema.json` and includes localized edition
summary text, section counts (`story_count`), section anchors, story detail
hrefs (`detail_href` and `href`), published dates, evidence counts
(`evidence_count`), and sanitized URLs.

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
`data/edition.json`, the `row-one-app/v1` edition payload, and stable generated
site paths such as `index.html`, `assets/`, and `details/`.

The manifest contains only discovery metadata, counts, readiness status, and
capabilities. It does not duplicate story arrays, section arrays, absolute
host/port URLs, LAN preview URLs, local machine paths, source collection output,
or deployment state.

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
`row-one-app/v1` JSON contract, source collection, matching, scoring, ranking,
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
- `.row-one-site` marker

The latest-only cleanup is intentionally narrow. `--latest-only` removes only known ROW ONE generated children:
`index.html`, `.row-one-site`, `details/`, `assets/`, and `data/`. It does not
delete unrelated files in the output directory. If an existing directory has
generated-looking children but no `.row-one-site` marker, cleanup refuses to
continue so user files are not silently removed.

## Commands

- `row-one build`: builds the static ROW ONE site from existing local Fashion
  Radar report/state data. Important flags: `--as-of`, `--output-dir`, and
  `--latest-only`.
- `row-one refresh`: runs the single local daily refresh command for ROW ONE by
  refreshing the daily report data and generated site in one command. Important
  flags: `--as-of` and `--output-dir`; latest-only cleanup is built in.
- `row-one preview`: builds the static ROW ONE site and prints daily readiness
  details. Important flags: `--as-of`, `--output-dir`, `--latest-only`,
  `--host`, `--port`, and `--dry-run-serve-url`.
- `row-one local-ops`: prints a ROW ONE local daily ops runbook for 04:00
  refresh, fixed IP:port serving, preview, and cron snippets. It prints
  snippets only and does not install timers, build the site, start the server,
  or mutate files.
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
```

Both commands print snippets only; they do not install cron jobs or systemd
timers. `row-one local-ops` also prints fixed IP:port serving guidance, including
`Open from LAN: http://<LAN-IP>:8787`, and the manual preview/serve commands for
the latest-only local ROW ONE site.
