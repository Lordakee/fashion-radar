I'll review the Stage 95 design and plan. Let me start by reading all the relevant files in parallel.
Let me check if the test file already exists and look at related tests, as well as review the review protocol and the review prompt file itself.
The test file doesn't exist yet (to be created). Let me verify the referenced test `test_docs_reference_existing_paths` exists, check the existing test_cli_docs for similar patterns, and look at recent stage work for independence.
Important finding: `test_docs_reference_existing_paths` may not exist. Let me verify and check the existing stage 91-94 patterns plus the existing stage-95 review artifacts.
Confirmed a critical issue. Let me do final verification on stage 91-94 independence and existing Source Boundary guards.
# Stage 95 Plan Review Findings

## Critical

**C1 — Verification command references a non-existent test.**
`tests/test_cli_docs.py::test_docs_reference_existing_paths` does not exist anywhere in the repo (confirmed via repo-wide grep; the 59 tests in `tests/test_cli_docs.py` do not include it, and Stage 95's scope forbids editing `test_cli_docs.py`, so it will never be added by this stage). The broken command appears in both the design spec (`docs/superpowers/specs/2026-06-18-stage-95-architecture-source-boundary-docs-design.md:49`) and the plan (`docs/superpowers/plans/2026-06-18-stage-95-architecture-source-boundary-docs-plan.md:85`):

```
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_docs_reference_existing_paths tests/test_architecture_boundary_docs.py -q
```

Running it fails at collection (`ERROR: not found: ...test_cli_docs.py::test_docs_reference_existing_paths`), which breaks Task 3 verification. Fix before implementation: drop the `test_docs_reference_existing_paths` node (run only `tests/test_architecture_boundary_docs.py -q`), or replace it with a real existing test.

## Important

**I1 — `_markdown_section` helper is fragile and diverges from repo convention.**
The plan's helper (`plan.md:54-57`) builds `marker = f"## {heading}"` without newline anchoring. The string `"## Source Boundary"` is a substring of `"### Source Boundary"`, so a future `### Source Boundary` subsection appearing earlier in the file would make `split(marker, 1)` target the wrong location and silently assert-pass. The established helper in `tests/test_cli_docs.py:389-392` anchors with `marker = f"\n{heading}\n"` and asserts against `f"\n{text}"`, which is immune to this. Recommend matching the existing convention. Not a current break (no `### Source Boundary` exists today), but it undermines the drift-guard's reliability.

## Minor

**M1 — Phrase 5 stops short of the release anchor.** `"non-core platform collection is not part"` (`plan.md:73`) omits `"of v0.1.0"`. Extending to `"non-core platform collection is not part of v0.1.0"` more fully pins the release-scope claim; `v0.1.0` survives normalization unchanged.

**M2 — `docs/reviews/opencode-stage-95-plan-review.md` already exists with stale partial content** (leftover thinking text from a prior run). Task 1 overwrites it, so not a blocker — flagging so it is not mistaken for a real prior review.

## Review Question Answers

1. **Docs assertions present?** Yes. All six proposed phrases exist in the current `## Source Boundary` section (`docs/architecture.md:401-406`). Verified against normalized text: phrases 1-6 all match.
2. **Phrases stable / not overly broad?** Mostly yes. Phrases 1, 2, 4 are well-anchored full clauses. Phrases 3 (`"user-provided csv/json files"`) and 6 (`"source-boundaries.md"`) are short but are scoped within the extracted section, so false-positive risk is low. Phrase 5 is fine but could be tighter (M1).
3. **Scope test-only and independent of 91-94?** Yes. Stage 95 creates a new `tests/test_architecture_boundary_docs.py` targeting a distinct section. Stages 91-94 produced `test_data_retention_docs.py`, `test_source_pack_quality_docs.py`, `test_scheduling_docs.py`, `test_dashboard_docs.py`; no file or section overlap. No existing test guards `## Source Boundary`, so the stage is non-redundant. Plan does not touch any disallowed file.
4. **Verification commands sufficient?** No — broken by C1. Commands 1, 3, 4 (focused pytest, ruff check, ruff format) are sufficient; command 2 must be fixed.
5. **Critical/Important blockers?** Yes: C1 and I1 above. Fix C1 before implementation; address I1 (and optionally M1) for a robust, convention-aligned guard.

Note on review tooling: `AGENTS.md` / `docs/REVIEW_PROTOCOL.md` specify plan reviews via local Claude Code (`claude --effort max --permission-mode plan ...`). The plan's Task 1 instead invokes `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`. That matches this review's requested model, but it diverges from the documented protocol command form — worth confirming that substitution is intended.
