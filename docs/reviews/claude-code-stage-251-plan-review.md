# Stage 251 Plan Review
**Verdict:** APPROVE_WITH_NITS

## Critical
None.

## Important
None.

## Nits
- **`search_prefix` is unconstrained free-form `str`** (`search_prefix: str = "ytsearch"`), unlike the `Literal[...]` fields the mirrored siblings use (`TwitterSourceSettings.output_format`, `InstagramSourceSettings.target_type`). Harmless in Stage 251 (the field is never read until Stage 252), but in Stage 252 the collector builds `f"{search_prefix}{N}:{query}"`, so an empty/garbage value yields a malformed `yt-dlp` search expression. Consider `Literal["ytsearch", "ytsearchdate"]` or a non-empty validator — or explicitly defer to Stage 252 to keep this plumbing byte-identical to Stage 241.
- **Be explicit about the `test_workflows.py` registration test.** Stage 241 *renamed* `test_default_collectors_register_html_sitemap_xiaohongshu_and_instagram` → `..._instagram_and_twitter` and added an `isinstance` assertion. The plan lists `test_workflows.py` in scope but doesn't spell out the rename → `..._twitter_and_youtube` + new assertion. It's a per-collector `isinstance` check with no length assertion, so it won't fail on its own — just ensure the executor extends it rather than leaving YOUTUBE unasserted.
- **Naming proximity with the existing `yt_dlp` import adapter.** `external_tool_adapters.py` / `external_tool_readiness.py` already ship a `yt_dlp` "yt-dlp Metadata Export" *manual-import* adapter — a distinct path from the new live `SourceType.YOUTUBE` collector. No code collision (`yt_dlp` label vs `"youtube"` enum value), but flag for Stage 253 docs to disambiguate the two YouTube routes.
- **Trivia:** "runner line-73 + line-97 guards" is loose — the two `source.type not in {…}` sets are currently at ~77–84 and ~104–110; the File Map's "both guard sets" is unambiguous. Enum placement (after `TWITTER`, before `MANUAL_IMPORT`) is only implied; obvious from the mirror.

## Summary
Faithful, low-risk mechanical mirror of Stage 241 (verified against commit `b2fb2da`). All five criteria pass:

1. **`YouTubeSourceSettings` shape — sound.** `ytdlp_path: str | None` mirrors `twitter_cli_path`/`instaloader_path`; `max_videos_per_run` reuses the identical `Field(default=20, gt=0, le=200)` bound; `ConfigDict(extra="forbid")` consistent. `search_prefix` defaults `"ytsearch"` and composes with `max_videos_per_run` into the Stage 252 `ytsearch<N>:<query>` command — the field set supports the spec's collector design (one nit on its lack of constraint).
2. **Validator + `SourceType` + `SourceDefinition` field — consistent with `TWITTER`.** `YOUTUBE = "youtube"` enum member, `youtube: YouTubeSourceSettings = Field(default_factory=…)` field, and the `if self.type == SourceType.YOUTUBE and not self.query` branch each slot directly after their TWITTER counterparts (source.py:17 / 107 / 133–134).
3. **Runner dual-guard — correct.** YouTube items are yt-dlp metadata (youtube watch URLs); article enrichment must be skipped exactly as for the other social sources. Adding `YOUTUBE` to *both* `source.type not in {…}` sets (extractor selection ~77–84 and enrichment ~104–110) is right. These are the only guard sets gating social sources — `source_liveness.py` and `source_packs.py` special-case only RSS/RSSHUB/GDELT and intentionally skip social types, matching Stage 241, so no third guard is missed.
4. **Plumbing only — confirmed.** No DB schema change; `yt-dlp` stays an external CLI (no Python dep); `git diff --exit-code -- uv.lock pyproject.toml` is in the verification. `check_release_hygiene.py` enumerates no source types (spec's "no hygiene change" holds). Stub `collect` returns `CollectorResult.success(source, items=[], started_at=started_at)`, matching the `Collector` Protocol and the Stage 241 stub exactly.
5. **No exhaustive `SourceType` pin that breaks.** Repo-wide grep found no `set(SourceType)`/`len(SourceType)`/`for … in SourceType` assertion, and `cli.py` exposes no source-type `choices`. The docs-guard (`test_source_boundaries_docs.py`) asserts per-source *phrases* (instagram, twitter), added in the docs stage (253) — adding the enum member alone breaks nothing. `test_config.py`'s `{"rss","gdelt"}` set assertions are scoped to example config files that don't change in 251.

Recommend proceeding; resolve the `search_prefix` nit now or explicitly defer it to Stage 252.
