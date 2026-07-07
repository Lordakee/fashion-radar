# Stage 335 ROW ONE Saved Article Reading Paths Design

## Goal

Make `articles/index.html` behave more like an edited daily reading surface by
adding a generated-site-only "Saved Article Reading Paths" section. The section
should organize already-saved local article content into a small set of
scan-first paths such as Read First, People & Brands, Products, and Source
Structure, so a reader can decide what to read next without opening every
source card.

## Current Gap

Stages 326-334 built the dedicated saved article library page and progressively
added source grouping, signal indexing, saved article content groups, text-source
provenance, and per-card local excerpts. The page now exposes more local text,
but it still does not explicitly tell a reader "start here, then follow this
path." The existing saved article content organization already contains the
right source material; it needs a reading-path presentation layer.

## Chosen Approach

Add a small generated-site-only reading-path view model derived from the existing
`RowOneSavedArticleLibrary` plus `RowOneSavedArticleContentOrganization`:

- Each content-organization group becomes one reading path when it has usable
  cards.
- Each path contains up to three ordered steps from the group's cards.
- Each step reuses the card title, source, section label, localized lead,
  safe detail-page content-section anchor, paragraph evidence indices, and
  references.
- A content-organization card is eligible only when its canonical detail path
  also exists in the saved article library through a safe reader, digest, or
  evidence route. This keeps direct rendering safe when a caller passes unsafe
  library entry paths.
- Rendering happens only inside `articles/index.html` and links only to existing
  local generated detail anchors.

This makes the saved article page more editorial without changing content
generation. It avoids a new JSON artifact, avoids app/runtime/manifest contract
changes, and avoids new collection or extraction behavior.

## Why A New Builder Instead Of Template-Only

Stage 334 used a template-only lookup because it only mirrored snippets into
matching source cards. Reading paths are a distinct presentation surface with
path counts, path cards, step caps, and path-level copy. Keeping that selection
and capping logic in a small private builder keeps `templates.py` from becoming
the only place that owns product behavior, and it gives the path semantics direct
unit coverage.

The builder should stay private to the generated ROW ONE site. It should not
write files and should not be serialized into public app JSON.

## UI Behavior

The saved article page should render this order when all sections exist:

1. saved article library hero;
2. saved signal index;
3. saved article reading paths;
4. saved article content organization;
5. source-grouped saved article library cards.

The reading-path section should include:

- bilingual section title:
  - `Saved Article Reading Paths`
  - `保存文章阅读路径`
- a compact bilingual dek that frames the paths as editorial routes through the
  local saved text;
- one path card per existing content organization group, capped at four paths;
- each path card should show the path title/dek, a step count, up to three
  ordered steps, a safe "Start path" link to the first step, and per-step safe
  evidence links when available.

The path cards should be professional and dense, not a marketing hero. They
should support scanning, comparison, and repeated use in the daily workflow.

## Data Flow

1. `render_row_one_site()` already builds `saved_article_library` and
   `saved_article_content_organization`.
2. Stage 335 adds `build_row_one_saved_article_reading_paths()` and calls it
   with both objects.
3. `_write_saved_article_library_page()` receives the reading paths and passes
   them into `render_saved_article_library_html()`.
4. `render_saved_article_library_html()` renders the reading paths before the
   standalone content organization section.
5. The homepage and generated JSON contracts remain unchanged.

## Safety And Contract Boundaries

Do not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `row-one-runtime/v1`
- JSON schemas
- `data/articles/<story-id>.json` sidecar schema
- source collection
- fetching
- matching
- extraction
- scoring
- ranking
- LLM behavior
- connector behavior
- scheduling
- deployment behavior
- market grouping
- domestic/international classification
- compliance-review product behavior

Do not add:

- full article republication on `articles/index.html`
- outbound article URLs in the reading-path section
- new extraction or crawling behavior
- new summary generation behavior
- new social/community platform behavior
- `data/saved-article-reading-paths.json`
- any generated JSON contract for this section

All links rendered by the reading-path section must validate generated detail
paths and local content-section or paragraph anchors before prefixing `../`.
Unsafe routes, traversal, wrong fragments, and `javascript:` routes must omit
the unsafe step/link text from the reading-path section.

## Tests

Add tests that prove:

- the builder derives paths from existing content organization groups, caps paths
  and steps, and omits empty input;
- `articles/index.html` renders `Saved Article Reading Paths` / `保存文章阅读路径`
  before saved article content organization and before the source grid;
- generated-site fixtures show existing local leads inside the reading-path
  section, not only in the content organization or source cards;
- unsafe reading-path step paths and wrong fragments do not render the unsafe
  step text or link;
- long path step leads are truncated and escaped;
- path cards link only to safe `../details/<story>.html#local-article-content-section-N`
  and `../details/<story>.html#local-article-paragraph-N` anchors;
- `edition.json`, `manifest.json`, and `runtime.json` do not expose reading-path
  vocabulary or local text;
- no `data/saved-article-reading-paths.json` file is generated;
- `README.md` and `docs/row-one.md` document the Stage 335 generated-site-only
  boundary.

## Out Of Scope

- No social/community platform expansion.
- No crawler/source work.
- No new article extraction dependency.
- No LLM-generated summaries.
- No full-article publication on the library index.
- No app contract change.
- No generated images.
- No broad ROW ONE visual redesign.
- No compliance-review functionality.
