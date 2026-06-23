# Stage 181 Code Rereview

## Summary

The post-review change adds a single explicit assertion that both community
docs contain the adapter catalog table header
`| Adapter id | Display/source name | Platform label | Format | Pattern |`,
directly closing the first review's Minor M1. The fix is correctly scoped: it
is a standalone static-string check placed alongside the existing
`"Known adapter ids:"` guard, it is isolated from the advisory-wording phrase
loop, and it does not touch runtime, CLI, connectors, or the lockfile. The
trailing Markdown fence on the review artifact was also removed. No Critical,
Important, or material Minor findings remain. Approved for release
verification.

## Question Answers

1. Still matches the approved plan. The change is purely additive inside the
   already-planned test `test_community_signal_docs_list_current_external_tool_adapter_catalog`
   (`tests/test_external_tool_contract_parity.py:120`). No new test, no new
   constant, no runtime/CLI/connector/lockfile change. The asserted string is
   byte-identical to the plan's Task 2 reference header and to the headers
   actually rendered in `docs/community-signal-import.md:206` and
   `docs/community-signal-quality.md:29`. Scope boundaries (advisory-only,
   no platform coverage/demand proof) are unchanged.

2. M1 is correctly addressed without over-constraining prose. The new assert
   (`tests/test_external_tool_contract_parity.py:127-129`) checks the literal
   header against the whitespace-normalized doc text for both docs. It sits as
   a standalone check between the `"Known adapter ids:"` assertion
   (`tests/test_external_tool_contract_parity.py:126`) and the registry-derived
   per-row loop (`tests/test_external_tool_contract_parity.py:130-131`), and is
   deliberately kept out of the advisory-phrase loop
   (`tests/test_external_tool_contract_parity.py:133-142`). This closes the M1
   gap exactly: a header-only rename (e.g. "Platform label" -> "Platform") with
   data rows intact would now trip the test, while any real value drift is
   still caught by the per-row assertions. The header is static (not
   adapter-derived), so placing it as a standalone assert rather than inside
   `expected_rows` is the more correct choice than the M1 options offered — it
   keeps `expected_rows` purely registry-derived. No surrounding prose is
   constrained; the phrase loop still only anchors advisory wording. Whitespace
   normalization (`" ".join(...split())` at line 124) means reflow cannot mask
   a real header-word mismatch.

3. No Critical or Important findings. Independently re-run:
   `uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q`
   -> 7 passed; `ruff check` -> All checks passed; `ruff format --check` -> 1
   file already formatted. The header string matches both docs exactly and
   appears once per doc, so the `in` check is meaningful. The review artifact
   now ends cleanly at `docs/reviews/opencode-stage-181-code-review.md:107`
   with no trailing code fence.

## Critical

None.

## Important

None.

## Minor

None material.

The implementation is approved for release verification.
