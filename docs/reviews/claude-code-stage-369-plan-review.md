Here is the plan review for Stage 369.

---

## Stage 369 Plan Review — Local Article Intelligence Brief

**Reviewed:** `docs/superpowers/specs/2026-07-09-stage-369-local-article-intelligence-brief-design.md` and `docs/superpowers/plans/2026-07-09-stage-369-local-article-intelligence-brief-plan.md`
**Codebase checked:** models, templates, saved_article_body_organizer (Stage 368), saved_article_local_section_binder, render, articles, fragment regexes

---

### Critical

**C-1 — Chip cap constant conflicts between design doc and plan.**

- Design doc: "max 4 chips per lane"
- Plan Task 4 constants: `LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE = 5`

The test in Task 2 imports and exercises this constant. If the implementor writes the test against the design's "4" but creates the constant as "5", the capping tests will either silently pass with wrong semantics or fail. One value must be canonical before Task 2 starts. Resolve the spec doc first, then carry the corrected number into the constant.

---

### Important

**I-1 — `_reference_lane_key` mapping is unspecified in both docs.**

`RowOneReference.type` is a plain `str` with no enum constraint. The plan lists `_reference_lane_key` as a private helper that must map `type` values to the "brands / products / people / themes" lane keys, but neither the design doc nor the plan defines which `type` strings map to which lane. At runtime this controls whether any lane emits chips at all.

The fix before implementation: add a `_LANE_KEY_BY_REFERENCE_TYPE` mapping constant to the design (or equivalently to the builder spec section in the plan) that lists the expected `type` values for each lane. This is cheap to add now and prevents an entire section rendering empty on first run.

**I-2 — Paragraph assertion wording in Task 2 filter test uses "paragraph 0" to mean two different things.**

The test says:
- "Assert only paragraph `0` is emitted as evidence." — means the *data item* at index 0.
- "Assert no paragraph 0, 2, 100, negative, bool, or string href appears." — means the *rendered anchor* `#local-article-paragraph-0`, which is structurally invalid because paragraph anchors are 1-based (`index + 1`).

A developer reading the two lines back-to-back can infer the opposite: that index 0 should both be emitted and not appear. Clarify the second assertion to read "Assert no `#local-article-paragraph-0` href appears (anchors begin at paragraph-1)."

---

### Low

**L-1 — `_safe_local_article_intelligence_href` should explicitly delegate to the existing fragment regexes.**

`templates.py:150–152` already defines:

```
_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE  → local-article-paragraph-[1-9][0-9]*
_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE  → local-article-content-section-[1-9][0-9]*
```

The design says "reuse existing fragment regexes" but the plan lists the new helper without saying which existing constant to delegate to. Name them explicitly in the plan so the implementation does not accidentally write a third regex for the same anchors.

**L-2 — Wrapper guard in Task 6 assumes `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` exists in `test_workflows.py`.**

The guard test calls that function directly. Its existence follows an established Stage 368 pattern, so this is low-risk, but the plan should include a one-line note that the caller was introduced in Stage 368 and must still be present, not just assumed. If it was renamed in a future stage before369 ships, the guard test will fail to compile.

**L-3 — Anchor offset not documented as a trap.**

Both confirmed anchor conventions are 1-based (`index + 1` for paragraphs, `section_position` from `enumerate(..., start=1)` for sections). The plan does not note this, and the natural mistake is to emit `#local-article-paragraph-{index}` for index 0, producing `#local-article-paragraph-0`, which the existing fragment regex explicitly rejects. Add a single comment in the builder task noting N = index + 1 for paragraphs, N = section_position (1-based) for sections.

---

### Feasibility

**Confirmed feasible.** The placement is verifiable in code:

- `render_local_article_page_html` (templates.py:777) already embeds `{local_article_body_organizer}` and `{local_article_section}` in that f-string order; inserting a new `{local_article_intelligence_brief}` between them requires only adding the builder call and one interpolation slot.
- `_render_local_article` (templates.py:14432) produces `<section id="local-article"` as the boundary marker the render test checks against.
- Section anchors are `#local-article-content-section-{N}` (N from enumerate start=1), confirmed in `saved_article_local_section_binder.py:119`. Paragraph anchors are `#local-article-paragraph-{index+1}`, confirmed at line 199 of the same file and in `_paragraph_view_model` in the Stage 368 organizer.

### Generated-site-only boundary

Well specified. Denylist covers JSON contract keys, artifact filenames, and the wrapper guard covers the render path. No new route, schema, or runtime/manifest change is introduced. The boundary paragraph text in Task 6 is exhaustive. No leakage issues found.

### Test plan

RED/GREEN structure is correct. Task 2 RED runs before any production file exists. The render tests correctly check page-scope exclusion (index.html, articles/index.html, detail pages). Contract and artifact denylist tests in Task 6 are necessary and correctly scoped.

### Commit scope

12 files (1 new builder, 1 templates update, 1 new test file, 4 modified test files, 2 docs, 4 review artifacts). Appropriate for one commit.

---

### Verdict

**Do not start Task 4 until C-1 is resolved.** Fix the chip cap constant in the design doc or the plan (pick one authoritative source), then carry the correct number forward.

**Clarify I-1 before Task 4** by adding the `type` → lane key mapping to the design doc or the plan constants block. `I-2` and `L-1` through `L-3` are editorial — fix them at the start of the relevant task. No architectural change is needed.

The plan is otherwise implementation-ready.
