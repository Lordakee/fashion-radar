# Stage 298 ROW ONE Bilingual Local Article Body Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ROW ONE detail-page local article bodies participate in the existing English/Chinese language toggle when ROW ONE already has Chinese story context, without adding translation services or changing source collection.

**Architecture:** Add an optional `paragraphs_zh` list to `RowOneLocalArticle` sidecars. Build English local article paragraphs exactly as Stage 297 does; build Chinese companion paragraphs from existing ROW ONE Chinese fields for summary/context fallback and duplicate source-language extracted paragraphs when no translation exists. Render bilingual paragraph spans only when `paragraphs_zh` aligns with `paragraphs`; otherwise keep the current plain rendering for backward compatibility.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

Stage 297 ensures every generated detail page has useful local article content, but the local article body itself is still effectively monolingual. The section heading has `Local Article / 本地正文`, while the body remains plain source-language paragraphs. Stage 298 improves the content layer: source-extracted paragraphs remain faithful to the source language, and ROW ONE-generated fallback/context paragraphs get Chinese counterparts from existing `RowOneStory` localized fields.

This is not a translation feature. It does not call external models or services, does not alter collection, and does not claim source text has been translated. It uses only data already present in `RowOneStory`.

## File Structure

- Modify `src/fashion_radar/row_one/models.py`
  - Add `paragraphs_zh: list[str] = Field(default_factory=list)` to `RowOneLocalArticle`.
- Modify `src/fashion_radar/row_one/articles.py`
  - Build aligned English/Chinese local article paragraph lists.
  - Use story Chinese fields for fallback/context paragraphs.
  - Duplicate extracted source paragraphs into `paragraphs_zh` when no Chinese source paragraph exists.
  - Replace and remove the Stage 297 `_story_local_article_paragraphs(...)` helper so it does not remain as dead code.
- Modify `src/fashion_radar/row_one/templates.py`
  - Render local article paragraphs as paired language spans only when `paragraphs_zh` length matches `paragraphs`.
  - Preserve current plain rendering when no aligned Chinese list exists.
- Modify `tests/test_row_one_articles.py`
  - Assert Stage 297 short/fallback enrichment now populates `paragraphs_zh`.
  - Assert substantial extraction without ROW ONE enrichment duplicates source paragraphs for language-toggle consistency.
- Modify `tests/test_row_one_render.py`
  - Assert `paragraphs_zh` is written to sidecar JSON.
  - Assert bilingual paragraph spans render correctly.
  - Assert old/plain local articles without `paragraphs_zh` still render safely.
  - Assert Chinese paragraph content is escaped safely.

## Task 1: Plan Review Gate

- [ ] Create `docs/reviews/claude-code-stage-298-plan-review-prompt.md` and `docs/reviews/opencode-stage-298-plan-review-prompt.md`.
- [ ] Attempt Claude Code plan review with `--effort max`; if unavailable, record `Verdict: UNAVAILABLE`.
- [ ] Run opencode fallback plan review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- [ ] Fix Critical/Important findings before implementation.

## Task 2: RED Article Builder Tests

- [ ] **Step 1: Assert fallback failure builds Chinese paragraphs**

In `tests/test_row_one_articles.py`, update `test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure`:

```python
article = articles["the-row-signal-1234567890"]
assert article.paragraphs == [
    "Summary",
    "Editorial",
    "Important",
    "Context",
    "Path",
]
assert article.paragraphs_zh == [
    "摘要",
    "编辑",
    "重要",
    "背景",
    "路径",
]
```

- [ ] **Step 2: Assert skipped/cleaned fallback keeps Chinese companion list**

In `test_build_row_one_local_articles_cleans_fallback_without_mutating_story_summary`, keep the existing `paragraphs` expectation and add:

```python
assert articles["the-row-signal-1234567890"].paragraphs_zh == [
    "摘要",
    "编辑",
    "重要",
    "背景",
    "路径",
]
```

This accepts that a cleaned source summary may not have a sentence-level Chinese translation; the first Chinese paragraph remains the stored story summary.

- [ ] **Step 3: Assert short extracted text duplicates source paragraph and localizes context**

In `test_build_row_one_local_articles_enriches_short_extracted_text`, add:

```python
assert articles["the-row-signal-1234567890"].paragraphs_zh == [
    "Tiny source note.",
    "编辑",
    "重要",
    "背景",
    "路径",
]
```

- [ ] **Step 4: Assert substantial extracted text gets aligned source-language companion paragraphs**

In `test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text`, add:

```python
assert articles["the-row-signal-1234567890"].paragraphs_zh == paragraphs
```

- [ ] **Step 5: Run RED tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_cleans_fallback_without_mutating_story_summary \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_enriches_short_extracted_text \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text \
  -q
```

Expected before implementation: tests fail with `AttributeError` or empty `paragraphs_zh`.

## Task 3: GREEN Article Builder Implementation

- [ ] **Step 1: Add the optional model field**

In `src/fashion_radar/row_one/models.py`, change `RowOneLocalArticle`:

```python
class RowOneLocalArticle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    story_id: str
    title: str | None = None
    url: str
    source_name: str
    extracted_at: datetime
    published_at: datetime | None = None
    paragraphs: list[str] = Field(default_factory=list)
    paragraphs_zh: list[str] = Field(default_factory=list)
    skipped: bool = False
    reason: str | None = None
```

- [ ] **Step 2: Add language-specific context helper**

In `src/fashion_radar/row_one/articles.py`, replace `_local_article_context_text(story)` with:

```python
def _local_article_context_text(story: RowOneStory, *, language: str = "en") -> str:
    return "\n\n".join(
        text
        for text in (
            getattr(story.editorial_takeaway, language),
            getattr(story.why_it_matters, language),
            getattr(story.signal_context, language),
            getattr(story.reader_path, language),
        )
        if text.strip()
    )
```

- [ ] **Step 3: Replace summary/context paragraph helper**

Delete the existing `_story_local_article_paragraphs(...)` helper and replace it
with:

```python
def _story_local_article_paragraph_sets(
    story: RowOneStory,
    text: str,
    *,
    max_chars: int,
    source_paragraphs_zh: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    paragraphs = text_to_local_article_paragraphs(text, max_chars=max_chars)
    if not paragraphs:
        return [], []
    paragraphs_zh = list(source_paragraphs_zh or paragraphs)
    if len(paragraphs_zh) != len(paragraphs):
        paragraphs_zh = list(paragraphs)

    total_chars = sum(len(paragraph) for paragraph in paragraphs)
    if total_chars >= min(max_chars, LOCAL_ARTICLE_MIN_CONTEXT_CHARS):
        return paragraphs, paragraphs_zh

    context_text_en = _local_article_context_text(story, language="en")
    if not context_text_en:
        return paragraphs, paragraphs_zh

    context_paragraphs_en = text_to_local_article_paragraphs(
        context_text_en,
        max_chars=max_chars - total_chars,
    )
    if not context_paragraphs_en:
        return paragraphs, paragraphs_zh

    context_paragraphs_zh = text_to_local_article_paragraphs(
        _local_article_context_text(story, language="zh"),
        max_chars=max_chars,
    )
    context_paragraphs_zh = _align_local_article_language_paragraphs(
        context_paragraphs_en,
        context_paragraphs_zh,
    )
    return [*paragraphs, *context_paragraphs_en], [*paragraphs_zh, *context_paragraphs_zh]
```

After this step, `src/fashion_radar/row_one/articles.py` must not contain a
definition named `_story_local_article_paragraphs`.

- [ ] **Step 4: Add alignment helper**

Add:

```python
def _align_local_article_language_paragraphs(
    paragraphs: list[str],
    paragraphs_zh: list[str],
) -> list[str]:
    aligned = list(paragraphs_zh[: len(paragraphs)])
    if len(aligned) < len(paragraphs):
        aligned.extend(paragraphs[len(aligned) :])
    return aligned
```

- [ ] **Step 5: Use paragraph sets in extracted path**

In `_build_story_local_article(...)`, replace:

```python
paragraphs = _story_local_article_paragraphs(
    story,
    result.text,
    max_chars=source.row_one_article.max_chars,
)
if not paragraphs:
    return _fallback_story_summary_article(story, url, source, extracted_at=extracted_at)
return RowOneLocalArticle(
    ...
    paragraphs=paragraphs,
    ...
)
```

with:

```python
paragraphs, paragraphs_zh = _story_local_article_paragraph_sets(
    story,
    result.text,
    max_chars=source.row_one_article.max_chars,
)
if not paragraphs:
    return _fallback_story_summary_article(story, url, source, extracted_at=extracted_at)
return RowOneLocalArticle(
    ...
    paragraphs=paragraphs,
    paragraphs_zh=paragraphs_zh,
    ...
)
```

- [ ] **Step 6: Use paragraph sets in fallback path**

In `_fallback_story_summary_article(...)`, replace the paragraph build with:

```python
summary_zh = text_to_local_article_paragraphs(
    story.summary.zh,
    max_chars=source.row_one_article.max_chars,
)
paragraphs, paragraphs_zh = _story_local_article_paragraph_sets(
    story,
    story.summary.en,
    max_chars=source.row_one_article.max_chars,
    source_paragraphs_zh=summary_zh,
)
```

Pass both fields into `RowOneLocalArticle`.

- [ ] **Step 7: Run GREEN article tests**

Run the command from Task 2 Step 5. Expected: all selected tests pass.

## Task 4: RED Render Tests

- [ ] **Step 1: Update local article render test**

In `tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content`, construct `RowOneLocalArticle` with:

```python
paragraphs_zh=[
    "第一段本地正文，关于 The Row 需求。",
    "第二段本地正文，补充造型语境。",
],
```

Add assertions:

```python
assert '<span data-lang="en">First local paragraph about The Row demand.</span>' in detail_html
assert '<span data-lang="zh">第一段本地正文，关于 The Row 需求。</span>' in detail_html
assert article_json["paragraphs_zh"] == [
    "第一段本地正文，关于 The Row 需求。",
    "第二段本地正文，补充造型语境。",
]
```

- [ ] **Step 2: Add missing Chinese list fallback test**

Add:

```python
def test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs(tmp_path) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["One source paragraph.", "Second source paragraph."],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert "<p>One source paragraph.</p>" in detail_html
    assert "<p>Second source paragraph.</p>" in detail_html
    assert 'data-lang="zh">One source paragraph.' not in detail_html
```

- [ ] **Step 3: Add mismatched Chinese list fallback test**

Add:

```python
def test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch(tmp_path) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["One source paragraph.", "Second source paragraph."],
        paragraphs_zh=["一段中文。"],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert "<p>One source paragraph.</p>" in detail_html
    assert "<p>Second source paragraph.</p>" in detail_html
    assert '<span data-lang="zh">一段中文。</span>' not in detail_html
```

- [ ] **Step 4: Extend escaping coverage for Chinese paragraphs**

In `test_render_row_one_detail_escapes_local_article_content`, add:

```python
paragraphs_zh=[
    '<img src=x onerror="alert(1)"> 中文 & quoted text',
],
```

and assert:

```python
assert (
    "&lt;img src=x onerror=&quot;alert(1)&quot;&gt; 中文 &amp; quoted text"
    in detail_html
)
assert 'onerror="alert' not in detail_html
```

- [ ] **Step 5: Run RED render tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs \
  tests/test_row_one_render.py::test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch \
  tests/test_row_one_render.py::test_render_row_one_detail_escapes_local_article_content \
  -q
```

Expected before implementation: bilingual span assertions fail; the new mismatch test may fail until rendering fallback is added.

## Task 5: GREEN Render Implementation

- [ ] **Step 1: Update `_render_local_article` paragraph rendering**

In `src/fashion_radar/row_one/templates.py`, replace the current `paragraphs = [...]` block with:

```python
paragraphs = _render_local_article_paragraphs(article)
```

Add:

```python
def _render_local_article_paragraphs(article: RowOneLocalArticle) -> list[str]:
    source_paragraphs = [paragraph for paragraph in article.paragraphs if paragraph.strip()]
    if not source_paragraphs:
        return []
    if len(article.paragraphs_zh) != len(article.paragraphs):
        return [f"      <p>{_esc(paragraph)}</p>" for paragraph in source_paragraphs]
    rendered: list[str] = []
    for paragraph_en, paragraph_zh in zip(article.paragraphs, article.paragraphs_zh, strict=True):
        if not paragraph_en.strip():
            continue
        zh = paragraph_zh if paragraph_zh.strip() else paragraph_en
        rendered.append(
            "      <p>"
            f'<span data-lang="en">{_esc(paragraph_en)}</span>'
            f'<span data-lang="zh">{_esc(zh)}</span>'
            "</p>"
        )
    return rendered
```

- [ ] **Step 2: Run GREEN render tests**

Run the command from Task 4 Step 5. Expected: all selected tests pass.

## Task 6: Verification And Site Proof

- [ ] Run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
rg -n "def _story_local_article_paragraphs" src/fashion_radar/row_one/articles.py
```

Expected for the `rg` command: exit code `1` and no matches.

- [ ] Run release gate:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv lock --check
```

- [ ] Rebuild today's site:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-05T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
```

- [ ] Run a proof script that verifies:
  - `story_count == 18`
  - `data/articles/*.json == 18`
  - each article sidecar has `paragraphs`
  - each article sidecar has `paragraphs_zh`
  - `len(paragraphs_zh) == len(paragraphs)` for every sidecar
  - every detail page with `id="local-article"` includes at least one `data-lang="zh"` paragraph span

## Task 7: Code Review, Commit, Push

- [ ] Create `docs/reviews/claude-code-stage-298-code-review-prompt.md` and `docs/reviews/opencode-stage-298-code-review-prompt.md`.
- [ ] Attempt Claude Code with `--effort max`; record `Verdict: UNAVAILABLE` if it does not produce a completed body.
- [ ] Run opencode code review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- [ ] Fix Critical/Important findings.
- [ ] Commit and push:

```bash
git add src/fashion_radar/row_one/models.py \
  src/fashion_radar/row_one/articles.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_articles.py \
  tests/test_row_one_render.py \
  docs/superpowers/plans/2026-07-05-stage-298-row-one-bilingual-local-article-body-plan.md \
  docs/reviews/claude-code-stage-298-*.md \
  docs/reviews/opencode-stage-298-*.md
git diff --cached --check
git commit -m "Stage 298: add bilingual row one local article bodies"
git push origin main
```

## Handoff Summary Template

```markdown
**Handoff Summary**
- Repo: `/home/ubuntu/fashion-radar`
- Branch/commit: `main` at `<sha>`, pushed to `origin/main`
- Verified commands: focused article/render tests, full suite, ruff, release hygiene, uv lock, today site rebuild bilingual sidecar proof
- Uncommitted files: `<git status --short>`
- Generated site: `reports/row-one/site` rebuilt but ignored
- Next step: continue local content depth or content presentation polish.
```
