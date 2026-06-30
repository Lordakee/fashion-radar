# Stage 254 Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical
None.

## Important
None. All four review checks pass against the current tree (HEAD 9d10f6f):

1. **Architecture sentence + guard are consistent and correct.** The doc edit (`docs/architecture.md:422-424`) turns "(Phase 2: Xiaohongshu)" into "(Phase 2-5: Xiaohongshu, Instagram, Twitter/X, YouTube)", leaving the rest of the sentence ("is use-at-your-own-risk, non-core, and provides no demand proof or platform coverage verification") intact. The guard edit (`tests/test_architecture_boundary_docs.py:35`) pins exactly the casefolded substring "opt-in social-platform collection (phase 2-5: xiaohongshu, instagram, twiter/x, youtube) is use-at-your-own-risk", which is a true substring of the post-edit sentence under `_normalized`. The other five phrases pinned by `test_architecture_source_boundary_keeps_core_scope_and_local_import_limits` are untouched by the edit, so that test stays green. This also realigns the prose with the already-correct Collectors bullet (`architecture.md:56`).

2. **New XHS guard anchors on an XHS-specific phrase.** "xiaohongshu (小红书) via xiaohongshu-mcp" is unique to the Xiaohongshu bullet (`source-boundaries.md:240`) and mirrors the IG ("instagram via instaloader"), Twitter ("twitter/x via twitter-cli"), and YouTube ("youtube via yt-dlp") anchors. "login-required", "use-at-your-own-risk", and the coverage phrase all appear verbatim in lines 240-244, and the guard reads the whole doc with `_normalized` exactly like the other three — true parity.

3. **No existing guard broken.** The only test referencing the old architecture phrase is line 35, which the plan updates in lockstep. No test pins the old architecture wording elsewhere, and the source-boundaries guards are additive.

4. **Docs + guard only.** Scope In = `architecture.md` + the two test files; Out explicitly excludes code/schema/dep; verification includes `git diff --exit-code -- uv.lock pyproject.toml`. No collector, schema, or dependency surface is touched.

## Nits
- **AGENTS.md keps the same staleness.** `AGENTS.md:5-6` still says "opt-in social-platform collection (Phase 2: Xiaohongshu) is use-at-your-own-risk and not enabled by default." It's not pinned by any guard (so nothing breaks) and the release review flagged only the architecture Source Boundary, so deferring is defensible — but if the goal is to eliminate "Phase 2 only" staleness, this is the same stale example in the agent-facing doc. Worth a one-line note in the plan on why it's intentionally left (e.g., it reads as an example, and "not enabled by default" remains true for all four).
- **Use the canonical coverage phrase.** Scope line 16 writes the XHS anchor loosely as "no demand proof / no coverage verification". The implementation should pin the exact phrase the other three guards use — "no demand proof and no platform coverage verification" — which is what the doc actually says (line 244), to kep the four guards literally identical on that anchor.

## Summary
Tight, well-scoped docs+guard polish. The architecture prose/guard pair is internally consistent and matches the existing tree, and the new Xiaohongshu guard achieves real symmetry with the IG/Twitter/YouTube guards via an XHS-specific anchor. No existing guard breaks and there is no code/schema/dep surface. Two nits only: decide whether to also de-stale AGENTS.md (or document why not), and pin the canonical "no demand proof and no platform coverage verification" phrase in the new guard. Safe to proceed.
