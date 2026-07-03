Review the Stage 269 ROW ONE display/media readiness implementation.

Repo: /home/ubuntu/fashion-radar
Branch: main

Objective:
- Add a stable `display` object to every ROW ONE story in the app JSON payload.
- Add deterministic story display metadata and shared display/image-source sanitation helpers.
- Render lead/card/detail visual slots with safe images or typographic fallbacks.
- Persist ROW ONE language preference in guarded localStorage.
- Document display/media readiness without calling OpenDesign or generating images.

Relevant design and plan:
- docs/superpowers/specs/2026-07-02-stage-269-row-one-display-readiness-design.md
- docs/superpowers/plans/2026-07-02-stage-269-row-one-display-readiness-plan.md

Changed areas to review:
- src/fashion_radar/row_one/models.py
- src/fashion_radar/row_one/display.py
- src/fashion_radar/row_one/__init__.py
- src/fashion_radar/row_one/edition.py
- src/fashion_radar/row_one/render.py
- src/fashion_radar/row_one/templates.py
- schemas/row-one-app.schema.json
- tests/test_row_one_edition.py
- tests/test_row_one_app_contract.py
- tests/test_row_one_render.py
- tests/test_row_one_docs.py
- docs/row-one.md

Please focus on:
1. Contract correctness: `row-one-app/v1` payloads always include schema-valid display data.
2. Safety: unsafe image URLs/paths cannot enter JSON or HTML; there is one shared source of truth for image source sanitation.
3. Rendering correctness: visual slots render on index, cards, and detail pages with escaped content and stable relative paths.
4. Browser behavior: language preference persistence does not break when localStorage is unavailable.
5. Backward compatibility: existing manual `RowOneStory` construction without `display` still renders and serializes with fallback display metadata.
6. Scope: no OpenDesign calls, no image generation, no new collectors, no deploy/schedule install, no compliance-review product feature.
7. Tests: coverage is meaningful and not overfit to implementation trivia.

Return Critical findings first, then Important, then Minor. If acceptable, say so explicitly.
