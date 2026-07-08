READY FOR IMPLEMENTATION.

I reviewed each specified area against the design and plan:

**Fixture count** — Eight stories across four named sources plus one overflow. Vogue gets three stories (enough to exercise the two-link cap), WWD gets two (to exercise case-fold merging), one each for Business of Fashion and The Cut, one overflow. Count is sufficient for all assertions.

**Reference cap fixture** — The first Vogue story is given more than five unique refs across `entity_refs`, `product_refs`, and `designer_refs`, and the plan explicitly asserts that only five chips render. Cap constant `DAILY_LOCAL_SOURCE_DESK_MAX_REFS_PER_SOURCE = 5` matches.

**`title=None` fixture** — Assigned explicitly to the third Vogue story. The render test asserts the literal string `None` does not appear and that a fallback (story headline) or omitted sublabel is used instead.

**`body_source_labels` type/dedup/render consistency** — Labels are collected as `LocalizedText` tuples, deduped by `(label.en.casefold(), label.zh.casefold())` in source-story order, stored on `_DailyLocalSourceDeskSource.body_source_labels` as `tuple[LocalizedText, ...]`, and rendered bilingually. No separate cap constant; the known label set is small. Consistent throughout.

**`href` None/empty handling** — `_safe_daily_local_source_desk_page_href` rejects non-`str` (covers `None` and `123`), empty string, and whitespace. The filtering test fixture includes both `None` and `123` mapped hrefs.

**Safe href rules** — All six rejection conditions are covered: leading `.`, `/`, `//`; whitespace; nested path (`nested/story.html`); mismatched stem (`mismatch-source-desk-3333333333.html`); traversal (`../secret.html`); and non-`.html` / bare `.` / `..`. The `PurePosixPath` guard rejects absolute paths and multi-part paths. The stem-equality check prevents stem mismatches.

**Generated-site-only boundary** — Enforced at three layers: `render.py` wires the href map only inside `render_row_one_site`; the homepage-only site test asserts absence from `articles/` and `data/` artifacts; the workflow guard denylists all six stem variants. The design's non-goals explicitly forbid new data files, routes, and schema fields.

**Docs assertion consistency** — The docs drift test asserts the exact sentence inserted into README and `docs/row-one.md`, and that sentence contains every required phrase (`Stage 362`, `Daily Local Source Desk`, `daily-local-source-desk`, all three `does not create` JSON file statements, `does not change schemas`, `does not add fetching`, `does not add outbound article URLs as primary navigation`, `does not add compliance-review behavior`). Assertions match the inserted text.

No Critical or Important blockers found.

**READY FOR IMPLEMENTATION.**
