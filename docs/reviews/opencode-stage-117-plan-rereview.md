I'll review the updated Stage 117 plan. Let me read all the relevant files in parallel.
Now let me read the current docs and test targets to verify the plan against actual file content.
Let me read the rest of the test file to understand the existing test structure the new test extends.
Let me verify the anchor heading exists in community-signal-import.md and that referenced paths/sections are valid.
I've completed a thorough trace of every test assertion in Task 1 against the actual scoped sections of each doc (using the `between()` markers) combined with the proposed pointer texts in Task 2. Here is my review.

---

# Stage 117 Updated Plan Rereview

## Verification Of Prior Important Findings (I1–I5)

I traced each loop assertion in the new test (`plan.md:116-126`) against the **current** scoped section content of each doc **plus** the proposed pointer text. All five prior Important findings are resolved:

| # | Finding | Status | Evidence |
|---|---------|--------|----------|
| I1 | `generic_community_export` missing in README/first-run | **Resolved** | README pointer (`plan.md:153-159`) and first-run pointer (`plan.md:178-184`) both now include `generic_community_export` |
| I2 | CLI used shorthand command names | **Resolved** | CLI pointer (`plan.md:166-171`) now uses full `` `external-tool-readiness` `` / `` `external-tool-workflow` `` |
| I3 | Test asserted `docs/`-prefixed anchor in CLI | **Resolved** | Test (`plan.md:126`, `128-130`) now asserts `community-signal-import.md#external-tool-export-directory-examples` (no `docs/`); CLI pointer link target matches the correct sibling-relative path |
| I4 | first-run omitted csv/json/`generic_community_export` | **Resolved** | first-run pointer now says "checked-in `generic_community_export` CSV/JSON directory preflight examples" |
| I5 | Checklist pointer underspecified | **Resolved** | Checklist item (`plan.md:191-197`) is now explicit, includes `generic_community_export`, `external-tool-readiness`, `external-tool-workflow`, the example README path, and the anchor |

### Assertion-by-section trace (existing content + new pointer)

Required loop tokens per section: `examples/community-tool-handoff-directory.example/readme.md`, `external-tool-readiness`, `external-tool-workflow`, `generic_community_export`, `preflight examples`, `checked-in`, `csv`, `json`, `community-signal-import.md#external-tool-export-directory-examples`.

- **README** (scoped `README.md:111-128`): existing section already supplies the example README path, `csv`, `json`, `checked-in`; new pointer supplies the five remaining tokens. ✓
- **CLI** (scoped `cli-reference.md:220-230`): existing section supplies example README path, `csv`, `json`, `checked-in`; new pointer supplies the rest. ✓
- **first-run** (scoped `first-run.md:94-100`): existing section supplies none of the nine; new pointer supplies all nine. ✓
- **checklist** (scoped `github-upload-checklist.md:160-186`): existing section supplies example README path, `csv`, `json`; new pointer supplies the rest. ✓

Boundary markers for all four `between()` calls are present and unique; anchor heading `## External Tool Export Directory Examples` confirmed at `docs/community-signal-import.md:150`; example README exists. The RED step will genuinely fail (scoped README section lacks `external-tool-readiness`), and the GREEN step will pass.

## Critical Findings
None.

## Important Findings
None.

## Minor Findings

- **M1 (carried over, informational):** Design/plan still specify `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` for review while `AGENTS.md` and `docs/github-upload-checklist.md:513-515` mandate `claude --effort max --permission-mode plan`. Consistent with the user's explicit glm-5.2 review request; not a blocker.
- **M2 (prior):** Resolved — first-run pointer now uses matching display/target (`community-signal-import.md#…`, no `docs/`).
- **M3 (carried over, cosmetic):** README insertion point ("after the list of example paths") is mildly ambiguous, but both candidate points (`README.md:118` and `:127`) fall inside the scoped section, so the test passes either way.

## Scope-Boundary Check

Stage 117 remains docs/tests-only. The plan modifies only `README.md`, `docs/cli-reference.md`, `docs/first-run.md`, `docs/github-upload-checklist.md`, `tests/test_cli_docs.py`, and review artifacts (`plan.md:15-29`). It explicitly excludes `src/`, `uv.lock`, `pyproject.toml`, schemas, collectors, source packs, entity packs, dashboard, importers, scoring, reports, and CI. The pointer texts only **reference** existing Stage 116 commands and checked-in examples; they introduce **no** source acquisition, scraping, scheduling, monitoring, connector, platform-API, account/cookie, compliance/audit, or ranking behavior.

## Final Statement

**There are no remaining Critical or Important blockers before implementation.** All five prior Important findings (I1–I5) are fully resolved, the test/pointer texts are internally consistent, the RED/GREEN steps will behave as documented, and the stage stays within its docs/tests-only boundary.
