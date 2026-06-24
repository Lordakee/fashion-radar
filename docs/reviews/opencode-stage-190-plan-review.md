# Stage 190 Plan Review

The design and plan are coherent in intent and the boundary discipline is sound. RSS/RSSHub and GDELT probe semantics are correct for a liveness diagnostic (no coverage/demand over-claiming), the boundaries are explicitly preserved, and the fake-client/monkeypatch seams are well-structured. However, one Critical gate defect and two Important incoherences must be resolved before implementation.

## Critical

**1. Release gate breaks: `ruff format --check` is invoked on explicit `.md` files.**

The plan runs (plan:950 and plan:969):
```
uv --no-config run --frozen ruff format --check ... README.md docs/architecture.md docs/source-packs.md docs/source-pack-quality.md docs/cli-reference.md CHANGELOG.md
```
`ruff` has no `preview` enabled in `pyproject.toml` (`[tool.ruff.format]`/`[tool.ruff]` exist, no `preview = true`). With markdown formatting still experimental, this exits **2**:
```
error: Failed to format README.md: Markdown formatting is experimental, enable preview mode.
```
Every prior stage's gate uses `ruff format --check .` (directory scan, skips non-Python) or lists only `.py` files (e.g. stage-182:229, stage-186:184, stage-102:292). Verified: `ruff format --check .` exits 0; `ruff format --check README.md` exits 2. This will fail Task 4 Step 4 and Task 5 Steps 1/3.

Fix: drop all `.md` files from the explicit `ruff format --check` argument lists; use `ruff format --check .` for the full gate and list only the `.py` files for per-task checks.

## Important

**2. `http_status` seam incoherence: the model/table promise a value the seams cannot supply.**

`SourceLivenessResult.http_status` (design:138, plan:385) and the table "HTTP" column (design:256, plan renderer test:243) imply HTTP status capture. But the planned `HttpProbeClient` Protocol exposes only `get_text` / `get_json` / `close` (plan:415-418), and `FakeClient` has no status field (plan:72-94). Neither `get_text` nor `get_json` returns a status code, so real probes can only ever set `http_status=None`; no probe test asserts it (only the renderer test hard-codes 200). Result: a permanently empty "HTTP" column in every real run, untested.

Resolve before coding — either (a) add a status-bearing seam (e.g. `get_response(...)` returning an object with `.status_code` + `.text`/`.json()`, and update `FakeClient` + both probes), or (b) drop `http_status` and the HTTP column from v1. The plan must pick one explicitly.

**3. CLI test coverage in Task 3 is thinner than the design's testing strategy.**

The design's CLI test obligations (design:284-292) list seven cases; the plan implements four. Missing:
- "error report exits 1 while still printing output" — this guards the "output printed before exit-code evaluation" guarantee (design:230); without it a regression that exits-1-without-printing is uncaught.
- "invalid format does not call builder" (design:291).
- "warning-only report exits 0 without strict" — only the strict→1 inverse is tested (plan:800).

Add these so the TDD step matches the spec's stated coverage.

## Minor

**4. `elapsed_ms` determinism is set up but never asserted.** `test_rss_liveness_live_feed_counts_entries_from_fixture` wires `monotonic=monotonic_sequence([10.0, 10.025])` (plan:558) but never asserts the resulting `elapsed_ms` (e.g. `== 25`), despite the design committing to "deterministic ... `elapsed_ms` through clock seams" (design:280). Add the assertion so a units/sign bug is caught.

**5. Design/plan model drift for report-level findings.** The design's Data Model references `findings: list[SourceLivenessFinding]` (design:166) and uses findings for invalid config (design:170) but never defines `SourceLivenessFinding` / `SourceLivenessFindingSeverity`; the plan correctly introduces them (plan:356-368). Update the design's Data Model section to define these so spec and plan agree. (Note: the invalid-config test message assertion `"requires url"` at plan:226 matches `SourceDefinition.validate_source_target` at `models/source.py:88`, so that part is consistent.)

**6. Skipped-result `elapsed_ms` is unspecified.** `elapsed_ms` is required (no default, plan:384) but `_skipped_result` is not shown and no test pins its value (presumably 0). State it explicitly.

## Per review question

1. **Boundary preservation** — yes. `source-pack-lint` stays offline/non-fetching, `collect_sources` keeps ownership of persistence/health, and `source-liveness` is a separate read-only probe surface (design:66-77). Clean.
2. **Models/JSON/table/exit coherence** — mostly coherent and testable, except the `http_status` seam gap (Important #2).
3. **RSS/GDELT probe semantics** — correct. bozo→degraded, entries→live, no-entries→empty, `maxrecords=1`/`timespan=<hours>h` is minimal and honest; boundaries explicitly disclaim coverage/demand proof.
4. **TDD/no-live-network/proxy safety** — RED/GREEN structure is good and synthetic-proxy env on Task 2 Step 4 / Task 5 is a sound safety net (fake clients injected), but the ruff gate defect (Critical #1), missing CLI tests (Important #3), and unasserted `elapsed_ms` (Minor #4) need addressing.
5. **Fake-client / elapsed / monkeypatch risks** — monkeypatch seam is correct (`cli_module.build_source_liveness_report` is imported and called as a module-level name, matching the existing `lint_source_pack` pattern; lambda arity matches the CLI call). Main risk is the `http_status` seam (Important #2).
6. **External/social/community expansion** — avoided. Only RSS/RSSHub/GDELT are probed; no `external-tool-*`/`community-*`/`imported-*` modules touched; out-of-scope (design:62) and boundaries (design:261-266) are explicit.

## Verdict

**Not yet approved for implementation.** Fix Critical #1 and Important #2–#3 (the Minor items can be folded in during implementation), then the plan is approvable.
