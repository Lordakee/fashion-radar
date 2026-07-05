# opencode Stage 298 Plan Review

**Reviewer:** opencode (GLM 5.2, variant `max`)
**Plan:** `docs/superpowers/plans/2026-07-05-stage-298-row-one-bilingual-local-article-body-plan.md`
**Verdict:** APPROVED — no Critical or Important findings; proceed to implementation after fixing the Claude Code I1 dead-code note (already covered by the plan text).

## Findings

### Critical

None.

### Important

None.

### Minor

**M1. `source_paragraphs_zh` is discarded on length mismatch (by design).**
In `_story_local_article_paragraph_sets`, when the caller-supplied Chinese
summary list (`source_paragraphs_zh`) has a different length than the
recomputed English `paragraphs`, the reset
`paragraphs_zh = list(paragraphs)` replaces the Chinese summary with the
English source text. The same applies to extracted source text where
`source_paragraphs_zh` is `None` and `paragraphs_zh` starts as an English
duplicate. This is the documented "duplicate when no translation" behavior
and is acceptable for v0.1.0, but implementers should be aware that a real
multi-sentence `story.summary.zh` that splits into a different paragraph
count than `story.summary.en` will be dropped in favor of English duplicate
text. No change required.

**M2. Step ordering in Task 3 forward-references later helpers.**
Task 3 Step 3 (`_story_local_article_paragraph_sets`) calls
`_align_local_article_language_paragraphs` (defined in Step 4) and the new
language-parameterized `_local_article_context_text` (Step 2). Python
resolves module-level functions at call time, so this works, but the
sequencing reads awkwardly. Implementers may define Step 4 before Step 3 to
keep definition-before-use order; the result is identical.

**M3. `language` parameter is an unbounded `str`.**
`_local_article_context_text(story, *, language: str = "en")` uses
`getattr(story.editorial_takeaway, language)`. Because no default is passed
to `getattr`, an invalid language raises `AttributeError`. The helper is
internal-only and always called with `"en"` or `"zh"`, so this is safe, but
`Literal["en", "zh"]` would make the contract explicit. Optional.

**M4. Proof script in Task 6 is prose-only.**
The site-rebuild proof (18 sidecars, `paragraphs_zh` present,
`len(paragraphs_zh) == len(paragraphs)`, at least one `data-lang="zh"`
span per detail page) is described in narrative form without a committed
script path. This matches prior stages' style, and the `rg` guard plus the
pytest assertions in Tasks 2 and 4 already enforce the invariants in CI.
No change required.

## Answers To Review Questions

1. **Technical feasibility with current architecture?** Yes. The change
   touches exactly four files (`models.py`, `articles.py`, `templates.py`,
   and the two test files) and reuses the existing
   `text_to_local_article_paragraphs` pipeline, the existing `_esc` HTML
   escaper (`templates.py:2377`, `html.escape(quote=True)`), and the
   existing `[data-lang="en"]` / `[data-lang="zh"]` CSS toggle rules at
   `templates.py:1193-1196`. All three `RowOneLocalArticle` construction
   sites are covered: `articles.py:198` (extracted path, Task 3 Step 5),
   `articles.py:225` (fallback path, Task 3 Step 6), and the model itself
   (`models.py:37`, Task 3 Step 1). The sidecar JSON writer at
   `render.py:172` uses `article.model_dump(mode="json")`, so
   `paragraphs_zh` is auto-serialized with no extra wiring.

2. **Backward compatibility for legacy articles without `paragraphs_zh`?**
   Yes, double-covered. (a) `paragraphs_zh: list[str] = Field(default_factory=list)`
   lets Pydantic validate any future JSON missing the field. (b) The render
   helper's guard
   `if len(article.paragraphs_zh) != len(article.paragraphs): return [plain <p>]`
   falls back to the Stage 297 plain rendering whenever the Chinese list is
   absent, empty, or mismatched. Task 4 Step 2 (`test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs`)
   and Step 3 (`test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch`)
   exercise both branches directly. Note that on-disk sidecars are
   regenerated each build, so there is no on-disk migration concern; the
   backward-compat path is defensive.

3. **Are the planned tests sufficient?** Yes. Coverage matrix:
   - Bilingual rendering happy path: Task 4 Step 1
     (`test_render_row_one_detail_includes_local_article_content`) asserts
     both `data-lang="en"` and `data-lang="zh"` spans and the sidecar JSON
     `paragraphs_zh` payload.
   - Missing Chinese list: Task 4 Step 2 asserts plain `<p>` rendering and
     that no `data-lang="zh"` span leaks.
   - Mismatched Chinese list: Task 4 Step 3 asserts plain `<p>` rendering
     even when `paragraphs_zh` is non-empty but length-mismatched.
   - Escaping: Task 4 Step 4 extends
     `test_render_row_one_detail_escapes_local_article_content` with a
     Chinese span containing `<img src=x onerror="alert(1)"> 中文 & quoted text`
     and asserts the escaped form plus `'onerror="alert' not in detail_html`.
     `_esc` uses `html.escape(quote=True)`, which produces the expected
     `&lt;`, `&gt;`, `&amp;`, `&quot;` sequences.
   - Article-builder population: Task 2 covers the fallback failure path
     (Step 1), the cleaned fallback path (Step 2), short extracted text
     (Step 3), and substantial extracted text (Step 4). The expected
     `paragraphs_zh` lists were traced against the `_edition()` fixture's
     Chinese fields (`摘要`, `编辑`, `重要`, `背景`, `路径`) and match the
     `_story_local_article_paragraph_sets` + `_align_local_article_language_paragraphs`
     logic, including the case where Chinese context produces more
     paragraphs than the English budget allows (alignment truncates to the
     English count).

   The existing `test_build_row_one_local_articles_enriches_after_unusable_source_tail`
   (max_chars=38) is not modified by the plan but continues to pass:
   `paragraphs == ["Tiny source note.", "Editorial", "Important"]` and
   `sum(len) <= 38` still hold; `paragraphs_zh` is auto-populated but
   unchecked by that test. `test_workflows.py:269`
   (`test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`)
   is also unbroken: its single source paragraph appears in both the
   English span and (duplicated) the Chinese span, so the substring
   assertions against `detail_html` and `cached_article` still hit.

4. **Critical or Important issues to fix before implementation?** None.

   The prior Claude Code partial review's I1 (dead-code
   `_story_local_article_paragraphs`) is already handled by the plan:
   - File Structure section line 27: "Replace and remove the Stage 297
     `_story_local_article_paragraphs(...)` helper so it does not remain as
     dead code."
   - Task 3 Step 3: "Delete the existing `_story_local_article_paragraphs(...)`
     helper and replace it with:" the new `_story_local_article_paragraph_sets`.
   - Task 6 verification: `rg -n "def _story_local_article_paragraphs" src/fashion_radar/row_one/articles.py`
     with expected exit code 1 and no matches.

   The Claude Code partial review ended before reaching these sections, so
   its I1 is a false positive against the current plan text. No additional
   fix is needed.

## Result

Proceed to Task 2 (RED Article Builder Tests). The plan is technically
sound, backward-compatible, does not change the `row-one-app/v7` contract
(article sidecars at `data/articles/*.json` are not part of the app
contract payload), does not add translation services or platform
collection, and stays within the Stage 297 boundary of operating only on
data already present in `RowOneStory`.
