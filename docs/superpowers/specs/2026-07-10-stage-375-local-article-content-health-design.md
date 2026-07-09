# Stage 375 Local Article Content Health Design

## Goal

Stage 375 adds read-only Local Article Content Health for generated ROW ONE
sites. The feature verifies that saved local article sidecars are not only
routed, but also rendered as local article pages with the expected local article
section, saved-body container, paragraph anchors, and same-page content-section
anchors.

## User Value

Stage 374 proves that saved local article pages are reachable. A route can still
exist while the page is not useful: the local article section may be missing, the
saved local article body container may be absent, paragraph anchors may be
absent, or content-section links may point to anchors that were not rendered.

Stage 375 turns that gap into an operational health signal. `row-one status`
rejects generated sites where saved local article sidecars exist but their local
article pages do not expose the saved local body and anchors needed for the
daily reading experience. `row-one ops-check` reports the same condition with a
refresh action.

## Product Shape

Feature name: **Local Article Content Health** / **本地文章内容健康检查**.

The health check is generated-site-only and read-only. It inspects existing
files:

- `data/articles/*.json`
- `articles/<story-id>.html`

When no renderable saved local article sidecars exist, the health status is
`not_applicable`. This includes sites with no sidecars and read-only ops
discovery cases where every discovered sidecar has no non-empty paragraphs.

When saved local article sidecars exist, the status is `ready` only if every
saved article page has:

- the local article section anchor `id="local-article"`
- the saved-body container anchor `id="local-article-body"`
- a paragraph anchor for every non-empty saved paragraph:
  `id="local-article-paragraph-N"`
- a content-section anchor for every sidecar `content_sections` entry, matching
  the current renderer's one-anchor-per-section behavior:
  `id="local-article-content-section-N"`

Otherwise the status is `missing`.

## Architecture

Create a focused module:

`src/fashion_radar/row_one/local_article_content_health.py`

The module owns a pure dataclass and analyzer:

```python
@dataclass(frozen=True)
class RowOneLocalArticleContentHealth:
    status: str
    article_count: int
    paragraph_anchor_count: int
    content_section_anchor_count: int
    missing_article_sections: tuple[str, ...]
    missing_body_containers: tuple[str, ...]
    missing_paragraph_anchors: tuple[str, ...]
    missing_content_section_anchors: tuple[str, ...]
```

Create a small shared helper module:

`src/fashion_radar/row_one/local_article_anchors.py`

It owns shared local article anchor constants, one-based anchor builders, and
the HTML id parser used by both status integrity and content health.

The content-health analyzer accepts `site_dir` and an optional mapping of
validated current story ids to `RowOneLocalArticle` sidecars. When sidecars are
supplied, it uses that exact validated set. When no sidecars are supplied, it
discovers safe `data/articles/*.json` sidecars for read-only ops diagnostics and
ignores malformed discovered sidecars rather than crashing `row-one ops-check`.
Content health evaluates renderable sidecars only: a sidecar must have at least
one non-empty saved paragraph, because the current renderer omits the whole
local article section when there are no rendered paragraphs. Empty-paragraph
sidecars therefore do not create local article content expectations; if no
renderable sidecars exist, content health returns `not_applicable`.

The module also exposes:

- `row_one_local_article_content_health_payload(...)`
- `validate_row_one_local_article_content_health(...)`

`status_integrity.py` uses the strict path after `_load_article_sidecars(...)`
has already accepted current story ids and sidecar schemas. This keeps status
validation tied to the current edition and avoids a second loose discovery pass.
It returns a small combined generated-site health object:

```python
@dataclass(frozen=True)
class RowOneGeneratedSiteHealth:
    local_article_routes: RowOneLocalArticleRouteHealth
    local_article_content: RowOneLocalArticleContentHealth
```

`article_count` means the number of renderable saved local articles evaluated by
content health. In strict status validation, sidecars have already passed the
existing non-empty paragraph check, so this count should align with the current
validated article set. In read-only ops discovery, it can differ from route
health's sidecar count because route health validates safe sidecar stems and
routes, while content health parses sidecars and ignores malformed or
non-renderable files. `paragraph_anchor_count` and
`content_section_anchor_count` mean expected anchors currently present; missing
expected anchors are listed separately.

`row-one ops-check` uses the read-only discovery path and reports a diagnostic
payload even when strict status validation is not being run.

## Data Sources

Stage 375 reuses only current generated site files and existing saved local
article sidecar JSON.

It does not read remote URLs, call source collection, fetch articles, extract
article bodies, score stories, rank stories, call LLMs, use connectors, schedule
jobs, deploy services, generate images, or review compliance.

## Anchor Semantics

Stage 375 applies these anchor expectations only to renderable saved local
article sidecars: those with at least one non-empty paragraph. This mirrors
`_render_local_article(...)`, which returns no local article section when
`_render_local_article_paragraphs(...)` has no output.

The local article section anchor is required once per saved local article page:

```html
id="local-article"
```

The saved-body container anchor is required once per saved local article page:

```html
id="local-article-body"
```

For each non-empty `RowOneLocalArticle.paragraphs[index]`, the generated article
page must include:

```html
id="local-article-paragraph-{index + 1}"
```

The paragraph number preserves the original paragraph index. Blank paragraph
slots are skipped, but they do not shift later paragraph anchor numbers.

For each sidecar content section, the generated article page must include:

```html
id="local-article-content-section-{section_position}"
```

The current article-page renderer writes one
`id="local-article-content-section-N"` card for every
`RowOneLocalArticle.content_sections` entry. Stage 375 should therefore expect
one content-section anchor per sidecar content section, using the original
one-based section position. It should not borrow the stricter body-section
marker predicate, because section markers are a separate body-insertion feature
that only marks sections with usable paragraph support.

The analyzer should parse HTML ids with `HTMLParser` rather than string matching
so single quotes, attribute ordering, and unrelated text do not create false
results.

The shared anchor helper should expose both `parse_html_ids(html: str) -> set[str]`
for existing cached validation paths and `html_ids(path: Path) -> set[str]` as a
path-reading convenience for generated-site diagnostics.
It should keep HTMLParser's existing attribute-name normalization behavior, so
`id`, `ID`, and mixed-case variants are treated consistently.

## Status Integration

`validate_row_one_generated_site_integrity(...)` should compute content health
after route health and local-intelligence validation. It should return
`RowOneGeneratedSiteHealth`, exposing both `local_article_routes` and
`local_article_content` to the CLI status payload without changing generated JSON
contracts.

If sidecars exist and content health is not `ready`, `row-one status` fails with
a clear message naming the first missing section or anchor, such as:

- `row-one local article section is missing: articles/the-row-signal.html#local-article`
- `row-one local article body container is missing: articles/the-row-signal.html#local-article-body`
- `row-one local article paragraph anchor is missing: articles/the-row-signal.html#local-article-paragraph-2`
- `row-one local article content-section anchor is missing: articles/the-row-signal.html#local-article-content-section-1`

The validator checks missing article sections first, missing body containers
second, missing paragraph anchors third, and missing content-section anchors
fourth so first-error reporting is deterministic.

The machine-readable status payload adds a CLI-only top-level
`local_article_content` object. This is not written into `data/edition.json`,
`data/manifest.json`, `data/runtime.json`, `row-one-app/v7`,
`row-one-manifest/v1`, or `row-one-runtime/v1`.

The human `row-one status` output adds a compact line:

`Local article content: ready (N saved local articles, M paragraph anchors)`

## Ops-Check Integration

`build_row_one_ops_check_payload(...)` adds top-level `local_article_content`.

If saved local article sidecars exist but content health is `missing`, the
overall ops status becomes `attention` and actions include:

`Run `fashion-radar row-one refresh --output-dir <site_dir>`.`

The human `row-one ops-check` output adds:

`Local article content: ready|missing|not_applicable`

## Site Integration Boundaries

Stage 375 does not create:

- `data/local-article-content-health.json`
- `data/article-content-health.json`
- `data/content-health.json`
- `local-article-content-health.html`
- `article-content-health.html`
- `content-health.html`

It does not add a new route family. It validates existing generated article
pages created by earlier stages.

It does not alter `index.html`, `articles/index.html`, `articles/<story-id>.html`,
or detail page rendering. It does not publish full articles outside existing
local article pages and does not add outbound article URLs as primary navigation.

## Documentation Boundary Paragraph

Stage 375 adds read-only generated-site Local Article Content Health to
`row-one status` and `row-one ops-check`; it reuses current generated
`data/articles/*.json` saved local article sidecars, existing
`articles/<story-id>.html` pages, existing local article section anchors,
existing saved local article body container anchors, existing saved paragraph
anchors, and existing local content-section anchors to verify that already-saved
local article bodies are rendered inside same-site article pages without
changing app-facing contracts; it adds CLI-only content-health status payload
fields, but it does not create `data/local-article-content-health.json`, does
not create `data/article-content-health.json`, does not create
`data/content-health.json`, does not create `local-article-content-health.html`,
does not create `article-content-health.html`, does not create
`content-health.html`, does not create new article-source sidecars, does not
create new route families, does not alter `index.html`, `articles/index.html`,
`articles/<story-id>.html`, or detail page rendering, does not publish full
articles outside existing local article pages, does not add outbound article
URLs as primary navigation, and does not change row-one-app/v7,
row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts,
source collection, fetching, matching, extraction, scoring, ranking, LLM,
connector, scheduling, deployment, market grouping, domestic/international
classification, analytics, personalization, recommendation, or compliance-review
behavior.

## Tests

Analyzer tests should prove:

- no sidecars returns `not_applicable`
- complete article pages return `ready`
- missing `id="local-article"` returns `missing`
- missing `id="local-article-body"` returns `missing`
- missing paragraph anchors are reported deterministically
- missing content-section anchors are reported deterministically
- unsafe discovered sidecar stems are ignored in read-only ops discovery
- malformed discovered sidecars do not crash read-only ops discovery
- supplied validated article mapping is used exactly and sorted deterministically
- HTML id parsing accepts standard attribute variants
- empty-paragraph sidecars, including skipped sidecars, do not require local
  article section, body container, paragraph, or content-section anchors
- `validate_row_one_local_article_content_health(...)` accepts `not_applicable`
  without raising

Status tests should prove:

- `row-one status --json` includes CLI-only `local_article_content`
- `row-one status` succeeds for generated article pages with saved body and
  anchors
- `row-one status` rejects missing local article section anchors when sidecars
  exist
- `row-one status` rejects missing saved-body container anchors when sidecars
  exist
- `row-one status` rejects missing paragraph anchors
- `row-one status` rejects missing content-section anchors

Ops-check tests should prove:

- content health is included in JSON payloads
- missing local article content produces `attention`
- missing local article content produces a refresh action
- human ops-check output includes the content-health line

Docs and workflow tests should prove:

- README and `docs/row-one.md` include the exact Stage 375 boundary paragraph
  before Stage 374
- stale boundary phrases are absent
- generated app/runtime/manifest contracts do not contain Stage 375 identifiers
- forbidden Stage 375 artifact names are not generated
- the content-health analyzer is read-only and generated-site-only

## Out of Scope

Stage 375 does not add social platform connectors, crawling, article acquisition,
article extraction, LLM summarization, recommendation logic, analytics, app UI,
deployment, image generation, homepage modules, article library visual modules,
article-page visual modules, or compliance-review behavior.
