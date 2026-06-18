I'll review Stage 88 systematically. Let me start by reading the design, plan, and review artifacts in parallel.
Now let me read the implementation files and verify scope via git.
Scope confirmed: only 3 test files modified, plus new spec/plan/review artifacts. Let me verify the test assertions against the actual schema and docs, and run the verification commands.
Let me read the "Optional Fields" section of the docs to confirm all 8 asserted terms exist verbatim, then run verification.
All 8 terms verified verbatim in docs (lines 436-441). Now running the broader module tests and ruff.
All verification passes. The implementation matches the plan exactly. Here are my findings.

# Stage 88 Code Review Findings

Reviewing against current `main` state of `src/`, `schemas/`, `tests/`, and `docs/`. All assertions verified against the live codebase; all verification commands re-run green.

## Verdict

**No Critical or Important blockers.** The implementation faithfully executes the Stage 88 plan, stays within the test-only scope, and is technically correct against existing schema/profile/template/docs behavior. Proceed to final verification, commit, and push.

## Verification Re-Run (all green)

- Focused tests: `3 passed in 0.66s` (`tests/test_community_signal_profile.py:48`, `tests/test_external_tool_contract_parity.py:132`, `tests/test_cli_docs.py:1258`).
- Module tests: `77 passed in 0.91s`.
- `ruff check` on the three modified test files: `All checks passed!` (import order `csv, io, json, shlex` is alphabetically correct).

## Scope Confirmation

`git status`: only `tests/test_cli_docs.py`, `tests/test_community_signal_profile.py`, `tests/test_external_tool_contract_parity.py` modified (36 insertions, 1 deletion). New untracked files are the Stage 88 spec/plan/review artifacts. No `src/`, schema, docs-content, lint, import, manifest, `uv.lock`, CI, `AGENTS.md`, or `docs/REVIEW_PROTOCOL.md` changes. Diff is byte-identical to the plan's Task 2/3/4 instructions.

## Findings (ordered by severity)

### Critical / Important
None.

### Minor / Informational (non-blocking, carried over from plan review)

**M1. Subsumed JSON-item assertion.** `tests/test_external_tool_contract_parity.py:148` — the new `assert all("suggested_platform_labels" not in item for item in payload["items"])` is logically subsumed by the existing `assert all(set(item) == profile_fields for item in payload["items"])` on line 147 (since `profile_fields` already excludes the label per `tests/test_community_signal_profile.py:77`). Harmless; adds explicit boundary documentation.

**M2. CSV-header parse duplicates a helper.** `tests/test_external_tool_contract_parity.py:158` inlines `next(csv.reader(io.StringIO(csv_text)))` while `tests/test_community_signal_profile.py:42-45` already has a `_csv_header()` helper. Acceptable for test-local self-containment; no drift risk worth a shared helper for two call sites.

**M3. "Optional Fields" section overshoot.** `_markdown_section_exact_heading(..., "Optional Fields")` at `tests/test_cli_docs.py:1259` also captures the trailing "Do not include raw comments..." paragraph (`docs/community-signal-import.md:445-448`). All 8 asserted terms still match verbatim in lines 436-441, so informational only.

## Answers to Review Questions

1. **Matches plan and scope?** Yes. Diff matches the plan's Task 2/3/4 verbatim. Scope is strictly test-only plus the four Stage 88 review/spec/plan artifacts; nothing from the disallowed list was touched.

2. **Assertions correct for existing behavior?** Yes, all verified:
   - `suggested_platform_labels` is a top-level profile model field (`src/fashion_radar/community_signal_profile.py:77`), distinct from `required_fields`/`optional_fields`/`allowed_fields`/`prohibited_fields` (lines 72-75) → all four `not in` assertions hold.
   - Schema `signal["properties"]` contains exactly 8 fields; `suggested_platform_labels` absent (`schemas/community-signals.schema.json:38-80`) → absence assertion holds.
   - `platform` schema is `{"type": "string", "minLength": 1, ...}` with no `enum`/`const` (`schemas/community-signals.schema.json:64-68`) → type/enum/const assertions hold.
   - All 8 docs phrases exist verbatim in `docs/community-signal-import.md:436-441` → docs test holds.
   - Template JSON `items` keys equal `profile.allowed_fields`; CSV header equals field mappings → both absence assertions hold.

3. **Avoids over-constraining future advisory label additions?** Yes. Stage 88 asserts only *absence* of `suggested_platform_labels` from row/schema/template surfaces and *type/enum/const* shape of `platform`. It does not pin the label list contents, label ordering, or adapter-label equality. The existing membership check `adapter.platform_label in profile.suggested_platform_labels` (`tests/test_external_tool_contract_parity.py:99`) is untouched, so new labels remain free to be added. Docs test pins advisory *phrases*, not exact paragraph wording.

4. **Critical/Important blockers?** **No.** Proceed to final verification, commit, and push.

## Scope-boundary confirmation

The diff introduces none of the prohibited items: no scraping, connectors, browser automation, platform APIs, login/cookie/session/token behavior, media downloads, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, schema enums, new linter restrictions, or compliance-review product features. The `## Boundaries` section of the design doc mirrors this list verbatim, and the implementation honors it.
