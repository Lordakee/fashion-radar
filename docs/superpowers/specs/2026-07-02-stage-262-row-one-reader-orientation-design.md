# Stage 262 ROW ONE Reader Orientation Design

## Goal

Stage 262 improves ROW ONE as a daily reader experience by adding a
deterministic reader-orientation layer to the static site. It makes the homepage
scannable, gives readers a fast path into each section, and gives detail pages a
clear path back to their section context, without changing collection, matching,
ranking, scoring, JSON contract semantics, deployment, or external integrations.

## Product Gap

Stage 260 created the ROW ONE static daily site. Stage 261 added deterministic
editorial synthesis to each story. The remaining product gap is navigation:
readers can see organized stories, but the homepage has no contents rail or
section jump layer, story cards do not expose enough orientation metadata, and
detail pages only link back to the homepage instead of the story's section.

Stage 262 closes that gap inside the existing `collect -> match -> report ->
ROW ONE` presentation path. It keeps all information derived from the existing
`RowOneEdition`, `RowOneSection`, and `RowOneStory` objects.

## Stage Direction Rationale

The current user goal is to make ROW ONE work as a professional daily fashion
web experience for app/web consumption. Although the broader release track often
prioritizes source coverage and matching quality, Stage 262 intentionally stays
presentation-only because it directly improves the ROW ONE site the user is
asking to develop now and does not disturb the already-approved collection,
matching, reporting, or external-tool boundaries.

If the user does not continue prioritizing ROW ONE app/site work after this
stage, the next release-track stage should return to curated source coverage or
deterministic matching quality.

## Chosen Approach

Add reader-orientation UI in `fashion_radar.row_one.templates`:

- A homepage "Edition Contents" navigation block after the masthead and before
  the story sections.
- One contents row per configured section, using the section key as an anchor
  target and the current `edition.section_stories(section.key)` count.
- Bilingual section names and count labels that reuse the existing language
  toggle behavior.
- Lightweight story-card metadata showing section, source, date, and evidence
  count so readers can scan cards without opening each detail page.
- Detail-page navigation back to the story's homepage section anchor with
  bilingual text.

The implementation intentionally avoids changing `RowOneStory` ranking, story
IDs, section caps, detail-page paths, JSON payload shape, cleanup behavior, or
server behavior. A broader app-facing JSON contract is a better Stage 263
candidate because it touches data compatibility rather than the site reading
experience.

## Data Inputs

Stage 262 uses only existing local fields:

- `RowOneEdition.sections`
- `RowOneEdition.section_stories(section.key)`
- `RowOneSection.key`, `title`, and `dek`
- `RowOneStory.section_key`, `source_name`, `published_at`, `evidence`,
  `detail_path`, and existing bilingual story fields

No new persisted model fields are required.

## Rendering

Homepage rendering adds:

- `<nav class="edition-nav" aria-label="Edition contents">`
- one safe internal link per section: `href="#<section.key>"`
- bilingual section title and count text
- section descriptions from existing `section.dek`

Story cards replace the standalone source-only card meta line with a compact
orientation row derived from the current story and the active
`RowOneSection.title` already being rendered:

- section label from `story.section_key`
- source name
- published date when available
- evidence count

Detail rendering adds:

- a section anchor link in the detail header or article lead area:
  `../index.html#<story.section_key>`
- bilingual link text: "Back to section" / "回到栏目"

All dynamic values remain escaped through the existing `_esc()` helper. Internal
links are generated only from typed `RowOneSectionKey` values.

## Boundaries

This stage is presentation-only. It does not:

- collect new sources;
- add scraping, browser automation, platform APIs, login cookies, proxy pools,
  CAPTCHA bypass, or paywall bypass;
- call LLMs, translation services, image services, or paid APIs;
- add deployment, publishing, or remote hosting;
- change section caps, story ranking, story IDs, or scoring;
- change `data/edition.json` beyond the existing Stage 261 behavior;
- add demand proof, platform coverage verification, geographic market inference,
  or compliance-review product behavior.

## Acceptance Criteria

- The homepage renders an edition contents block before story sections.
- Each contents link points to an existing section anchor and includes a current
  story count.
- Empty sections still appear in the contents block and keep their empty-state
  rendering in the section body.
- Story cards render compact orientation metadata for section, source, optional
  date, and evidence count without duplicating the old source-only card meta
  line.
- Detail pages render a safe back-to-section link using the story's section key.
- Existing bilingual language toggling still works for the new labels.
- Existing HTML escaping, unsafe URL omission, detail path validation, bounded
  cleanup, and dry-run serve behavior remain unchanged.
- Documentation describes the reader-orientation layer and its presentation-only
  boundary.
- Focused ROW ONE tests and the full verification gate pass.
