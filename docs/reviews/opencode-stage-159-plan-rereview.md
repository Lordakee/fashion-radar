# Stage 159 Plan Rereview

## Verdict

C1 and I1 are fully resolved. The plan is safe to implement with no critical or
important findings. A few minor follow-ups remain.

## First-Review Finding Verification

### C1 - Resolved

The UI-marker check is narrowed to line-start position in plan Task 2, Step 3:

```python
def has_review_tool_ui_marker(line: str) -> bool:
    stripped = line.lstrip()
    return (
        stripped.startswith(("\u2192", "\u2731"))
        or stripped.startswith("build \u00b7")
    )
```

The false-positive RED test
`test_stage_159_review_artifact_with_inline_arrow_prose_passes` writes inline
arrow prose and asserts the release-hygiene checker accepts it.

### I1 - Resolved

The regex now accepts numbered rereviews:

```python
r"...-(?:plan|code|release)-(?:review|rereview(?:-[0-9]+)?)\.md$"
```

`test_stage_159_numbered_rereview_artifact_is_checked` targets
`opencode-stage-159-code-rereview-2.md`, which is RED under the old pattern and
GREEN under the new one.

## Minor Findings

- m1: The prompt-exclusion test name still is not selected by the focused
  `-k "review_artifact or review_capture"` filter. Rename it to include the
  contiguous `review_artifact` substring or broaden the filter.

- m2: `REVIEW_CAPTURE_UI_MARKERS` is defined but unused in the planned snippet.
  Drop it or consume it.

- m3: The release-review artifact is created after the final hygiene gate. Re-run
  `scripts/check_release_hygiene.py` after the release review and before commit.

- m4: The design release-gate block omits the release-hygiene script. Sync the
  design with the plan.

## Answers To Review Questions

1. C1 and I1 are fully resolved.
2. Tests and snippets are internally consistent, except for the minor focused
   filter naming issue noted above.
3. Scope is still process-only. No product/runtime, social collection,
   scraping, browser automation, platform API, login/cookie/token, scheduling,
   monitoring, source acquisition, demand proof, ranking, coverage verification,
   or compliance-review product behavior is introduced.
4. The plan is safe to implement with no critical or important findings.

## Summary

Implement-ready after minor cleanup. The remaining findings are non-blocking,
but should be addressed before coding because they are straightforward.
