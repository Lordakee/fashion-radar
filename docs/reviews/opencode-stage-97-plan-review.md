I'll review the Stage 97 design and plan. Let me read the relevant files first.
Let me verify a few additional things — check if the test file already exists, look at similar docs test patterns, and confirm the plan's scope.
Let me read the most analogous existing test files to verify conventions match.
Let me verify all 19 phrases actually match the normalized doc by running a quick check.
## Stage 97 Plan Review Findings

No Critical or Important blockers. Findings ordered by severity below.

### Critical
None.

### Important
None.

### Low / Non-blocking
1. **Short-phrase fragility** — `plan.md:67,86` (`"platform search"`) and `plan.md:69` (`"fetch pages"`) are 2-word assertions. They are distinctive within this doc's context and consistent with the granularity in `tests/test_source_pack_quality_docs.py:23-24` (`"open sqlite"`, `"collect source items"`), so the drift sensitivity is acceptable and intentional. No change required.
2. **Test naming** — `plan.md:58,75` use `_keep_local_read_only_boundary` / `_keep_non_claim_boundary`. These mirror the Stage 96 precedent (`tests/test_source_pack_quality_docs.py:17,32,42`) and are clear enough.

### Answers to review questions

1. **Are the proposed docs assertions present in current `docs/entity-pack-quality.md`?** Yes. All 19 phrases verified against the whitespace-collapsed, casefolded doc:
   - Test 1 phrases live in `docs/entity-pack-quality.md:3-12` (intro paragraph + boundaries paragraph).
   - Test 2 phrases live in `docs/entity-pack-quality.md:10-12` and `docs/entity-pack-quality.md:239-247` (Limits section).
   - Programmatic check returned `ALL 19 PHRASES PRESENT`.

2. **Are the phrases stable enough and not overly broad?** Yes. 17 of 19 are distinctive multi-word clauses; the two short ones (`"platform search"`, `"fetch pages"`) are scoped to a sentence whose drift the guard is meant to catch. No substring is broad enough to false-pass against unrelated text.

3. **Is the scope safely test-only and independent from Stages 91 through 96?** Yes. The only allowed source change is a new `tests/test_entity_pack_quality_docs.py` plus review artifacts. `spec.md:16-24` and `plan.md:22-24` explicitly exclude `docs/entity-pack-quality.md`, `src/`, schemas, deps/`uv.lock`, CI, `tests/test_cli_docs.py`, and runtime lint tests. The new file is standalone — it imports only `pathlib`, reads one Markdown file, and shares no state with prior stages. Module layout matches the Stage 96 precedent exactly (`tests/test_source_pack_quality_docs.py:1-15`).

4. **Are the verification commands sufficient?** Yes. `plan.md:97-103` runs the new test alone, the new test alongside `tests/test_entity_pack_lint.py` (proves non-interference), `ruff check`, `ruff format --check`, and `git diff --check`. `plan.md:118-127` adds release hygiene, full pytest with proxy unset, repo-wide ruff, `UV_NO_CONFIG=1 uv lock --check`, the mirror-URL scan, `git diff --exit-code -- uv.lock pyproject.toml`, staged hygiene, and a secret scan. Coverage is complete for a docs-only guard.

5. **Are there any Critical or Important blockers before implementation?** No Critical or Important blockers. Safe to proceed with implementation.
