I'll review the Stage 118 implementation. Let me start by understanding what changed and reading the relevant files.
Let me read the working-tree diffs for the scoped files and the stage artifacts in parallel.
Now let me read the review artifacts and the test helper context to verify conventions.
Let me verify the test helpers exist, the section headings exist in each doc, and run the actual test.
Let me read the helper implementations and verify the actual section contents in each doc.
Let me verify the README and checklist sections, then run the focused test and full CLI docs suite.
All helpers and section headings verified. Now let me run the new test and the full CLI docs suite using the no-config frozen pattern the stage documents.
All 61 tests pass. Let me do final scope verification — confirm only the intended files changed and lint is clean.
## Review: Stage 118 — Agent UV Run Hygiene

### Verification results

| Check | Result |
|---|---|
| New test passes | ✓ (`test_agent_verification_docs_prefer_no_config_frozen_uv_run`) |
| Full `tests/test_cli_docs.py` | ✓ 61 passed |
| Ruff check + format on test file | ✓ clean |
| Scope (only 5 scoped files + 8 artifacts) | ✓ no `src/`, `pyproject.toml`, `uv.lock`, `.github/` changes |
| Helpers/constants exist & used correctly | ✓ `AGENTS_DOC` (test_cli_docs.py:27), `_read` (:310), `_normalized_text` (:318), `_markdown_section_exact_heading` (:410) |
| Section headings exist & boundaries correct | ✓ all four `##` headings present; helper stops at next same-or-higher heading |

**Point 1 — separation of concerns:** All four sections now cleanly distinguish the three paths: mirror-backed local install (`UV_DEFAULT_INDEX=... uv sync --frozen --dev`), agent-run verification (`uv --no-config run --frozen ...`), and public lockfile validation (`UV_NO_CONFIG=1 uv lock --check`). Each new bullet explicitly states mirror-backed commands stay as "frozen mirror install commands, not test or lockfile regeneration commands."

**Point 2 — required phrases in all four sections:** Verified both by the passing section-scoped test and manual inspection of each `_markdown_section_exact_heading` slice. All five (`uv --no-config run --frozen`, `agent-run verification`, `mirror-backed`, `uv.lock`, `frozen mirror install`) present; line-wrapped variants normalize correctly via `_normalized_text`.

**Point 3 — test conventions:** Section-scoped (extracts each section, then loops), reuses existing constants/helpers, placed cohesively after `test_dependency_mirror_docs_explain_lockfile_recovery`.

**Point 4 — scope purity:** `git diff` for `uv.lock`, `pyproject.toml`, `src/*`, `.github/*` is empty. No runtime/dependency/connector/scraping/scheduling/monitoring/source-acquisition/ranking/coverage/compliance changes.

### Critical findings
None.

### Important findings
None.

### Minor findings
- **M-1** (low-signal assertion): The `"uv.lock"` token pre-exists in 3 of the 4 scoped sections (AGENTS `Dependencies And Mirrors`, `Project Practice`, `Before Upload`), so that one assertion would pass even without the new bullet. The other four phrases are distinctive and section-binding, so the drift guard still serves its purpose; consistent with the stage's visibility intent. Non-blocking.
- **M-2** (plan-doc prose, carried from rereview): The plan still says "Keep the existing frozen mirror install bullets" for `## Project Practice`, but that section had no such bullets (the phrase lives in `## Recover A Mirror-Rewritten Lockfile`). Implementation is unaffected; the plan text is just imprecise.
- **M-3** (out of scope, carried): `AGENTS.md` Review Gates still mandate Claude Code `--effort max` while stages use opencode `glm-5.2 --variant max`. Not a Stage 118 matter.

### Final statement

**Stage 118 is ready to ship.** The docs cleanly separate mirror-backed frozen local installs from no-config frozen agent-run verification, all four scoped sections contain the required phrases (section-scoped and verified), the new test follows existing path/helper conventions, and scope is strictly docs/tests-only with no `uv.lock`/`pyproject.toml`/runtime/CI/connector/scraping/compliance changes. No Critical or Important blockers. The implementer should still run the full release gate (full `pytest`, `ruff`, `UV_NO_CONFIG=1 uv lock --check`, marker scan, `git diff --exit-code -- uv.lock pyproject.toml`) per plan Task 4 before push — that is procedural, not a defect in this stage's changes.
