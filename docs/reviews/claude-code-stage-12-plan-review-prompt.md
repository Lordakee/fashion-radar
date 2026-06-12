# Claude Code Stage 12 Plan Review Prompt

You are reviewing the Stage 12 plan for Fashion Radar. Run this as a read-only
planning review. Do not edit files, do not commit, do not call the network, do
not run collectors, do not create directories, do not open SQLite, and do not
execute platform/social tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-12-plan-review-prompt.md
```

## Goal

Stage 12 should improve daily fashion information quality by adding local
source-pack diagnostics and expanding the public RSS/GDELT starter pack with
bounded GDELT coverage lanes. The feature should help users catch weak local
source-pack configuration before collection.

This is not a product-facing compliance review, audit workflow, safety
workflow, or approval UI.

## Plan And Design To Review

Please review:

- `docs/superpowers/specs/2026-06-12-stage-12-source-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-12-source-pack-quality-plan.md`

## Proposed Architecture

- Keep `settings.py` and `load_source_config()` as strict schema validation.
- Add `src/fashion_radar/source_packs.py` as a pure local lint/diagnostics
  module.
- Read raw YAML first so omitted fields such as `weight` can be diagnosed.
- Validate with `load_source_config()` before typed lint checks.
- Return structured findings with severity, code, message, optional
  source_name, and optional field.
- Add one flat Typer command:

```bash
fashion-radar source-pack-lint PATH
fashion-radar source-pack-lint PATH --format json
fashion-radar source-pack-lint PATH --strict
```

- Default exit behavior:
  - non-zero on structural config errors and lint errors;
  - warnings print but do not fail unless `--strict` is set.
- Expand `configs/source-packs/fashion-public.example.yaml` with bounded GDELT
  lanes for runway, designer-brand momentum, retail/resale, shoes/footwear,
  accessories/handbags, creative-director moves, and beauty/fashion crossover.
- Keep existing RSS entries and public-pack RSS article extraction disabled.
- Add docs for source-pack quality tuning and command usage.

## Tech Stack

- Python 3.11+
- Pydantic `BaseModel`
- `enum.StrEnum`
- pathlib
- PyYAML
- Typer
- pytest
- ruff
- uv

## Explicit Out Of Scope

The plan must not add or document:

- Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Reddit, Pinterest, or
  other platform connectors
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or platform search
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxies, proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining platform exports from social platforms
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, images, videos, media downloading, or reposting
- Google News RSS or any new source type
- complete source coverage, platform-wide coverage, market-wide trend proof,
  verified demand outside the configured source set, real-time social
  monitoring, or top social trends
- LLM scoring, embeddings, vector databases, image recognition, or paid service
  requirements
- DB migrations, source-health schema changes, collector changes, dashboard
  changes, report semantics changes, or network calls
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, or policy checklist

## Review Questions

Please focus on:

1. Whether Stage 12 improves source quality without adding risky collection,
   network fetches, or social/platform extraction behavior.
2. Whether `source_packs.py` is the right module boundary instead of expanding
   `settings.py`.
3. Whether reading raw YAML before `load_source_config()` is justified for
   missing-field diagnostics.
4. Whether the planned lint rules are useful and not overreaching.
5. Whether duplicate source names should be errors because source health and
   run logs are source-keyed.
6. Whether duplicate targets/queries as warnings and missing tags as warnings
   are appropriate.
7. Whether `source-pack-lint` should stay flat rather than introducing a new
   nested Typer group.
8. Whether the command is read-only and cannot create data/report/config
   directories or SQLite files.
9. Whether public pack expansion through bounded GDELT lanes is reasonable and
   avoids unverified live RSS additions.
10. Whether tests and docs cover the behavior and boundaries well enough for
    GitHub upload.

## Response Format

Start with one of:

- `Approved for Stage 12 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
