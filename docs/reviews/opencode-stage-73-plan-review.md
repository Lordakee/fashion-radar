I'll review the Stage 73 design and plan documents. Let me read them along with the current implementation context.
Now let me examine the current implementation, test fixture, and adapter registry to verify the plan's accuracy.
Now let me locate the adapter registry to verify the expected adapter map, and check the Stage 72 CLI test for comparison.
Let me read the adapter registry definition and the Stage 72 CLI test to verify the expected map.
Let me see the Stage 72 `expected_adapters` definition in test_cli.py to compare with the proposed map.
Let me verify whether `external_tool_adapters_payload()` is used by any integration test (CLI stub) that would be affected by expanding the fixture.
Let me find the name of the integration test that consumes the stubbed payload.
I now have full context to deliver the review. Cross-checking the proposed `EXPECTED_EXTERNAL_TOOL_ADAPTERS` map against the verified source-of-truth in `src/fashion_radar/external_tool_adapters.py:108-234` and the Stage 72 CLI test map at `tests/test_cli.py:541-559`.

---

# Stage 73 Plan Review

**Verdict: Approved for implementation. No Critical or Important findings.**

## Answers to Review Questions

**1. Expected adapter map correct and consistent with the registry?** Yes. All seven entries in the design's `EXPECTED_EXTERNAL_TOOL_ADAPTERS` (`docs/.../stage-73-...design.md:43-52`) match `src/fashion_radar/external_tool_adapters.py:108-233` exactly in id order, `input_format`, `pattern`, and `source_name`:
- `rednote_mcp` json/`*.json`/Rednote MCP Export
- `xiaohongshu_crawler` csv/`*.csv`/Xiaohongshu Crawler Export
- `instaloader` json/`*.json`/Instaloader Export
- `tiktok_api` json/`*.json`/TikTok-Api Export
- `yt_dlp` json/`*.json`/yt-dlp Metadata Export
- `x_search_export` csv/`*.csv`/X Search Export
- `generic_community_export` csv/`*.csv`/Generic Community Export

It also matches the Stage 72 map at `tests/test_cli.py:541-559`. Pinning independently of the runtime registry (rather than importing it) is the right call — it lets smoke catch registry drift, consistent with how the other `EXPECTED_*` constants in the script are pinned. `list(EXPECTED_EXTERNAL_TOOL_ADAPTERS)` preserves insertion order on Py3.11, so the `assert_equal("adapter ids", ...)` is an exact order+content match.

**2. Avoids broadening runtime behavior?** Yes. Touched files are limited to `scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py`. No changes to `src/fashion_radar/external_tool_adapters.py`, CLI, or registry. Validation stays static (JSON contract + `shlex.split` on readiness strings). Out-of-scope list explicitly excludes all AGENTS.md-forbidden behaviors.

**3. Error messages and test mutations clear enough?** Yes. The refactored `required_readiness_value(parts, adapter_id, flag)` embeds `{adapter_id}` in every message, so the proposed later-adapter drift assertion (`xiaohongshu_crawler readiness input_format`) is unambiguous. Existing `adapters[0]` negative-case regexes (`missing value for '--source-name'`, `readiness command is not shell-parseable`, `recommended_commands must be a list`, `missing external-tool-readiness command`) still match because their substrings are preserved in the new message format. The id-list mutation on `adapters[1]` + `"adapter ids"` assertion correctly proves later-position coverage.

**4. Critical/Important issues?** None.

## Minor Notes

- **M1 — `import shlex` not mentioned.** The proposed `external_tool_command` helper (plan Step 5) uses `shlex.join`, but `tests/test_first_run_smoke.py` does not currently import `shlex`. The implementer must add it; worth a one-line note in Step 5.

- **M2 — Second consumer of the fixture not acknowledged.** `external_tool_adapters_payload()` is also used as a CLI stub at `tests/test_first_run_smoke.py:1861` inside `test_run_first_run_flow_uses_deterministic_local_command_sequence` (line 1794), which feeds the payload through the *full* `validate_external_tool_adapters`. Expanding the fixture therefore implicitly exercises that integration path too — good coverage, but every one of the 7 readiness commands must be fully well-formed (not just the unit test's positive case). Task 2's `uv ... pytest tests/test_first_run_smoke.py -q` will catch any regression; consider naming this test in the plan so the implementer expects it.

- **M3 — Plan-review artifacts have no creation step.** `opencode-stage-73-plan-review-prompt.md` / `opencode-stage-73-plan-review.md` are listed in the commit (`plan:297`) and File Map, but only the *code*-review pair gets an explicit step (Task 2 Step 2). They're handled implicitly by the AGENTS.md review workflow, but a one-line note would close the loop.

- **M4 — Cosmetic `.get` inconsistency.** Plan Step 4's first loop uses `str(adapter.get("id", ""))` while the second uses `str(adapter.get("id"))` (default `None` → `"None"`). The second form is unreachable as a bug because the preceding `assert_equal` on ids guarantees valid keys, but `str(adapter["id"])` would be clearer.

The plan is sound, well-scoped, and AGENTS.md-compliant. Proceed to implementation.
