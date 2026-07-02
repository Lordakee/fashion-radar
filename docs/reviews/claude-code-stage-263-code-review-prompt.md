# Stage 263 Code Review Prompt

You are reviewing the current uncommitted Stage 263 implementation in /home/ubuntu/fashion-radar.

Work read-only. Do not edit files.

Base SHA: 79f0cb4af5475026e0272c04828ef911282856d5
Current SHA: 79f0cb4af5475026e0272c04828ef911282856d5 plus uncommitted working-tree changes.

Stage 263 goal:
- Add a stable app-facing ROW ONE JSON contract at generated data/edition.json.
- Contract version: row-one-app/v1.
- Keep ROW ONE HTML rendering, collection, matching, ranking, cleanup, server, schedule, and social/platform integrations unchanged.

Primary files changed or added:
- src/fashion_radar/row_one/render.py
- schemas/row-one-app.schema.json
- tests/test_row_one_app_contract.py
- tests/test_row_one_render.py
- tests/test_row_one_cli.py
- tests/test_row_one_docs.py
- tests/test_package_archives.py
- scripts/check_package_archives.py
- docs/row-one.md
- docs/architecture.md
- docs/superpowers/specs/2026-07-02-stage-263-row-one-app-contract-design.md
- docs/superpowers/plans/2026-07-02-stage-263-row-one-app-contract-plan.md
- pyproject.toml
- uv.lock

Review focus:
1. App contract correctness: required fields, versioning, dates, section metadata, detail hrefs, evidence hrefs, counts, and sanitized URLs.
2. Schema correctness: strict objects, const version, nullable URL/date handling, format validation expectations, and whether public docs match schema.
3. Regression risk: sparse sections, invalid detail paths, latest-only cleanup behavior, HTML rendering, CLI build output, and package archive checks.
4. Dependency and lockfile hygiene: explicit jsonschema dev dependency and minimal uv.lock change.
5. Tests: whether the focused tests prove the new behavior and existing ROW ONE behavior remains intact.
6. Docs/review hygiene: no stale contract examples or review stubs.

Already verified locally:
- uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py tests/test_row_one_app_contract.py tests/test_package_archives.py tests/test_row_one_docs.py scripts/check_package_archives.py
- uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/render.py tests/test_row_one_app_contract.py tests/test_package_archives.py tests/test_row_one_docs.py scripts/check_package_archives.py
- uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_app_contract.py tests/test_row_one_cli.py::test_row_one_build_command_writes_non_ascii_story_detail_path tests/test_row_one_docs.py tests/test_package_archives.py -q
- UV_NO_CONFIG=1 uv lock --check
- git diff --check

Return findings grouped by Critical, Important, Minor, with file/line references where possible. End with one verdict: Approved, Approved with minor notes, or Needs changes.
