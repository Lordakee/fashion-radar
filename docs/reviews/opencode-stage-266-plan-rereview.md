## Stage 266 Plan Re-Review

### Previously-reported blockers — status

- **C1 (render tests vs. `test_row_one_render.py` fixture + escaped HTML): FIXED.** Task 3 assertions now match the actual `_edition()` fixture: headline escapes to `The Row &lt;signals&gt; &quot;quiet&quot; demand` (matches existing assertion at `tests/test_row_one_render.py:144`), takeaway to `The Row is today&#x27;s priority signal.` (`:145`), detail summary to `Original source summary: The Row signal with &lt;angle&gt; detail.`, and index description to `ROW ONE organized 1 local fashion signal for today.`. Index/detail meta title prefixes and the full twitter:title all resolve against `_esc` output.
- **I1 (timestamp regex): FIXED.** Plan line 340 now reads `"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"`, identical to `schemas/row-one-app.schema.json:29`; JSON-parses to a regex that matches `2026-07-02T04:00:00Z`.
- **I2 (`app_contract.path` drift match): FIXED.** Plan line 148 now uses `"was expected"` for the `const` mutation, consistent with the existing app-contract drift test (`tests/test_row_one_app_contract.py:209`).
- **M1 (avoid recomputing app payload): FIXED.** `build_row_one_manifest_payload(edition, app_payload=None)` reuses the payload already built at `render.py:44`; the render passes it in (plan lines 240).
- **M2 (concrete README step): FIXED.** Task 4 Step 5 now pins the exact bullet `- [ROW ONE local static site](docs/row-one.md)`.

### Critical
None.

### Important
- **I3-recur — Docs test still fails on case sensitivity (plan line 651).** The assertion is:
  ```python
  assert "do not upload generated ROW ONE site artifacts" in checklist.lower()
  ```
  Only the haystack is lowercased. `checklist.lower()` turns the dictated wording "Do not upload generated ROW ONE site artifacts." (`docs/github-upload-checklist.md`) into `"...generated row one site artifacts."`, while the needle keeps uppercase `ROW ONE`. Python's `in` is case-sensitive, so this is `False`. Every other mixed-case assertion in this test correctly does `needle.lower() in haystack.lower()` (lines 643, 645–647); line 651 is the lone exception. `test_row_one_docs_describe_manifest_and_editorial_polish` will therefore pass Step 2 (red, as expected) but **fail Step 6 (Expected: PASS)** even after the docs are written correctly. Fix: `assert "do not upload generated ROW ONE site artifacts".lower() in checklist.lower()` (or write the needle all-lowercase).

### Minor
- **m1** — `_meta_description`'s 180-char truncation path (and its `"…"` ellipsis) is never exercised; all fixture strings are short. Not a blocker, just untested behavior.
- **m2** — Lead story is intentionally also kept in the section grid (design acknowledges); top story now appears twice on the homepage. Acceptable for v1, noting for completeness.

### Verified correct (no blockers)
- Scope remains sidecar manifest + presentation/docs only. `row-one-app/v1` (`data/edition.json` + `schemas/row-one-app.schema.json`) untouched; no change to collection/matching/scoring/ranking/scheduling/server/cleanup/app-payload. `GENERATED_CHILDREN` already covers `data/`, so `data/manifest.json` is cleaned by `--latest-only`.
- Manifest schema is strict (`additionalProperties: false`, `const` paths/versions, `enum` readiness) and its drift matrix (contract_version/extra/generated_at/path/readiness.status/capabilities) all map to the right jsonschema messages.
- `schemas/row-one-manifest.schema.json` ships in the sdist automatically via hatchling VCS defaults (`pyproject.toml` only excludes `docs/reviews` and `docs/superpowers`); the explicit `SDIST_REQUIRED_PATHS`/`SDIST_FILES` additions make it enforceable. No `pyproject.toml` change required, and `test_package_metadata` is unaffected.
- All helper names referenced by the plan exist in `templates.py` (`_esc`, `_section_title`, `_render_story_orientation`, `_internal_detail_href`) and `section_stories` is used elsewhere; meta insertion points (`<head>` after viewport) are valid in both index and detail templates.

### Verdict
**Revise before implementation (one small fix).** C1, I1, I2, M1, and M2 are resolved and scope/boundaries are sound, but the docs test at plan line 651 still cannot pass as written due to the `ROW ONE` case mismatch. Lowercase the needle (one-character change) and the plan is executable end-to-end to a green suite.
