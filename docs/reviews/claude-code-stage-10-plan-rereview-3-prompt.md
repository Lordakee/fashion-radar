# Claude Code Stage 10 Plan Rereview 3 Prompt

You are rereviewing the Stage 10 plan for Fashion Radar after fixes to prior
Stage 10 plan reviews. Run this as a read-only planning review. Do not edit
files, do not commit, do not call the network, do not run collectors, and do
not execute platform/social tooling.

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-10-plan-rereview-3-prompt.md
```

## Goal

Approve or reject the Stage 10 plan for local, read-only trend delta analysis.
Stage 10 should show local observed entities and candidate phrases that are new
in the current comparison snapshot, rising, cooling, stable, or dropped between
two local scoring snapshots.

## Files To Review

- `docs/superpowers/specs/2026-06-12-stage-10-trend-delta-design.md`
- `docs/superpowers/plans/2026-06-12-stage-10-trend-delta-plan.md`
- `docs/reviews/claude-code-stage-10-plan-review.md`
- `docs/reviews/claude-code-stage-10-plan-rereview.md`
- `docs/reviews/claude-code-stage-10-plan-rereview-2.md`

## Prior Blocking Findings To Verify

Please verify these are now resolved:

1. Dashboard config plumbing is explicit: `fashion-radar dashboard` passes
   `--config-dir`, dashboard parses it, loads scoring config and optional entity
   config, and handles missing/invalid config without creating `data_dir`.
2. Read-only schema guard requires all tables used by entity scoring and
   candidate discovery, especially `entity_first_seen`, before trend reads.
3. `TrendDelta.baseline_mentions` means baseline snapshot current-window
   mentions; internal scoring baseline-window counts use explicit
   `current_internal_baseline_mentions` and
   `baseline_internal_baseline_mentions`.
4. Candidate discovery uses configured candidate settings; CLI/dashboard display
   `limit` is applied after comparison and sorting, not before snapshot
   discovery.
5. `--as-of` remains explicit and examples/smoke tests provide it.
6. `baseline_as_of >= as_of` is rejected before database access.
7. Missing database JSON output is a full `TrendComparison` with metadata and
   `deltas == []`, not a bare list.
8. Existing databases are opened read-only and no trend migrations, persistent
   trend tables, writable indexes, or database writes are planned.
9. Mixed-direction score/mention movement is conservative and deterministic:
   `score_delta > 0` with `mention_delta < 0` is `stable`, and
   `score_delta < 0` with `mention_delta > 0` is `stable`.
10. Comparison keys use `normalize_alias_key()`.
11. Dashboard default `as_of` uses latest local `items.collected_at` when items
    exist and current UTC only for an existing empty database.
12. Tests cover CLI option plumbing, default baseline, include-dropped,
    post-comparison limit, invalid config/date no-directory-creation,
    incompatible DB read-only rejection, dashboard config plumbing, dashboard
    missing DB no-directory-creation, and local-only visible copy.

## Scope Boundary

The plan must not add or document:

- platform search or automated social collection
- crawlers, scrapers, browser automation, Playwright, Selenium, MCP platform
  scraping servers, or account automation
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining exports from Instagram, TikTok, X/Twitter,
  Xiaohongshu, or similar platforms
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile internals, images, videos, media downloading, or reposting
- claims of complete social listening, complete platform coverage, verified
  demand, market-wide trend proof, or real-time social monitoring
- LLM scoring, embeddings, vector databases, image recognition, or paid service
  requirements

## Response Format

Start with one of:

- `Approved for Stage 10 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
