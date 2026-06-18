I'll rereview the Stage 85 plan. Let me read the relevant files in parallel.
Now let me verify the prior finding is resolved by checking the actual test file and docs to make sure no new blockers exist.
Let me verify the test function structure and current docs content to ensure no new blockers exist.
Let me check whether any smoke/release-hygiene tests pin the full profile/manifest JSON key set, which a new field could break.
I need to check `test_cli.py` lines 507 and 5120 — these have stable key-order assertions for the profile and manifest CLI JSON output that the plan does NOT update.
I found a significant gap. Let me verify there are no other full-key-list assertions I'm missing (e.g., in smoke tests or release-hygiene scripts).
# Stage 85 Plan Rereview — Findings

Ordered by severity. Prior **I-1 is resolved**. **One new Important finding.** No Critical blockers.

## Prior Important Finding (I-1): RESOLVED ✅

Task 7 (plan.md:177-183) now instructs adding the exact advisory sentence to `docs/community-signal-import.md`:

> `` `suggested_platform_labels` is advisory local provenance label guidance for the optional handoff `platform` field. It is not a schema enum, not a linter restriction, not platform coverage, and not demand proof. ``

All seven verbatim phrases required by the `test_community_signal_profile_docs_are_linked` loop (plan.md:211-223) are present: `suggested_platform_labels`, `advisory local provenance label guidance`, `` optional handoff `platform` field ``, `not a schema enum`, `not a linter restriction`, `not platform coverage`, `not demand proof`. The same sentence is also added to `community-signal-quality.md` (plan.md:201-205). Both docs will pass.

## Important

### I-2 (NEW): `tests/test_cli.py` pins full profile + manifest JSON key order, but the plan never updates it

Two CLI-level tests assert the **complete** JSON key list via `assert list(payload) == [...]`:

- `tests/test_cli.py:501` (`test_community_signal_profile_prints_json`) — expected list has no `suggested_platform_labels`; will fail after Task 2.
- `tests/test_cli.py:5108` (manifest CLI test) — expected list has no `suggested_platform_labels`; will fail after Task 3.

The plan updates the *parallel* model-level stable-order tests (`tests/test_community_signal_profile.py:114` via Task 4; `tests/test_community_handoff_manifest.py:33` via Task 5) but misses these CLI-level twins. The File Map (plan.md:21-30) omits `tests/test_cli.py`, and **Task 8 focused verification does not run it** — so the focused gate gives false confidence. The breakage is only caught in Task 9's full `pytest`, and the plan gives the implementer no instruction on where/how to fix it.

**Fix:** Add to the File Map and insert a Task (or extend Task 4/5):
- At `tests/test_cli.py:513`, insert `"suggested_platform_labels"` immediately after `"json_envelopes"`.
- At `tests/test_cli.py:5120`, insert `"suggested_platform_labels"` immediately after `"supported_input_formats"` (i.e., before `"suggested_filename"`).
- Add `tests/test_cli.py` to Task 8's focused pytest + ruff commands.

Verified no other payload test breaks: the remaining `assert list(payload) == [...]` sites pin independent models (candidates, workflows, templates, readiness, adapters, lint), none of which embed the profile/manifest. `scripts/check_first_run_smoke.py` references only command names, not profile keys.

## Minor (non-blocking, unchanged from prior review)

- **M-1:** Still no `CHANGELOG.md` entry; project convention for the community-signal stage series uses one.
- **M-2:** Still no explicit "no `cli.py` edit needed" note (JSON serialization is automatic via pydantic; only the two table renderers change).

## Recommendation

Address **I-2** (add `tests/test_cli.py` to scope + Task 8 verification, with the two key-list insertions), then proceed to implementation. Prior I-1 is fully resolved. No Critical blockers; no scraping/connectors/platform-API/schema-enum/linter/compliance-review behavior introduced.
