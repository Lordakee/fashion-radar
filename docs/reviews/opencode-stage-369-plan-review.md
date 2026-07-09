## Stage 369 Revised Plan/Spec Review (opencode)

Reviewed only the attached pack. No files inspected, no commands run.

---

### Resolved Claude Code Findings

**C-1 (Critical) — RESOLVED.** Design doc caps chips per lane at 4 (line 73); plan Task 4 now sets `LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE = 4` (line 318). The earlier 5→4 conflict is gone. Both sources agree at 4.

**I-1 (Important) — RESOLVED via alternate (sound) approach.** Instead of inventing a new `_LANE_KEY_BY_REFERENCE_TYPE` mapping, the plan now delegates to the existing `row_one_saved_article_reference_bucket(reference)` helper as the canonical reference-type mapping (spec lines 67–70, plan lines 333–336). Lanes are restricted to the `brands` / `products` / `people` buckets; the `themes` lane derives from section titles and item labels not already emitted as reference chips. The stray `_reference_lane_key` helper is no longer in the private-helper list (plan lines 340–348), so the design and plan are internally consistent. This is cleaner than Claude's suggestion because it reuses one canonical mapping rather than adding a second one.

**I-2 (Important) — RESOLVED.** Task 2 filter test now reads: "Assert no `#local-article-paragraph-0` href appears because paragraph anchors are 1-based (`index + 1`)" (plan lines 220–221). The earlier contradiction between "paragraph 0 emitted" and "no paragraph-0 href" is removed; the 1-based anchor rule is stated inline.

**L-1 (Low) — RESOLVED.** Task 5 now names the constants explicitly: `_safe_local_article_intelligence_href` delegates to `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` and `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` (plan lines 374–376). No risk of a third regex.

**L-2 (Low) — RESOLVED.** Task 6 wrapper guard now carries the one-line provenance note Claude asked for: it "depends on the existing `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` workflow test remaining in `tests/test_workflows.py`" (plan lines 441–443).

**L-3 (Low) — RESOLVED.** Task 4 adds an "Anchor numbering rules" block (plan lines 337–339): paragraph `N = index + 1`, content-section `N = 1-based section_position`. The 1-based trap is now documented in the builder task.

---

### New Findings

**N-1 (Low / informational) — `SUPPORT_CHARS` cap is plan-only.**
Plan Task 4 introduces `LOCAL_ARTICLE_INTELLIGENCE_BRIEF_SUPPORT_CHARS = 110` (line 322) to bound `RowOneLocalArticleIntelligenceRoute.support`. The design doc's cap list (spec lines 72–76) only enumerates lanes/chips/evidence/route/excerpt and is silent on support-text length. This is a reasonable extension and consistent in spirit, but it is a value not authorized by the spec. Either add "max support length around 110 characters" to the design's cap list, or drop the constant and reuse `EXCERPT_CHARS`. Non-blocking.

**N-2 (Low / informational) — Commit file count.**
Task 7 `git add` lists 14 files (1 builder, 1 templates, 1 new test, 3 modified tests, 2 docs, 2 spec/plan, 4 reviews), not the 12 Claude cited. Still one-commit sized; just correct the count in any handoff summary.

---

### Feasibility

Confirmed by the pack alone. Placement is unambiguous: insert `{local_article_intelligence_brief}` between `{local_article_body_organizer}` and `{local_article_section}` in `render_local_article_page_html`. Builder is a pure function over `RowOneStory` + `RowOneLocalArticle` with deterministic caps and a documented `None`-return rule. RED→GREEN ordering (Task 2/3 RED before Task 4/5 GREEN) is preserved.

### Generated-site-only boundary

Well specified and tight. Task 6's boundary paragraph (plan lines 406–408) enumerates the three forbidden JSON names, three forbidden HTML names, no new sidecars/routes, no `index.html` / `articles/index.html` / detail-page changes, no outbound article URLs as primary nav, and no contract/schema/runtime/manifest/source-collection/fetching/scoring/ranking/LLM/connector/scheduling/deployment/analytics/personalization/recommendation/compliance behavior. Workflow JSON-contract denylist (plan lines 412–421) and artifact denylist across root, `articles/`, `data/`, `data/articles/` (plan line 422) are present. The wrapper guard monkeypatches `_render_local_article_intelligence_brief` and reuses the Stage 368 SQLite-non-mutation test, so the render path is covered even when the section is suppressed.

### Commit size

Single commit, ~14 files, all stage-scoped. Appropriate.

---

### Verdict

**All six Claude Code findings (C-1, I-1, I-2, L-1, L-2, L-3) are resolved.** The plan is feasible, generated-site-only, and one-commit sized.

**Proceed to implementation.** Address N-1 (either add the support-chars line to the spec or drop the constant) at the start of Task 4; correct the file count in the Task 7 handoff summary. No other blockers.
