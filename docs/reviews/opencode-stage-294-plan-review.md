## Verdict

Not approved as-is. The scope and app-contract boundary are correct, the
render-time-only approach is sound, and the plan properly excludes
`build_row_one_app_payload`, `data/edition.json`, SQLite, and `edition.summary`.
However, the Task 2 application list omits one static-HTML surface that renders
`story.summary` directly into `index.html`, so the plan's own Task 1 acceptance
test cannot pass when Task 2 is implemented as written. The plan also
re-derives cleaning logic that already exists and is tested elsewhere.

## Critical

**C1. `_render_lead_story` is omitted from the cleaning surface list, but it
renders `story.summary` into `index.html`.** `_render_lead_story` renders the
lead story summary in addition to the normal section card. The Task 1 fixture
places the story in `top_stories`, so `_lead_story` returns it and the lead
story block is emitted on `index.html`. Task 2 Step 2 lists only
`render_detail_html` meta description, `render_detail_html` Summary section, and
`_render_story_card`. Following the plan literally, generated prefixes and feed
markup would still appear in `index.html` via the lead-story block. Task 2 Step
2 must add `_render_lead_story` English/Chinese summary spans to the application
list.

## Important

**I1. The plan duplicates cleaning logic that already exists and is tested in
`src/fashion_radar/row_one/articles.py`.** The existing article cleanup covers
the same prefixes, boilerplate phrases, entity decoding, script/style stripping,
and whitespace normalization. Reuse the existing helpers by factoring a shared
helper, or explicitly justify why a second implementation is needed. Two
divergent cleaners will drift.

**I2. Task 4 Step 2's `rg` pattern includes a bare `<img` alternative that will
match legitimate story-visual images.** Scope the `<img` check to summary
contexts, or drop `<img` from the broad generated-site scan and rely on summary
markers such as `Original source summary`, `来源摘要`, `Read the full story here`,
`阅读全文`, `点击查看全文`, and feed-specific markers like
`webfeedsFeaturedVisual`.

**I3. Task 5 Step 4 uses a literal `...` in the `git add` command.** Replace
`docs/reviews/...` with explicit review file paths or a shell-expanded glob.

**I4. Task 4 Step 3 hard-codes `16` local-article-body detail files.** This
number is fixture/run dependent. Derive the expected count from generated
`data/articles/*.json`, or phrase the expectation as equal to the number of
sidecar JSON files written.

## Recommendation

- Add `_render_lead_story` to the summary cleaning application list.
- Reuse the existing article cleaning helpers by extracting a shared helper that
  both article sidecar cleanup and static summary display can call.
- Narrow the generated-site dirty-content scan to avoid false positives from
  legitimate images.
- Replace the literal `...` in the commit step with explicit review file paths.
- Make local-article count acceptance data-derived.
