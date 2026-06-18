Review Stage 80 of Fashion Radar.

Context:
- Goal: clarify the local route from a user-controlled external export
  directory into Fashion Radar's existing sanitized CSV/JSON local handoff,
  validation, import, and review commands.
- Scope: docs and docs drift tests only.
- Current stage-local review tool: opencode with
  zhipuai-coding-plan/glm-5.2 max.

Expected files:
- README.md
- docs/community-signal-import.md
- docs/cli-reference.md
- tests/test_cli_docs.py
- CHANGELOG.md
- Stage 80 plan/spec/review artifacts under docs/superpowers and docs/reviews

Out of scope:
- src/
- dependency manifests
- uv.lock
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/github-upload-checklist.md
- any runtime connector, scraper, platform API, scheduling, or compliance-review
  product feature

Required behavior:
- The docs must explain that Fashion Radar can consume user-controlled external
  export directories only through sanitized CSV/JSON local file handoff.
- The route must use existing commands only:
  external-tool-adapters -> external-tool-readiness -> external-tool-workflow ->
  community-signal-lint-dir -> community-candidates-dir ->
  community-handoff-check-dir -> import-signals-dir -> imported-review-workflow.
- Boundary language must stay explicit: this does not run upstream tools, does
  not search platforms, does not scrape, does not call platform APIs, does not
  add connectors, does not prove demand, does not rank brands, and does not
  verify platform coverage.

Checks already run:
- uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_external_tool_import_path_points_to_local_handoff_route tests/test_cli_docs.py::test_community_signal_import_docs_have_external_tool_import_roadmap tests/test_cli_docs.py::test_cli_reference_local_import_section_has_external_tool_route -q
- uv --no-config run --frozen pytest tests/test_cli_docs.py -q
- uv --no-config run --frozen ruff check tests/test_cli_docs.py
- uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
- git diff --check -- README.md docs/community-signal-import.md docs/cli-reference.md CHANGELOG.md tests/test_cli_docs.py

Please review the staged-equivalent working tree changes, not uv.lock. Report
findings by severity:
- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional cleanup.

Focus on spec compliance, docs drift test quality, misleading capability
wording, Markdown section split hazards, and accidental scope expansion.
