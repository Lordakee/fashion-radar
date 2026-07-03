## Stage 269 ROW ONE Display/Media Readiness — Code Review

**Verdict: Acceptable with one Important finding to address.**

The implementation is well-structured, safe-by-default, and scope-compliant. All 1740 tests pass, ruff is clean, backward compatibility is preserved, and the design objectives are met. One contract-consistency gap is worth fixing now.

### Critical
None.

### Important

**1. Schema `imageSrc` asset-path pattern is stricter than the Python sanitizer — renderer can emit schema-invalid payloads.**

`safe_story_image_src` (display.py:41) accepts any `assets/...` path that has no `\`, no control chars, and no `..` traversal. But the schema `imageSrc` second branch (schema:317) only allows `[A-Za-z0-9._~-]`. Characters like space, `+`, `!`, `$`, `&`, `=`, `:`, `@`, `%` pass Python but fail the schema.

Verified end-to-end: a manual story with `src="assets/foo bar.png"` renders into `data/edition.json` with `"src": "assets/foo bar.png"`, which then fails `row-one-app.schema.json` validation (1 error at `stories.0.display.image`).

This is unreachable for generated stories (all images are `null` in this stage), but it is a real contract gap: the single source of truth for "safe" diverges between the sanitizer and the schema, so any future image source with a non-trivial filename would silently break the `row-one-app/v1` contract guarantee.

Fix options (pick one):
- Align the Python sanitizer to the schema by restricting asset path characters to `[A-Za-z0-9._~-]` in `_safe_asset_path`; or
- Broaden the schema pattern to match the plan's suggested charset (`[A-Za-z0-9._~!$&'()*+,;=:@%/-]`) and have Python enforce that same set.

The plan (lines 355-368) actually specified the broader charset, so the schema drifted from the plan during implementation.

### Minor

**2. Double sanitization of image `src`/`source_url` is harmless but redundant.** `display_for_story` (display.py:31) already produces a sanitized `RowOneStoryDisplay` via `_safe_story_image`, then `_image_payload` (render.py:217) re-runs `safe_story_image_src` and `safe_external_url` on the already-clean values. Same in `templates.py:803`. Not a bug — just two passes over the same data. Consider having `_display_payload`/`_render_story_visual` trust the output of `display_for_story` directly, or drop the sanitization inside `display_for_story` and keep it only at the I/O boundaries.

**3. Docs duplicate the OpenDesign sentence awkwardly.** `docs/row-one.md:72-75` emits both "OpenDesign imagery is optional…" and "Open Design imagery is optional…" back-to-back. The plan (line 653) required this to keep the old docs test stable while introducing the new phrasing, so it is intentional — but it reads as a typo to a human. Consider merging into one sentence, or add a one-line code comment in the doc explaining the intentional duplication.

**4. `_story_visual_initials` test coupling.** The render test asserts `"THE ROW" in index_html` from a headline of `'The Row <signals> "quiet" demand'`. The initials helper (`templates.py:825`) takes the first two `[A-Za-z0-9]+` words, so `"The Row <signals>"` → `"THE ROW"`. This is reasonable but tightly coupled to the word-splitting regex; if the headline were `"The Row's signal"` the apostrophe split would still yield `THE ROW` — fine, just worth being aware that the initials contract is implicit.

### What's done well

- **Safety**: `safe_story_image_src` correctly rejects backslashes, control chars (incl. DEL), `..` traversal in both raw and URL-decoded form (`%2e%2e`), absolute paths, and non-`assets/` prefixes. Single shared helper imported by both `render.py` and `templates.py` — no duplicated logic.
- **Backward compatibility**: `display` defaults to `None`; `display_for_story` synthesizes section-based fallback. Existing `RowOneStory(...)` construction without `display` works in render, JSON, and HTML.
- **Browser robustness**: JS wraps both `getItem` and `setItem` in try/catch, defaults to `"en"`, and only persists on user toggle (`persist: false` on initial load avoids overwriting a corrupted/missing key with the default).
- **Contract**: `row-one-app/v1` stays additive; `additionalProperties: false` maintained on `storyDisplay`/`storyImage`; schema rejects unknown variants/accent; display is in `required`.
- **Rendering**: lead/card/detail slots all present; detail page correctly prefixes asset paths with `../`; all visible values escaped via `_esc`; unsafe paths fall back to typographic block, never enter HTML.
- **Scope**: no OpenDesign calls, no image generation, no new collectors, no deploy/schedule/compliance-review additions. CSS moves to the cold editorial palette as specified; old palette colors verified absent.

### Recommendation
Address finding **#1** (schema/sanitizer charset alignment) before this stage is considered release-ready, since it directly affects the `row-one-app/v1` contract guarantee that is central to this stage's objective. The rest are minor and can be addressed at your discretion.
