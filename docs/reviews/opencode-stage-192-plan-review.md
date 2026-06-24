# Stage 192 Plan Review

## Critical

None. The plan stays inside the report builder/renderer plus documentation,
adds no CLI command, no public Daily Brief model-shape change, no
connector/scraping/LLM/dashboard contract mutation, and keeps source
attribution intact.

## Important

1. The Task 2 docs test phrases did not match the proposed
   `Current Follow-Up Status` replacement, so the original Task 2 Step 4
   "Expected: pass" was false. Specifically:
   - Assertion `"Stage 189 fixed review-capture hygiene gaps."` did not match
     the proposed bullet ending `"...review-capture hygiene gaps exposed by this
     review record and the Stage 188 review chain."`
   - Assertion `"Stage 191 added the Daily Brief Heat Narrative."` did not
     match the proposed bullet ending `"...Daily Brief Heat Narrative to
     generated daily reports."`

   `_normalized_text(...)` collapses whitespace only, so the punctuation and
   substring mismatch would have kept the GREEN gate failing. The plan needed to
   reconcile the assertions and replacement wording before implementation.

## Minor

1. `CHANGELOG.md` placement should use a refinement-oriented subsection such as
   `### Fixed` rather than `### Added`, because this stage is report-polish and
   status correction rather than a new contract surface.
2. The de-duplication design should note that if `health_items` reaches the
   section limit, recent-run caveats for the same sources remain suppressed.
   This is deterministic and reasonable, just worth being explicit.
3. A mixed-case de-duplication example is worth covering in the focused tests
   because `_source_caveat_key(...)` casefolds `(source_name, source_type)`.

## Verdict

Not approved until the Task 2 wording/test mismatch is fixed.
