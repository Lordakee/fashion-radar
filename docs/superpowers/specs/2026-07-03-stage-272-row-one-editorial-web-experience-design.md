# Stage 272 ROW ONE Editorial Web Experience Design

## Goal

Stage 272 makes the generated ROW ONE website feel like a professional fashion
intelligence product, not just a functional static report. It uses the
`row-one-app/v2` content organization from Stage 271 to improve the homepage
and detail page reading experience while staying fully local, deterministic,
and static.

This stage closes the current product gap between a machine-readable organized
payload and a polished daily website that can be opened from the app or browser.

## Design Read

ROW ONE is a local editorial fashion-intelligence site for a design-conscious
reader. The visual language should be premium, restrained, and magazine-like,
with a cold luxury palette, dense-but-readable story rails, and no marketing
landing-page hero.

Design dials:

- Design variance: 6
- Motion intensity: 3
- Visual density: 5

## Current State

ROW ONE currently generates:

- a static homepage with masthead, readiness strip, section navigation, lead
  story, section blocks, and story cards;
- static detail pages with bilingual headings and evidence links;
- `data/edition.json` using `row-one-app/v2`, including `content_sections`,
  `detail_sections`, and `evidence_summary`;
- `data/manifest.json` and `data/runtime.json` for discovery/runtime status;
- deterministic language-toggle JavaScript and local CSS.

The page is functional and contract-safe, but it still underuses the Stage 271
organization. In particular, section navigation is only a directory grid, story
cards do not expose enough rail-level scanning hierarchy, detail pages do not
provide an article-level table of contents, and the page lacks a stronger ROW
ONE product surface for daily use.

## Stage Boundary

Stage 272 is presentation-only.

It will not:

- add collectors or source acquisition;
- scrape social platforms;
- call platform APIs;
- call LLMs or translation services;
- generate or fetch images;
- install cron/systemd timers;
- deploy or publish the site;
- change `row-one-app/v2`, `row-one-manifest/v1`, or `row-one-runtime/v1` schema
  shapes;
- add compliance-review product features.

Local deployment installation and daily 04:00 automation remain deferred to a
future stage. Stage 272 may mention that the existing runtime surface supports
fixed local serving, but it will not install or start background services.

## User Experience

### Homepage

The homepage should read as a daily editorial command surface:

- a top masthead with ROW ONE, edition date, readiness, language controls, and
  concise daily summary;
- a richer edition rail using existing sections and story counts;
- a lead story area that feels like the first editorial read, not a generic
  card;
- section blocks with scannable story cards that expose source, date, evidence
  count, tags, editorial takeaway, and detail link;
- empty sections that still look intentional and preserve the grid.

The homepage should remain static HTML produced from `RowOneEdition`; it should
not fetch `data/edition.json` client-side.

### Detail Pages

Detail pages should feel like structured article briefs:

- a sticky or prominent article utility header with brand return, section return,
  language controls, source/date/evidence metadata;
- an article contents rail that mirrors the emitted `row-one-app/v2`
  `detail_sections` order:
  Summary, Why It Matters, Editorial Takeaway, Signal Context, Reader Path,
  Evidence Trail;
- visually distinct evidence trail cards that clearly show safe clickable links
  and unsafe retained evidence rows without exposing unsafe URLs;
- stronger typographic rhythm for bilingual content.

The detail page should use the same deterministic fields already present on
`RowOneStory`.

## Implementation Approach

Keep the implementation inside the existing static renderer:

- `src/fashion_radar/row_one/templates.py` remains the renderer for homepage,
  details, CSS, and JS.
- Tests stay in `tests/test_row_one_render.py` and `tests/test_row_one_docs.py`.
- Documentation updates stay in `docs/row-one.md` and `README.md`.

No new runtime package dependency is required. CSS should use the existing
single-file `row_one_css()` approach. JavaScript remains limited to language
toggle behavior and small static-page affordances if needed.

## Visual Rules

Use a cold luxury palette already aligned with the current site:

- paper/steel/chrome neutrals;
- ink text;
- cobalt accent;
- no beige/brass/espresso palette;
- no purple/blue AI-glow gradients;
- no decorative blobs;
- no cards inside cards.

Typography can keep the existing local Georgia-backed `RowOneSerif` display
fallback and system sans body stack. Stage 272 should improve hierarchy,
spacing, labels, borders, and responsive behavior rather than introducing
external fonts.

## Tests

Add or update tests for:

- homepage renders a professional masthead/product surface with daily summary
  and readiness;
- homepage section navigation exposes rail-level story counts and content labels;
- story cards expose source/date/evidence/tags/takeaway/detail link in a
  predictable hierarchy;
- detail pages render article contents in the same order as the emitted
  `row-one-app/v2` `detail_sections`;
- evidence trail renders safe links and unsafe retained evidence rows safely;
- CSS contains the new layout hooks and keeps banned palette values out;
- docs describe the Stage 272 editorial website experience without implying new
  acquisition, deployment, or automation behavior.

## Acceptance Criteria

- The generated static site remains deterministic and local-only.
- The full existing ROW ONE app, manifest, runtime, CLI, and first-run tests keep
  passing.
- The site visibly uses organized content rather than merely listing links.
- No generated website artifacts are committed.
- No external dependency, paid API, platform API, browser automation, image
  generation, deployment, or timer installation is introduced.
