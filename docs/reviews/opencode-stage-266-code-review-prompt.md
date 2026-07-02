Review the Stage 266 implementation before commit/push.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-266-row-one-app-discovery-editorial-polish-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-266-row-one-app-discovery-editorial-polish-plan.md
Plan reviews:
- docs/reviews/opencode-stage-266-plan-review.md
- docs/reviews/opencode-stage-266-plan-rereview.md
- docs/reviews/opencode-stage-266-plan-final-rereview.md

Goal:
Add a ROW ONE app discovery manifest, homepage lead story presentation,
deterministic SEO/social metadata, and source-checkout docs for opening the
local ROW ONE site.

Changed implementation areas:
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `schemas/row-one-manifest.schema.json`
- `tests/test_row_one_render.py`
- `tests/test_row_one_app_contract.py`
- `docs/row-one.md`
- `docs/first-run.md`
- `README.md`
- `docs/github-upload-checklist.md`
- `tests/test_row_one_docs.py`
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`

Focused verification already run:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py tests/test_package_archives.py -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py scripts/check_package_archives.py tests/test_package_archives.py`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_docs.py scripts/check_package_archives.py tests/test_package_archives.py`
- `git diff --check`

Review criteria:
- Manifest remains a small discovery contract and does not duplicate edition
  stories/sections.
- `row-one-app/v1` remains backwards compatible.
- Manifest schema is strict and shipped in sdist.
- Generated `data/manifest.json` is runtime output only and not committed.
- Lead story and metadata are presentation-only and do not change
  ranking/scoring/collection/scheduling/server/cleanup.
- Docs give a clear GitHub/source-checkout local ROW ONE path.
- No compliance-review product features, new collectors, LLM calls, image
  generation, deployment, paid APIs, or system service installation were added.
- Tests and release gate direction are adequate for shipping.

Do not edit files. Return concise Critical / Important / Minor findings and a
verdict.
