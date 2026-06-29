# Stage 215 RSSHub Self-Host Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document how a user self-hosts RSSHub (Docker) and configures Fashion Radar `rsshub` sources against it, broadening news/official-site coverage without adding fragile curated feeds to the composition-pinned public source pack.

**Architecture:** Docs-only stage. Fashion Radar already supports `SourceType.RSSHUB` (collected by `RssCollector`). RSSHub is a mature, MIT-licensed, community-maintained feed generator that turns sites/platforms without native feeds into RSS. This stage adds a self-host guide (Docker run, configuring a Fashion Radar `rsshub` source pointing at the local RSSHub instance, boundary caveats) to `docs/source-packs.md`, a docs-guard test, and a CHANGELOG entry. No source code, no source-pack data change (the public pack composition is pinned at 20 by `tests/test_source_packs.py:35`; curated-feed additions are a separate, live-validation-gated follow-up), no schema/dependency change.

**Tech Stack:** Markdown docs, Python docs-guard test, `uv --no-config run --frozen pytest`, Claude Code + opencode (`glm-5.2 --variant max`) review.

## Scope

**In scope:**
- `docs/source-packs.md`: new "## Self-Hosted RSSHub" section (Docker one-liner, configuring a `type: rsshub` source with `url:` pointing at the local RSSHub route, robots/attribution/boundary caveats, no demand proof / no platform coverage verification).
- `tests/test_source_packs_docs.py` (or an existing docs-guard file): a test pinning the RSSHub self-host wording.
- `CHANGELOG.md`: `### Added` entry.
- Cross-link from `README.md` Configuration section to the new guide (one line).

**Out of scope:** adding feeds to `configs/source-packs/fashion-public.example.yaml` (composition-pinned + needs live validation — separate follow-up), any source code, any dependency/lockfile/schema change, any change to RSSHUB collection behavior.

## File Map

- Modify `docs/source-packs.md` — add `## Self-Hosted RSSHub` section.
- Modify `README.md` — one-line pointer in Configuration.
- Add/modify a docs-guard test (e.g., `tests/test_source_packs_docs.py` if present, else `tests/test_cli_docs.py` or a new pin in an existing docs-guard).
- Modify `CHANGELOG.md`.

## Key content contracts

The new `## Self-Hosted RSSHub` section in `docs/source-packs.md` must contain (pinned by the docs-guard, whitespace-normalized, case-insensitive):
- "Self-Hosted RSSHub"
- "docker run" (the Docker one-liner)
- "type: rsshub" (the Fashion Radar source type)
- "no demand proof and no platform coverage verification" (the standard boundary caveat)
- "robots" (attribution/robots caveat)

Suggested section body (adapt; keep contract phrases):
```markdown
## Self-Hosted RSSHub

RSSHub is a mature, MIT-licensed, community-maintained feed generator that turns
sites and platforms without native feeds into RSS/Atom. Self-hosting it lets you
broaden Fashion Radar coverage of official sites and news without fragile
per-site scraping. Fashion Radar already supports `type: rsshub` sources
(collected by the same RSS collector).

Run a local RSSHub instance with Docker:

    docker run -d --name rsshub -p 1200:1200 diygod/rsshub

Then add a Fashion Radar source pointing at a local RSSHub route:

    - name: "Example Site via RSSHub"
      type: rsshub
      url: "http://localhost:1200/example/site"

Users are responsible for respecting each upstream site's terms and robots
rules. RSSHub routes are community-maintained and may break when upstream sites
change. RSSHub-sourced signals are local observed signals only; they provide no
demand proof and no platform coverage verification.
```

## Tasks (summary)

- **Task 0 (plan review):** Claude Code reviews this plan; opencode revises. Record `docs/reviews/claude-code-stage-215-plan-review.md`.
- **Task 1 (docs, RED → GREEN):** add the docs-guard test first (RED — the docs do not yet contain the phrases), then add the `## Self-Hosted RSSHub` section + README pointer (GREEN), run the guard.
- **Task 2 (changelog + focused + Claude Code review + release verification + commit):** CHANGELOG `### Added`; focused docs-guard pytest; ruff; full gate; `claude --effort max ...` review; commit "Stage 215: document self-hosted RSSHub for broader source coverage"; push.

## Verification

Docs-guard green; full release gate (pytest, ruff, hygiene, lock, sync, smoke, git diff) green; `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Docs-only; zero risk to code/schema/deps/composition.
- Directly serves the "scrape various official sites and news" goal via the mature RSSHub ecosystem (no new fragile scraper code).
- Boundary caveats preserved (robots, no demand proof, no platform coverage verification).
- Curated-feed additions to the pinned public pack are explicitly deferred (need live validation).
