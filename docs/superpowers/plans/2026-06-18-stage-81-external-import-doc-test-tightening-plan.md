# Stage 81 External Import Doc Test Tightening Plan

> **For agentic workers:** keep this node tests/artifacts-only unless a scoped
> assertion exposes an existing documentation mismatch. Use local opencode for
> plan and code review with `opencode run --model
> zhipuai-coding-plan/glm-5.2 --variant max`.

## Goal

Tighten Stage 80 docs drift tests so boundary language must remain inside the
new README external import section and the CLI local import guidance.

## File Map

- Modify `tests/test_cli_docs.py`.
- Add Stage 81 review artifacts under `docs/reviews/`.
- Add this plan and the matching design spec under `docs/superpowers/`.
- Do not modify `src/`, dependency manifests, `uv.lock`, `AGENTS.md`,
  `docs/REVIEW_PROTOCOL.md`, or `docs/github-upload-checklist.md`.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-81-plan-review-prompt.md`.
- [ ] Run local opencode plan review.
- [ ] Fix Critical or Important findings before implementation.

## Task 2: Tighten Docs Tests

- [ ] Add an exact-heading Markdown section helper modeled on
  `_markdown_section_matching_heading` so known headings can be matched without
  inline-heading split hazards.
- [ ] In `test_readme_external_tool_import_path_points_to_local_handoff_route`,
  use the exact-heading helper to extract the heading-inclusive
  `### External Tool Import Path` section and assert both route anchors and
  boundary phrases inside that section. Do not split on
  `external-tool-readiness`, because the route itself contains that command.
- [ ] In `test_cli_reference_local_import_section_has_external_tool_route`,
  assert the boundary phrases against `normalized_section`, not whole-document
  `normalized`.
- [ ] Avoid inline literal `## ...` strings in docs. This node should not need
  docs edits.

## Task 3: Focused Verification

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_readme_external_tool_import_path_points_to_local_handoff_route \
  tests/test_cli_docs.py::test_cli_reference_local_import_section_has_external_tool_route \
  -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check -- tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-18-stage-81-external-import-doc-test-tightening-design.md \
  docs/superpowers/plans/2026-06-18-stage-81-external-import-doc-test-tightening-plan.md \
  docs/reviews/opencode-stage-81-plan-review-prompt.md \
  docs/reviews/opencode-stage-81-plan-review.md
```

## Task 4: Code Review And Full Verification

- [ ] Create `docs/reviews/opencode-stage-81-code-review-prompt.md`.
- [ ] Run local opencode code review.
- [ ] Fix Critical or Important findings.
- [ ] Run full verification:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
```

For `UV_NO_CONFIG=1 uv lock --check`, temporarily restore `HEAD:uv.lock`, run
the check and public mirror scan, then restore the local mirror `uv.lock` and
keep it unstaged.

## Task 5: Commit And Publish

- [ ] Stage only these Stage 81 files:

```bash
git add -- \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-18-stage-81-external-import-doc-test-tightening-design.md \
  docs/superpowers/plans/2026-06-18-stage-81-external-import-doc-test-tightening-plan.md \
  docs/reviews/opencode-stage-81-plan-review-prompt.md \
  docs/reviews/opencode-stage-81-plan-review.md \
  docs/reviews/opencode-stage-81-code-review-prompt.md \
  docs/reviews/opencode-stage-81-code-review.md
```

- [ ] Confirm `uv.lock` is not staged.
- [ ] Run staged release hygiene and high-confidence secret scan.
- [ ] Commit with message `Tighten external import docs tests`.
- [ ] Push safely without persisting the token in remote URLs or git config.
- [ ] Verify local/remote `main` alignment and GitHub Actions success.
