# Stage 231 Instagram Source Plumbing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `SourceType.INSTAGRAM` + `InstagramSourceSettings` + a no-op `InstagramCollector` stub + default registration + runner dual enrichment-skip guard — plumbing only, no live instaloader calls (those land in Stage 232).

**Architecture:** Mirrors Stage 212 (HTML/SITEMAP plumbing) and Stage 222 Task 1 (XIAOHONGSHU plumbing). New enum member + Pydantic settings sub-model + validator branch + no-op collector + registration + runner guards. No DB schema change, no dependency change.

**Tech Stack:** Python 3.11, Pydantic v2, pytest, `uv --no-config run --frozen`, Claude Code + opencode review.

## Scope

**In:** `SourceType.INSTAGRAM`; `InstagramSourceSettings` (instaloader_path, login_user, max_posts_per_run, target_type); `SourceDefinition.instagram`; `validate_source_target` branch (requires query); `src/fashion_radar/collectors/instagram.py` no-op stub; registration in `_default_collectors()`; runner line-73 + line-97 guards extended to include `INSTAGRAM`; tests.

**Out:** real instaloader subprocess/parse (Stage 232); docs (Stage 233); schema/dep changes.

## File Map

- `src/fashion_radar/models/source.py` — SourceType member, InstagramSourceSettings, SourceDefinition field, validator branch.
- `src/fashion_radar/collectors/instagram.py` (new) — no-op stub.
- `src/fashion_radar/workflows.py` — import + registration.
- `src/fashion_radar/collectors/runner.py` — add `INSTAGRAM` to both guard sets.
- `tests/test_source_model.py`, `tests/test_collectors_instagram.py` (new), `tests/test_collectors_runner.py`, `tests/test_workflows.py`.

## Key contracts

`InstagramSourceSettings` (after XiaohongshuSourceSettings):
```python
class InstagramSourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    instaloader_path: str | None = None
    login_user: str | None = None
    max_posts_per_run: int = Field(default=20, gt=0, le=200)
    target_type: Literal["hashtag", "profile"] = "hashtag"
```
(`Literal` already imported in source.py.)

Validator branch (after the XIAOHONGSHU branch):
```python
        if self.type == SourceType.INSTAGRAM and not self.query:
            raise ValueError("instagram source requires query")
```

No-op stub `InstagramCollector.collect` returns `CollectorResult.success(source, items=[], started_at=started_at)`.

## Tasks (summary)

- **Task 0 (plan review):** Claude Code; opencode revises. `docs/reviews/claude-code-stage-231-plan-review.md`.
- **Task 1 (plumbing, RED→GREEN):** all model + stub + registration + guard + tests.
- **Task 2 (focused + Claude Code code review + full gate + commit):** "Stage 231: add Instagram source plumbing".

## Verification

Focused: `tests/test_source_model.py tests/test_collectors_instagram.py tests/test_collectors_runner.py tests/test_workflows.py tests/test_config.py`. Full gate. `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Mechanical mirror of 212/222-Task-1; low risk.
- Plumbing only (no live instaloader); fail-closed/registration pattern consistent.
- No schema/dep change.
