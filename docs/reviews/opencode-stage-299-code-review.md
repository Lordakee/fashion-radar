# opencode Stage 299 Code Review

Reviewer: opencode (`zhipuai-coding-plan/glm-5.2`, variant `max`)

Scope: Uncommitted Stage 299 changes in `/home/ubuntu/fashion-radar` at base
`ab99230`.

Verdict: CHANGES REQUIRED

## Findings

### Critical

None.

### Important

**I1. Brief `what_happened` card renders raw, uncleaned HTML from
`story.summary`, breaking the scan-layer UX for a significant share of stories.**

`_local_article_brief_sections` assigned the `what_happened` body directly from
`story.summary`. Production RSS summaries can contain raw feed HTML such as
anchors, images, and inline styles. `_render_local_article_brief` escapes those
values, so the output remains XSS-safe, but the escaped tags are displayed as
literal prose inside the brief card.

Generated-site inspection showed the rebuilt site had 18 article sidecars and
18 detail pages, but 9 of 18 sidecars had raw HTML markup in the
`what_happened` body. The other brief bodies (`why_it_matters`,
`signal_context`, `watch_next`) did not show the same problem.

This is inconsistent with the rest of the detail page, where summary text is
rendered through existing cleanup logic before display. Local article body
paragraphs are also cleaned before saving. The brief path bypassed both cleanup
paths.

Required fix:

- Clean the summary-backed `what_happened` brief body before saving it to the
  sidecar.
- Add a regression test using summary HTML such as `<a><img></a>` and assert the
  resulting `brief_sections[0].body` is readable prose with no visible HTML tag
  text.

### Minor

**M1. Brief body shares `LocalizedText` references with the story.**

This is safe today because the strings are immutable and the build path does not
mutate the body fields, but a copy would make the sidecar data flow explicit.

**M2. `aria-label="ROW ONE brief"` is English-only.**

Acceptable for now, but not fully bilingual.

**M3. Empty story fields render an empty brief card.**

Not observed in the generated site; non-blocking.

## Review Questions

1. Backward compatibility with existing sidecars and model usage: yes.
2. Four brief sections mapped to the correct `RowOneStory` fields: yes, except
   the summary-backed card needed cleanup before saving.
3. Avoiding duplicate `why_it_matters`, `signal_context`, and `reader_path` in
   the local article body: yes.
4. Bilingual brief rendering and escaping: structurally correct and XSS-safe,
   but escaping alone was not enough for raw feed summary readability.
5. Legacy local article rendering when `brief_sections` is empty: yes.
6. Test coverage: meaningful overall, but missing raw-feed-summary regression
   coverage before this review.
7. Blocking issues: I1 must be fixed before commit/push.
