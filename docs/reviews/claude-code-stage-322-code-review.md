Here are the findings from reviewing the Stage 322 diff.

---

## Critical

None.

---

## Important

None.

---

## Minor

**1. Two-layer dedupe uses different normalizers (intentional, but worth documenting)**

`_deduped_editorial_brief_trail` in `render.py` normalizes labels with `clean_row_one_text`, while `_render_editorial_brief_trail` in `templates.py` uses `_editorial_brief_display_text`. The two functions don't normalize identically, so the second layer dedupes on a slightly different text form than the first. This is consistent with the existing pattern used for brief items (same split between render.py and templates.py). No bug, but a comment on `_editorial_brief_source_trail` noting "template dedupe operates on display-normalized labels" would make the intent explicit for future maintainers. The existing comment says "template dedupe is a safety net", which partially covers it.

**2. Cap of 3 is a safety net only — current call sites cannot reach it**

`EDITORIAL_BRIEF_MAX_TRAIL_ITEMS = 3` is enforced at render time. With the current call sites, `what_happened` produces at most 1 item (brief only, no content keys, no paragraph fallback), `why_it_matters` at most 2 (brief + one content section), and `watch_next` at most 2 (brief/paragraph + one content section). The cap is structurally sound but will never trigger with current inputs. That is fine as a safety net, but worth noting so it is not mistakenly treated as a meaningful constraint on future call sites.

**3. No explicit assertion that `href=None` trail items render as `<span>` rather than `<a>`**

`test_render_index_html_filters_editorial_brief_source_trail_links` confirms unsafe hrefs are absent from the HTML and that labels are escaped, but it does not assert that a filtered-href item (or an explicit `href=None` item) renders as `<span class="editorial-brief-trail-item">` rather than as an `<a>`. The XSS safety is confirmed by the escape assertions, but a targeted assertion like `assert '<span class="editorial-brief-trail-item">' in section_html` for the `href=None` case would close the structural gap.

**4. `::after { content: "↗" }` on `.editorial-brief-link` is not aria-hidden**

CSS `content` values are exposed to some screen readers (NVDA, JAWS, VoiceOver behaviour varies). The north-east arrow `↗` appended to "Read locally / 本地阅读" may be announced as "northeast arrow" or similar. Adding `font-style: normal` does not suppress this. A common mitigation is `content: "↗" / ""` (the CSS `/ ""` alt-text syntax, supported in modern browsers) or moving the arrow to a `<span aria-hidden="true">` in the template. This is low-priority given the existing bilingual label already conveys full meaning, but it is the kind of thing that fails an accessibility audit.

---

**Summary**: The generated-site-only boundary is clean — no new JSON contract fields, schema changes, or runtime/manifest fields. `_safe_editorial_brief_href` correctly gates all trail hrefs through the existing detail-path allowlist and fragment regex (`local-article-paragraph-[1-9][0-9]*`, `local-article-content-section-[1-9][0-9]*`). All displayed text goes through `_esc()`. The `<a>` → `<article>` card refactoring is structurally correct (avoids invalid nested links). Test coverage is comprehensive across render, omission, unsafe-link filtering, cap/dedupe, workflow boundary, docs, and CSS. No critical or important issues remain.
