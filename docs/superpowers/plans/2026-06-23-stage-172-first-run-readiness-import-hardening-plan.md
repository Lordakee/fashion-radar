# Stage 172 First-Run Readiness Import Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the first-run smoke readiness parity test fail loudly if `fashion_radar.external_tool_readiness` is missing or broken, instead of silently skipping behind a stale Stage 66 fallback.

**Architecture:** Tighten `tests/test_first_run_smoke.py` only. Add a RED meta test that rejects a `skipif` mark on the readiness parity test, then replace the optional import fallback and stale skip decorator with a direct import of `build_external_tool_readiness`. Keep runtime source, first-run smoke script behavior, adapter metadata, payload shapes, command order, boundaries, and install hints unchanged.

**Tech Stack:** Pytest, Python imports, existing `build_external_tool_readiness(...)`, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_first_run_smoke.py`
  - Add a small meta test that rejects `skipif` on the external-tool-readiness
    parity test.
  - Replace the optional import fallback with a direct import.
  - Remove the stale `@pytest.mark.skipif(...)` decorator and redundant
    `assert build_external_tool_readiness is not None`.
- Add: `docs/superpowers/specs/2026-06-23-stage-172-first-run-readiness-import-hardening-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-172-first-run-readiness-import-hardening-plan.md`
- Add: `docs/reviews/opencode-stage-172-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-172-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-172-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-172-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-172-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-172-release-review.md`

## Task 1: Add RED Meta Test

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add the meta test**

Immediately after
`test_external_tool_readiness_payload_matches_real_rednote_readiness(...)`, add:

```python
def test_external_tool_readiness_payload_parity_is_not_conditionally_skipped() -> None:
    marks = getattr(
        test_external_tool_readiness_payload_matches_real_rednote_readiness,
        "pytestmark",
        [],
    )

    assert all(mark.name != "skipif" for mark in marks)
```

- [ ] **Step 2: Run RED check**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_is_not_conditionally_skipped -q
```

Expected before implementation: fails because
`test_external_tool_readiness_payload_matches_real_rednote_readiness` still has a
`skipif` pytest mark.

## Task 2: Remove Stale Optional Import And Skip

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Replace optional import fallback**

Replace:

```python
try:
    from fashion_radar.external_tool_readiness import build_external_tool_readiness
except ModuleNotFoundError:  # pragma: no cover - removed once Stage 66 core lands.
    build_external_tool_readiness = None
```

with:

```python
from fashion_radar.external_tool_readiness import build_external_tool_readiness
```

- [ ] **Step 2: Remove stale skip decorator and redundant assertion**

Delete this decorator block:

```python
@pytest.mark.skipif(
    build_external_tool_readiness is None,
    reason="Stage 66 core external_tool_readiness module is not implemented yet.",
)
```

Inside `test_external_tool_readiness_payload_matches_real_rednote_readiness(...)`,
delete:

```python
    assert build_external_tool_readiness is not None
```

- [ ] **Step 3: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_is_not_conditionally_skipped -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_matches_real_rednote_readiness -q
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-172-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-172-code-review.md`
- Add: `docs/reviews/opencode-stage-172-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-172-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-172-code-review-prompt.md` with a prompt
that asks local opencode to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-172-first-run-readiness-import-hardening-design.md`
- `docs/superpowers/plans/2026-06-23-stage-172-first-run-readiness-import-hardening-plan.md`
- `tests/test_first_run_smoke.py`

The prompt must require the response to start with:

```text
# Stage 172 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-172-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-172-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact if opencode includes process chatter or command logs.

- [ ] **Step 3: Run release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: all commands pass; token and extraheader checks report no secrets.

- [ ] **Step 4: Create and run release review**

Create `docs/reviews/opencode-stage-172-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 172 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-172-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_first_run_smoke.py \
  docs/superpowers/specs/2026-06-23-stage-172-first-run-readiness-import-hardening-design.md \
  docs/superpowers/plans/2026-06-23-stage-172-first-run-readiness-import-hardening-plan.md \
  docs/reviews/opencode-stage-172-plan-review-prompt.md \
  docs/reviews/opencode-stage-172-plan-review.md \
  docs/reviews/opencode-stage-172-code-review-prompt.md \
  docs/reviews/opencode-stage-172-code-review.md \
  docs/reviews/opencode-stage-172-release-review-prompt.md \
  docs/reviews/opencode-stage-172-release-review.md
git commit -m "test: require external readiness smoke import"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 covers the RED meta test, Task 2 covers stale fallback
  removal, and Task 3 covers review/release/commit requirements.
- Placeholder scan: no placeholder implementation steps remain.
- Type consistency: no runtime types or payload shapes change.
- Scope check: this is a focused first-run smoke test hardening stage.
