# Stage 241 Plan Review
**Verdict:** APPROVE

## Critical
None.

## Important
None.

## Nits
- The no-op stub specification in the plan ("returns `CollectorResult.success(source, items=[], started_at=started_at)`") should clarify whether `finished_at` is also `started_at` for the stub, consistent with how skip results are constructed in runner.py:54. Inspecting other collectors during implementation will resolve this.

## Summary
The plan cleanly mirrors Stage 231 (Instagram plumbing). All five review criteria pass:

1. **TwitterSourceSettings shape:** Sound. `Literal` output_format matches Instagram's `target_type` pattern; `Field(default=20, gt=0, le=200)` bounds mirror `max_posts_per_run`; `ConfigDict(extra="forbid")` consistent; `twitter_cli_path` optional mirrors `instaloader_path`.

2. **Consistency with INSTAGRAM:** SourceType enum placement (after INSTAGRAM, before MANUAL_IMPORT) correct; SourceDefinition.twitter field placement (after instagram:97) correct; validator branch (after INSTAGRAM:121-122) mirrors pattern exactly.

3. **Runner dual-guard:** Both guard sets correctly identified at runner.py:77-82 (article extractor skip) and runner.py:103-108 (enrichment skip). TWITTER should join {HTML, SITEMAP, XIAOHONGSHU, INSTAGRAM} in both.

4. **Plumbing only:** No schema/dep change confirmed. Verification includes `git diff --exit-code -- uv.lock pyproject.toml`; twitter-cli is external (no new Python dep); stub collector defers subprocess logic to Stage 242.

5. **Pinned SourceType sets:** Plan addresses workflows.py `_default_collectors()` registration and lists test files needing attention (test_source_model, test_collectors_runner, test_workflows, test_config). File map complete.

Low-risk mechanical addition. APPROVE.
