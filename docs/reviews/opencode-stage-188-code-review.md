# Stage 188 Code Review

## Q1 — Proxy-sensitive tests resolved without changing runtime behavior?

**Yes, the test-side fix itself is correct and verified.**

- `tests/test_collectors_runner.py:60-68` — `_rss_source(...)` now defaults `article={"enabled": False}` via payload merge while preserving per-test overrides, so the three collector tests (`records_failure_and_continues`, `passes_started_at_to_timing_aware_collectors`, `stores_source_weight_and_collected_at`) no longer trigger default `FashionHttpClient` → `httpx.Client` construction.
- `tests/test_workflows.py:61-84` — the injected-collector test now sets `article={"enabled": False}` and pins proxy env via `monkeypatch`.
- The plan-review **I1** finding was correctly applied: the new seam guard `test_collect_configured_sources_with_injected_collectors_ignores_proxy_env` (test_workflows.py:87-112) now includes `article={"enabled": False}`, so it reaches GREEN instead of staying RED.
- No `src/` runtime files changed (`git show --stat HEAD` → 0 src files), so runtime proxy behavior in `utils/http.py` and `collectors/runner.py` is untouched. Verified: focused set (11 passed) and full suite pass under `ALL_PROXY/HTTPS_PROXY/HTTP_PROXY=http_proxy=socks5h://127.0.0.1:9`.

## Q2 — Roadmap corrections scoped and consistent with product direction?

**Yes.** The edits are coherent with the brief and with `AGENTS.md` scope boundaries:

- `README.md` — adds `## Current Roadmap Focus` (source coverage, source-health, matching, optional summary; handoff frozen for v0.1.x).
- `docs/PROJECT_BRIEF.md:160-176` — adds `## Current Review-Aligned Priorities` listing the same four pillars.
- `docs/architecture.md:14-16,80-83` — collapses the handoff pipeline steps and adds an explicit priority note.
- `docs/REVIEW_PROTOCOL.md:14-15,38-43` — requires each stage to name the core gap it closes and freezes `external-tool-*`/`community-handoff-*`/`imported-*` unless fixing a release-blocking defect.
- `CHANGELOG.md` — `### Fixed` entry recorded.

The direction (source breadth/health → matching quality → optional summarization; freeze further handoff expansion) matches the full-project review recommendation and the project's free-first/local-first scope.

## Q3 — Critical / Important issues

### Critical

**C1 — The code-review artifact was a timeout stub when this review started.**

At the start of this review, `docs/reviews/opencode-stage-188-code-review.md`
contained only a timeout record and self-verification notes instead of completed
review findings. This is a forbidden live-capture stub in the precise sense
`AGENTS.md` prohibits ("no live-capture stubs ... or empty output") and
`docs/REVIEW_PROTOCOL.md` prohibits (each stage must end with a completed local
opencode code review, then fixes for findings).

Concretely verified:

- `scripts/check_release_hygiene.py --repo-root .` found the timeout-stub
  review record after Stage 189 added that detector.
- Full suite: `1 failed, 1392 passed` — `tests/test_release_hygiene.py::test_current_repository_tracked_review_artifacts_have_no_capture_findings`.

This means Plan Task 4 Step 3 ("Expected: completed review output with no
Critical or Important findings") and Task 5 Step 1 ("Expected: all commands
pass") were **not** met before commit `48cddf8` was pushed. The required fix is
to replace the stub with this completed review record and re-run the full gate
until green.

### Important

**I1 — The two workflow proxy tests are now functionally identical (zero incremental coverage).**

`test_collect_configured_sources_uses_injected_collectors` (test_workflows.py:61-84) and `test_collect_configured_sources_with_injected_collectors_ignores_proxy_env` (test_workflows.py:87-112) are duplicates: same monkeypatched proxy env, same `article={"enabled": False}` fixture, same `FakeCollector`, same call, same three assertions. The first test's name ("uses_injected_collectors") no longer describes what it uniquely does — it also pins proxy and disables article — so it was effectively renamed into the guard test. Recommend dropping one, or restoring the original to its injected-collector focus (no proxy/article pin) and letting the dedicated test own the proxy-seam guard.

### Minor

- **M1 — Doc edits exceed the plan's "add a note" framing.** README collapsed ~30 existing "What It Does" bullets into one 3-line summary, and `architecture.md` removed ~15 pipeline steps. This is consistent with the freeze intent and the architecture component blocks (which carry the boundary constraints) are preserved, so it is acceptable, but it reduces discoverability of the still-shipping frozen commands and is broader than the spec described.
- **M2 — CHANGELOG `### Fixed` ordering.** Inserted between `### Added` and `### Changed`; Keep a Changelog convention places `Fixed` after `Changed`/`Removed`. Cosmetic.

## Verdict

**Changes requested.** The Stage 188 *code and test* changes are sound and the test-isolation objective is met (Q1 ✓) without altering runtime proxy behavior, and the roadmap redirection is well-scoped and on-direction (Q2 ✓). However, the stage cannot be considered complete as committed: **C1** (timeout-stub review artifact breaking the release gate on `main`) must be fixed — replace with a real completed code review and re-run the full gate to green; **I1** (duplicate test) should be resolved at the same time. Minor items can be folded in opportunistically.
