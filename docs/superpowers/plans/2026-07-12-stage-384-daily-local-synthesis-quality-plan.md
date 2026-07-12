# Stage 384 Daily Local Synthesis Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the Stage 383 Daily Local Synthesis Brief so the generated homepage avoids empty editorial paragraphs, keeps its generated-site-only sentinel strict, and remains readable on narrow screens with long article/source/link text.

**Architecture:** Keep Stage 384 generated-site-only and template/test/docs focused. Do not change builders, JSON artifacts, app/runtime/manifest/schema contracts, source collection, scraping, LLM behavior, scheduling, analytics, recommendation, personalization, compliance-review behavior, or route families. Update only the homepage renderer defenses, CSS wrapping, workflow sentinel strictness, and boundary documentation/tests.

**Tech Stack:** Python server-rendered HTML helpers in `templates.py`, pytest, existing ROW ONE render/workflow/docs tests, ruff, uv frozen verification commands.

---

## Product Gap

Stage 383 added a homepage Daily Local Synthesis Brief that organizes saved local article material into a compact cross-article read. The next quality gap is defensive presentation polish: manually supplied or future edge payloads can render an empty thesis paragraph, long unbroken strings can stress the dark synthesis cards on mobile, and the workflow sentinel uses `raising=False`, which is weaker than the generated-site-only boundary tests should be.

Stage 384 should make the existing section more resilient without widening the data contract or creating another content surface.

## Scope Decision

- Modify only generated-site rendering/tests/docs for the existing Daily Local Synthesis Brief.
- Do not modify `src/fashion_radar/row_one/daily_local_synthesis_brief.py` unless plan review identifies a blocker; the current builder semantics from Stage 383 remain authoritative.
- Do not add new models, JSON files, routes, schemas, app payload fields, manifest/runtime fields, source adapters, scraping, LLM calls, scheduled jobs, analytics, personalization, recommendation, or compliance-review features.
- Keep the section on `index.html` only, between Daily Local Article Intelligence Brief and Daily Local Saved Article Organizer.

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Omit `.daily-local-synthesis-brief-thesis` when both normalized languages are blank.
  - Add wrapping/overflow protection for synthesis card titles, meta chips, and route labels.
- Modify `tests/test_row_one_render.py`
  - Add render test that blank `brief.thesis` omits the thesis paragraph while keeping opening/cards/basis.
  - Extend CSS test to assert wrapping rules for `.daily-local-synthesis-brief-card h3`, `.daily-local-synthesis-brief-card-meta span`, and `.daily-local-synthesis-brief-route`.
- Modify `tests/test_workflows.py`
  - Change Stage 383 sentinel monkeypatch from `raising=False` to `raising=True`.
- Modify `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`
  - Add Stage 384 generated-site-only boundary paragraph above Stage 383.
- Create review artifacts under `docs/reviews/`
  - `claude-code-stage-384-plan-review.md`
  - `opencode-stage-384-plan-review.md`
  - code review artifacts after implementation.

## Requirements

1. Empty thesis handling:
   - `_render_daily_local_synthesis_brief(...)` must render the thesis paragraph only when `brief.thesis.en` or `brief.thesis.zh` normalizes to non-empty text.
   - If one language is present, preserve current fallback behavior for the missing language.
   - Omit only the thesis paragraph; do not omit title, dek, opening, cards, or basis.

2. Mobile/long-text wrapping:
   - Long unbroken synthesis card titles, source/meta chips, and route labels must not force horizontal overflow.
   - Add CSS using existing style conventions, preferably `overflow-wrap: anywhere;` and `min-width: 0;` where needed.
   - Keep the dark editorial visual style from Stage 383.

3. Workflow sentinel strictness:
   - `tests/test_workflows.py::test_stage_383_daily_local_synthesis_brief_stays_homepage_only` must monkeypatch `_render_daily_local_synthesis_brief` with `raising=True` so helper rename/removal fails immediately.
   - Keep existing homepage-only assertions unchanged.

4. Docs/boundary:
   - Stage 384 docs must state this is generated-site-only Daily Local Synthesis Brief presentation hardening.
   - Docs must say it does not create JSON artifacts, routes, schemas, app/runtime/manifest changes, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connectors, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.

## Tasks

### Task 1: RED render test for blank thesis omission

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Add test `test_render_daily_local_synthesis_brief_omits_blank_thesis_paragraph` near existing Daily Local Synthesis Brief render tests.

Test shape:

```python
def test_render_daily_local_synthesis_brief_omits_blank_thesis_paragraph() -> None:
    brief = replace(
        _daily_local_synthesis_brief_fixture(),
        thesis=LocalizedText(en="   ", zh=""),
    )

    html = render_index_html(_edition(), daily_local_synthesis_brief=brief)
    section_html = _daily_local_synthesis_brief_section_html(html)

    assert 'class="daily-local-synthesis-brief"' in section_html
    assert 'class="daily-local-synthesis-brief-opening"' in section_html
    assert 'class="daily-local-synthesis-brief-card"' in section_html
    assert 'class="daily-local-synthesis-brief-basis"' in section_html
    assert 'class="daily-local-synthesis-brief-thesis"' not in section_html
```

- [ ] Run RED command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_daily_local_synthesis_brief_omits_blank_thesis_paragraph -q
```

Expected: FAIL because the thesis paragraph still renders.

### Task 2: Implement thesis paragraph omission

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] In `_render_daily_local_synthesis_brief(...)`, compute `thesis_html` after `thesis_en` and `thesis_zh` are normalized.

Implementation shape:

```python
    thesis_html = (
        f'''  <p class="daily-local-synthesis-brief-thesis">
    <span data-lang="en">{_esc(thesis_en or thesis_zh)}</span>
    <span data-lang="zh">{_esc(thesis_zh or thesis_en)}</span>
  </p>
'''
        if thesis_en or thesis_zh
        else ""
    )
```

- [ ] Replace the current always-rendered thesis `<p>` in the returned HTML with `{thesis_html}`.
- [ ] Keep escaping and language fallback identical when text exists.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_daily_local_synthesis_brief_omits_blank_thesis_paragraph -q
```

Expected: PASS.

### Task 3: CSS wrapping test and implementation

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] Extend `test_row_one_css_includes_daily_local_synthesis_brief_styles` to assert standalone wrapping rules.

Expected assertions:

```python
    assert re.search(
        r"\.daily-local-synthesis-brief-card h3\s*\{[^}]*overflow-wrap:\s*anywhere",
        css,
    )
    assert re.search(
        r"\.daily-local-synthesis-brief-card-meta span\s*\{[^}]*overflow-wrap:\s*anywhere",
        css,
    )
    assert re.search(
        r"\.daily-local-synthesis-brief-route\s*\{[^}]*overflow-wrap:\s*anywhere",
        css,
    )
    assert re.search(
        r"\.daily-local-synthesis-brief-card\s*\{[^}]*min-width:\s*0",
        css,
    )
    assert re.search(
        r"\.daily-local-synthesis-brief-card-meta\s*\{[^}]*min-width:\s*0",
        css,
    )
```

- [ ] Run RED command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_row_one_css_includes_daily_local_synthesis_brief_styles -q
```

Expected: FAIL until CSS wrapping is added.

- [ ] Add CSS in `row_one_css()` as standalone selector blocks so the tests prove each target selector owns the wrapping rule:

```css
.daily-local-synthesis-brief-card h3 {
  overflow-wrap: anywhere;
}

.daily-local-synthesis-brief-card-meta {
  min-width: 0;
}

.daily-local-synthesis-brief-card-meta span {
  overflow-wrap: anywhere;
}

.daily-local-synthesis-brief-route {
  overflow-wrap: anywhere;
}
```

Do not use only a grouped selector block for these additions; the CSS test intentionally requires standalone selector coverage for `.daily-local-synthesis-brief-card h3`, `.daily-local-synthesis-brief-card-meta span`, and `.daily-local-synthesis-brief-route`.

- [ ] Run the same CSS test again.

Expected: PASS.

### Task 4: Workflow sentinel strictness

**Files:**
- Modify: `tests/test_workflows.py`

- [ ] Change Stage 383 sentinel monkeypatch from:

```python
    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_synthesis_brief",
        lambda _brief: sentinel,
        raising=False,
    )
```

to:

```python
    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_synthesis_brief",
        lambda _brief: sentinel,
        raising=True,
    )
```

- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py::test_stage_383_daily_local_synthesis_brief_stays_homepage_only -q
```

Expected: PASS.

### Task 5: Docs boundary paragraph

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] Add paragraph above Stage 383 in both docs:

```text
Stage 384 hardens the generated-site-only Daily Local Synthesis Brief presentation on the ROW ONE homepage by omitting blank thesis paragraphs, tightening the existing homepage-only renderer sentinel, and adding long-text wrapping for synthesis card titles, source chips, and saved-article route labels; it reuses the Stage 383 homepage section, current render model, existing CSS, and existing generated local article page routes while adding presentation-focused regression coverage without changing app-facing contracts; it does not create `data/daily-local-synthesis-quality.json`, does not create `data/daily-synthesis-quality.json`, does not create `daily-local-synthesis-quality.html`, does not create `daily-synthesis-quality.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
```

- [ ] Add docs test `test_row_one_docs_describe_stage_384_daily_local_synthesis_quality_boundary` requiring the exact paragraph in README and docs, placed before Stage 383.
- [ ] Include stale phrase checks for both `creates ...` and `writes ...` variants of `data/daily-local-synthesis-quality.json`, `data/daily-synthesis-quality.json`, `daily-local-synthesis-quality.html`, and `daily-synthesis-quality.html`, plus checks around new routes, contract/schema/source/scraping/LLM/scheduling/analytics/recommendation/compliance-review behavior.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_384_daily_local_synthesis_quality_boundary -q
```

Expected: PASS.

### Task 6: Focused and related verification

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py -k "daily_local_synthesis_brief" \
  tests/test_workflows.py::test_stage_383_daily_local_synthesis_brief_stays_homepage_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_384_daily_local_synthesis_quality_boundary \
  -q
```

Expected: PASS.

Then run broader related suite:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_daily_local_synthesis_brief.py \
  -q
```

Expected: PASS.

### Task 7: Code review and final gates

- [ ] Run formal code review artifacts:

```bash
claude --effort max --permission-mode plan --no-session-persistence --tools Read,Grep,Glob,LS,Bash -p "$(cat /tmp/stage384-code-review-prompt.md)" > docs/reviews/claude-code-stage-384-code-review.md
NO_COLOR=1 opencode run --model zhipuai-coding-plan/glm-5.2 --variant max "$(cat /tmp/stage384-code-review-prompt.md)" > docs/reviews/opencode-stage-384-code-review.md
```

If Claude times out again, write a non-empty review-attempt note and rely on opencode plus frozen local gates; clean process chatter from opencode review artifacts before release hygiene.

- [ ] Fix every Critical/Important review finding, with rereview artifacts if needed.
- [ ] Run final gates:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git diff --cached --check
```

Expected: all pass.

### Task 8: Commit and push

- [ ] Stage files:

```bash
git add README.md docs/row-one.md docs/reviews docs/superpowers/plans/2026-07-12-stage-384-daily-local-synthesis-quality-plan.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
```

- [ ] Commit and push:

```bash
git commit -m "Stage 384: harden daily local synthesis brief"
git push origin main
```

- [ ] Handoff summary must include repo status, verified commands, uncommitted files, and next step.

## Acceptance Criteria

- Blank synthesis thesis does not render an empty `.daily-local-synthesis-brief-thesis` paragraph.
- Existing non-empty thesis text still renders with escaped EN/ZH fallback.
- Long synthesis card titles, source/meta chips, and route labels have CSS wrapping coverage.
- Stage 383 homepage-only workflow sentinel uses `raising=True`.
- Stage 384 docs describe generated-site-only presentation hardening and deny contract/artifact/route/source/LLM/compliance changes.
- Focused, related, and final frozen gates pass.
