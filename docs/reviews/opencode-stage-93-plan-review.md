I'll review the Stage 93 plan. Let me start by reading all the relevant files in parallel.
Let me verify the proposed assertions actually match the current doc by running a read-only check (no file modifications).
All 11 assertions match. Let me check for any existing scheduling-docs coverage that could overlap or conflict, and verify the proposed test file doesn't already exist.
## Stage 93 Plan Review — Findings

**No Critical or Important blockers.** All proposed assertions are present in the current doc (verified by execution), the scope is purely additive/test-only, and it is independent of other stages. Details below, ordered by severity.

---

### Informational / Low (optional, not blockers)

**L1 — `_section` fails non-gracefully if heading is removed.**
`docs/.../plan.md:57-58` `text.split(f"## {heading}", 1)[1]` raises `IndexError` (not a clean `assert` failure) if `## Generate Examples` is ever renamed/removed. For a drift guard this is arguably desired (any heading change is intentional drift that should surface loudly), so it is acceptable. Optional: wrap with an explicit `assert f"## {heading}" in text`.

**L2 — `"you review yourself"` is the most generic phrase.**
`plan.md:81`. It is fine in context (paired with the ``local `.eml` handoff file`` phrase immediately before it), but it is the phrase most likely to match unintended rewording. Not worth changing; noted for awareness.

**L3 — Phrases are intentionally exact (backticks, `->` arrows).**
`plan.md:67` (`` `run` executes `collect -> match -> report` in one local process ``) and `plan.md:78` will break on cosmetic reformatting. This is correct drift-guard behavior (forces intentional review on rewording), not a defect.

---

### Answers to review questions

**1. Are the proposed docs assertions present in current `docs/scheduling.md`?**
Yes — all 11. Verified by running the exact normalization + matching logic against the live file:
- `test1` (`plan.md:64-71`) → all 5 match against `scheduling.md:3,4,10,14,15`
- `test2` (`plan.md:77-83`) → all 4 match against `scheduling.md:33-37`
- `test3` (`plan.md:90-94`) → both match the `## Generate Examples` section (`scheduling.md:41`)

**2. Are the phrases stable enough and not overly broad?**
Yes. 10 of 11 are highly specific (daemon, serial-run delegation, `collect -> match -> report`, sqlite-overlap, digest file list, no email/webhook/browser/daemon, `.eml` handoff, `schedule-example` print-only, installs nothing). Only `"you review yourself"` is generic (see L2), and it is adequately anchored by its neighbor phrase. None are so broad they'd match arbitrary unrelated text.

**3. Is the scope safely test-only and independent from Stages 91/92/94?**
Yes. Only `tests/test_scheduling_docs.py` (new) + review artifacts are touched. Confirmed: the file does not yet exist; `docs/scheduling.md` is read-only here; `tests/test_cli_docs.py:53` references `scheduling.md` only in `PATH_CONSISTENCY_DOCS` (no boundary overlap); `tests/test_scheduling.py` and `tests/test_cli.py` cover runtime behavior, not docs. No shared mutable state with other stages.

**4. Are the verification commands sufficient?**
Yes. Focused gate (`plan.md:101-107`: new file + combined scheduling tests + `ruff check` + `ruff format --check` + `git diff --check`) plus full hygiene gate (`plan.md:122-131`: release hygiene, full pytest, repo-wide ruff, `UV_NO_CONFIG=1 uv lock --check`, mirror-URL scan, lockfile/pyproject diff). Commands are valid — I ran `uv --no-config run --frozen pytest tests/test_scheduling.py tests/test_cli_docs.py -q` → 71 passed.

**5. Critical/Important blockers before implementation?**
None.

**Verdict:** Safe to proceed to implementation. The plan is internally consistent with the design spec, correctly bounded, and the assertions are sound.
