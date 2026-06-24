# Stage 188 Proxy Test Isolation And Roadmap Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make collector/workflow tests independent of host proxy environment and update roadmap documents so the next stages return to product-value work.

**Architecture:** Use the existing failing tests as the RED proof under a synthetic proxy environment, apply a test-only fix so injected-collector tests no longer trigger default article-extraction HTTP client creation, then update brief/roadmap docs to freeze further handoff-surface expansion and re-prioritize source coverage, source health, matching quality, and optional summarization.

**Tech Stack:** Python, pytest, monkeypatch, existing collector/workflow seams, Markdown docs, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_collectors_runner.py`
- Modify: `tests/test_workflows.py`
- Modify: `docs/PROJECT_BRIEF.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Add: `docs/superpowers/specs/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-plan.md`
- Add: `docs/reviews/opencode-stage-188-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-188-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-188-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-188-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-188-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-188-release-review.md`

## Task 1: Reproduce The Existing Proxy-Sensitive Failures

**Files:**

- Modify: `tests/test_collectors_runner.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add one explicit workflow-boundary seam guard in final GREEN form**

Add a test near `test_collect_configured_sources_uses_injected_collectors`:

```python
def test_collect_configured_sources_with_injected_collectors_ignores_proxy_env(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("ALL_PROXY", "socks5h://127.0.0.1:9999")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:8080")
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:8080")

    source = SourceDefinition(
        name="Fixture Feed",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
        weight=1.7,
        article={"enabled": False},
    )

    results = collect_configured_sources(
        data_dir=tmp_path / "data",
        sources=[source],
        collectors={SourceType.RSS: FakeCollector()},
        now=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert results[0].status.status == "success"
```

- [ ] **Step 2: Run the existing failing tests plus the new workflow test and verify RED**

Run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 \
HTTPS_PROXY=socks5h://127.0.0.1:9 \
HTTP_PROXY=socks5h://127.0.0.1:9 \
http_proxy=socks5h://127.0.0.1:9 \
uv --no-config run --frozen pytest \
  tests/test_collectors_runner.py::test_collect_sources_records_failure_and_continues_to_next_source \
  tests/test_collectors_runner.py::test_collect_sources_passes_started_at_to_timing_aware_collectors \
  tests/test_collectors_runner.py::test_collect_sources_stores_source_weight_and_collected_at \
  tests/test_workflows.py::test_collect_configured_sources_uses_injected_collectors \
  tests/test_workflows.py::test_collect_configured_sources_with_injected_collectors_ignores_proxy_env \
  -q
```

Expected: the three existing collector/workflow tests fail under the synthetic
proxy environment because they still trigger the default article-extraction HTTP
client path. The new workflow-boundary guard is already written in its final
GREEN form and should pass once collected.

## Task 2: Apply The Test-Side Fix And Verify GREEN

**Files:**

- Modify: `tests/test_collectors_runner.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Implement the smallest fix**

Update `tests/test_collectors_runner.py` so `_rss_source(...)` defaults to
`article={"enabled": False}` using payload merging:

```python
def _rss_source(name: str, **overrides: object) -> SourceDefinition:
    payload = {
        "name": name,
        "type": SourceType.RSS,
        "url": f"https://example.com/{name}.xml",
        "article": {"enabled": False},
    }
    payload.update(overrides)
    return SourceDefinition(**payload)
```

Then update `test_collect_configured_sources_uses_injected_collectors` so its
source fixture explicitly sets `article={"enabled": False}` and accepts
`monkeypatch` to pin the proxy regression at the workflow boundary.

Use this exact shape:

```python
def test_collect_configured_sources_uses_injected_collectors(
    tmp_path: Path, monkeypatch
) -> None:
    for key in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY", "http_proxy"):
        monkeypatch.setenv(key, "socks5h://127.0.0.1:9")

    source = SourceDefinition(
        name="Fixture Feed",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
        weight=1.7,
        article={"enabled": False},
    )

    results = collect_configured_sources(
        data_dir=tmp_path / "data",
        sources=[source],
        collectors={SourceType.RSS: FakeCollector()},
        now=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    engine = create_sqlite_engine(default_database_path(tmp_path / "data"))
    stored = ItemRepository(engine).get_item(1)
    assert results[0].status.status == "success"
    assert stored["source_weight"] == 1.7
    assert stored["collected_at"] == "2026-06-11T12:00:00+00:00"
```

Do not modify runtime proxy behavior in `src/`.

- [ ] **Step 2: Run the RED set again and verify GREEN**

Run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 \
HTTPS_PROXY=socks5h://127.0.0.1:9 \
HTTP_PROXY=socks5h://127.0.0.1:9 \
http_proxy=socks5h://127.0.0.1:9 \
uv --no-config run --frozen pytest \
  tests/test_collectors_runner.py::test_collect_sources_records_failure_and_continues_to_next_source \
  tests/test_collectors_runner.py::test_collect_sources_passes_started_at_to_timing_aware_collectors \
  tests/test_collectors_runner.py::test_collect_sources_stores_source_weight_and_collected_at \
  tests/test_workflows.py::test_collect_configured_sources_uses_injected_collectors \
  tests/test_workflows.py::test_collect_configured_sources_with_injected_collectors_ignores_proxy_env \
  -q
```

Expected: all five tests pass.

- [ ] **Step 3: Run the surrounding test files**

Run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 \
HTTPS_PROXY=socks5h://127.0.0.1:9 \
HTTP_PROXY=socks5h://127.0.0.1:9 \
http_proxy=socks5h://127.0.0.1:9 \
uv --no-config run --frozen pytest tests/test_collectors_runner.py tests/test_workflows.py -q
```

Expected: both files pass cleanly under the synthetic proxy environment.

## Task 3: Correct Roadmap Documents

**Files:**

- Modify: `docs/PROJECT_BRIEF.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add roadmap correction note to the project brief**

Add a short section after `## Recommended First Public Version`:

```markdown
## Current Direction Correction

The external/community handoff surface is considered sufficient for the current
MVP unless a real bug is found. The next implementation stages should
prioritize product-critical work instead:

- broader and healthier fashion source coverage;
- source-health and feed-liveness diagnostics;
- better matching quality for real fashion entities and product phrases;
- optional report summarization after the deterministic pipeline is stable.
```

- [ ] **Step 2: Add a concise priority note to README**

Near `## What It Does Not Do` and before `## Quickstart`, add a short
contributor-facing roadmap note:

```markdown
## Current Roadmap Focus

Near-term v0.1.x work is focused on the core pipeline: broader source coverage,
source-health visibility, stronger deterministic matching, and an optional
summary layer for reports. No new external-tool, community-handoff, or
imported-review surface area is planned unless a release-blocking defect
requires maintenance.
```

- [ ] **Step 3: Add architecture note freezing handoff expansion**

In `docs/architecture.md`, near the external/community handoff component block,
add:

```markdown
The current external/community handoff surface is intentionally enough for the
MVP. Additional handoff-surface expansion is lower priority than improving the
core collect → match → score → report workflow.
```

- [ ] **Step 4: Record the correction in CHANGELOG**

Add a `### Fixed` subsection under `## [Unreleased]` with:

```markdown
### Fixed

- Stage 188 isolates injected collector/workflow tests from proxy-configured
  host environments and corrects roadmap emphasis toward source coverage,
  source health, matching quality, and optional report summaries over further
  external/community handoff expansion.
```

- [ ] **Step 5: Update review protocol with prioritization guidance**

Add a short paragraph in `docs/REVIEW_PROTOCOL.md`:

```markdown
Once a documentation or contract surface is already stable, future stages
should prefer unresolved product-critical capabilities and real defects over
additional wording-only or parity-only hardening on that same surface.
```

## Task 4: Focused Verification And Code Review

**Files:**

- Modify: tests and docs listed above
- Add: `docs/reviews/opencode-stage-188-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-188-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY \
  uv --no-config run --frozen pytest tests/test_collectors_runner.py tests/test_workflows.py -q
uv --no-config run --frozen ruff check \
  tests/test_collectors_runner.py \
  tests/test_workflows.py
uv --no-config run --frozen ruff format --check \
  tests/test_collectors_runner.py \
  tests/test_workflows.py \
  README.md \
  docs/PROJECT_BRIEF.md \
  docs/architecture.md \
  docs/REVIEW_PROTOCOL.md \
  CHANGELOG.md
```

Expected: focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-188-code-review-prompt.md` requiring the
response body to start with:

```text
# Stage 188 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-188-code-review-prompt.md)" > "$tmp_review" 2>&1
awk 'BEGIN{copy=0} /^# Stage 188 Code Review/{copy=1} copy{print}' "$tmp_review" > docs/reviews/opencode-stage-188-code-review.md
if [ ! -s docs/reviews/opencode-stage-188-code-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-188-code-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no Critical or Important findings.

## Task 5: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-188-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-188-release-review.md`

- [ ] **Step 1: Run release gate**

Run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 \
HTTPS_PROXY=socks5h://127.0.0.1:9 \
HTTP_PROXY=socks5h://127.0.0.1:9 \
http_proxy=socks5h://127.0.0.1:9 \
uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: all commands pass.

- [ ] **Step 2: Create and run release review**

Create `docs/reviews/opencode-stage-188-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 188 Release Review
```

Run the same temp-file capture flow used for code review and copy the completed
review to `docs/reviews/opencode-stage-188-release-review.md`.

- [ ] **Step 3: Commit and push**

Run:

```bash
git add \
  tests/test_collectors_runner.py \
  tests/test_workflows.py \
  README.md \
  docs/PROJECT_BRIEF.md \
  docs/architecture.md \
  docs/REVIEW_PROTOCOL.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-design.md \
  docs/superpowers/plans/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-plan.md \
  docs/reviews/opencode-stage-188-plan-review-prompt.md \
  docs/reviews/opencode-stage-188-plan-review.md \
  docs/reviews/opencode-stage-188-code-review-prompt.md \
  docs/reviews/opencode-stage-188-code-review.md \
  docs/reviews/opencode-stage-188-release-review-prompt.md \
  docs/reviews/opencode-stage-188-release-review.md
git commit -m "fix: isolate proxy-sensitive tests"
git push origin main
```

## Self-Review Notes

- Spec coverage: test isolation and roadmap correction are both covered.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: no new collectors, no new connectors, no new handoff
  features, and no database schema changes.
