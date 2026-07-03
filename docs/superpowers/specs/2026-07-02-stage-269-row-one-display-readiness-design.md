# Stage 269 ROW ONE Display Readiness Design

## Objective

Prepare ROW ONE for a more professional, image-ready daily fashion site by adding a stable display/media contract for each story, rendering deterministic visual slots in the static site, and persisting the bilingual language preference in the browser.

This stage is intentionally bounded. It does not call OpenDesign, generate images, fetch images, add collectors, deploy a server, install schedules, or add compliance-review product features.

## Current State

- ROW ONE already renders a static index, detail pages, CSS, JS, `data/edition.json`, and `data/manifest.json`.
- The app contract is versioned as `row-one-app/v1` and currently contains text, links, dates, section metadata, and evidence, but no visual/display metadata.
- The rendered site has bilingual buttons, but every page load resets the language to English.
- The site styling is functional, but its current warm paper and oxblood palette is too close to a common generated luxury default. The next visual step should be colder, sharper, and more editorial.
- The app schema uses `additionalProperties: false`, so visual readiness must be introduced through an explicit schema/test update instead of ad hoc payload fields.

## Design Read

Reading this as: a local fashion editorial daily site for one owner and an app client, with a restrained magazine/edit-room visual language, leaning toward native HTML/CSS, deterministic server-side rendering, and a cold monochrome palette with one controlled accent.

Dial values:

- `DESIGN_VARIANCE: 5`: enough editorial asymmetry to feel considered, but not an experimental landing page.
- `MOTION_INTENSITY: 2`: static generated HTML with hover/focus states only.
- `VISUAL_DENSITY: 5`: daily information surface, not a sparse marketing hero.

## Proposed Shape

Add story display models:

- `RowOneStoryImage`
  - `src: str`
  - `alt: LocalizedText`
  - `credit: str | None`
  - `source_url: str | None`
- `RowOneStoryDisplay`
  - `variant: "editorial" | "portrait" | "product" | "signal"`
  - `accent: "ink" | "graphite" | "steel" | "cobalt" | "rose"`
  - `image: RowOneStoryImage | None`

Add `display: RowOneStoryDisplay | None = None` to `RowOneStory`. Edition building should assign deterministic display metadata to generated stories:

- `top_stories`: `editorial`, `ink`
- `brand_moves`: `editorial`, `graphite`
- `celebrity_style`: `portrait`, `rose`
- `hot_products`: `product`, `cobalt`
- `rising_radar`: `signal`, `steel`

Manual `RowOneStory` construction may omit `display`; render and app payload helpers must still emit a deterministic fallback display object based on the section key. That keeps existing tests and outside callers compatible while making the app payload stable.

Display mapping and image-source safety should have one production source of truth. Add a small `fashion_radar.row_one.display` module that exposes:

- `display_for_section(section_key)`;
- `display_for_story(story)`;
- `safe_story_image_src(value)`.

Edition generation, app payload rendering, and HTML templates must import these helpers instead of carrying local copies.

## App Contract

Each story in `data/edition.json` should include a required `display` object:

```json
{
  "variant": "editorial",
  "accent": "ink",
  "image": null
}
```

When `image` is present, `src` must be sanitized before entering the app payload. Allowed image sources are:

- safe `http://` or `https://` URLs with a host;
- generated ROW ONE asset paths matching `assets/...` without traversal, absolute paths, control characters, or backslashes.

If an image source is unsafe, the payload should set `image` to `null`. Templates should use the same safe image decision so unsafe paths never enter HTML.

The contract version remains `row-one-app/v1` because this project is still in local alpha and the change is additive for the generated app payload. The schema must still reject unknown fields and invalid display variants.

## Static Site Rendering

The site should render a visual layer in three places:

- lead story: a larger visual slot beside the lead text;
- story cards: a compact visual strip/header before the card headline;
- detail page: a story hero visual block near the top.

If `display.image` is safe and present, render an `<img>` with localized alt text. If no image is present, render a deterministic fallback visual using the display variant, headline initials, section title, and neutral editorial patterning. The fallback should be real HTML/CSS, not hand-drawn SVG art.

The CSS should move away from warm paper/oxblood and use a cold editorial system:

- near-white paper;
- ink/charcoal text;
- steel/chrome surfaces;
- one restrained cobalt accent;
- no gradient blobs, decorative orbs, or fake product screenshots.

## Language Preference

`row-one.js` should:

- read `localStorage["row-one:language"]`;
- accept only `en` or `zh`;
- default to `en` if storage is missing or unavailable;
- write the selected language after a toggle click;
- continue updating `document.documentElement.lang`, `body.lang-zh`, and `aria-pressed`.

Storage failures must not break page interaction.

## Tests

Add or update focused tests before production changes:

- edition tests prove deterministic display assignment by section;
- app contract tests prove generated payload contains `display`, schema validates it, unsafe image sources become `null`, and schema rejects invalid display variants;
- render tests prove the index, cards, detail page, CSS, and JS include the new visual slots and language persistence hooks;
- docs tests prove ROW ONE documentation describes display/media readiness and the future OpenDesign boundary.

## Non-Goals

- No OpenDesign calls.
- No raster image generation.
- No image downloads.
- No new media cache.
- No collector or social platform changes.
- No schedule install or deploy.
- No app framework rewrite.
- No compliance-review product feature.

## Acceptance Evidence

- `tests/test_row_one_edition.py` covers deterministic display metadata.
- `tests/test_row_one_app_contract.py` covers schema-safe display payloads.
- `tests/test_row_one_render.py` covers visual slots, safe image handling, CSS palette hooks, and persisted language preference.
- `tests/test_row_one_docs.py` covers documentation.
- Focused tests pass before broader gates.
