# Stage 361 Daily Local Article Reading Brief Design

## Context

Stage 360 added homepage Daily Local Article Capsules, which turn saved local
article text into compact article cards with same-site article links. The next
useful increment is to organize those saved articles into an editorial reading
brief that answers what to read first and why, without adding new data
contracts or relying on new extraction, scoring, ranking, LLM, connector, or
scheduling behavior.

## Goal

Add a generated-site-only homepage section named **Daily Local Article Reading
Brief**. It should sit after Daily Local Article Capsules and before Saved
Article Content Organization. It should group already-saved local article
content into deterministic reading lanes, using existing current-edition
stories, `RowOneLocalArticle` paragraphs, `brief_sections`, `content_sections`,
story references, body-source labels, generated local article page hrefs, and
existing local article anchors.

## Non-Goals

- Do not add app-facing schema or payload fields.
- Do not create `data/daily-local-article-reading-brief.json`,
  `data/daily-local-reading-brief.json`, or `data/article-reading-brief.json`.
- Do not create new route families or standalone HTML artifacts for the brief.
- Do not publish full articles on the homepage.
- Do not add outbound article URLs as primary navigation.
- Do not add fetching, extraction, scoring, ranking, LLM, connector,
  scheduling, deployment, analytics, personalization, recommendation, or
  compliance-review behavior.

## Design

The homepage renderer derives a capped set of reading-brief groups from the
current edition and already-saved local articles. The renderer stays in
`templates.py` and accepts the same generated article href map that Stage 360
uses.

The section has three deterministic lanes:

1. **Read First** / **先读这个**: earliest eligible current-edition articles
   with usable saved paragraphs.
2. **Brand Watch** / **品牌观察**: articles whose story references include
   brand/person/designer entities or whose local article content sections use
   `entities` or `brand_signals`.
3. **Product Watch** / **单品观察**: articles whose story references include
   product-like objects or whose local article content sections use
   `product_signals`.

Lane descriptions are fixed copy:

- Read First: EN `Start with the saved local articles that set the day's
  editorial context.` / ZH `先读建立今日编辑背景的本地保存文章。`
- Brand Watch: EN `Brand and designer reads pulled from current saved local
  text.` / ZH `来自当前本地保存正文的品牌与设计师阅读线索。`
- Product Watch: EN `Product reads that connect saved paragraphs to items,
  bags, shoes, and accessories.` / ZH `把保存段落连接到单品、手袋、鞋履与配饰的阅读线索。`

Each lane renders up to three article rows. Each row contains:

- story headline and local article title fallback;
- source name and body-source label;
- a short reason drawn from `story.why_it_matters`, then first local article
  brief section, then first content-section item, then first saved paragraph;
- same-site article digest link;
- one paragraph anchor chip built from the first valid saved paragraph used by
  the row.

Links are emitted only when the generated local article page href map contains
a safe single-file `.html` href whose filename stem equals the current story id.
The renderer never derives article links from story IDs alone.

The fill order is deterministic: build Read First first, then Brand Watch, then
Product Watch. Deduplicate story ids across groups in that order, then stop
after four total rendered items.

Item title construction is deterministic: `title.en` is the normalized
`RowOneStory.headline`; `title.zh` is the normalized `RowOneLocalArticle.title`
when present, otherwise the normalized story headline. `article_title` stores
the same normalized local article title as a subtitle/meta value and is omitted
when the article has no title.

## Rendering Boundary

The feature renders only inside `index.html`. It does not alter:

- `articles/index.html`;
- `articles/<story-id>.html`;
- story detail pages;
- `data/edition.json`;
- `data/manifest.json`;
- `data/runtime.json`;
- local article sidecar JSON.

## Testing Strategy

Tests should follow Stage 360 patterns:

- direct render test for headings, grouping, ordering, caps, reasons, body
  source labels, paragraph anchors, same-site links, and escaping;
- filtering test for unsafe story ids, missing articles, empty paragraphs,
  unsafe hrefs, traversal, nested paths, whitespace hrefs, leading dots/slashes,
  and mismatched href stems;
- placement test after Daily Local Article Capsules and before Saved Article
  Content Organization;
- site-generation test proving homepage-only behavior and contract/artifact
  denylist;
- CSS selector test;
- docs boundary test in both README and `docs/row-one.md`;
- workflow generated-site-only guard test.

## Review Notes

This is intentionally a presentation layer. It improves the website's ability
to organize downloaded/local article information without claiming new analysis,
trend scores, or generated summaries beyond deterministic excerpts from saved
content.
