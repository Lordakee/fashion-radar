# Claude Code Stage 17 Plan Review Prompt

You are reviewing the Stage 17 plan for Fashion Radar. Run this as a read-only
planning review. Do not edit files, do not commit, do not call the network, do
not run collectors, do not create directories, do not open SQLite, and do not
execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-17-plan-review-prompt.md
```

## Goal

Stage 17 should add a local, read-only directory-level community signal
diagnostics command:

```bash
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv"
fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json"
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --format json
fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json" --strict
```

The command should help external tools controlled by the user write multiple
sanitized local handoff files into a local directory and preflight them before
any single-file `import-signals --dry-run` or import step.

This is not a product-facing compliance review, audit workflow, safety workflow,
policy checklist, approval UI, authorization verifier, platform connector,
scraper, crawler, browser automation flow, social monitoring system, source
acquisition tool, multi-file import, multi-file dry-run, watch folder, or
current-hotness ranking.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-17-community-signal-directory-lint-design.md`
- `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`

## Proposed Architecture

- Extend `src/fashion_radar/community_signals.py` with a
  `CommunitySignalDirectoryLintResult`.
- Enumerate regular files directly under one local directory with
  `directory.iterdir()` and `fnmatch.fnmatch(path.name, pattern)` using a
  required non-recursive `--pattern`.
- Reuse the existing `lint_community_signal_file()` for every matched file.
- Aggregate file count, row count, valid row count, severity counts,
  field/source/platform counts, and per-file results.
- Add `fashion-radar community-signal-lint-dir DIRECTORY --input-format csv|json --pattern PATTERN --format table|json --source-name TEXT --strict`.
- Add focused module tests, CLI tests, and docs.
- Do not change import storage behavior, entity matching, scoring, collectors,
  reports, dashboard, DB schema, dependencies, lockfile, or existing
  `import-signals` behavior.

## Explicit Out Of Scope

The plan must not add or document:

- social/platform connectors, platform search, remote community ingestion, or
  automated social collection;
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or source-acquisition
  workflows;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- official or unofficial social platform APIs;
- instructions for obtaining platform/community exports;
- raw comments, full post bodies, private messages, author handles, account IDs,
  follower lists, profile URLs, images, videos, media downloading, reposting, or
  archive redistribution;
- recursive scanning, watch folders, background jobs, schedulers, multi-file
  import, or multi-file dry-run;
- current hotness claims, platform-wide claims, social-wide claims,
  community-wide claims, market-wide trend proof, verified demand outside
  configured local signals, real-time monitoring, or top social trend rankings;
- Google News RSS or any new source type;
- paid API requirements, LLM scoring, embeddings, vector databases, image
  recognition, sentiment analysis, or internet lookups;
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, matcher behavior changes, persistent adapter tables,
  or scoring algorithm changes;
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, authorization verification, policy checklist, or legal review feature.

## Review Questions

Please focus on:

1. Whether directory batch lint is the right next local-only step after
   single-file community signal lint.
2. Whether the module boundary should reuse `lint_community_signal_file()` and
   avoid reimplementing row validation.
3. Whether direct-child `directory.iterdir()` plus
   `fnmatch.fnmatch(path.name, pattern)` and regular-file filtering is a clear
   and safe Stage 17 directory behavior.
4. Whether no-match and invalid-directory should be errors.
5. Whether the proposed JSON/table output shapes are deterministic and useful.
6. Whether tests prove read-only/no-artifact behavior and strict exit behavior.
7. Whether docs avoid platform/source acquisition instructions, platform claims,
   and policy/compliance/audit product features.
8. Whether verification is sufficient before GitHub upload.

## Response Format

Start with one of:

- `Approved for Stage 17 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
