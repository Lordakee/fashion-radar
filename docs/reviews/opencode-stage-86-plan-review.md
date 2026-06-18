I'll review the Stage 86 plan. Let me read all the relevant files first.
Let me find the referenced test and check the existing test patterns for the adapter registry.
I have everything needed to complete the review. Let me verify the section helpers behave as the plan assumes by checking the exact section boundaries.
I now have a complete picture. Stage 85 already established the canonical advisory sentence in `docs/community-signal-import.md:288` and `docs/community-signal-quality.md:20` using the phrasing "`suggested_platform_labels` is advisory local provenance label guidance...", and the existing test at `tests/test_cli_docs.py:1245-1255` locks that phrasing into those two docs. Stage 86 extends the same advisory semantics to the README and CLI reference adapter tables.

---

# Stage 86 Plan Review Findings

## Severity-Ordered Findings

### Critical
None.

### Important
None.

### Minor / Info (optional, non-blocking)

**M1 — Phrasing diverges from the Stage 85 canonical sentence.**
The established advisory sentence (locked by `tests/test_cli_docs.py:1247`) is:

> "`suggested_platform_labels` is **advisory local provenance label guidance** for the optional handoff `platform` field."

The Stage 86 plan (`docs/superpowers/plans/2026-06-18-stage-86-adapter-platform-label-docs-plan.md:95-99`, `115-119`) introduces a new formulation:

> "The Platform label column reflects **advisory `suggested_platform_labels` guidance** for the optional handoff `platform` field."

Both are accurate and advisory, and the Stage 86 test only requires `"advisory"` + `"suggested_platform_labels"` separately, so it will pass. But harmonizing with the Stage 85 wording (e.g., "advisory local provenance label guidance for the optional handoff `platform` field") would reduce drift across docs. This is stylistic; the "The Platform label column reflects..." table-specific framing is appropriate for the adapter-table context.

**M2 — Boundary-term parity with Stage 85 boundary docs is partial.**
Stage 85 boundary docs (`AGENTS.md`, `community-signal-import.md`, `community-signal-quality.md`) frame the labels with the exact negation set. The proposed prose covers "not a schema enum / not a linter restriction / not platform coverage / not demand proof", which matches. No gap — noting only that the existing `test_external_tool_adapter_registry_docs_are_linked_and_bounded` (`tests/test_cli_docs.py:1461`) already enforces the broader adapter boundary vocabulary across the full README/CLI docs, so the new prose does not weaken anything.

---

## Review Question Answers

**1. Does the plan clarify `Platform label` semantics without implying platform support, coverage, schema validation, or demand proof?**
Yes. The prose (`plan.md:94-99` and `114-119`) explicitly states the labels are "not a schema enum, not a linter restriction, not platform coverage, and not demand proof" and frames them as "advisory ... guidance for the optional handoff `platform` field". The accuracy is backed by `tests/test_external_tool_contract_parity.py:97` (`adapter.platform_label in profile.suggested_platform_labels`), confirming the table column values are members of the advisory list. No platform-support/coverage/validation/demand-proof implication.

**2. Are the README and CLI reference insertion points correct?**
Yes.
- README (`README.md:146-147`): new paragraph added immediately after the existing "Display/source name column reflects..." paragraph, inside `## What It Does Not Do` (lines 85–217) and after the `Known adapter ids:` table (lines 134–144). Confirmed within the `_markdown_section(text, "## What It Does Not Do")` window — the next `\n## ` is `## Quickstart` at line 218; the nested `### External Tool Import Path` (H3) does not terminate the section because `_markdown_section` splits on `\n## ` (exactly two hashes + space), not `\n### `.
- CLI reference (`docs/cli-reference.md:127-128`): new indented paragraph added after the existing 2-space-indented "Display/source name column..." paragraph, staying under the `- external-tool-adapters:` bullet and before the `- external-tool-template:` bullet at line 129. Within the `## Local Import And Community Handoff` section (lines 80–238).

**3. Is the proposed docs drift test scoped tightly enough to the adapter table sections?**
Yes. The test (`plan.md:46-70`) uses `_markdown_section` to isolate exactly two sections: README `## What It Does Not Do` and CLI reference `## Local Import And Community Handoff`. It will not produce false failures from `community-signal-import.md`, `community-signal-quality.md`, or other sections. The required-term list (`plan.md:59-69`) matches the proposed prose verbatim (verified term-by-term against normalized+casefolded text, including the backtick-bearing term `"optional handoff \`platform\` field"` which `_normalized_text` preserves). The pre-existing `test_community_signal_profile_docs_are_linked` (`tests/test_cli_docs.py:1231-1255`) remains scoped to the import/quality docs, so there is no overlap or conflict. TDD red state is genuine: neither section currently contains `"platform label column"`, `"suggested_platform_labels"`, `"advisory"`, `"not a schema enum"`, etc.

**4. Are the verification commands sufficient?**
Yes. Task 2 verifies the targeted red test fails; Task 5 runs the new test plus the full `tests/test_cli_docs.py`; Task 6 runs the complete release-hygiene suite (`pytest`, `ruff check`, `ruff format --check`, `UV_NO_CONFIG=1 uv lock --check`, mirror-URL scan on `uv.lock`, `git diff --exit-code -- uv.lock pyproject.toml`, `git diff --check`, staged-hygiene `check_release_hygiene.py`, staged secret scan). This matches the AGENTS.md lockfile-hygiene conventions (`UV_NO_CONFIG=1` for public lockfile checks).

**5. Are there any Critical or Important blockers before implementation?**
No. There are no Critical or Important blockers. The two Minor notes above are optional consistency refinements. The plan is docs/test-only, touches only the allowed files (`README.md`, `docs/cli-reference.md`, `tests/test_cli_docs.py`, review artifacts), leaves `src/`, schemas, lint/import behavior, adapter/template/workflow/readiness behavior, dependency manifests, `uv.lock`, CI workflows, `AGENTS.md`, and `docs/REVIEW_PROTOCOL.md` untouched, and introduces no scraping/connectors/platform-APIs/login-cookie/media/monitoring/scheduling/source-acquisition/demand-proof/ranking/coverage/schema-enum/linter/compliance-review behavior.

**Recommendation:** Proceed to implementation. Optionally adopt the canonical Stage 85 phrase "advisory local provenance label guidance" in place of "advisory `suggested_platform_labels` guidance" for cross-doc consistency (this would require also updating the test's required-term tuple at `plan.md:59-69` accordingly).
