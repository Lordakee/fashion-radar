# Stage 80 External Tool Import Onboarding Design

## Goal

Make the external/community tool import path easier to understand for users who
already have exports from tools such as Rednote/Xiaohongshu tools, Instaloader,
TikTok-Api, yt-dlp metadata exports, X search exports, or generic community
tools.

## Context

Fashion Radar already exposes the local handoff primitives:

- `external-tool-adapters`
- `external-tool-readiness`
- `external-tool-template`
- `external-tool-workflow`
- `community-signal-profile`
- `community-handoff-manifest`
- `community-signal-lint-dir`
- `community-candidates-dir`
- `community-handoff-check-dir`
- `import-signals-dir`
- post-import review commands such as `imported-signals`, `candidates`,
  `trends`, and `imported-review-workflow`

The remaining onboarding gap is sequence clarity. A new user can see many
commands but may not know the safe path from a user-controlled external export
directory to local Fashion Radar review output.

## Scope

In scope:

- Add a compact external-tool import path to `README.md`.
- Add a short `## External Tool Import Roadmap` section to
  `docs/community-signal-import.md`.
- Add a compact row or note in `docs/cli-reference.md` that points users from
  external tool discovery/readiness to local directory lint/import/review.
- Add focused docs drift tests in `tests/test_cli_docs.py`.
- Add a changelog entry and stage-local opencode review artifacts.

Out of scope:

- Runtime CLI behavior changes.
- New commands, command flags, adapters, collectors, source packs, entity packs,
  scheduling behavior, dashboard behavior, or package metadata changes.
- Installing or running upstream tools.
- Scraping, browser automation, platform APIs, login/session/cookie/token/proxy
  behavior, media downloads, monitoring, scheduling, source acquisition, demand
  proof, ranking, platform coverage verification, or compliance-review product
  features.
- Dependency or public lockfile changes. The local dirty `uv.lock` mirror
  rewrite remains out of stage and must not be staged.

## Design

### README

Add a small paragraph or bullet group near the existing external tool handoff
description that gives the end-to-end orientation:

1. inspect adapter shape;
2. check local command readiness;
3. print template/workflow/profile/manifest guidance;
4. lint and preview a user-controlled export directory;
5. dry-run and import local rows;
6. review imported rows, candidates, trends, and heat movement locally.

The wording must make clear that Fashion Radar does not search or scrape these
platforms; the upstream export is produced outside Fashion Radar by a
user-controlled tool.

### Community Signal Import Doc

Add `## External Tool Import Roadmap` before `## External Tool Handoff
Templates`. The roadmap should be a compact table with phases:

- Discover
- Prepare
- Validate
- Import
- Review

Each phase should list only existing commands and point to existing local file
handoff concepts. The section should include exact boundary language:

- `user-controlled external export directory`
- `sanitized CSV/JSON local file handoff`
- `does not run upstream tools`
- `does not search platforms`
- `does not scrape`
- `does not call platform APIs`
- `does not add connectors`
- `does not prove demand`
- `does not rank brands`
- `does not verify platform coverage`

### CLI Reference

Add one compact orientation paragraph under `## Local Import And Community
Handoff` before the command list. It should say that external tool import uses
existing local commands only and follows:

`external-tool-adapters -> external-tool-readiness -> external-tool-workflow ->
community-signal-lint-dir -> community-candidates-dir ->
community-handoff-check-dir -> import-signals-dir -> imported-review-workflow`

Keep this as guidance only; no command surface changes.

### Tests

Add docs drift tests in `tests/test_cli_docs.py` that pin:

- the new community-signal import roadmap section and its phase/command terms;
- the CLI reference orientation sequence;
- the README external import path summary and boundary language.

Tests should use normalized text checks and section splits that avoid matching
inline literal `## ...` heading strings. Do not introduce doc text that poisons
existing `_markdown_section` helpers.

## Acceptance Criteria

- Users can find the local external-tool import sequence from README,
  `docs/community-signal-import.md`, and `docs/cli-reference.md`.
- The sequence uses only existing commands.
- Docs clarify that external/community tools are user-controlled producers of
  local CSV/JSON handoff files.
- Docs do not imply Fashion Radar searches, scrapes, logs in, monitors,
  schedules, calls platform APIs, ranks demand, or verifies platform coverage.
- Docs drift tests pin the route and boundary language.
- No `src/`, dependency manifest, public `uv.lock`, `AGENTS.md`,
  `docs/REVIEW_PROTOCOL.md`, or `docs/github-upload-checklist.md` changes are
  required.
