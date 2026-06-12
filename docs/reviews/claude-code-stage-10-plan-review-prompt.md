# Claude Code Stage 10 Plan Review Prompt

You are reviewing the Stage 10 plan for Fashion Radar. Run this as a read-only
planning review. Do not edit files, do not commit, do not call the network, do
not run collectors, and do not execute platform/social tooling.

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-10-plan-review-prompt.md
```

## Goal

Stage 10 should add local trend delta analysis so users can see which locally
observed fashion signals are new, rising, cooling, stable, or dropped between
two scoring snapshots.

This stage must not add platform collection. It must use only local SQLite data
and existing deterministic scoring/candidate discovery.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-10-trend-delta-design.md`
- `docs/superpowers/plans/2026-06-12-stage-10-trend-delta-plan.md`

## Proposed Architecture

- Reuse existing `score_entities()` and `discover_candidates()`.
- Add trend Pydantic output models.
- Add a comparator that compares current and baseline snapshots.
- Add `fashion-radar trends` as a read-only CLI command.
- Add a dashboard trend tab.
- Keep missing DB and invalid input paths from creating `data_dir`.
- Open existing SQLite databases in read-only mode.
- Pass `--config-dir` through the dashboard launcher and load dashboard scoring
  config explicitly.
- Reject `baseline_as_of >= as_of` before database access.
- Compare trend `baseline_mentions` against the baseline snapshot's
  current-window mentions, not internal scoring baseline-window mentions.
- Apply CLI/dashboard display limits after comparison, not before candidate
  discovery snapshots.
- Use the existing `normalize_alias_key()` behavior for trend comparison keys.
- Avoid schema migrations and avoid new runtime external services.

## Tech Stack

- Python 3.11+
- Typer
- Pydantic
- SQLAlchemy read-only SQLite URI connections
- Plain Typer table-style output with `typer.echo`
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

## Review Questions

Please focus on:

1. Whether the plan genuinely satisfies the user's need to see local heat
   changes and newly rising brands/products/candidate phrases.
2. Whether the read-only CLI/data flow is technically sound and avoids creating
   databases on missing/invalid input paths.
3. Whether reusing `score_entities()` and `discover_candidates()` is the right
   approach instead of inventing a second heat algorithm.
4. Whether the trend model fields and status rules are sufficient and not
   misleading.
5. Whether dashboard config plumbing is complete and deterministic.
6. Whether schema guards cover all tables needed by entity scoring and candidate
   discovery.
7. Whether candidate discovery and display limits are separated correctly.
8. Whether `baseline_mentions` and `baseline_as_of` semantics are unambiguous.
9. Whether the tests are enough to catch safety, correctness, and read-only
   regressions.
10. Whether any wording risks implying platform-wide or market-wide trend proof.

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
