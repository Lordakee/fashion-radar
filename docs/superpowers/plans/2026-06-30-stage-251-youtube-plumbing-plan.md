# Stage 251 YouTube Source Plumbing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** Add `SourceType.YOUTUBE` + `YouTubeSourceSettings` + a no-op `YouTubeCollector` stub + default registration + runner dual enrichment-skip guard — plumbing only (no live yt-dlp calls; those land in Stage 252). Mirrors Stage 241 (Twitter plumbing).

**Architecture:** New enum member + Pydantic settings sub-model + validator branch + no-op collector + registration + runner guards. No DB schema change, no dependency change.

**Tech Stack:** Python 3.11, Pydantic v2, pytest, `uv --no-config run --frozen`, Claude Code + opencode review.

## Scope

**In:** `SourceType.YOUTUBE`; `YouTubeSourceSettings` (ytdlp_path, max_videos_per_run, search_prefix); `SourceDefinition.youtube`; `validate_source_target` branch (requires query); `src/fashion_radar/collectors/youtube.py` no-op stub; registration in `_default_collectors()`; runner line-73 + line-97 guards extended to `YOUTUBE`; tests.

**Out:** real yt-dlp subprocess/parse (Stage 252); docs (Stage 253); schema/dep changes.

## File Map

- `src/fashion_radar/models/source.py` — SourceType member, YouTubeSourceSettings, SourceDefinition field, validator branch.
- `src/fashion_radar/collectors/youtube.py` (new) — no-op stub.
- `src/fashion_radar/workflows.py` — import + registration.
- `src/fashion_radar/collectors/runner.py` — add `YOUTUBE` to both guard sets.
- `tests/test_source_model.py`, `tests/test_collectors_youtube.py` (new), `tests/test_collectors_runner.py`, `tests/test_workflows.py`.

## Key contracts

`YouTubeSourceSettings` (after TwitterSourceSettings):
```python
class YouTubeSourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ytdlp_path: str | None = None
    max_videos_per_run: int = Field(default=20, gt=0, le=200)
    search_prefix: str = "ytsearch"
```

Validator branch (after TWITTER):
```python
        if self.type == SourceType.YOUTUBE and not self.query:
            raise ValueError("youtube source requires query")
```

No-op stub `YouTubeCollector.collect` returns `CollectorResult.success(source, items=[], started_at=started_at)`.

## Tasks (summary)

- **Task 0 (plan review):** Claude Code; opencode revises. `docs/reviews/claude-code-stage-251-plan-review.md`.
- **Task 1 (plumbing, RED→GREEN):** model + stub + registration + guard + tests.
- **Task 2 (focused + Claude Code code review + full gate + commit):** "Stage 251: add YouTube source plumbing".

## Verification

Focused: `tests/test_source_model.py tests/test_collectors_youtube.py tests/test_collectors_runner.py tests/test_workflows.py tests/test_config.py`. Full gate. `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Mechanical mirror of Stage 241; low risk.
- Plumbing only; no live yt-dlp.
- No schema/dep change.
