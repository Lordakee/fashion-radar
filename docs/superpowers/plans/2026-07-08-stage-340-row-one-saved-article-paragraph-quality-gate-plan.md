# Stage 340 ROW ONE Saved Article Paragraph Quality Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Filter high-confidence extraction boilerplate out of saved local article paragraphs before sidecar and HTML rendering while preserving terse valid fashion-news paragraphs and existing ROW ONE contracts.

**Architecture:** Keep the change inside the existing local article preparation path. Add a conservative private predicate in `articles.py` and call it from `text_to_local_article_paragraphs()` after paragraph normalization but before max-character accounting, so downstream `paragraphs`, `paragraphs_zh`, content-section indices, detail anchors, article pages, and library excerpts stay aligned.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses/models, deterministic regex/string filtering, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/articles.py`
  - Add private high-confidence paragraph noise patterns.
  - Add `_publishable_local_article_paragraph(paragraph: str) -> bool`.
  - Call the predicate from `text_to_local_article_paragraphs()` before character-budget accounting.
  - Keep fallback, extractor, source, schema, and render behavior unchanged.

- Modify `tests/test_row_one_articles.py`
  - Add focused unit tests for paragraph filtering, budget behavior, short-valid paragraph preservation, fallback behavior, mixed extracted text, and paragraph-index alignment.

- Modify `tests/test_row_one_render.py`
  - Re-run existing Stage 339 local article page and saved article library tests as regression coverage. Add a render assertion only if paragraph filtering causes a currently unguarded anchor/index behavior gap.

- Modify `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`, `tests/test_workflows.py`
  - Document Stage 340 and pin no-contract-change boundaries.

- Create/modify review artifacts under `docs/reviews/`
  - Add compact plan review prompt before implementation.
  - Add code review prompt and review result after implementation.

---

### Task 1: Add failing paragraph quality tests

**Files:**
- Modify: `tests/test_row_one_articles.py`

- [ ] **Step 1: Add filtering test for high-confidence boilerplate**

Add this test near the existing `text_to_local_article_paragraphs()` tests:

```python
def test_text_to_local_article_paragraphs_filters_extraction_boilerplate() -> None:
    text = """
    We use cookies to improve your experience.

    Sign up for our newsletter.

    Share this article.

    Advertisement.

    Image credit: Courtesy of the brand.

    https://example.com/fashion/story

    The Row opened a Milan showroom after buyers cited stronger demand for quiet-luxury tailoring.

    window.__INITIAL_STATE__ = {"tracking": true};

    阅读全文。

    Miu Miu named a new CEO.
    """

    paragraphs = text_to_local_article_paragraphs(text, max_chars=220)

    assert paragraphs == [
        "The Row opened a Milan showroom after buyers cited stronger demand for quiet-luxury tailoring.",
        "Miu Miu named a new CEO.",
    ]
```

- [ ] **Step 2: Add test that filtered paragraphs do not consume budget**

```python
def test_text_to_local_article_paragraphs_filters_noise_before_budgeting() -> None:
    text = """
    Subscribe to continue reading this article and unlock unlimited fashion coverage.

    The Row opened a Milan showroom after buyers cited stronger demand.

    Buyers cited demand.
    """

    paragraphs = text_to_local_article_paragraphs(text, max_chars=95)

    assert paragraphs == [
        "The Row opened a Milan showroom after buyers cited stronger demand.",
        "Buyers cited demand.",
    ]
```

- [ ] **Step 3: Add test preserving terse valid fashion news**

```python
def test_text_to_local_article_paragraphs_preserves_short_valid_fashion_news() -> None:
    text = """
    Prices rose.

    Buyers cited demand.

    The Row opened a showroom.

    Miu Miu named a CEO.

    Zendaya wore Margaux.

    Sales rose 8%.

    品牌发布了新系列。
    """

    assert text_to_local_article_paragraphs(text, max_chars=500) == [
        "Prices rose. Buyers cited demand. The Row opened a showroom. Miu Miu named a CEO.",
        "Zendaya wore Margaux. Sales rose 8%. 品牌发布了新系列。",
    ]
```

- [ ] **Step 4: Add fallback test for low-quality-only extracted article text**

Use the existing helper patterns in `tests/test_row_one_articles.py` for `_edition()`, `_source()`, and fake extractors. The assertion should confirm:

```python
assert article.body_source == "summary_fallback"
assert article.reason == "no_publishable_paragraphs"
assert article.title == story.headline
assert article.paragraphs
assert all("Subscribe to continue" not in paragraph for paragraph in article.paragraphs)
```

- [ ] **Step 5: Add mixed extracted text and index-alignment test**

Create an extractor result whose text starts with boilerplate and then includes valid paragraph text that references existing story entities/products. Assert:

```python
assert article.body_source == "extracted"
assert article.paragraphs[0].startswith("The Row")
assert len(article.paragraphs_zh) == len(article.paragraphs)
for section in article.content_sections:
    for item in section.items:
        for index in item.paragraph_indices:
            assert 0 <= index < len(article.paragraphs)
```

- [ ] **Step 6: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py -q
```

Expected: new filtering tests fail because boilerplate is still emitted as publishable paragraphs.

---

### Task 2: Implement deterministic paragraph quality gate

**Files:**
- Modify: `src/fashion_radar/row_one/articles.py`

- [ ] **Step 1: Add private regex patterns near module constants**

Add conservative patterns below `LOCAL_ARTICLE_STORY_ID_RE`:

```python
LOCAL_ARTICLE_NOISE_FULL_RE = re.compile(
    r"^(?:"
    r"advertisement|sponsored content|paid post|"
    r"share this article|share article|back to top|skip to content|"
    r"related articles?|more from .+|"
    r"sign up for (?:our )?newsletter|subscribe to (?:our )?newsletter|"
    r"download (?:our )?app|follow us on (?:instagram|tiktok|x|twitter)|"
    r"subscribe to continue(?: reading)?|sign in(?: to continue)?|"
    r"create an account|already a subscriber|free article limit|"
    r"we use cookies|accept cookies|manage preferences|privacy policy|"
    r"image credit:?.+|photo:?.+|courtesy of .+|"
    r"copyright .+|all rights reserved|rss feed|"
    r"阅读全文|点击查看全文|订阅|登录后继续|广告|分享本文"
    r")\.?$",
    re.IGNORECASE,
)
LOCAL_ARTICLE_NOISE_PREFIX_RE = re.compile(
    r"^(?:"
    r"by [A-Z][A-Za-z .'-]{1,80}|"
    r"published on .+|updated on .+|"
    r"last modified .+|"
    r"\d{1,2} [A-Z][a-z]+ \d{4}|"
    r"[A-Z][a-z]+ \d{1,2}, \d{4}"
    r")$"
)
LOCAL_ARTICLE_CODE_FRAGMENT_RE = re.compile(
    r"(?:<script\b|</script>|window\.|document\.|function\s*\(|"
    r"\{[^{}]{0,80}:[^{}]{0,80}\}|[.#]?[a-z0-9_-]+\s*\{[^{}]*\})",
    re.IGNORECASE,
)
LOCAL_ARTICLE_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
```

- [ ] **Step 2: Add `_publishable_local_article_paragraph()`**

Add below `text_to_local_article_paragraphs()` or near paragraph helpers:

```python
def _publishable_local_article_paragraph(paragraph: str) -> bool:
    normalized = normalize_row_one_paragraph(paragraph)
    if not normalized:
        return False
    folded = normalized.casefold()
    compact = re.sub(r"\s+", " ", normalized).strip()
    if LOCAL_ARTICLE_NOISE_FULL_RE.fullmatch(compact):
        return False
    if len(compact) <= 140 and LOCAL_ARTICLE_NOISE_PREFIX_RE.fullmatch(compact):
        return False
    if LOCAL_ARTICLE_CODE_FRAGMENT_RE.search(compact):
        return False
    url_matches = LOCAL_ARTICLE_URL_RE.findall(compact)
    if url_matches and (
        len(compact) <= 120
        or sum(len(match) for match in url_matches) / max(len(compact), 1) >= 0.35
    ):
        return False
    if folded in {"menu", "search", "newsletter", "cookies", "privacy", "advertising"}:
        return False
    if folded in {"菜单", "搜索", "订阅", "登录", "广告", "隐私"}:
        return False
    return True
```

Adjust exact pattern details if tests show false positives, but keep the function conservative.

- [ ] **Step 3: Call predicate from `text_to_local_article_paragraphs()`**

Change:

```python
        if not paragraph:
            continue
        remaining = max_chars - used_chars
```

to:

```python
        if not paragraph:
            continue
        if not _publishable_local_article_paragraph(paragraph):
            continue
        remaining = max_chars - used_chars
```

- [ ] **Step 4: Run focused article tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py -q
```

Expected: pass.

---

### Task 3: Document Stage 340 and pin boundaries

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add Stage 340 documentation paragraph**

Add this exact boundary paragraph to both `README.md` and `docs/row-one.md` near the existing Stage 339/320 ROW ONE stage history:

```text
Stage 340 adds a Saved Article Paragraph Quality Gate for local article bodies; it filters high-confidence extraction boilerplate such as cookie banners, newsletter prompts, share widgets, navigation fragments, ads, code fragments, URL-heavy snippets, image credits, RSS fragments, and obvious Chinese read-more/login/share prompts before saved local article paragraphs are written to existing article sidecars and rendered on detail pages, the saved article library, and first-class local article pages; it preserves terse valid fashion-news paragraphs, keeps existing summary fallback behavior when extracted text has no publishable paragraphs, reuses existing content-section paragraph indices and local article anchors, and does not add scraping, fetching, source collection, social connectors, LLM summaries, ranking, trend scoring, heat scoring, compliance review, scheduling, deployment behavior, schema changes, new JSON artifacts, or changes to row-one-app/v7, row-one-manifest/v1, or row-one-runtime/v1.
```

- [ ] **Step 2: Add documentation guard test**

Add `test_row_one_docs_describe_stage_340_saved_article_paragraph_quality_gate_boundary()` in `tests/test_row_one_docs.py`. It should:

```python
expected = "Stage 340 adds a Saved Article Paragraph Quality Gate ..."
for content in (README_TEXT, ROW_ONE_DOC):
    normalized = _normalized(content)
    assert _normalized(expected) in normalized
    stage_340_pos = normalized.index("stage 340")
    stage_339_pos = normalized.index("stage 339")
    assert stage_340_pos < stage_339_pos
    stage_340_slice = normalized[stage_340_pos:stage_339_pos]
    for forbidden in (
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "writes data/saved-article-paragraph-quality-gate.json",
        "writes a new json artifact",
        "adds scraping",
        "adds fetching",
        "adds source collection",
        "adds social connectors",
        "adds llm summaries",
        "adds ranking",
        "adds trend scoring",
        "adds heat scoring",
        "adds compliance review",
        "adds scheduling",
        "adds deployment behavior",
    ):
        assert forbidden not in stage_340_slice
```

Use the repository's existing constants/function names if they differ.

- [ ] **Step 3: Add workflow contract/artifact guards**

In `tests/test_workflows.py`, extend the existing ROW ONE generated-site workflow guard to assert generated contract payloads and cached sidecars do not contain:

```python
(
    '"saved_article_paragraph_quality_gate"',
    '"paragraph_quality_gate"',
    '"saved_paragraph_quality_gate"',
    '"article_paragraph_quality_gate"',
    '"quality_gate"',
    "saved-article-paragraph-quality-gate",
    "paragraph-quality-gate",
    "Saved Article Paragraph Quality Gate",
    "saved-article-paragraph-quality-gate.json",
)
```

Also assert these artifact paths are absent:

```python
output_dir / "saved-article-paragraph-quality-gate.json"
output_dir / "articles" / "saved-article-paragraph-quality-gate.json"
output_dir / "data" / "saved-article-paragraph-quality-gate.json"
output_dir / "saved-article-paragraph-quality-gate.html"
output_dir / "articles" / "saved-article-paragraph-quality-gate.html"
output_dir / "data" / "saved-article-paragraph-quality-gate.html"
```

- [ ] **Step 4: Run docs/workflow focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: pass after documentation and guard updates.

---

### Task 4: Run Stage 339/340 regression verification

**Files:**
- No required edits unless failures reveal a defect.

- [ ] **Step 1: Run local article page/library regression tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "local_article_page or saved_article_library"
```

Expected: pass.

- [ ] **Step 2: Run focused article/docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: pass.

- [ ] **Step 3: Run full verification suite**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git grep -n "ghp_\\|sk-" -- . ':!uv.lock'
```

Expected: pytest and ruff/format/lock/diff checks pass. Secret scan returns no committed secrets.

---

### Task 5: Review, commit, and push

**Files:**
- Create: `docs/reviews/claude-stage-340-code-review-prompt.md`
- Create: `docs/reviews/claude-stage-340-code-review.md`

- [ ] **Step 1: Prepare code review prompt**

Create a compact prompt containing:

- Stage 340 objective and scope.
- Plan path.
- `git diff --stat`.
- Base SHA and HEAD SHA or current uncommitted diff instruction if pre-commit review is used.
- Focus areas: false-positive filtering risk, fallback behavior, paragraph-index alignment, contract stability, docs/workflow guards.

- [ ] **Step 2: Run Claude Code review**

Run the local reviewer with max effort. Use the installed command form supported by this machine, for example:

```bash
claude --effort max < docs/reviews/claude-stage-340-code-review-prompt.md > docs/reviews/claude-stage-340-code-review.md
```

If that exact command is unsupported, inspect `claude --help` and use the equivalent non-interactive local command with max effort.

- [ ] **Step 3: Resolve Critical/Important review findings**

Fix valid findings, re-run focused tests, and re-run review if the fix changes Stage 340 behavior materially.

- [ ] **Step 4: Commit**

Run:

```bash
git status -sb
git add src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py tests/test_row_one_render.py README.md docs/row-one.md tests/test_row_one_docs.py tests/test_workflows.py docs/superpowers/specs/2026-07-08-stage-340-row-one-saved-article-paragraph-quality-gate-design.md docs/superpowers/plans/2026-07-08-stage-340-row-one-saved-article-paragraph-quality-gate-plan.md docs/reviews/claude-stage-340-plan-review-prompt.md docs/reviews/claude-stage-340-plan-review.md docs/reviews/claude-stage-340-code-review-prompt.md docs/reviews/claude-stage-340-code-review.md
git commit -m "Stage 340: add saved article paragraph quality gate"
```

- [ ] **Step 5: Push**

Run:

```bash
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.112.3 push origin main
```

- [ ] **Step 6: Handoff Summary**

Report:

- Repo status.
- Commit SHA.
- Pushed branch.
- Verified commands.
- Uncommitted files.
- Next recommended stage.
