# Stage 343 ROW ONE Saved Article Content Organization Group Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site-only summary strips to ROW ONE Saved Article Content Organization groups so `articles/index.html` explains each group’s source breadth, saved-card count, evidence paragraph count, and capped first-seen references before the card grid.

**Architecture:** Keep the feature inside the existing ROW ONE HTML/CSS renderer. Reuse `RowOneSavedArticleContentOrganizationGroup.cards`, existing card references, paragraph indices, and safe detail-path helpers; do not change models, JSON artifacts, source acquisition, extraction, ranking, scheduling, deployment, or app contracts.

**Tech Stack:** Python 3.12, existing dataclasses/Pydantic models in `fashion_radar.row_one`, HTML string rendering in `src/fashion_radar/row_one/templates.py`, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Add constants for summary reference cap.
  - Add a private helper that aggregates safe group cards into metrics and capped reference chips.
  - Insert the summary in `_render_saved_article_content_organization_group()` between group header and grid.
  - Add CSS selectors for `.saved-article-content-organization-summary*`.
- Modify `tests/test_row_one_render.py`
  - Add TDD coverage for summary metrics, safe-path filtering, evidence dedupe, reference escaping/capping, and CSS selectors.
- Modify `README.md` and `docs/row-one.md`
  - Add the Stage 343 boundary paragraph before Stage 342.
- Modify `tests/test_row_one_docs.py`
  - Add a docs guard requiring the Stage 343 paragraph in both docs and verifying it precedes Stage 342.
- Modify `tests/test_workflows.py`
  - Extend the existing ROW ONE write-site workflow guard to assert the summary marker appears only in generated HTML and no Stage 343 contract keys/artifacts are created.

---

### Task 1: Add Failing Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add a render test for group summary metrics and chips**

Add this near the existing saved article content organization render tests:

```python
def test_render_saved_article_content_organization_group_summary() -> None:
    first_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="First summary card", zh="第一张摘要卡"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="First lead", zh="第一条摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 1, 1),
        references=(
            RowOneReference(name="The Row", type="brand", label="brand"),
            RowOneReference(name="Margaux", type="product", label="bag"),
        ),
    )
    second_card = replace(
        first_card,
        title=LocalizedText(en="Second summary card", zh="第二张摘要卡"),
        source_name="Business of Fashion",
        detail_path="details/another-signal-1234567890.html#local-article-content-section-2",
        paragraph_indices=(0,),
        references=(RowOneReference(name="The Row", type="brand", label="brand"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[first_card, second_card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert 'class="saved-article-content-organization-summary"' in section_html
    assert "2 saved cards" in section_html
    assert "2 saved articles" in section_html
    assert "2 sources" in section_html
    assert "3 evidence paragraphs" in section_html
    assert "The Row" in section_html
    assert "Margaux" in section_html
    assert section_html.index('class="saved-article-content-organization-summary"') < (
        section_html.index('class="saved-article-content-organization-grid"')
    )
```

This test intentionally uses two different generated detail-page paths so the
saved-article metric proves distinct article counting.

- [ ] **Step 2: Add a test for same-article multi-section dedupe**

```python
def test_render_saved_article_content_organization_group_summary_dedupes_same_article_sections() -> None:
    base_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="First section", zh="第一栏目"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="First lead", zh="第一条摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    base_card,
                    replace(
                        base_card,
                        title=LocalizedText(en="Second section", zh="第二栏目"),
                        detail_path=(
                            "details/the-row-signal-1234567890.html"
                            "#local-article-content-section-2"
                        ),
                        paragraph_indices=(1,),
                    ),
                ],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert "2 saved cards" in section_html
    assert "1 saved article" in section_html
    assert "2 evidence paragraphs" in section_html
```

- [ ] **Step 3: Add a test for unsafe cards not contributing to summary**

```python
def test_render_saved_article_content_organization_group_summary_filters_unsafe_cards() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe summary card", zh="安全摘要卡"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(RowOneReference(name="Safe Ref", type="brand", label="tracked"),),
    )
    unsafe_card = replace(
        safe_card,
        title=LocalizedText(en="Unsafe summary card", zh="不安全摘要卡"),
        source_name="Unsafe Source",
        detail_path="javascript:alert(1)#local-article-content-section-1",
        paragraph_indices=(0, 1, 2),
        references=(RowOneReference(name="Unsafe Ref", type="brand", label="tracked"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card, unsafe_card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert "1 saved card" in section_html
    assert "1 saved article" in section_html
    assert "1 source" in section_html
    assert "1 evidence paragraph" in section_html
    assert "Safe Ref" in section_html
    assert "Unsafe Ref" not in section_html
    assert "Unsafe Source" not in section_html
    assert "javascript:alert" not in section_html
```

- [ ] **Step 4: Add a test for reference escaping and cap**

```python
def test_render_saved_article_content_organization_group_summary_escapes_and_caps_refs() -> None:
    cards = []
    for index in range(1, 7):
        cards.append(
            RowOneSavedArticleContentOrganizationCard(
                title=LocalizedText(en=f"Card {index}", zh=f"卡片 {index}"),
                source_name="Source",
                section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                section_label=LocalizedText(en="Products", zh="产品"),
                lead=LocalizedText(en="Lead", zh="摘要"),
                detail_path=(
                    "details/the-row-signal-1234567890.html"
                    f"#local-article-content-section-{index}"
                ),
                paragraph_indices=(0,),
                references=(
                    RowOneReference(
                        name=f"Ref <{index}>",
                        type="brand",
                        label=f"Label <{index}>",
                    ),
                ),
            )
        )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="products",
                title=LocalizedText(en="Products", zh="产品"),
                dek=LocalizedText(en="Product context", zh="产品背景"),
                cards=cards,
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert "Ref &lt;1&gt;" in section_html
    assert "Label &lt;1&gt;" in section_html
    assert "Ref <1>" not in section_html
    assert "Ref &lt;6&gt;" not in section_html
```

The reference cap should exclude the sixth chip when the implementation cap is
five. Reference chips use first-seen safe card order, not frequency ranking.

- [ ] **Step 5: Add CSS selector coverage**

```python
def test_row_one_css_includes_saved_article_content_organization_summary_styles() -> None:
    css = row_one_css()

    for selector in (
        ".saved-article-content-organization-summary",
        ".saved-article-content-organization-summary-metric",
        ".saved-article-content-organization-summary-refs",
        ".saved-article-content-organization-summary-ref",
    ):
        assert selector in css
```

- [ ] **Step 6: Run the new tests and verify they fail for the missing feature**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "content_organization_group_summary"
```

Expected: tests fail because the summary strip and CSS selectors do not exist yet.

---

### Task 2: Implement Group Summary Renderer

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add a reference cap constant near saved article constants**

Add:

```python
SAVED_ARTICLE_CONTENT_ORGANIZATION_SUMMARY_MAX_REFS = 5
```

- [ ] **Step 2: Add summary helper near `_render_saved_article_content_organization_group`**

Add:

```python
def _render_saved_article_content_organization_group_summary(
    group: RowOneSavedArticleContentOrganizationGroup,
) -> str:
    safe_cards: list[tuple[RowOneSavedArticleContentOrganizationCard, str]] = []
    for card in group.cards:
        href = _safe_saved_article_content_organization_href(card.detail_path)
        if href is None:
            continue
        safe_cards.append((card, href))
    if not safe_cards:
        return ""

    source_names = {
        normalize_row_one_paragraph(card.source_name).casefold()
        for card, _href in safe_cards
        if normalize_row_one_paragraph(card.source_name)
    }
    detail_paths = {_saved_article_content_organization_detail_path_key(href) for _card, href in safe_cards}
    detail_paths.discard("")
    evidence_keys: set[tuple[str, int]] = set()
    for card, href in safe_cards:
        detail_key = _saved_article_content_organization_detail_path_key(href)
        if not detail_key:
            continue
        for paragraph_index in card.paragraph_indices:
            if not isinstance(paragraph_index, int) or isinstance(paragraph_index, bool):
                continue
            if paragraph_index < 0:
                continue
            evidence_keys.add((detail_key, paragraph_index))
    refs = _saved_article_content_organization_summary_refs(safe_cards)
    ref_block = _render_saved_article_content_organization_summary_refs(refs)
    metrics = "".join(
        (
            _render_saved_article_content_organization_summary_metric(
                _count_label(len(safe_cards), "saved card", "saved cards"),
                f"{len(safe_cards)} 张卡片",
            ),
            _render_saved_article_content_organization_summary_metric(
                _count_label(len(detail_paths), "saved article", "saved articles"),
                f"{len(detail_paths)} 篇文章",
            ),
            _render_saved_article_content_organization_summary_metric(
                _count_label(len(source_names), "source", "sources"),
                f"{len(source_names)} 个来源",
            ),
            _render_saved_article_content_organization_summary_metric(
                _count_label(
                    len(evidence_keys),
                    "evidence paragraph",
                    "evidence paragraphs",
                ),
                f"{len(evidence_keys)} 个证据段落",
            ),
        )
    )
    return f"""      <div class="saved-article-content-organization-summary">
        <div class="saved-article-content-organization-summary-metrics">{metrics}</div>
{ref_block}
      </div>
"""
```

- [ ] **Step 3: Add small supporting helpers**

Add:

```python
def _saved_article_content_organization_detail_path_key(href: str) -> str:
    path, _separator, _fragment = href.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    return str(safe_path) if safe_path is not None else ""


def _render_saved_article_content_organization_summary_metric(
    value_en: str,
    value_zh: str,
) -> str:
    return (
        '<span class="saved-article-content-organization-summary-metric">'
        f'<span data-lang="en">{_esc(value_en)}</span>'
        f'<span data-lang="zh">{_esc(value_zh)}</span>'
        "</span>"
    )


def _saved_article_content_organization_summary_refs(
    safe_cards: Sequence[tuple[RowOneSavedArticleContentOrganizationCard, str]],
) -> list[RowOneReference]:
    # First-seen card order keeps the summary deterministic and cheap.
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for card, _href in safe_cards:
        for ref in card.references:
            name = normalize_row_one_paragraph(ref.name)
            ref_type = normalize_row_one_paragraph(ref.type)
            label = normalize_row_one_paragraph(ref.label)
            if not name:
                continue
            key = (name.casefold(), ref_type.casefold(), label.casefold())
            if key in seen:
                continue
            seen.add(key)
            refs.append(RowOneReference(name=name, type=ref_type, label=label))
            if len(refs) >= SAVED_ARTICLE_CONTENT_ORGANIZATION_SUMMARY_MAX_REFS:
                return refs
    return refs


def _render_saved_article_content_organization_summary_refs(
    refs: Sequence[RowOneReference],
) -> str:
    if not refs:
        return ""
    chips = "".join(
        '<span class="saved-article-content-organization-summary-ref">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(ref.label.strip() or ref.type.strip())}</span>"
        "</span>"
        for ref in refs
    )
    return f"""        <div class="saved-article-content-organization-summary-refs"
          aria-label="Saved article content organization group references">
{chips}
        </div>"""
```

- [ ] **Step 4: Insert summary in group renderer**

Inside `_render_saved_article_content_organization_group`, after `if not cards: return ""`, compute:

```python
summary = _render_saved_article_content_organization_group_summary(group)
```

Insert `{summary}` between the group header and the grid.

- [ ] **Step 5: Add CSS next to existing content organization styles**

Add:

```css
.saved-article-content-organization-summary {
  border: 1px solid var(--line);
  display: grid;
  gap: 8px;
  padding: 10px;
}
.saved-article-content-organization-summary-metrics,
.saved-article-content-organization-summary-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-content-organization-summary-metric,
.saved-article-content-organization-summary-ref {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 5px;
  padding: 6px 8px;
}
.saved-article-content-organization-summary-ref span:last-child {
  color: var(--muted);
}
```

- [ ] **Step 6: Run render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "content_organization_group_summary or saved_article_content_organization"
```

Expected: selected tests pass.

---

### Task 3: Add Documentation And Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add Stage 343 documentation paragraph before Stage 342**

Add this exact paragraph to `README.md` and `docs/row-one.md` before the Stage 342
paragraph:

```markdown
Stage 343 adds generated-site only Saved Article Content Organization group summaries inside `articles/index.html`; it reuses existing saved article content organization groups, existing organization cards, existing card detail-path anchors, existing card references, and existing paragraph indices to show per-group saved-card counts, saved-article counts, source counts, evidence paragraph counts, and capped reference chips before each group grid without changing app-facing contracts; it does not create `data/saved-article-content-organization-summary.json`, does not create `data/content-organization-group-summary.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 2: Add docs guard before the Stage 342 docs guard**

Add:

```python
def test_row_one_docs_describe_stage_343_content_organization_group_summary_boundary() -> None:
    expected = _normalized(
        "Stage 343 adds generated-site only Saved Article Content Organization "
        "group summaries inside `articles/index.html`; it reuses existing saved "
        "article content organization groups, existing organization cards, "
        "existing card detail-path anchors, existing card references, and "
        "existing paragraph indices to show per-group saved-card counts, "
        "saved-article counts, source counts, evidence paragraph counts, and "
        "capped reference chips before each group grid without changing "
        "app-facing contracts; it does not create "
        "`data/saved-article-content-organization-summary.json`, does not "
        "create `data/content-organization-group-summary.json`, does not create "
        "new article-source sidecars, does not create new route families, does "
        "not publish full articles on the library index, does not add outbound "
        "article URLs as primary navigation, does not change row-one-app/v7, "
        "row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, "
        "source collection, fetching, matching, extraction, scoring, ranking, "
        "LLM, connector, scheduling, deployment, market grouping, "
        "domestic/international classification, analytics, personalization, "
        "recommendation, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage_343_pos = normalized.index(
            "stage 343 adds generated-site only saved article content organization"
        )
        stage_342_pos = normalized.index(
            "stage 342 adds generated-site only saved paragraph context cues"
        )
        assert stage_343_pos < stage_342_pos
        stage = normalized[stage_343_pos:stage_342_pos]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "creates `data/saved-article-content-organization-summary.json`",
            "writes `data/saved-article-content-organization-summary.json`",
            "creates `data/content-organization-group-summary.json`",
            "writes `data/content-organization-group-summary.json`",
            "writes a new json artifact",
            "creates new article-source sidecars",
            "creates new route families",
            "publishes full articles on the library index",
            "adds outbound article urls",
            "adds source collection",
            "adds fetching",
            "adds matching",
            "adds extraction",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds deployment behavior",
            "adds analytics",
            "adds personalization",
            "adds recommendation",
            "adds compliance review",
        ):
            assert stale_phrase not in stage
```

- [ ] **Step 3: Extend workflow artifact and contract guards**

In `tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`,
add generated HTML assertion near the existing `articles/index.html` reads:

```python
if 'class="saved-article-content-organization-group"' in articles_html:
    assert 'class="saved-article-content-organization-summary"' in articles_html
```

The workflow fixture may not always build a populated content organization group;
the guard prevents this generated-site assertion from failing when the section is
absent while still requiring the summary whenever a group is present.

Add app-contract negative assertions:

```python
assert "saved_article_content_organization_summary" not in generated_contract_payload
assert "content_organization_group_summary" not in generated_contract_payload
assert "Saved Article Content Organization Group Summary" not in generated_contract_payload
assert "saved-article-content-organization-summary" not in generated_contract_payload
assert "content-organization-group-summary" not in generated_contract_payload
```

Extend the artifact absence list with:

```python
output_dir / "saved-article-content-organization-summary.json",
output_dir / "articles" / "saved-article-content-organization-summary.json",
output_dir / "data" / "saved-article-content-organization-summary.json",
output_dir / "content-organization-group-summary.json",
output_dir / "articles" / "content-organization-group-summary.json",
output_dir / "data" / "content-organization-group-summary.json",
output_dir / "saved-article-content-organization-summary.html",
output_dir / "articles" / "saved-article-content-organization-summary.html",
output_dir / "data" / "saved-article-content-organization-summary.html",
```

- [ ] **Step 4: Run docs and workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: all selected tests pass after implementation.

---

### Task 4: Review, Full Verification, Commit, And Push

**Files:**
- Review all changed files.

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "content_organization_group_summary or saved_article_content_organization"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

- [ ] **Step 3: Request Claude Code review of completed node**

Create `docs/reviews/claude-code-stage-343-code-review-prompt.md`, then run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-343-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-343-code-review.md
rm -f "$tmp_review"
```

Fix all critical and important findings before continuing.

- [ ] **Step 4: Stage and scan for token-shaped secrets**

Run:

```bash
git add README.md docs/row-one.md docs/reviews/claude-code-stage-343-plan-review-prompt.md docs/reviews/claude-code-stage-343-plan-review.md docs/reviews/opencode-stage-343-plan-review-prompt.md docs/reviews/opencode-stage-343-plan-review.md docs/reviews/claude-code-stage-343-code-review-prompt.md docs/reviews/claude-code-stage-343-code-review.md docs/superpowers/specs/2026-07-08-stage-343-saved-article-content-organization-group-summary-design.md docs/superpowers/plans/2026-07-08-stage-343-saved-article-content-organization-group-summary-plan.md src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
if git diff --cached -U0 | rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}'; then exit 1; else echo "No token-shaped secrets in staged diff"; fi
```

- [ ] **Step 5: Commit and push**

Run:

```bash
git commit -m "Stage 343: add content organization group summaries"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

- [ ] **Step 6: Write handoff summary**

Report repo state, pushed commit, verified commands, uncommitted files, and next
step recommendation.
