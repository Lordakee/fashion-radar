## Stage 362 Code Review — Daily Local Source Desk

---

### Critical

None.

---

### Important

**Type annotation mismatch on `_render_daily_local_source_desk` — `local_articles_by_story_id`**

The inner function `_daily_local_source_desk_sources` correctly declares `local_articles_by_story_id: Mapping[str, RowOneLocalArticle] | None` and handles `None` safely via `local_articles = local_articles_by_story_id or {}`. The outer `_render_daily_local_source_desk` however declares it as `Mapping[str, RowOneLocalArticle]` (non-optional), while `render_index_html` calls it with the potentially-`None` `local_articles_by_story_id` parameter. This is a type annotation lie — a strict type checker would flag it. Runtime is safe because the delegation to `_daily_local_source_desk_sources` absorbs the `None`. The identical annotation pattern exists on `_render_daily_local_article_reading_brief` (pre-existing), so Stage 362 is consistent with the codebase, but both are technically wrong. Not blocking, but worth tracking as a cleanup item.

---

### Minor

**Unused class `daily-local-source-desk-body-source` (singular)**

`_render_daily_local_source_desk_source` emits `class="daily-local-source-desk-body-source"` on each inner span, but no CSS rule targets that selector directly. Styling lands correctly via the ancestor selector `.daily-local-source-desk-body-sources span`. The CSS test only checks for `.daily-local-source-desk-body-sources` (plural), consistent with how the styling actually works. The singular class is dead decoration. Zero functional impact.

**`groups` accumulator inner type is `dict[str, object]`**

Every mutation requires a cast (`int(group["article_count"])`) or an `isinstance` guard (`if isinstance(body_source_keys, set)`). This matches adjacent Stage 360/361 accumulator style, so it's project-consistent, but a small `@dataclass` or `TypedDict` accumulator would eliminate the guards and make the code self-documenting. Not a problem in the current form.

**Ref cap applies per source, not per article**

`DAILY_LOCAL_SOURCE_DESK_MAX_REFS_PER_SOURCE` (5) is consumed across all articles for a given source group. Once the first article fills the cap, refs from subsequent articles of the same source are silently dropped. This is intentional given the design (source-level view, not article-level), and the test fixture confirms the count (`vogue_group.count('class="daily-local-source-desk-ref"') == 5`). Worth knowing when reasoning about what surface coverage looks like for high-volume sources.

---

### Correctness confirmations

**Href safety** — `_safe_daily_local_source_desk_page_href` is a character-for-character copy of the validated reading brief equivalent. It gates on `safe_local_article_story_id` twice (input + derived), rejects `None`/non-string, rejects whitespace, rejects leading `.`/`/`/`//`, enforces exactly one PurePosixPath part, enforces `.html` suffix, and requires the filename stem to match the story ID. The filter test covers traversal, nested paths, hidden files, absolute paths, whitespace, slash prefixes, bare dot/dotdot, `None`, integer, and ID-mismatch hrefs — all correctly excluded.

**Escaping** — Every user-derived string (`source_name`, `story_headline`, `article_title`, `ref.name`, `ref.label`) goes through `normalize_row_one_paragraph` + `_esc()` before entering HTML. Body source labels come from `row_one_body_source_label` (hard-coded enum outputs) but are still passed through `_esc()`. Href values go through the validator which ensures they are safe ASCII paths, and then `_esc()` at the attribute level. The test confirms `<script>`, `<b>`, `<Business>`, and raw URLs do not appear unescaped.

**Grouping/sorting/caps** — Grouping is casefold-keyed (verified by "wwd"/"WWD" merge test). Sort is `(-article_count, -saved_paragraph_count, casefold_name, raw_name)` — descending volume, then alphabetical with deterministic tiebreak. Cap at 4 sources is asserted (`len(sources) <= DAILY_LOCAL_SOURCE_DESK_MAX_SOURCES`). Overflow source "Zzz Overflow Source" is confirmed absent. Source name preservation (first-seen casing wins) is confirmed by the absence of the lowercase `wwd` title variant.

**Generated-site-only boundary** — Section is confirmed present in `index.html`, absent from `articles/index.html`, individual article pages, and detail pages. JSON contract payload (`edition.json`, `manifest.json`, `runtime.json`) contains no `daily_local_source_desk` or `daily-local-source-desk` strings. No `source-desk`, `daily-local-sources`, or variant filenames appear in any output directory. The workflow-level test monkeypatches `_render_daily_local_source_desk` out of the template module and reruns the full file write check — clean separation confirmed.

**Section ordering** — Template f-string placement is `reading_brief` → `source_desk` → `saved_article_content_organization`. Two ordering tests cover both the three-section case and the case where the reading brief is absent, verifying `source_desk` remains before `saved_article_content_organization` in both configurations.

**Backward compatibility** — `render_index_html` gains one optional `Mapping[str, str] | None = None` parameter. `render_row_one_site` gains one kwarg wiring line. No existing call sites are affected.

---

### Readiness

**Ready to merge.** Implementation is correct, boundary is enforced at both template and workflow level, href validation is complete, all user-derived content is escaped, grouping/sorting/caps behave as specified, and the test suite covers positive cases, all known unsafe href patterns, omission conditions, ordering, CSS presence, and file-level artifacts. The type annotation note on `_render_daily_local_source_desk` is a carry-forward from Stage 361 and does not require a fix in this stage.
