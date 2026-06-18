# Stage 79 Onboarding Roadmap Design

## Goal

Make the GitHub first-time user path easier to choose without changing any
runtime behavior.

## Context

The project already has strong local-only boundary language and deterministic
first-run examples. The remaining onboarding gap is orientation: a new reader
must scan a long README and several detailed docs before understanding which
path to run first, when to use the manual sample, when to use smoke scripts, and
where entity packs fit.

Stage 79 should improve that orientation with docs and docs drift tests only.

## Scope

In scope:

- Add a compact `Start Here` section near the top of `README.md`.
- Add a compact chooser table to `docs/first-run.md`.
- Add a beginner roadmap to `docs/cli-reference.md`.
- Clarify that `docs/entity-packs.md` describes an optional local matching
  layer to copy after `init` and before `match`/`report`.
- Add focused docs drift tests in `tests/test_cli_docs.py`.
- Add a changelog entry and stage-local opencode review artifacts.

Out of scope:

- Runtime CLI behavior changes.
- New commands or command flags.
- Any source collection expansion.
- Scraping, browser automation, platform APIs, login/session/cookie/token/proxy
  behavior, media downloads, monitoring, scheduling, source acquisition, demand
  proof, ranking, platform coverage verification, or compliance-review product
  features.
- Dependency or public lockfile changes. The local dirty `uv.lock` mirror
  rewrite remains out of stage and must not be staged.
- Changes to authoritative review protocol docs: `AGENTS.md`,
  `docs/REVIEW_PROTOCOL.md`, and `docs/github-upload-checklist.md`.

Stage 79 uses stage-local opencode review artifacts per the latest user
instruction. That stage-local review choice must stay in this stage's planning
and review files only; it must not alter the authoritative protocol docs listed
above.

## Design

### README

Add `## Start Here` after the intro and before `## What It Does`. The section
should say:

- use `docs/first-run.md` first;
- the recommended first-time path is the manual repo-local sample when the user
  wants inspectable output and dashboard data;
- automated source-checkout smoke and installed-wheel smoke are verification
  paths, not the main exploratory path;
- entity packs are optional and can be copied after `init` before `match` and
  `report`;
- all onboarding paths are local-first, do not add live platform collection,
  and do not add social connectors.

Keep the section short so the existing detailed README content remains the
source of full command examples.

### First-Run Guide

Under `## Choose Your First Run`, add a Markdown table with four choices:

1. `Manual repo-local sample`
2. `Automated source-checkout smoke`
3. `Installed-wheel smoke`
4. `Reset repo-local sample`

The table should distinguish who the path is for, where it writes, and the
primary command or section. It must clearly label the manual repo-local sample
as the recommended first-time path for inspectable output.

The first-run chooser prose must include the exact normalized phrases the docs
drift tests will pin:

- `manual repo-local sample when you want inspectable output`
- `automated source-checkout smoke when you want disposable verification`
- `installed-wheel smoke when you need package verification`
- `reset repo-local sample after local experiments`
- `temporary config/data/report/export directories`

The reset row must use the literal `Reset The Repo-Local Sample` section label.

### CLI Reference

Add `## Beginner Roadmap` before `## Shared Path Options`. The roadmap should
group existing commands into these phases:

- Setup
- Local sample/import
- Match/report/review
- Dashboard
- Cleanup

It should point to `first-run.md` and `entity-packs.md` rather than duplicating
the full command walkthrough. The boundary sentence must use the repetitive
forms `does not add platform automation` and `does not add connectors` so the
normalized docs test checks the intended phrases directly.

### Entity Packs

Clarify near the top that entity packs are optional local templates copied after
`init` and before first `match`/`report` if a user wants a broader watchlist.
Keep the boundary language explicit: packs only change local matching and do
not add sources, ingestion, scraping, live collection, ranking, demand proof, or
platform coverage.

## Acceptance Criteria

- README has a short `Start Here` section before `What It Does`.
- First-run docs have a four-row chooser table under `Choose Your First Run`.
- CLI reference has a beginner roadmap using only existing command names and
  existing docs links.
- Entity-pack docs explain the optional local matching-layer sequence.
- Docs drift tests pin the new sections, exact first-run choice phrases, and key
  boundary language.
- No `src/`, dependency manifest, public `uv.lock`, `AGENTS.md`,
  `docs/REVIEW_PROTOCOL.md`, or `docs/github-upload-checklist.md` changes are
  required.
