# Stage 81 Code Review

## Verdict

No Critical or Important findings remain after replacing the live-capture stub
with this completed review artifact. The Stage 81 implementation tightens the
Stage 80 docs drift tests without changing runtime code, public docs prose,
dependency manifests, or `uv.lock`.

## Findings

### Critical

None.

### Important

None.

### Minor

- `_markdown_section_exact_heading` duplicates the same same-or-higher-level
  heading boundary logic used by `_markdown_section_matching_heading`. This is
  acceptable here because the new helper intentionally differs by using
  `re.escape`, exact heading text, and a line-end anchor.
- The community import roadmap test still checks its boundary phrases against
  the full document. Stage 81 intentionally leaves it unchanged because the
  roadmap's phase/command assertions are already scoped and the roadmap text
  itself contains the boundary sentence.

## Review Notes

- `_markdown_section_exact_heading` is heading-aware: it captures the Markdown
  heading marker, derives the heading level, and stops at the next heading of
  the same or higher level.
- The README test now asserts route terms and boundary phrases inside the
  `### External Tool Import Path` section.
- The CLI reference test now extracts `## Local Import And Community Handoff`
  with the heading-aware helper and checks boundary phrases against that
  normalized section text.
- The implementation does not split README on `external-tool-readiness`, which
  appears inside the target route before the boundary sentence.
- No `src/`, README/CLI/community/changelog prose, dependency manifest,
  `uv.lock`, `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, or
  `docs/github-upload-checklist.md` changes are part of this node.

## Verification Observed

- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_external_tool_import_path_points_to_local_handoff_route tests/test_cli_docs.py::test_cli_reference_local_import_section_has_external_tool_route -q`
- `uv --no-config run --frozen pytest tests/test_cli_docs.py -q`
- `uv --no-config run --frozen ruff check tests/test_cli_docs.py`
- `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py`
- `git diff --check` over the changed Stage 81 files
- `uv --no-config run --frozen python scripts/check_release_hygiene.py`
