# Stage 261 ROW ONE Editorial Synthesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic ROW ONE editorial synthesis so the daily site organizes information instead of only presenting links and source snippets.

**Architecture:** Extend the existing `fashion_radar.row_one` presentation model with three synthesis fields per story, generate those fields inside the existing edition builder from local report/item data, and render them in static HTML and JSON. Keep the work inside the Stage 260 presentation layer; do not add new collection, platform connectors, translation, LLM calls, or persistence.

**Tech Stack:** Python 3.11+, Pydantic, existing Fashion Radar report models, static HTML/CSS/JS template strings, pytest, Ruff.

---

## Stage Boundary

This stage closes the ROW ONE readability gap in the `collect -> match -> report`
pipeline. Stage 260 turns reports into a site; Stage 261 turns each site story
into a compact deterministic editorial briefing. The stage does not add new
source acquisition, scraping, browser automation, platform APIs, account/session
behavior, translation, LLM calls, image generation, paid APIs, deployment,
demand proof, platform coverage verification, or compliance-review product work.

## Files

- Modify: `src/fashion_radar/row_one/models.py`
- Modify: `src/fashion_radar/row_one/edition.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_edition.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `docs/row-one.md`
- Create: `docs/reviews/claude-code-stage-261-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-261-plan-review.md` only if a completed review body is captured
- Create if primary route is unavailable: `docs/reviews/opencode-stage-261-plan-review-prompt.md`
- Create if primary route is unavailable: `docs/reviews/opencode-stage-261-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-261-code-review-prompt.md`
- Create after implementation: `docs/reviews/claude-code-stage-261-code-review.md` only if a completed review body is captured
- Create if primary route is unavailable after implementation: `docs/reviews/opencode-stage-261-code-review-prompt.md`
- Create if primary route is unavailable after implementation: `docs/reviews/opencode-stage-261-code-review.md`

## Task 1: Extend ROW ONE Story Model And Builder Tests

**Files:**
- Modify: `src/fashion_radar/row_one/models.py`
- Modify: `tests/test_row_one_edition.py`

- [ ] **Step 1: Write failing model-field assertions**

Add assertions to the existing `test_build_row_one_edition_groups_editorial_sections`
test proving the first generated story has non-empty bilingual synthesis fields:

```python
story = edition.stories[0]
assert story.editorial_takeaway.zh
assert story.editorial_takeaway.en
assert story.signal_context.zh
assert story.signal_context.en
assert story.reader_path.zh
assert story.reader_path.en
```

- [ ] **Step 2: Write entity/candidate/recent synthesis tests**

Add focused tests:

```python
def test_build_row_one_edition_adds_entity_synthesis_from_report_fields() -> None:
    entity = _entity("The Row", "brand", score=9.2)
    edition = build_row_one_edition(report=_report(entities=[entity]), recent_items=[], as_of=AS_OF)
    story = edition.section_stories("brand_moves")[0]
    assert "The Row" in story.editorial_takeaway.en
    assert "5 current mentions" in story.signal_context.en
    assert "1 baseline" in story.signal_context.en
    assert "hot" in story.reader_path.en
    assert "品牌动态" in story.reader_path.zh


def test_build_row_one_edition_adds_candidate_synthesis_from_report_fields() -> None:
    candidate = _candidate("market loafer", "shoe", score=7.8)
    edition = build_row_one_edition(report=_report(candidates=[candidate]), recent_items=[], as_of=AS_OF)
    story = edition.section_stories("hot_products")[0]
    assert "market loafer" in story.editorial_takeaway.en
    assert "4 current mentions" in story.signal_context.en
    assert "0 baseline" in story.signal_context.en
    assert "rising" in story.reader_path.en
    assert "Hot Products" in story.reader_path.en


def test_build_row_one_edition_adds_recent_item_synthesis_from_local_item() -> None:
    recent_item = {
        "source_name": "Vogue Business",
        "url": "https://example.com/the-row",
        "title": "The Row sharpens its retail language",
        "summary": "A concise retail update with strong buyer interest.",
        "collected_at": AS_OF.isoformat(),
    }
    edition = build_row_one_edition(report=_report(), recent_items=[recent_item], as_of=AS_OF)
    story = edition.section_stories("top_stories")[0]
    assert "Vogue Business" in story.signal_context.en
    assert "retained local item" in story.signal_context.en
    assert "Vogue Business" in story.reader_path.en
```

- [ ] **Step 3: Run tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_edition.py -q
```

Expected: FAIL because `RowOneStory` does not yet define the new synthesis
fields.

- [ ] **Step 4: Add synthesis fields to the model**

Modify `RowOneStory` in `src/fashion_radar/row_one/models.py`:

```python
editorial_takeaway: LocalizedText
signal_context: LocalizedText
reader_path: LocalizedText
```

Do not add defaults. Generated stories and test fixtures must populate these
fields explicitly so missing synthesis is caught immediately.

- [ ] **Step 5: Verify model tests still fail for builder output**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_edition.py -q
```

Expected: FAIL until the builder passes the new fields into every `RowOneStory`.

## Task 2: Generate Deterministic Synthesis

**Files:**
- Modify: `src/fashion_radar/row_one/edition.py`
- Modify: `tests/test_row_one_edition.py`

- [ ] **Step 1: Implement entity synthesis helper**

Add helper:

```python
def _entity_synthesis(entity: EntityReport, *, section_key: RowOneSectionKey) -> tuple[LocalizedText, LocalizedText, LocalizedText]:
    section = _section_title(section_key)
    baseline = entity.baseline_mentions
    growth = _growth_ratio_label(entity.growth_ratio)
    if entity.growth_ratio is None:
        signal_context = LocalizedText(
            zh=f"本地窗口记录 {entity.current_mentions} 次当前提及，对比基线 {baseline} 次，暂无增长倍数。",
            en=f"The local window shows {entity.current_mentions} current mentions versus {baseline} baseline; growth ratio is unavailable.",
        )
    else:
        signal_context = LocalizedText(
            zh=f"本地窗口记录 {entity.current_mentions} 次当前提及，对比基线 {baseline} 次，增长倍数 {growth}。",
            en=f"The local window shows {entity.current_mentions} current mentions versus {baseline} baseline, a {growth}x growth ratio.",
        )
    return (
        LocalizedText(
            zh=f"{entity.entity_name} 是今日 {section.zh} 中最值得先看的信号之一。",
            en=f"{entity.entity_name} is one of today's priority signals in {section.en}.",
        ),
        signal_context,
        LocalizedText(
            zh=f"先按 {entity.label} 标签阅读，再对照{section.zh}中的同类信号。",
            en=f"Read it as a {entity.label} signal, then compare it with nearby {section.en} stories.",
        ),
    )
```

- [ ] **Step 2: Implement candidate synthesis helper**

Add helper:

```python
def _candidate_synthesis(candidate: CandidateReport, *, section_key: RowOneSectionKey) -> tuple[LocalizedText, LocalizedText, LocalizedText]:
    section = _section_title(section_key)
    baseline = candidate.baseline_mentions
    return (
        LocalizedText(
            zh=f"{candidate.phrase} 正被 ROW ONE 归入{section.zh}观察。",
            en=f"{candidate.phrase} is being tracked by ROW ONE inside {section.en}.",
        ),
        LocalizedText(
            zh=f"本地窗口记录 {candidate.current_mentions} 次当前提及，对比基线 {baseline} 次，首次出现于 {candidate.first_seen_at.date().isoformat()}。",
            en=f"The local window shows {candidate.current_mentions} current mentions versus {baseline} baseline, first seen on {candidate.first_seen_at.date().isoformat()}.",
        ),
        LocalizedText(
            zh=f"把它作为 {candidate.label} 的{section.zh}线索，而不是已验证需求证明。",
            en=f"Treat it as a {candidate.label} {section.en} signal, not demand proof.",
        ),
    )
```

- [ ] **Step 3: Implement recent-item synthesis helper**

Add helper:

```python
def _recent_item_synthesis(title: str, *, source_name: str, section_key: RowOneSectionKey) -> tuple[LocalizedText, LocalizedText, LocalizedText]:
    section = _section_title(section_key)
    return (
        LocalizedText(
            zh=f"《{title}》这条来自 {source_name} 的新近内容被纳入今日{section.zh}。",
            en=f"{title} from {source_name} is included in today's {section.en}.",
        ),
        LocalizedText(
            zh=f"这是一条来自 {source_name} 的本地保留条目，尚未额外推断市场地域或需求规模。",
            en=f"This is a retained local item from {source_name}; ROW ONE does not infer market region or demand size from it.",
        ),
        LocalizedText(
            zh=f"把它作为 {source_name} 的快速阅读入口，再进入原始来源核对细节。",
            en=f"Use it as a fast {source_name} reading entry point, then open the original source for details.",
        ),
    )
```

- [ ] **Step 4: Wire synthesis into all story constructors**

In `_story_from_entity`, `_story_from_candidate`, and `_story_from_recent_item`,
call the appropriate helper before creating `RowOneStory`, then pass:

```python
editorial_takeaway=editorial_takeaway,
signal_context=signal_context,
reader_path=reader_path,
```

- [ ] **Step 5: Run edition tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_edition.py -q
```

Expected: PASS.

## Task 3: Render Synthesis In HTML And JSON

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Update render fixture**

In `_edition()` in `tests/test_row_one_render.py`, populate the new
`RowOneStory` fields:

```python
editorial_takeaway=LocalizedText(
    zh="The Row 是今日重点信号。",
    en="The Row is today's priority signal.",
),
signal_context=LocalizedText(
    zh="本地报告显示它来自 1 个来源。",
    en="The local report shows one supporting source.",
),
reader_path=LocalizedText(
    zh="先看摘要，再打开证据链接。",
    en="Read the brief, then open the evidence link.",
),
```

- [ ] **Step 2: Write failing HTML assertions**

Add assertions to `test_render_row_one_site_escapes_html_and_omits_unsafe_links`:

```python
assert "The Row is today&#x27;s priority signal." in index_html
assert "The local report shows one supporting source." in detail_html
assert "Read the brief, then open the evidence link." in detail_html
```

- [ ] **Step 3: Write JSON assertions**

Add assertions to `test_render_row_one_site_writes_json_payload`:

```python
assert payload["stories"][0]["editorial_takeaway"]["en"] == "The Row is today's priority signal."
assert payload["stories"][0]["signal_context"]["zh"] == "本地报告显示它来自 1 个来源。"
assert payload["stories"][0]["reader_path"]["en"] == "Read the brief, then open the evidence link."
```

- [ ] **Step 4: Run renderer tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: FAIL until templates render the new fields.

- [ ] **Step 5: Render homepage synthesis**

In `_render_story_card`, add the takeaway `<p>` between the headline block's
closing `</div>` and the existing summary `<p>`:

```python
  <p class="story-takeaway">
    <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
    <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
  </p>
```

- [ ] **Step 6: Render detail synthesis panel**

In `render_detail_html`, before the evidence section, add:

```python
<section class="detail-panel">
  <p class="story-section">Editorial Synthesis</p>
  <h2>How To Read This Signal</h2>
  <p><span data-lang="en">{_esc(story.editorial_takeaway.en)}</span><span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span></p>
  <p><span data-lang="en">{_esc(story.signal_context.en)}</span><span data-lang="zh">{_esc(story.signal_context.zh)}</span></p>
  <p><span data-lang="en">{_esc(story.reader_path.en)}</span><span data-lang="zh">{_esc(story.reader_path.zh)}</span></p>
</section>
```

Add minimal CSS for `.story-takeaway`, `.detail-panel`, and `.story-section` if
no suitable style exists.

- [ ] **Step 7: Run renderer tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: PASS.

## Task 4: Documentation And Boundary Tests

**Files:**
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Write failing docs test assertions**

Add assertions that `docs/row-one.md` mentions:

```python
"editorial synthesis"
"deterministic"
"not translation"
"not LLM"
```

Use the existing docs test style in `tests/test_row_one_docs.py`.

- [ ] **Step 2: Run docs tests and verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 3: Update ROW ONE docs**

Add a section to `docs/row-one.md`:

```markdown
## Editorial Synthesis

ROW ONE adds deterministic editorial synthesis to each generated story. The
synthesis explains the local signal, the report context behind it, and a reader
path for scanning the story. It is generated only from retained local report and
item fields such as section, label, score, source count, source name, title, and
summary.

This is not translation, not LLM generation, not new scoring, and not demand
proof. It does not infer domestic/international market grouping unless explicit
source metadata is added in a future stage.
```

- [ ] **Step 4: Run docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: PASS.

## Task 5: Full Verification And Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-261-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-261-code-review.md` only if completed review output is captured
- Create if primary route is unavailable: `docs/reviews/opencode-stage-261-code-review-prompt.md`
- Create if primary route is unavailable: `docs/reviews/opencode-stage-261-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py -q
```

Expected: PASS.

- [ ] **Step 2: Run full verification**

Run:

```bash
git diff --check
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: PASS.

- [ ] **Step 3: Request primary code review**

Use the current project protocol:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "<diff-scoped Stage 261 code review prompt>"
```

The prompt must include the base SHA, head SHA, spec path, plan path, changed
files, and verification results.

- [ ] **Step 4: Use opencode fallback if primary review is unavailable**

If the primary route is unavailable, do not commit partial unavailable-review
records as completed review artifacts. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-261-code-review-prompt.md)"
```

Capture output to a temporary file first. Commit only one coherent completed
review body with a single verdict and no raw tool traces.

- [ ] **Step 5: Fix Critical and Important findings**

Apply fixes before committing Stage 261. Minor polish can be deferred only if it
does not affect correctness, tests, user requirements, or review protocol.

- [ ] **Step 6: Handoff Summary**

After commit/push, write:

- repo status;
- verified commands;
- uncommitted files;
- next step.

## Review Notes

Please review this stage for:

- whether synthesis is deterministic and derived only from local retained report/item fields;
- whether the added text improves ROW ONE as an information-organizing site without overclaiming;
- whether the fields are modeled explicitly enough for JSON consumers;
- whether the HTML remains escaped and compact;
- whether the boundary still excludes new scraping, connectors, translation, LLM calls, compliance-review product work, demand proof, and platform coverage verification.
