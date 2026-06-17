I'll review the Stage 75 design and plan. Let me first read the relevant documents and current state.
Now let me verify the current state of the adapter registry, the existing test file, and the docs that need to be modified.
Let me verify the adapter registry source and the first-run smoke script to validate the matrix and smoke claims.
Now let me check the first-run smoke script to verify the claim that it validates the adapter registry JSON contract across all seven adapters, and check the CLI reference doc and Stage 74 review.
Let me verify the Stage 74 plan review file (to check the correction note accuracy) and the CHANGELOG structure.
# Stage 75 Plan Review

## Verdict

**Approved for implementation.** No Critical or Important findings. The plan is well-scoped, docs/test-only, and faithful to the runtime registry and smoke behavior. A few Minor notes below.

## Critical

None.

## Important

None.

## Minor

**M1. Matrix column "Display/source name" conflates two model fields.**
The registry model (`src/fashion_radar/external_tool_adapters.py:62-63`) has separate `display_name` and `suggested_source_name` fields. They are identical for all seven adapters today, and the smoke validator (`scripts/check_first_run_smoke.py:537-554`) pins both to the same expected value, so the merged column is accurate now. The docs guard will not catch a future divergence between the two fields. Not blocking — the runtime contract already treats them as expected-equal — but worth a one-line footnote under the table stating the two fields are currently identical, or splitting into two columns if they are meant to be independently meaningful.

**M2. Matrix guard pins data rows only, not the header/separator.**
By design (`docs/superpowers/specs/2026-06-18-stage-75-adapter-docs-matrix-design.md:76-78`) only the seven data rows are asserted. This is a reasonable choice (data is the contract; header is cosmetic), but a column rename would pass silently. Acceptable trade-off; noting for awareness.

**M3. "Immediately after the existing first `external-tool-adapters` prose block" is slightly ambiguous in README.**
`README.md` references `external-tool-adapters` in several places (boundary paragraph at `README.md:105-114`, the quickstart command block at `README.md:330-331`, and the per-command paragraph at `README.md:445-456`). Plan Task 2 Step 1 says "first prose block," which points at the `README.md:105-114` boundary paragraph. Recommend the implementer place the matrix immediately after that boundary paragraph (before the `external-tool-template` paragraph at `README.md:116`) to avoid ambiguity. The CLI reference placement (Task 2 Step 2, after the bullet at `docs/cli-reference.md:75-87`) is clear.

**M4. Stage 74 correction note is accurate but appended after the "Recommendation" line.**
Verified `docs/reviews/opencode-stage-74-plan-review.md` is a clean, single coherent document (61 lines, no concatenation), so the Stage 74 code review's M1 finding was indeed resolved before commit and the proposed correction note is factually correct. Appending `### Correction Note` after the final `**Recommendation:**` line is acceptable and non-invasive. A stricter alternative would be to annotate the M1 entry inline (e.g., add `_Resolved before Stage 74 commit; see Correction Note._`), but appending is fine.

**M5. `FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE` constant placement is described loosely.**
Plan Task 1 Step 1 says "Near the external-tool docs constants." The test file has several external-tool constant blocks (`tests/test_cli_docs.py:187-268`). Any reasonable placement works; suggest pinning it adjacent to `EXTERNAL_TOOL_READINESS_*` constants for discoverability.

## Answers To Review Questions

1. **Is the expected adapter matrix correct and aligned with the current registry?** Yes. All seven rows match `src/fashion_radar/external_tool_adapters.py:108-233` exactly: `rednote_mcp`, `xiaohongshu_crawler`, `instaloader`, `tiktok_api`, `yt_dlp`, `x_search_export`, `generic_community_export` with matching platform labels, formats, patterns, and display/source names. The same seven-tuple is independently pinned in `scripts/check_first_run_smoke.py:102-115`.

2. **Are README and CLI reference the right public docs to guard with full-row assertions?** Yes. Both are already treated as authoritative public-surface docs by `tests/test_cli_docs.py` (e.g., `test_external_tool_adapter_registry_docs_are_linked_and_bounded` at `tests/test_cli_docs.py:1022`). Full-row matching is the right granularity: short tokens like `x`, `csv`, `json`, `media` appear elsewhere and would produce false positives as bare substring assertions.

3. **Is the first-run smoke adapter-registry sentence accurate and scoped to the current smoke behavior?** Yes. `scripts/check_first_run_smoke.py:1175-1179` runs `external-tool-adapters --format json` inside the smoke, and `validate_external_tool_adapters` (`scripts/check_first_run_smoke.py:495-642`) iterates every adapter and asserts `contract_version`, `execution_mode`, all adapter ids, `display_name`, `platform_label`, `suggested_source_name`, `recommended_input_format`, `recommended_pattern`, `suggested_export_directory`, and the full `recommended_commands` shape including the `external-tool-readiness` preflight. "Across all seven adapters" is accurate.

4. **Is the Stage 74 code-review resolution note appropriate as a Stage 75 release-trail cleanup?** Yes. The M1 finding described a corrupted plan-review artifact; that artifact is now clean, confirming the fix landed before the Stage 74 commit. A Stage 75 release-trail correction note is the right place to record this so the audit trail is self-consistent without rewriting the historical code review.

5. **Does the plan avoid runtime behavior and external platform behavior changes?** Yes. The File Map touches only `README.md`, `docs/cli-reference.md`, `docs/first-run.md`, `CHANGELOG.md`, `tests/test_cli_docs.py`, the Stage 74 review artifact, and Stage 75 review artifacts. No `src/`, `scripts/`, `pyproject.toml`, or `uv.lock` changes. No connectors, scraping, browser automation, platform APIs, login/cookie/session/token/proxy/CAPTCHA behavior, media download, monitoring/scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review behavior is introduced.

6. **Are there any Critical or Important issues to fix before implementation?** No. Only the Minor notes M1–M5 above; none are blocking.

## Scope-Boundary Check

The change is strictly documentation and docs-test hardening. The staged TDD flow (Task 1 adds failing guards, Task 2 updates docs, Task 3 verifies) is sound, and the verification commands in Task 3 Step 1 cover focused tests, full `tests/test_cli_docs.py`, ruff check/format, release hygiene, `git diff --check`, and full pytest. The full-row normalization strategy (`_normalized_text` collapses whitespace, backtick-bearing expected rows match normalized doc substrings) is correct.

## Note On Review Path

The plan and design both record that this stage uses `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` for stage-local review per explicit user direction, and that this does not alter `docs/REVIEW_PROTOCOL.md`. This is consistent with the user's instruction; no protocol document is modified by this plan.
