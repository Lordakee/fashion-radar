# Stage 241 Twitter Source Plumbing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** Add `SourceType.TWITTER` + `TwitterSourceSettings` + a no-op `TwitterCollector` stub + default registration + runner dual enrichment-skip guard — plumbing only (no live twitter-cli calls; those land in Stage 242). Mirrors Stage 231 (Instagram plumbing).

**Architecture:** New enum member + Pydantic settings sub-model + validator branch + no-op collector + registration + runner guards. No DB schema change, no dependency change.

**Tech Stack:** Python 3.11, Pydantic v2, pytest, `uv --no-config run --frozen`, Claude Code + opencode review.

## Scope

**In:** `SourceType.TWITTER`; `TwitterSourceSettings` (twitter_cli_path, max_tweets_per_run, output_format); `SourceDefinition.twitter`; `validate_source_target` branch (requires query); `src/fashion_radar/collectors/twitter.py` no-op stub; registration in `_default_collectors()`; runner line-73 + line-97 guards extended to `TWITTER`; tests.

**Out:** real twitter-cli subprocess/parse (Stage 242); docs (Stage 243); schema/dep changes.

## File Map

- `src/fashion_radar/models/source.py` — SourceType member, TwitterSourceSettings, SourceDefinition field, validator branch.
- `src/fashion_radar/collectors/twitter.py` (new) — no-op stub.
- `src/fashion_radar/workflows.py` — import + registration.
- `src/fashion_radar/collectors/runner.py` — add `TWITTER` to both guard sets.
- `tests/test_source_model.py`, `tests/test_collectors_twitter.py` (new), `tests/test_collectors_runner.py`, `tests/test_workflows.py`.

## Key contracts

`TwitterSourceSettings` (after InstagramSourceSettings):
```python
class TwitterSourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    twitter_cli_path: str | None = None
    max_tweets_per_run: int = Field(default=20, gt=0, le=200)
    output_format: Literal["json", "text"] = "json"
```
(`Literal` already imported.)

Validator branch (after INSTAGRAM):
```python
        if self.type == SourceType.TWITTER and not self.query:
            raise ValueError("twitter source requires query")
```

No-op stub `TwitterCollector.collect` returns `CollectorResult.success(source, items=[], started_at=started_at)`.

## Tasks (summary)

- **Task 0 (plan review):** Claude Code; opencode revises. `docs/reviews/claude-code-stage-241-plan-review.md`.
- **Task 1 (plumbing, RED→GREEN):** model + stub + registration + guard + tests.
- **Task 2 (focused + Claude Code code review + full gate + commit):** "Stage 241: add Twitter source plumbing".

## Verification

Focused: `tests/test_source_model.py tests/test_collectors_twitter.py tests/test_collectors_runner.py tests/test_workflows.py tests/test_config.py`. Full gate. `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Mechanical mirror of Stage 231; low risk.
- Plumbing only; no live twitter-cli.
- No schema/dep change.
