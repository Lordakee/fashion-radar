I'll review the Stage 75 implementation systematically. Let me start by understanding what changed.
Now let me verify the actual runtime registry matches the documented matrix:
All 7 rows match the runtime registry exactly. Let me run the actual CLI JSON output and execute the verification suite independently:
Runtime matches docs exactly. Now let me verify the Stage 74 correction note and run the test suite:
Correction note is factually accurate — the Stage 74 plan-review is now a clean single document. Now let me run the verification suite independently:
All verification reproduces cleanly (43 docs tests pass, 1100 full pytest pass, ruff clean, hygiene clean, `git diff --check` clean, runtime JSON matches the documented matrix exactly). Here is my Stage 75 code review.

---

## Stage 75 Code Review

**Critical:** None.
**Important:** None.
**Minor:** None blocking (M1–M3 below, all non-actionable or already acknowledged).

### Answers to review questions

1. **Does the docs matrix match the current runtime adapter registry exactly?** Yes. I ran `external-tool-adapters --format json` and diffed every cell against both `README.md:120-126` and `docs/cli-reference.md:89-95`: all seven rows (`rednote_mcp`, `xiaohongshu_crawler`, `instaloader`, `tiktok_api`, `yt_dlp`, `x_search_export`, `generic_community_export`) match in id, display/source name, platform label, format, pattern, and registry order (`src/fashion_radar/external_tool_adapters.py:108-231`). The footnote stating `display_name` and `suggested_source_name` are identical for these adapters is accurate and independently verified.

2. **Are the docs tests strong enough?** Yes, for the contract surface. The guard asserts each of the seven full Markdown row strings (with backticks and pipes) against `_normalized_text` of both docs (`tests/test_cli_docs.py:1082-1086`), so any cell value change or row deletion fails. The first-run smoke phrase is pinned verbatim in both README and `docs/first-run.md` via `FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE`. Gaps, all acknowledged in the Stage 75 plan-review M2: header/separator renames and undocumented extra rows would pass silently. Acceptable — data rows are the contract.

3. **Is the Stage 74 correction note factually supported?** Yes. `docs/reviews/opencode-stage-74-plan-review.md` is a clean, single, coherent 61-line document with no concatenation or mid-word breaks. The appended Correction Note (`docs/reviews/opencode-stage-74-code-review.md:48-53`) accurately records that the original M1 finding referred to a corrupted draft that was fixed before the Stage 74 commit.

4. **Is the changelog entry scoped correctly?** Yes. `CHANGELOG.md:185-188` explicitly states "documentation/test-only and adds no runtime adapter or external-platform behavior," matching the docs/test-only diff.

5. **Runtime, dependencies, external-platform behavior unchanged?** Yes. `git diff --stat HEAD -- src/ scripts/ pyproject.toml uv.lock` is empty; the full working-tree diff is six files (4 docs, 1 review artifact, 1 test file) totaling +70 lines.

6. **Critical/Important before commit?** None.

### Minor notes

- **M1 (acknowledged).** Header/separator and extra-row drift would not fail the guard. Plan-review M2 already accepted this trade-off; no action needed.
- **M2.** Matrix row *order* is not enforced by the test. The runtime smoke independently pins order, so this is cosmetic; flagging only for awareness.
- **M3.** Plan-review M1's `display_name`/`suggested_source_name` conflation was addressed by the footnote under both tables — good response to the review finding.

### Scope-boundary check

Strictly docs and docs-test hardening. No connectors, scraping, browser automation, platform APIs, login/cookie/session/token/proxy/CAPTCHA behavior, media download, monitoring/scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review product behavior introduced.

### Verification re-run (this review)

- `external-tool-adapters --format json` → 7 adapters, every cell matches docs.
- `pytest tests/test_cli_docs.py -q` → 43 passed.
- `ruff check` + `ruff format --check` on `tests/test_cli_docs.py` → clean.
- `scripts/check_release_hygiene.py` → passed.
- `git diff --check` → clean.
- `pytest -q` → 1100 passed.

**Recommendation:** Proceed to commit.
