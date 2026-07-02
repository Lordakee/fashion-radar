# ROW ONE

ROW ONE is the local daily fashion-news site generated from Fashion Radar output.
It turns existing daily report data into a static editorial website with a
homepage, detail pages, bilingual UI controls, JSON data, and a small local
server for testing.

## Quick Start

Run the normal Fashion Radar pipeline first, then build and serve the ROW ONE
site:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar run --as-of "$AS_OF"
uv run fashion-radar row-one build --as-of "$AS_OF" --latest-only
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

## Generated Files

`row-one build` writes a static site under the selected output directory:

- `index.html`
- `details/`
- `assets/row-one.css`
- `assets/row-one.js`
- `data/edition.json`
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
- `row-one serve`: serves a generated site directory. Important flags:
  `--site-dir`, `--host`, `--port`, and `--dry-run`.
- `row-one schedule`: prints examples for 04:00 local scheduling without
  installing timers.

## Scheduling

ROW ONE scheduled output is a two-step refresh. It runs `fashion-radar run`
first to refresh the daily report, then runs
`fashion-radar row-one build --latest-only` with the same timestamp. This
refreshes the daily report before rebuilding the ROW ONE site.

Use:

```bash
uv run fashion-radar row-one schedule --time 04:00
```

The command prints snippets only; it does not install cron jobs or systemd
timers.
