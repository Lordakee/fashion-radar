# Stage 160 Plan Review

## Verdict

No critical or important findings. No blocking findings. The plan is the right
narrow next step after Stage 159, the RED tests are correctly designed and
verified to fail under the current line-membership implementation, the proposed
GREEN implementation is correct, and product scope boundaries are respected.

## Independent Verification

I independently checked the load-bearing cases before responding:

- Wrong group: `[gui_scripts]` currently returns rc=0, while the new test expects
  rc=1 with a section-aware error.
- Missing script with new wording: current code emits the old
  `entry_points.txt is missing ...` wording, so the updated assertion fails
  before implementation.
- Wrong target: current code emits a missing-line error, not a target-mismatch
  error.
- Malformed no-header content: current code returns rc=0, while the new test
  expects rc=1 with an `entry_points.txt is invalid:` prefix and no traceback.

I also simulated the proposed `validate_wheel_entry_points(...)` body against
happy path, wrong group, missing entry, wrong target, malformed input, empty
section, empty file, duplicate option, mixed-case section, and mixed-case key
cases. The proposed parser behavior is correct for the Stage 160 requirements.
`optionxform = str` correctly preserves script-name case, and
`interpolation=None` is appropriate for wheel entry-point metadata.

## Review Answers

1. Right narrow Stage 160: yes. Stage 160 closes a real release-gate gap where
   a `[gui_scripts]` line can satisfy the current line-membership check.
2. RED tests: yes. The planned tests prove wrong group, missing script, wrong
   target, malformed input, and no-traceback behavior.
3. Parser choice: yes. `ConfigParser(interpolation=None)` plus
   `optionxform = str` is appropriate. The default strict mode also catches
   duplicate options as invalid.
4. Error messages: yes. Missing entries and target mismatches are deterministic,
   and malformed entry-point metadata returns a controlled checker error.
5. Scope boundaries: yes. The change is purely local package archive validation.
   It adds no connectors, scraping, browser automation, platform APIs, account
   state, monitoring, scheduling, source acquisition, ranking, demand proof,
   coverage verification, or compliance-review product feature.
6. Review and release gates: yes. The plan includes local opencode code review,
   full release gate, local opencode release review, release-hygiene rerun, and
   commit/push.

## Findings

### Critical

None.

### Important

None.

### Minor

- m1: The design says to require a `[console_scripts]` section, while the
  proposed implementation reports missing expected console-script entries when
  the section is absent instead of emitting a dedicated missing-section error.
  This is functionally acceptable and matches the planned tests.
- m2: The malformed error embeds ConfigParser diagnostic text. The tests assert
  only the stable `entry_points.txt is invalid:` prefix, so they remain robust.

## Summary

No blocking findings. Stage 160 is safe to implement under the staged review
workflow.
