# opencode Stage 299 Plan Review

**Reviewer:** opencode (GLM 5.2, variant `max`)
**Verdict:** CHANGES REQUIRED

## Findings

### Critical

None.

### Important

**I1. Missing escaping coverage for brief section fields.**

Review question 3 asks whether tests cover escaping via existing `_esc`, but the
plan did not add a brief-section escaping assertion. The repo already has a
local article XSS-safety test; after Stage 299, `brief_sections` default to
`[]`, so that test would continue to pass without exercising `_esc` on brief
section titles or bodies.

Fix before implementation: extend render RED tests with a brief section whose
title/body contain HTML-special characters and assert the escaped form appears
while the raw dangerous form does not.

### Minor

**M1. Indentation mismatch in rendered brief cards.**

Purely cosmetic; no functional or test impact.

**M2. Label duplication on the detail page.**

The brief intentionally reuses labels that also appear later in the detail
panel. This is acceptable because the brief is the scan layer and the existing
panel is the detail layer.

## Verdict

Proceed after fixing I1. No Critical findings.
