## Stage 382 Local Article Synthesis Brief — Plan Review

---

### Critical

**C1 — Lead / thesis / article_adds fallback chains share overlapping source fields with no exclusivity rule**

`lead` falls back through `brief_sections[why_it_matters]` → `brief_sections[editorial_takeaway]` → `brief_sections[signal_context]` → `story.why_it_matters` → `story.summary` → first content-section body/item body. `thesis` falls back through `story.editorial_takeaway` → `brief_sections[editorial_takeaway]` → `brief_sections[signal_context]` → first content-section title/body pair. `article_adds` falls back to first meaningful content-section body → first item body → first paragraph.

When a local article has no `why_it_matters` brief section and the story has no `editorial_takeaway`, `lead` consumes `brief_sections[editorial_takeaway]`, but `thesis` then also tries `brief_sections[editorial_takeaway]` independently. More broadly, when sparse articles have only one content section, all three cards can pull from `content_sections[0].body`. The plan contains no consumed-field exclusivity rule, no "skip if already used by a prior card" guard, and no fallback-exhaustion guard. The brief would silently render three cards with identical or near-identical text, directly contradicting the stated goal of three distinct synthesis perspectives.

**Fix required before implementation:** Add an explicit field-ownership table or a consumed-field set that each card's fallback path updates. A minimal rule is: (a) `lead` owns `brief_sections[why_it_matters]` and `story.why_it_matters`/`story.summary`; (b) `thesis` owns `story.editorial_takeaway` and `brief_sections[editorial_takeaway]`/`brief_sections[signal_context]`; (c) `article_adds` owns the first content-section body **not already used by `lead`**. If a field was consumed by a higher-priority card, skip it. If all cards would render the same text after deduplication, the builder should return `None` rather than emit a brief with identical cards.

---

### Important

**I1 — `_safe_local_article_synthesis_href` duplicates `_safe_local_article_intelligence_href` completely**

`_safe_local_article_intelligence_href` at `templates.py:17666` already accepts `href: object`, strips whitespace, enforces the `#` prefix, rejects inline whitespace, and validates against `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` and `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE`. The plan specifies a new `_safe_local_article_synthesis_href` that "uses the existing...regexes already used by `_safe_local_article_intelligence_href`." Duplicating the body of this function creates a silent maintenance surface — if the anchor regex is ever updated only one function may be updated. The plan should instead specify that `_safe_local_article_synthesis_href` is an alias or thin wrapper, or that the synthesis render helpers call `_safe_local_article_intelligence_href` directly, or that both are replaced by a generic `_safe_local_article_same_page_href` delegated to by both brief renderers.

**I2 — `thesis` fallback to `brief_sections[editorial_takeaway]` not blocked when `lead` has already consumed it**

A related but distinct consequence of C1: the plan's `lead` fallback includes `brief_sections` with key `editorial_takeaway` (second in the key preference list). If `why_it_matters` is absent, `lead` takes `editorial_takeaway`. `thesis` then falls back to `story.editorial_takeaway`, then to `brief_sections[editorial_takeaway]` — pulling from the same field again. Even setting aside the broader C1 issue, this specific path must be closed. The plan must state whether `thesis` is permitted to use `editorial_takeaway` from brief sections when `lead` already consumed it, and if not, how the builder tracks that.

**I3 — Workflow sentinel test "force a local article fixture that renders the block" is under-specified**

Task 6 Step 3 says to "patch `_render_local_article_synthesis_brief` with `raising=True` to return a sentinel string, force a local article fixture that renders the block, run `render_row_one_site(...)`." The phrase "force a local article fixture" implies extra setup. But since the patch replaces the renderer entirely (not the builder), the patched function will be called for every article page render regardless of whether the builder returns `None` — so the sentinel will appear in every `articles/<story-id>.html`. The existing SQLite fixture used by `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` already includes at least one local article, which is sufficient. The plan should clarify this: the renderer patch is sufficient; no additional fixture forcing is needed. As written, an implementer may add unnecessary fixture coupling.

---

### Minor

**M1 — `<article>` grid element CSS class not shown in render HTML blueprint**

Task 5 Step 4 lists `.local-article-synthesis-brief-card` as a CSS selector target, but the render HTML spec in the plan shows `<article>` elements inside `.local-article-synthesis-brief-grid` with no class attribute. Specify `class="local-article-synthesis-brief-card"` on each `<article>` element in the render template so CSS selector and markup are unambiguously aligned.

**M2 — `_truncate_text` helper name diverges from the established `_truncate` convention**

Every existing sibling module (`local_article_intelligence_brief.py`, `saved_article_body_organizer.py`, `saved_article_key_signals.py`) names the single-string truncation helper `_truncate(value, limit)` and the localized version `_truncate_localized_text(value, limit)`. The plan introduces `_truncate_text(...)`, breaking this convention within the same sub-package. Use `_truncate` for single-string truncation and `_truncate_localized_text` for `LocalizedText` to match the established pattern.

**M3 — Paragraph anchor 1-based numbering not stated in builder private helper rules**

The builder rules reference `_paragraph_anchor(...)` and state anchor hrefs must be `#local-article-paragraph-N`, but do not explicitly specify that `N = index + 1` (1-based). The existing `local_article_intelligence_brief._paragraph_view_model` (line 324: `paragraph_number = index + 1`) and `saved_article_body_organizer._paragraph_view_model` (line 181) both use 1-based numbering. State `N = index + 1` explicitly in the builder private helper section to prevent an off-by-one mismatch with the rendered body anchors.

**M4 — `reader_move` character cap (140) is tighter than `thesis`/`article_adds` (160) without explanation**

`reader_move` is instructional navigational copy, not a text excerpt, yet it gets a smaller cap than the excerpt-like `thesis` and `article_adds` fields. The asymmetry is undocumented. Either align `reader_move` to160 chars (consistent with `thesis`/`article_adds`) or add an explicit rationale in the builder rules section.

**M5 — `basis_note` as a dataclass field adds testable surface for static copy that never varies**

`basis_note` is a fixed bilingual constant with no user-content derivation. Defining it as a dataclass field adds test surface and serialization weight for text that never changes. A module-level constant (`_BASIS_NOTE_EN`, `_BASIS_NOTE_ZH`) referenced directly by the renderer is simpler and self-documenting. This is a design preference, not a correctness issue; either approach is acceptable, but the plan should acknowledge the choice.

---

**Overall:** The plan is structurally sound — generated-site-only boundaries, href safety, escaping, test sequencing, docs, and denylist coverage are all well-specified and consistent with prior stages. Fix C1 (field exclusivity between the three synthesis cards) before implementation, as it is the core correctness risk. I1–I3 are addressable with targeted plan edits. M1–M5 are cleanups.

END_OF_
