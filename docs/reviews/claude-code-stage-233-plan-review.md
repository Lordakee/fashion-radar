# Stage 233 Plan Review
**Verdict:** APPROVE_WITH_NITS

## Critical
None.

## Important
None.

## Nits
1. **cli-reference.md collect bullet verbosity:** The collect command description at line 70-71 is already quite long. Adding Instagram will extend it further: "RSS/RSSHub/GDELT, plus `html` seed-URL and `sitemap` source types via the optional `article` extra, and opt-in `xiaohongshu` via an external xiaohongshu-mcp server, and opt-in `instagram` via instaloader". Consider whether this needs a line break or restructuring for readability, though matching the Xiaohongshu pattern is acceptable.

2. **Spec status update format:** Plan mentions "Status → Complete" for the design spec but doesn't detail the exact format (e.g., frontmatter field vs. inline heading). Minor since it's straightforward, but worth confirming it matches the spec's existing structure.

3. **Instagram opt-in wording precision:** The plan says "Instagram (via instaloader, login-required, use-at-your-own-risk, no demand proof / no coverage verification)" for source-boundaries.md. Verify this matches Xiaohongshu's exact structure: "Xiaohongshu (小红书) via xiaohongshu-mcp (Phase 2): login-required (QR scan managed by the external tool), use-at-your-own-risk; the user installs, runs, and logs into the external tool, and Fashion Radar only reads results over its local MCP HTTP endpoint. It provides no demand proof and no platform coverage verification." Instagram should mention that the user installs/runs instaloader separately, parallel to the Xiaohongshu pattern.

## Summary
The plan is well-structured and mirrors Stage 223's Phase 2 wrap pattern effectively. Docs scope is complete across all 4 files (cli-reference, source-packs, architecture, source-boundaries), the opt-in/use-at-your-own-risk framing is consistent with Xiaohongshu (Stages 221/222), the live-verification caveat for instaloader API field variance is included, scope discipline is tight (docs + guard + changelog only, no code/schema/dep changes), and release verification is comprehensive (full gate including packaging/installed-wheel smoke). The docs-guard placement in the Opt-In section is sound and won't conflict with existing guards for other sections. Nits are minor presentation/precision points that don't affect the core approach.
