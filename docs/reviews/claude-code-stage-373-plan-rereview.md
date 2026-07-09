**Re-Review: Stage 373 Local Article Body Section Markers - Post-opencode I1 Fix**

---

## Critical

None remain.

---

## Important

None remain.

All seven items from the original reviews are addressed in the current plan:

- **Story scope (C1):** Markers are now pre-built in `render_local_article_page_html` where `story` is in scope, then passed as keyword-only args through `_render_local_article` and `_render_local_article_paragraphs`. The plan explicitly prohibits calling the builder inside `_render_local_article_paragraphs`. Resolved.
- **Strict-index duplication policy (C2):** Validation stays local to the new builder with a mandatory alignment comment; the plan locks the same bool/non-int/negative/overflow/duplicate/blank-paragraph semantics. Opencode independently called this acceptable. Resolved.
- **Existing fragment regex reuse (I1):** Task 5 Step 2 names both `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` and `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` explicitly and requires `_safe_local_article_body_section_marker_href` to reuse them. Resolved.
- **Exact monkeypatch target (I2):** Plan names `fashion_radar.row_one.templates.build_row_one_local_article_body_section_markers` in both the "Plan Review Fixes" section and Task 6 Step 2. Resolved.
- **Helper determinism (I3):** `_story()` and `_article()` signatures are fully specified in Task 2 Step 1 with default `story_id="the-row-signal-1234567890"`, covering matched, mismatched, and unsafe-id variants. Resolved.
- **Chinese fallback title (M1):** Plan specifies `LocalizedText(en=f"Section {section_position}", zh=f"第 {section_position} 节")` in Task 3 Step 2 and the design spec. Resolved.
- **Stage 366 filing-cue interaction (opencode I1):** Plan suppresses `_render_local_article_body_filing_cue` on any paragraph carrying a Stage 373 marker; the render test asserts that paragraph does not carry `class="local-article-body-filing-cue"`. Both the design spec Rendering Contract and Task 5 Step 4 state this rule. Resolved.

---

## Minor

**M1 (opencode M2 — non-int rejection branch coverage at helper level):** The invalid-index builder test uses `paragraph_indices=[True, "0", -1, 0, 1, 1, 99]` and asserts only `paragraph_index == 1` is emitted. This proves the user-visible outcome. It does not add a direct unit test on the private strict-index helper itself, so if `RowOneLocalArticleContentItem.paragraph_indices: list[int]` coerces a string `"0"` before the builder sees it, the `non-int` defensive branch is silently untested. Acceptable at this stage; worth noting for a future helper-extraction step.

The other three opencode minors (M3 first non-empty item body, M4 content-section anchor assertion, and M1 duplication comment) are resolved in the current plan.
