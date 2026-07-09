# Stage 373 Code Review Findings

opencode reviewed the Stage 373 Local Article Body Section Markers implementation and cross-checked the Claude Code review.

## Critical

None.

## Important

None. The generated-site-only boundary, story-scope guard, href safety, body paragraph ordering, Stage 366 filing-cue suppression on marker paragraphs, escaping, tests, docs, and workflow guards are correct.

Focused verification observed by opencode:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_body_section_markers.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "body_section_marker or local_article_body_section_marker or stage_373"
# 13 passed, 496 deselected

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/local_article_body_section_markers.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_article_body_section_markers.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/local_article_body_section_markers.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_article_body_section_markers.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
# 6 files already formatted
```

Claude Code Minor M1 is fixed in code: the Stage 373 workflow guard patches `build_row_one_local_article_body_section_markers` with `raising=True`.

## Minor

**M1: Dead TDD shim retained.**

`tests/test_row_one_render.py` keeps the `try/except ModuleNotFoundError` fallback dataclass for `RowOneLocalArticleBodySectionMarker`. The module now exists, so the branch is dead. This is an established project pattern for TDD-red stubs and requires no action.

**M2: `_support_text` null return path is defensive and untested.**

`local_article_body_section_markers.py` can return `None` only if section body, all item bodies, and paragraph excerpt are empty after a paragraph already passed `paragraph.strip()`. This is effectively unreachable and low risk.

**M3: `zfill(2)` position badge is undocumented and unasserted.**

The marker header renders section positions as zero-padded two-digit strings. This is visually reasonable, but not documented in the spec or asserted by tests.

**M4: Contract-leak denylist is slightly asymmetric.**

The render contract-leak test forbids the singular class name `RowOneLocalArticleBodySectionMarker` and title-case plural names, but not a hypothetical pluralized class name `RowOneLocalArticleBodySectionMarkers`. The feature has no collection class, so this is acceptable.

**M5: Marker rendering is coupled to `include_body_filing_cues`.**

`_render_local_article_paragraphs` only uses `body_section_markers` when `include_body_filing_cues=True`. The sole current caller passes both, so there is no defect today; the coupling is just not expressed at the parameter level.
