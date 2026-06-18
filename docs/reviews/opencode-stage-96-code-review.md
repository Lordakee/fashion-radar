I'll review the Stage 96 implementation. Let me start by reading the relevant files and understanding the review protocol.
Now let me verify the actual `docs/entity-packs.md` content and check the related sibling tests to validate the assertions actually exist in the doc.
All files are new (untracked) — scope is respected. Now let me independently verify the test phrases actually match the normalized doc text and run the verification commands myself.
All 19 phrases match; apostrophe is ASCII. Now let me run the claimed verification commands myself to confirm they pass.
All verification passes. Let me run the remaining checks and confirm the independence claims and `git diff --check`.
All checks pass. Here are my findings.

---

# Stage 96 Code Review — Findings

I independently verified all 19 test phrases against the normalized `docs/entity-packs.md`, ran every claimed verification command, confirmed scope compliance via `git status`, and checked the sibling-test convention.

## Findings by Severity

### Critical
None.

### Important
None.

### Low / Informational (no action required before commit/push)

**L1 — Scope fully respected.** `git status` shows only new untracked files: `tests/test_entity_packs_docs.py` + Stage 96 spec/plan/review artifacts. No changes to `docs/entity-packs.md`, `configs/entity-packs/`, `src/`, schemas, manifests, `uv.lock`, CI, `tests/test_cli_docs.py`, or runtime entity-pack tests.

**L2 — Implementation matches the plan verbatim.** `tests/test_entity_packs_docs.py` is byte-identical to the Task 2 code block in `docs/superpowers/plans/2026-06-18-stage-96-entity-packs-docs-boundary-plan.md:41-91` (including the `from __future__` import, `ROOT`/`ENTITY_PACKS_DOC` constants, `_read_entity_packs_doc`/`_normalized` helpers, and both test functions).

**L3 — All 19 assertions verified present and stable.** I reproduced the `" ".join(text.split()).casefold()` normalization and confirmed every phrase matches. The apostrophe in "Fashion Radar's" (`docs/entity-packs.md:4`) is straight ASCII (`0x27`, verified via `unicodedata`), so `"without changing fashion radar's runtime behavior"` resolves correctly. No smart-quote risk.

**L4 — Standalone test is genuinely independent.** `tests/test_entity_packs_docs.py:1-4` imports only `from __future__ import annotations` and `from pathlib import Path`. It reads one Markdown file and does substring checks — no app-module imports, no YAML parsing, no SQLite, no CLI execution. Runs in 0.01s.

**L5 — Intentional, acceptable overlap with `tests/test_cli_docs.py`.** Existing broader CLI docs tests assert a subset of the same clauses (`tests/test_cli_docs.py:526`, `:1077-1078`, `:1105`). The Stage 96 file is a focused standalone drift guard; the duplication is defensive, not a blocker. Matches the one-file-per-stage convention of Stages 91–94 (`test_data_retention_docs.py`, `test_scheduling_docs.py`, `test_dashboard_docs.py`, `test_source_pack_quality_docs.py`).

**L6 — Normalization style diverges slightly from sibling.** Stage 96 normalizes whitespace/case; `test_data_retention_docs.py` asserts raw text. Both styles already coexist in the repo (`test_cli_docs.py` normalizes heavily), and normalization here is a net strength — resilient to incidental whitespace edits while still catching boundary-clause removal. No change needed.

## Answers to Review Questions

1. **Matches plan and scope?** Yes — test file is verbatim from the plan; scope is test-only + review artifacts.
2. **Assertions present, stable, boundary-scoped?** Yes — all 19 phrases independently verified; all are multi-word boundary clauses specific to entity-pack local matching / optional local sample limits; none are trivially broad.
3. **Independent of CLI docs tests and runtime entity-pack tests?** Yes — only stdlib imports, single-file read, no app/CLI/SQLite/YAML coupling. Both targeted test runs pass: `tests/test_entity_packs_docs.py` (2 passed) and `tests/test_entity_packs.py tests/test_entity_packs_docs.py` (13 passed).
4. **Critical/Important blockers before final verification, commit, push?** **No.** Ruff check/format clean, `git diff --check` clean, focused verification all green.

**Recommendation:** Proceed to full verification, commit, and push (plan Task 4).
