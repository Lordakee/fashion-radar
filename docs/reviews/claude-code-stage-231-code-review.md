# Stage 231 Code Review
**Verdict:** APPROVE_WITH_NITS

## Critical
None.

## Important
None.

## Nits
- **Architecture boundary doc not extended to phase 3.** `tests/test_architecture_boundary_docs.py:35` still asserts the Source Boundary section frames opt-in social collection as `"...(phase 2: xiaohongshu) is use-at-your-own-risk"`, with no phase-3 Instagram line. The test still passes (substring check), so this is not a break. Deferring to Stage 232 is defensible since the no-op collects nothing and the use-at-your-own-risk surface doesn't functionally exist yet — but flag it so the boundary doc gains a phase-3 Instagram opt-in line when the real collector lands.
- **Two settings fields are pre-declared but uncovered.** `InstagramSourceSettings.instaloader_path` and `login_user` (`source.py:69-70`) are forward plumbing for Stage 232 and aren't exercised. `test_instagram_source_with_query_is_valid` asserts only `target_type` and `max_posts_per_run` defaults — consider asserting the `None` defaults too, or hold these fields until 232 when they're consumed.
- **Dual-guard test covers one guard behaviorally.** `test_collect_sources_skips_article_enrichment_for_instagram` passes an explicit `article_extractor`, so it verifies the enrichment-skip guard (`runner.py:103-108`) but not the default-extractor-setup guard (`runner.py:73-82`) independently. This mirrors the existing Xiaohongshu test exactly, so it's consistent — noting only for completeness.
- **No-op returns SUCCESS, not SKIPPED.** `instagram.py:23` returns `CollectorResult.success(..., items=[])`, so a configured `instagram` source records a success with zero items every run (drives `record_success` in the runner). This is by-design for "exercised end-to-end" and is documented in the docstring; just be aware it can mask "not implemented yet" until Stage 232.

## Summary
All six verification points hold:
1. **Model** — `SourceType.INSTAGRAM` (`source.py:16`), `InstagramSourceSettings` with `Literal["hashtag","profile"]` `target_type` backed by the new `from typing import Literal` import (`source.py:4,66-72`), `SourceDefinition.instagram` default-factory field (`:97`), and the validator branch (`:121-122`) all mirror the Xiaohongshu pattern (`extra="forbid"`, `max_posts_per_run` ↔ `max_notes_per_run`, query-required guard).
2. **Stub** — `InstagramCollector.collect` (`instagram.py:17-23`) matches the runner `Collector` Protocol signature exactly and is a clean no-op success.
3. **Registration** — imported and wired in `_default_collectors()` (`workflows.py:9,128`), import order clean.
4. **Dual-guard** — `INSTAGRAM` added to **both** runner sets (`runner.py:81` and `:107`), so Instagram is excluded from default article extraction and enrichment like Xiaohongshu.
5. **Tests** — enum value, query-required, settings defaults, no-op success, registration, and enrichment-skip are all covered across the three test files.
6. **Plumbing only** — `source_type` persists as `String(64)` (`db/schema.py:34,76,91`) with no enum/CHECK constraint, so the new value needs no migration; `uv.lock`/`pyproject.toml` untouched. I also checked the other xiaohongshu-classified spots: `external_tool_readiness.py`/`external_tool_adapters.py` (instaloader entry) are correctly deferred to Stage 232 (no dep change), and `community_signal_profile.py:42` already lists `"instagram"` as a platform label — so nothing is missed in 231.

Nits are all follow-ups (chiefly the phase-3 boundary-doc line for Stage 232); none block this plumbing stage.
