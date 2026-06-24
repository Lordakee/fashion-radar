# Stage 189 Code Rereview

I re-evaluated the Stage 189 working tree against the committed state, the prior Stage 189 code review, the Stage 188 review chain, and the actual test/lint/hygiene gates. I re-ran the pinned docs test, the release-hygiene suite, the full pytest gate, ruff check/format on the changed files, and line-anchored scans of the review archive.

## Critical

None. Prior **C1 is resolved.** `docs/REVIEW_PROTOCOL.md:104-105` now reads *"If the review times out, record the timeout honestly in a separate scratch location and retry…"*, which restores the exact phrase pinned by `REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES` at `tests/test_review_protocol_docs.py:28`. The previously-failing `test_review_protocol_docs_document_capture_hygiene` now passes, and the full suite is green at **1393 passed** (previously `1 failed, 1392 passed`). The new wording also stays consistent with the timeout-stub detector — the pinned phrase and the detector no longer contradict.

## Important

None. Verified against the prior review's four open questions:

1. **C1 / docs gate** — resolved as above.
2. **Detector scope** — intact. The non-stage opencode blind spot is closed (`NON_STAGE_OPENCODE_REVIEW_ARTIFACT_PATTERN`, guarded against legacy stage files by the `(?!stage-[0-9]+-)` lookahead and the `stage >= 159` ordering), and timeout-stub rejection is live via `REVIEW_CAPTURE_TIMEOUT_STUB_PREFIXES` (`scripts/check_release_hygiene.py:90-94,431-433`). The three regression tests prove both directions: non-stage capture noise fails, staged timeout stub fails, and clean non-stage body passes. The checker reports the review archive clean against the current repo.
3. **Stage 188 artifacts** — coherent and free of capture noise. `opencode-stage-188-code-review.md` is a complete 62-line review (Q1/Q2/Q3 + Verdict), the code-rereview and release-rereview are self-consistent, and `opencode-full-project-review.md` is a clean 106-line review. Line-anchored scans of all Stage 188 records plus the full-project review found no ANSI escapes, no line-starting timeout-stub prefixes, and no line-starting tool-status/process-chatter prefixes.
4. **Duplicate proxy test** — resolved. `test_collect_configured_sources_uses_injected_collectors` (`tests/test_workflows.py:61-81`) no longer takes `monkeypatch` or pins proxy env; `test_collect_configured_sources_with_injected_collectors_ignores_proxy_env` (`tests/test_workflows.py:84-109`) uniquely owns the proxy-seam guard. The two now have a genuine behavioral difference, and the shared `article={"enabled": False}` is hermetic setup, not duplicated assertion behavior.

Ruff check and format are clean on `scripts/check_release_hygiene.py`, `tests/test_release_hygiene.py`, `tests/test_review_protocol_docs.py`, and `tests/test_workflows.py`.

## Minor

- **M1 — `opencode-full-project-review.md:103-104` still describes Stage 189 in future/intent tense** ("Stage 189 is intended to fix review-capture hygiene gaps…"). This is the carried M3 from the prior code review; now that Stage 189 is the active node and its hygiene work is effectively complete, the phrasing reads slightly oddly. Cosmetic and non-blocking for a historical pre-Stage-188 snapshot.
- The Stage 188 carried cosmetic items (CHANGELOG `### Fixed` ordering before `### Changed`; README/architecture edit breadth) remain as-is and are out of scope for Stage 189 — non-blocking.

## Verdict

**Approved for release verification.** Prior C1 is resolved, the full gate is green (1393 passed), the release-hygiene detector still rejects non-stage capture noise and staged timeout stubs while leaving the review archive clean, the Stage 188 review chain is coherent and capture-free, and the duplicate proxy-test concern stays resolved. The only remaining items are non-blocking cosmetic minors. The Stage 189 working tree is acceptable to proceed to release-gate verification.
