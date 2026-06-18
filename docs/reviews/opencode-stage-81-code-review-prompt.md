Review Stage 81 of Fashion Radar.

Goal:
- Tighten Stage 80 docs drift tests so external import boundary phrases are
  asserted inside the actual README and CLI reference guidance, not only
  somewhere in the full document.

Expected changed files:
- tests/test_cli_docs.py
- docs/superpowers/specs/2026-06-18-stage-81-external-import-doc-test-tightening-design.md
- docs/superpowers/plans/2026-06-18-stage-81-external-import-doc-test-tightening-plan.md
- docs/reviews/opencode-stage-81-plan-review-prompt.md
- docs/reviews/opencode-stage-81-plan-review.md
- docs/reviews/opencode-stage-81-code-review-prompt.md
- docs/reviews/opencode-stage-81-code-review.md

Out of scope:
- src/
- README.md, docs/cli-reference.md, docs/community-signal-import.md, and
  CHANGELOG.md prose
- dependency manifests
- uv.lock
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/github-upload-checklist.md
- any runtime connector, scraper, platform API, ranking, demand proof, or
  compliance-review product feature

Review focus:
- `_markdown_section_exact_heading` should be heading-aware and stop at the
  next heading of the same or higher level.
- README assertions should operate on the `### External Tool Import Path`
  section, not the full README.
- CLI reference boundary assertions should operate on the local import section
  text, not the full CLI reference.
- The implementation should not split README on `external-tool-readiness`,
  because that command appears inside the target route.
- Verification commands should cover focused tests, all docs tests, ruff, and
  whitespace checks.

Checks already run:
- uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_external_tool_import_path_points_to_local_handoff_route tests/test_cli_docs.py::test_cli_reference_local_import_section_has_external_tool_route -q
- uv --no-config run --frozen pytest tests/test_cli_docs.py -q
- uv --no-config run --frozen ruff check tests/test_cli_docs.py
- uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
- git diff --check -- tests/test_cli_docs.py docs/superpowers/specs/2026-06-18-stage-81-external-import-doc-test-tightening-design.md docs/superpowers/plans/2026-06-18-stage-81-external-import-doc-test-tightening-plan.md docs/reviews/opencode-stage-81-plan-review-prompt.md docs/reviews/opencode-stage-81-plan-review.md

Report findings by severity:
- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional cleanup.
