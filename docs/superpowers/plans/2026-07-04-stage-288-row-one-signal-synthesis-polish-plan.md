# Stage 288 ROW ONE Signal Synthesis Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish ROW ONE Signal Synthesis so rendered signal meta labels are bilingual and same-group signal ordering is covered by regression tests.

**Architecture:** Keep Stage 288 narrow and additive. The existing `build_row_one_app_payload()` already emits structured `signal_synthesis` data; this stage only hardens sorting expectations in the payload layer and improves the static HTML renderer so the language toggle covers the signal card metadata as well as the title, deck, boundaries, group labels, and summaries.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering in `src/fashion_radar/row_one/templates.py`, pytest, ruff, jsonschema contract validation.

---

## File Structure

- Modify `tests/test_row_one_app_contract.py`
  - Add a payload-level regression test for multiple brand signals in the same Signal Synthesis group.
  - Assert ordering by positive heat delta, evidence count, story count, and name fallback.
- Modify `tests/test_row_one_render.py`
  - Add a render-level regression test proving `.signal-synthesis-meta` contains English and Chinese labels under `data-lang`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Replace English-only signal meta spans with bilingual spans for source label, story count, evidence count, and heat delta.
- Create review artifacts in `docs/reviews/`
  - Stage 288 plan review prompt and output are created before implementation.
  - Save Stage 288 code review prompt and review output after implementation.

## Constraints

- Do not change `uv.lock` or `pyproject.toml`.
- Do not commit generated `reports/row-one/` artifacts.
- Do not add compliance-review product features.
- Keep changes scoped to Signal Synthesis polish and tests.
- Use `UV_NO_CONFIG=1 uv --no-config ...` for Python verification.

## Task 1: Add Signal Synthesis Ordering Regression

**Files:**
- Modify: `tests/test_row_one_app_contract.py`

- [ ] **Step 1: Write the failing test**

Add a test named `test_row_one_app_contract_orders_signal_synthesis_within_group`.

The test should:
- Build an edition with at least four brand references in separate stories.
- Use shared `entity_refs` of type `brand`.
- Set values so order is determined first by `positive_heat_delta_sum`, then `evidence_count`, then `story_count`, then case-insensitive name.
- Render the payload through `render_row_one_site()`.
- Assert the brand group signal names are sorted in the expected order.

- [ ] **Step 2: Run focused test and verify current coverage gap**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_app_contract_orders_signal_synthesis_within_group -q
```

Expected before implementation: the test should fail only if the expected behavior is not currently locked down or if the test setup is wrong. If it passes because the implementation already sorts correctly, keep it as a regression test and continue.

- [ ] **Step 3: Fix implementation only if test exposes a bug**

If the test exposes a real ordering bug, update `_signal_synthesis_sort_key()` in `src/fashion_radar/row_one/render.py` while preserving the existing priority:

```python
def _signal_synthesis_sort_key(signal: dict[str, object]) -> tuple[object, ...]:
    return (
        -int(signal["positive_heat_delta_sum"]),
        -int(signal["evidence_count"]),
        -int(signal["story_count"]),
        str(signal["name"]).casefold(),
        str(signal["name"]),
    )
```

- [ ] **Step 4: Verify ordering regression**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py::test_row_one_app_contract_orders_signal_synthesis_within_group -q
```

Expected: `1 passed`.

## Task 2: Add Bilingual Signal Meta Rendering

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Write the failing render test**

Add a test named `test_render_row_one_site_localizes_signal_synthesis_meta`.

The test should:
- Use `_edition()` and add an explicit `brand` reference to the existing story so Signal Synthesis renders.
- Render the site.
- Extract `<div class="signal-synthesis-meta">...</div>`.
- Assert English labels appear inside `data-lang="en"` spans:
  - `rising` or the explicit source label
  - `1 story`
  - `1 evidence link`
  - `+0 local delta`
- Assert Chinese labels appear inside `data-lang="zh"` spans:
  - the explicit source label
  - `1 条故事`
  - `1 条证据链接`
  - `+0 本地增量`
- Assert the meta block does not contain the old unlocalized literal `1 stories`.

- [ ] **Step 2: Run test to verify red/coverage gap**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_localizes_signal_synthesis_meta -q
```

Expected before implementation: fail because signal meta is currently English-only.

- [ ] **Step 3: Implement bilingual meta helper**

In `src/fashion_radar/row_one/templates.py`, add a small helper near `_render_signal_synthesis_card()`:

```python
def _signal_synthesis_meta_label(
    *,
    label: str,
    story_count: int,
    evidence_count: int,
    heat_delta: int,
) -> str:
    story_label_en = "1 story" if story_count == 1 else f"{story_count} stories"
    story_label_zh = f"{story_count} 条故事"
    evidence_label_en = (
        "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    )
    evidence_label_zh = f"{evidence_count} 条证据链接"
    heat_label_en = f"+{heat_delta} local delta"
    heat_label_zh = f"+{heat_delta} 本地增量"
    return (
        f'<span data-lang="en">{_esc(label)}</span>'
        f'<span data-lang="zh">{_esc(label)}</span>'
        f'<span data-lang="en">{_esc(story_label_en)}</span>'
        f'<span data-lang="zh">{_esc(story_label_zh)}</span>'
        f'<span data-lang="en">{_esc(evidence_label_en)}</span>'
        f'<span data-lang="zh">{_esc(evidence_label_zh)}</span>'
        f'<span data-lang="en">{_esc(heat_label_en)}</span>'
        f'<span data-lang="zh">{_esc(heat_label_zh)}</span>'
    )
```

Then call it from `_render_signal_synthesis_card()` instead of composing English-only meta spans inline.

- [ ] **Step 4: Verify render regression**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_localizes_signal_synthesis_meta -q
```

Expected: `1 passed`.

## Task 3: Focused Verification and Review Gate

**Files:**
- Create: `docs/reviews/claude-code-stage-288-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-288-code-review.md`
- Create: `docs/reviews/opencode-stage-288-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-288-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_app_contract.py tests/test_row_one_render.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
```

Expected: all commands exit `0`.

- [ ] **Step 2: Request review**

Try Claude Code review first if available. If unavailable with the known local authentication failure, record that failure in `docs/reviews/claude-code-stage-288-code-review.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max < docs/reviews/opencode-stage-288-code-review-prompt.md > docs/reviews/opencode-stage-288-code-review.md
```

- [ ] **Step 3: Fix Critical and Important review findings**

If review returns Critical or Important findings, fix them before final verification. Minor findings may be documented for later if out of scope.

## Task 4: Full Verification, Commit, Push, Handoff

**Files:**
- Modify only files listed above unless review requires a narrowly scoped fix.

- [ ] **Step 1: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
git diff --exit-code -- uv.lock pyproject.toml
```

Expected: all commands exit `0`.

- [ ] **Step 2: Commit**

Run:

```bash
git status --short
git add docs/superpowers/plans/2026-07-04-stage-288-row-one-signal-synthesis-polish-plan.md docs/reviews/ src/fashion_radar/row_one/templates.py tests/test_row_one_app_contract.py tests/test_row_one_render.py
git commit -m "Stage 288: polish row one signal synthesis"
```

- [ ] **Step 3: Push**

Run:

```bash
git push origin main
```

- [ ] **Step 4: Handoff Summary**

Report:
- Repo status
- Verified commands
- Uncommitted files
- Next step

## Self-Review

- Spec coverage: Covers the two known Stage 287 minor findings: bilingual `.signal-synthesis-meta` labels and same-group ordering coverage.
- Placeholder scan: No TODO/TBD placeholders remain.
- Type consistency: Tests and implementation use existing `RowOneReference`, `render_row_one_site()`, and `signal_synthesis` payload structures.
- Scope control: No dependency, lockfile, report artifact, or compliance feature changes are planned.
