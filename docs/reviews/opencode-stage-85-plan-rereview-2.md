Now let me verify the actual test file structure matches what the plan describes, to ensure the fix is accurate.
I found a potential issue. The plan references `test_community_handoff_manifest_prints_json` but the actual test name is `test_community_handoff_manifest_command_prints_json_with_stable_keys`. Let me verify both tests' key structure.
Let me confirm the exact test name and verify there's no shorter alias for the manifest CLI test.
Let me verify the real exit code when running the non-existent test name (without collection-only mode), since this determines whether the gate fails loud or silently passes.
Confirmed the defect. Let me verify the wrong test name appears only in the Task 9 command and not elsewhere, and confirm the profile test name is correct.
# Stage 85 Plan Rereview 2 — Findings

Ordered by severity. Prior **I-2 (CLI key-order) is substantially resolved** in the editing steps, but **one new Important defect remains** in the verification command. No Critical blockers.

## Prior Important Finding (I-2): Largely RESOLVED (editing) ✅, verification broken ❌

The editing scope is correct:
- File Map now lists `tests/test_cli.py` (plan.md:27).
- Task 7 (plan.md:173-211) correctly inserts `"suggested_platform_labels"` after `"json_envelopes"` in `test_community_signal_profile_prints_json` and after `"supported_input_formats"` in the manifest CLI test (i.e., before `suggested_filename` — verified at `tests/test_cli.py:5120-5121`), plus value assertions.
- Task 9 ruff/diff commands now include `tests/test_cli.py`.

## Important

### I-3 (NEW): Task 9 manifest CLI focused-pytest command uses a non-existent test node ID

Task 9 (plan.md:275) runs:

```
uv --no-config run --frozen pytest tests/test_cli.py::test_community_handoff_manifest_prints_json -q
```

That test name does not exist. The actual test is
`test_community_handoff_manifest_command_prints_json_with_stable_keys`
at `tests/test_cli.py:5077` (confirmed against the source and prior stage plans 52/54/59). Verified execution:

```
ERROR: not found: /home/ubuntu/fashion-radar/tests/test_cli.py::test_community_handoff_manifest_prints_json
no tests ran in 0.41s   EXIT: 4
```

So the manifest CLI focused-gate exits 4 (usage error). Consequence: the very manifest key-order test that I-2 demanded is **not actually exercised** by Task 9 — the gate either hard-fails (confusing the implementer) or, if masked, gives false confidence. The real regression is only caught later by Task 10's full `pytest`.

The profile-side command (plan.md:274, `test_community_signal_profile_prints_json`) is correct — only the manifest side is mistyped.

**Fix:** change plan.md:275 to:

```
uv --no-config run --frozen pytest tests/test_cli.py::test_community_handoff_manifest_command_prints_json_with_stable_keys -q
```

## Minor (non-blocking, unchanged)

- **M-1:** No `CHANGELOG.md` entry; the community-signal stage series conventionally adds one.
- **M-2:** No explicit "no `cli.py` edit needed" note (pydantic serializes the new field automatically; only the two table renderers change).

## Recommendation

Fix **I-3** (one-line test-node-id correction in Task 9), then proceed. After that fix, the prior I-2 loop is fully closed and no Critical/Important blocker remains. No scraping, connectors, platform APIs, schema enums, linter restrictions, or compliance-review behavior is introduced.
