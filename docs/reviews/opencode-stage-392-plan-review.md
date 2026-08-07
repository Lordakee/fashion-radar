# Stage 392 Plan Review - OpenCode Fallback

## Review Context

- Reviewer: local OpenCode fallback
- Model: `zhipuai-coding-plan/glm-5.2`
- Variant: `max`
- Scope: Stage 392 ROW ONE daily content acceptance gate
- Repository snapshot: `main` at `20a41a6`

Claude Code was invoked first in required read-only plan mode with `--effort
max` and no session persistence. It did not produce completed review output
within the bounded timeout. This record contains the completed fallback review,
not a substitute Claude Code approval.

## Findings

### Critical

1. Existing happy-path CLI tests require an explicit harness update. The shared
   refresh helper currently returns `None` from `collect_configured_sources` and
   asserts a fixed downstream call order. The implementation must change that
   helper to return a synthetic successful `CollectorResult` containing a fresh
   item, and insert the acceptance call at the correct point in the expected
   order. Otherwise unrelated existing refresh tests will fail before the new
   behavior is meaningfully tested.

### Important

1. Thresholds belong in a dedicated top-level `daily_content_acceptance` field
   on `ScoringConfig`, not inside `ScoringSettings`. This preserves the scoring
   formula boundary and allows the existing `version: 1` configuration to remain
   backward compatible through defaults.

2. `CollectedItem.published_at` is always present. Some collectors synthesize a
   date at collection time when an upstream item has no date, so the design must
   not claim to reject null dates. Freshness must be defined as
   `0 <= as_of - published_at <= max_fresh_item_age_hours`, and the synthesized
   date limitation must be documented.

3. Collection writes occur before the gate. A rejected refresh may retain
   collector run metadata and collected items; this stage must clearly state
   that it preserves the site, report artifacts, report pruning, and SQLite
   retention boundary rather than claiming a fully rolled-back invocation.

4. Documentation tests use explicit phrases and must be updated in lockstep
   with the CLI flag, rejection exit code, preserved-output guarantee, and
   schedule behavior.

5. Gate rejection must be distinct from an unexpected exception. It should emit
   a stable `ROW ONE refresh rejected:` diagnostic and exit 1, so cron/systemd
   accurately surface content rejection.

### Minor

1. Place the gate immediately after collection to avoid matching work when a
   run cannot publish. This is an optional improvement that is adopted by the
   revised design.

2. Count only `CollectorRunStatus.SUCCESS` toward successful collectors;
   `FAILED` and `SKIPPED` results do not count.

3. The one-shot bypass must log a clear warning and must not be represented as
   an environment-level or persisted configuration disablement.

4. The evaluator must accept an injected `as_of` and settings only. It must not
   call the clock, filesystems, SQLite, or network services.

## Verdict

**APPROVED WITH REVISIONS.** The revised design and plan incorporate the
Critical and Important findings above. Implementation may proceed only after
the settings and evaluator interfaces are integrated, focused tests are green,
and the post-implementation code/release review gate is complete.
