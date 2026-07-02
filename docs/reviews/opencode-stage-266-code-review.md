## Stage 266 Code Review — ROW ONE App Discovery & Editorial Polish

I independently re-ran the focused suite (137 passed) and a real `uv build`, which confirms `schemas/row-one-manifest.schema.json` ships in the sdist and `.gitignore` covers the generated `reports/row-one/site/data/manifest.json`.

### Critical
None.

### Important
- **I1 — Full release gate not yet confirmed for the touched surface.** Focused verification covered the four targeted test files, ruff, format, and `git diff --check`, but the changed docs/README/first-run paths are also exercised by `scripts/check_first_run_smoke.py` and `scripts/check_release_hygiene.py`, and sdist inclusion is only proven by `uv build` + `check_package_archives.py dist` (I verified the schema is included, but run it in the gate). Run the design's full release gate (build, archive check on real `dist/`, first-run smoke, release hygiene) before `git push`.

### Minor
- **m1 — Lead story is rendered twice.** The lead block and the `top_stories` grid both show the same top story. This is the explicit, lower-risk choice from the design/plan (rereview m3) and is fine, but flagging for editorial awareness.
- **m2 — `_meta_description` truncation branch is untested.** The `>180` char ellipsis path is never hit by fixtures (no fixture summary is that long). Simple function, but a coverage gap.
- **m3 — No `og:image` / `og:url`.** Metadata is text-only/deterministic by design (image generation is a non-goal); acceptable, just noting social cards will be text-only.
- **m4 — Cosmetic blank lines in `<head>`.** The meta tags are injected via a standalone `{ _render_meta_tags(...) }` f-string block, so the rendered HTML head has extra newlines around the meta cluster. Functionally harmless; substring assertions pass.

### Verified correct (no blockers)
- Manifest is a small, strict discovery contract: `additionalProperties:false`, `const` paths/versions, `enum` readiness, and contains **no** story/section arrays, absolute URLs, host/port, LAN URLs, or machine paths. Counts/paths/timestamps are reused from the already-built `app_payload` (no double build, no drift).
- `row-one-app/v1` (`data/edition.json` + `schemas/row-one-app.schema.json`) is **unchanged** — backwards compatible; manifest is additive only.
- Schema ships in sdist (hatchling default includes the git-tracked `schemas/` file; verified via real build). Runtime `data/manifest.json` is git-ignored and not committed.
- Lead story + SEO/social metadata are presentation-only in `templates.py`; no change to scoring/ranking/matching/collection/scheduling/server/cleanup/SQLite. Cleanup `GENERATED_CHILDREN` already covers `data/`.
- Docs give a clear source-checkout ROW ONE path (README bullet + `docs/row-one.md` manifest section + `docs/first-run.md` build/preview/serve block using the existing `uv run` convention + upload-checklist boundary note).
- No compliance-review feature, collector, LLM call, image generation, paid API, deployment, or system service added. Scope boundaries respected.

### Verdict
**Approved — proceed to commit/push**, contingent on running the full release gate called out in I1 (build + `check_package_archives.py dist` + `check_first_run_smoke.py` + `check_release_hygiene.py`) before pushing.
