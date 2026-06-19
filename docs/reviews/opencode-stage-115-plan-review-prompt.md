# Stage 115 Plan Review Prompt

You are reviewing a Fashion Radar implementation plan before code changes.
Use the local repository at `/home/ubuntu/fashion-radar`.

Review target:

- Design: `docs/superpowers/specs/2026-06-19-stage-115-xpoz-adapter-metadata-design.md`
- Plan: `docs/superpowers/plans/2026-06-19-stage-115-xpoz-adapter-metadata-plan.md`

Goal:

Add a new `xpoz_mcp` external-tool adapter metadata target for sanitized XPOZ
MCP / XPOZ Social Data API exports. This should help future social/community
signals from Instagram, TikTok, X/Twitter, Reddit, and related exports enter the
existing local CSV/JSON community signal handoff path.

Technical approach:

- Python 3.11 / Pydantic / Typer CLI / pytest / ruff / uv.
- Add runtime metadata in `src/fashion_radar/external_tool_adapters.py`.
- Add read-only readiness mapping in `src/fashion_radar/external_tool_readiness.py`.
- Keep `platform_label="community"` to avoid widening the community signal
  profile for a multi-platform aggregator in this stage.
- Update tests, first-run smoke pinned fixtures, README, and CLI reference.

Scope boundaries:

- Do not add scrapers, crawlers, connectors, MCP server execution, API clients,
  platform search, cookies/sessions, scheduling, media downloads, source
  acquisition, dashboard/report behavior, schema changes, dependency changes, or
  lockfile changes.
- Do not add a compliance/audit/legal-review product feature.
- The adapter must be metadata and local handoff guidance only.

Please evaluate:

1. Does the design/plan cover every runtime, test, smoke, and docs location
   that will drift when adding a new external-tool adapter?
2. Is `platform_label="community"` technically compatible with the current
   community signal profile and tests?
3. Is the readiness decision (`command=None`, `not_applicable`) appropriate for
   an XPOZ MCP/API export target that Fashion Radar does not run?
4. Are there any Critical or Important blockers before implementation?

Return findings ordered by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation or before commit.
- Minor: optional cleanup.

If there are no Critical/Important findings, say that explicitly.
