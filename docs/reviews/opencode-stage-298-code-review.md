# opencode Stage 298 Code Review

**Reviewer:** opencode (GLM 5.2, variant `max`)
**Stage:** 298 — ROW ONE bilingual local article bodies
**Base:** `f2c5343` (`Stage 297: enrich short row one local articles`)
**Verdict:** APPROVED

## Findings

### Critical

None.

### Important

None.

### Minor

**M1. Substantial-extracted-text and no-Chinese-source paths render English text
inside the `data-lang="zh"` span.**

In `_story_local_article_paragraph_sets(...)`, when `source_paragraphs_zh` is
`None`, extracted source paragraphs are duplicated verbatim into
`paragraphs_zh`. The render branch then emits the same source paragraph inside
the Chinese span. This is the documented "duplicate when no translation exists"
behavior, makes no claim of translation, and stays inside the free-first/no
external service boundary. No change required.

**M2. `_align_local_article_language_paragraphs(...)` backfills English when
Chinese context under-produces.**

If Chinese context cleaning yields fewer paragraphs than the English context,
the tail is filled with the English context text. This is the same v0.1.0
tradeoff as M1 and is acceptable for this node.

**M3. `summary_zh` length mismatch silently drops the Chinese summary.**

When caller-supplied `source_paragraphs_zh` splits into a different paragraph
count than the English summary, the reset to `list(paragraphs)` discards the
Chinese summary in favor of the English duplicate. This was already flagged as
a non-blocking plan-review note and can be revisited by a future sentence-level
alignment stage.

**M4. `language: str` is unbounded.**

`_local_article_context_text(story, *, language: str = "en")` uses `getattr`
with no default. The helper is private and only called with `"en"` or `"zh"`,
so this is a contract-clarity nit. `Literal["en", "zh"]` would make the intent
explicit. Optional.

## Verification Performed

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q` -> 71 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py` -> All checks passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py` -> 5 files already formatted
- `rg -n "_story_local_article_paragraphs" src/fashion_radar/row_one/ tests/` -> no matches, exit code 1
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -q -k "local_article or row_one_site"` -> 1 passed, 11 deselected

## Answers To Review Questions

1. **Backward-compatible with existing sidecars and model usage?** Yes.
   `paragraphs_zh: list[str] = Field(default_factory=list)` gives Pydantic a
   default for payloads that lack the field, and the render guard falls back to
   plain `<p>` rendering whenever the Chinese list is absent, empty, or
   mismatched.
2. **Paragraph alignment correct for the covered paths?** Yes. Fallback
   failure, cleaned fallback, short extracted text, and substantial extracted
   text are all covered in `tests/test_row_one_articles.py`.
3. **Template preserves legacy plain rendering on missing/mismatched Chinese
   paragraphs?** Yes. The two new render tests cover empty and mismatched
   `paragraphs_zh` branches.
4. **English and Chinese paragraphs escaped safely?** Yes. Both spans go
   through `_esc`, which delegates to `html.escape(..., quote=True)`, and the
   render test covers a Chinese paragraph containing an inline image/onerror
   payload.
5. **`row-one-app/v7` / `edition.json` contract preserved?** Yes. Article
   sidecars are written separately from `data/edition.json`; no app contract
   payload path changed.
6. **Any Critical or Important issues blocking commit/push?** No.

## Verdict

APPROVED. No Critical or Important findings. The implementation is contained,
verified, and safe to commit and push.
