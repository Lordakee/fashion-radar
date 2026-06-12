# Claude Code Stage 10 Plan Rereview Prompt

You are rereviewing the Stage 10 plan for Fashion Radar after fixes to the
first Stage 10 plan review. Run this as a read-only planning review. Do not
edit files, do not commit, do not call the network, do not run collectors, and
do not execute platform/social tooling.

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-10-plan-rereview-prompt.md
```

## Goal

Stage 10 should add local trend delta analysis so users can see which locally
observed fashion signals are new in the current comparison snapshot, rising,
cooling, stable, or dropped between two local scoring snapshots.

This stage must not add platform collection. It must use only local SQLite data
and existing deterministic scoring/candidate discovery.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-10-trend-delta-design.md`
- `docs/superpowers/plans/2026-06-12-stage-10-trend-delta-plan.md`

Also consider the previous review:

- `docs/reviews/claude-code-stage-10-plan-review.md`

## Proposed Architecture

- Reuse existing `score_entities()` and `discover_candidates()`.
- Add trend Pydantic output models.
- Add a comparator that compares current and baseline snapshots.
- Add `fashion-radar trends` as a read-only CLI command.
- Add a dashboard trend tab.
- Keep missing DB and invalid input paths from creating `data_dir`.
- Open existing SQLite databases in read-only mode.
- Avoid schema migrations and avoid persistent trend storage.
- Keep status labels conservative: mixed-direction score/mention movement should
  be `stable`, not rising or cooling.

## Tech Stack

- Python 3.11+
- Typer with plain table-style `typer.echo` output
- Pydantic
- SQLAlchemy read-only SQLite URI connections
- Streamlit optional dashboard
- pytest
- ruff
- uv

## Explicit Out Of Scope

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

## Rereview Questions

Please focus on whether the plan now resolves the previous review findings:

1. Invalid config/config-path regressions must be tested before DB opening.
2. CLI and dashboard must reject incompatible existing databases read-only.
3. Dashboard trend query must verify schema before reading and avoid schema
   initialization or migrations.
4. Stage 10 must forbid migrations, persistent trend tables, writable indexes,
   and DB writes.
5. Dashboard config loading and `--config-dir` plumbing must be specified.
6. Mixed-direction movement must be deterministic and not misleading.
7. Integration tests must prove `build_trend_comparison()` composes
   `score_entities()` and `discover_candidates()`.
8. CLI option plumbing for `--include-dropped`, `--limit`, default baseline, and
   missing-DB JSON output must be covered.
9. Runtime no-external-services scope must be clear.
10. Dashboard visible copy and docs must avoid market-wide or platform-wide
    claims.

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
