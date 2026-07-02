# Stage 264 ROW ONE Daily Readiness & Preview Design

## Goal

Stage 264 turns the existing ROW ONE static edition from "generated files exist"
into a daily-readable product surface that tells the user and downstream app
whether today's edition is ready to open.

## Product Gap

Stages 260-263 created the local ROW ONE site, detail pages, bilingual chrome,
reader orientation, editorial synthesis, local serving, schedule snippets, and
the `row-one-app/v1` JSON contract. The remaining day-to-day gap is operational:
users still need to infer readiness from separate commands and files. The
homepage does not clearly state when the edition was generated, how many stories
and evidence links are available, which sections are empty, or what URL/path to
open after a build.

Stage 264 closes that readiness gap without changing collection, scoring,
matching, ranking, social connectors, translation, image generation, hosting, or
the strict `row-one-app/v1` contract.

## Chosen Approach

Add a small readiness layer derived from existing `RowOneEdition` data:

- a deterministic `RowOneReadiness` summary in Python;
- a homepage "Latest Edition" status strip;
- a CLI `row-one preview` command that builds the static site and prints the
  local file/path, optional dry-run serve URL, story count, section count,
  evidence count, empty sections, generated timestamp, and readiness label;
- first-run/release smoke coverage that confirms ROW ONE CLI help and schedule
  output stay discoverable;
- package archive guardrails that keep ROW ONE docs/schema/package files in
  the source distribution.

This keeps the core static-site architecture intact and gives both humans and
app integrators a clear readiness signal before later visual polish or remote
deployment work.

## Architecture

```text
existing report/state
  -> existing build_row_one_edition()
  -> new readiness summary derived from RowOneEdition
  -> existing render_row_one_site()
  -> homepage status strip + CLI preview output
  -> existing local serve / schedule snippets
```

### Components

- `fashion_radar.row_one.readiness`
  - Defines `RowOneReadiness`.
  - Computes story count, section count, empty section keys/titles, safe evidence
    count, generated-at label, edition-date label, and readiness label.
  - Uses only existing `RowOneEdition` and shared ROW ONE utility helpers. It
    must not import from `templates.py`, because `templates.py` imports the
    readiness helper to render the homepage status strip.

- `fashion_radar.row_one.utils`
  - Holds shared helpers for safe external URLs and UTC formatting.
  - Is dependency-light and imported by `templates.py`, `render.py`, and
    `readiness.py` to avoid circular imports.

- `fashion_radar.row_one.templates`
  - Renders a compact homepage status strip immediately under the masthead.
  - Renders bilingual labels for generated time, edition date, story count,
    evidence count, and empty sections.

- `fashion_radar.cli`
  - Adds `fashion-radar row-one preview`.
  - Reuses the same options as `row-one build`, plus `--host`, `--port`, and
    `--dry-run-serve-url`.
  - Builds the site once, uses the returned internal `RowOneEdition` to compute
    readiness, prints the site path and readiness lines, and when requested
    prints the same safe local/LAN URL message used by `row-one serve --dry-run`.

- `scripts/check_first_run_smoke.py`
  - Adds ROW ONE CLI discoverability checks for `row-one --help`,
    `row-one build --help`, `row-one serve --help`, `row-one schedule --help`,
    and `row-one preview --help`.
  - Adds a schedule-output check proving the daily sequence remains
    `fashion-radar run` before `fashion-radar row-one build --latest-only`.

- `scripts/check_package_archives.py`
  - Requires `docs/row-one.md` and the ROW ONE package source files in the sdist
    alongside the already-required `schemas/row-one-app.schema.json`.

## Readiness Labels

Readiness is intentionally simple and deterministic:

- `ready` / `可阅读`: at least one story exists.
- `empty` / `暂无故事`: no stories exist, but the site is still valid and renders
  an empty-state edition.

This stage does not infer platform coverage, demand proof, market freshness, or
whether external websites were reachable. It only communicates the readability
of the generated local edition.

## Preview Output

`fashion-radar row-one preview` should print concise machine-readable-ish text:

```text
ROW ONE preview
Site: reports/row-one/site/index.html
JSON: reports/row-one/site/data/edition.json
Stories: 12
Sections: 5
Evidence links: 21
Empty sections: none
Generated at: 2026-07-02T04:00:00Z
Readiness: ready
Open: http://127.0.0.1:8787
```

The command does not start a long-running server. It gives the user the next URL
or path to open and remains safe in automated smoke tests.

`edition_date` is intentionally displayed as a date-only value in the readiness
surface while `data/edition.json` continues to emit the existing
`row-one-app/v1` date-time string. This is display copy, not a contract change.

## Boundaries

Stage 264 does not:

- add source acquisition, scraping, browser automation, platform APIs, login,
  cookies, proxy pools, CAPTCHA bypass, or paywall bypass;
- change matching, scoring, ranking, section caps, story IDs, or source
  attribution;
- call LLMs, translation services, image services, or paid APIs;
- add remote deployment, public hosting, authentication, cache invalidation, or
  background daemon management;
- add a compliance-review product feature;
- change the `row-one-app/v1` JSON contract shape.

## Acceptance Criteria

- `row-one preview` builds the same ROW ONE site as `row-one build` and prints
  the site path, JSON path, story count, section count, safe evidence count,
  empty section summary, generated timestamp, readiness label, and optional
  dry-run serve URL.
- The homepage contains a bilingual Latest Edition status strip derived from
  the current edition, including generated time, edition date, story count,
  evidence count, and empty sections.
- Empty editions render the status strip with `empty` readiness and do not crash.
- Unsafe evidence/source URLs are not counted as safe evidence links.
- The existing `data/edition.json` `row-one-app/v1` contract remains unchanged
  and existing schema tests continue to pass.
- First-run smoke checks cover ROW ONE subcommand help and schedule two-step
  refresh ordering.
- Package archive checks require ROW ONE docs, schema, and package source files.
- Focused ROW ONE tests, first-run smoke, package archive checks, Ruff, and the
  full pytest suite pass.
