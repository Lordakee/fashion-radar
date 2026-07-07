# Stage 340 ROW ONE Saved Article Paragraph Quality Gate Design

## Objective

Stage 340 improves the quality of locally saved article bodies by filtering obvious extraction noise before the text is stored in `data/articles/<story-id>.json` and rendered into `details/*.html`, `articles/index.html`, and first-class `articles/<story-id>.html` pages.

Stage 339 made local article reading first class. The next practical quality issue is that source extraction can occasionally surface site chrome, cookie banners, newsletter prompts, share prompts, image credits, RSS fragments, script leftovers, or navigation text as article paragraphs. Stage 340 adds a deterministic paragraph quality gate so the saved local reading experience contains publishable fashion-news text instead of boilerplate.

## User-Facing Result

When ROW ONE builds daily local article pages:

- Saved local article paragraphs exclude high-confidence boilerplate such as cookie banners, newsletter prompts, share widgets, navigation labels, ads, code fragments, and pure source metadata.
- Short but valid fashion-news paragraphs remain publishable.
- If an extracted article contains only low-quality paragraphs, ROW ONE falls back to the existing story summary article path with the existing `summary_fallback` behavior.
- Existing local article pages, detail-page anchors, saved article library links, article sidecars, and content-section paragraph indices continue to work.
- The feature remains invisible to app-facing JSON contracts except through cleaner existing paragraph text.

## Scope

### In Scope

- Add a deterministic private paragraph-quality predicate in `src/fashion_radar/row_one/articles.py`.
- Apply the predicate inside `text_to_local_article_paragraphs()` after normalization and before character-budget accounting.
- Filter high-confidence low-quality paragraphs without consuming the `max_chars` budget.
- Preserve short valid English and Chinese fashion-news sentences.
- Preserve existing `summary_fallback` and `no_publishable_paragraphs` behavior when all extracted paragraphs are filtered out.
- Add tests for boilerplate filtering, short valid paragraph preservation, fallback behavior, mixed extracted text, and paragraph-index alignment.
- Document the Stage 340 boundary in `README.md`, `docs/row-one.md`, and doc/workflow guard tests.

### Out of Scope

- No new scraping, fetching, extraction engine, platform API, connector, social-media crawler, scheduling, deployment, image generation, translation service, LLM summarization, ranking, heat scoring, trend scoring, market grouping, or compliance-review feature.
- No change to `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schema files, `data/edition.json`, `data/manifest.json`, or `data/runtime.json` contracts.
- No new JSON artifact such as `data/saved-article-paragraph-quality-gate.json`.
- No deletion or hiding of saved local articles that already have publishable paragraphs.
- No full article publication on the library index beyond existing capped local excerpts and links.
- No broad minimum-length rule, entity-required rule, or source-specific heuristic that could drop terse valid fashion-news paragraphs.

## Architecture

Stage 340 stays inside the ROW ONE local article preparation path.

`build_row_one_local_articles()` already calls `_build_story_local_article()` for each current-edition story. For extracted source text, `_story_local_article_paragraph_sets()` calls `text_to_local_article_paragraphs()`, and all downstream article fields use the resulting `paragraphs`. That makes `text_to_local_article_paragraphs()` the right choke point: filtering there keeps `paragraphs`, `paragraphs_zh`, `content_sections[*].items[*].paragraph_indices`, saved detail anchors, local article pages, and saved article library excerpts aligned around the final publishable paragraph list.

The gate should be conservative and deterministic. It should match full-paragraph or anchored boilerplate patterns, not generic words in the middle of otherwise valid reporting. For example, `Share this article` should be filtered, while `The share price rose after demand improved.` should remain.

## Quality Gate Rules

The private predicate should normalize whitespace and casefold text before matching. It should reject paragraphs only when they match high-confidence categories:

- Subscription, login, and paywall prompts: `subscribe to continue`, `sign in`, `create an account`, `already a subscriber`, `free article limit`.
- Cookie and privacy banners: `we use cookies`, `accept cookies`, `privacy policy`, `manage preferences`.
- Navigation and site chrome: `skip to content`, `back to top`, `related articles`, `share this article`, isolated `menu` or `search`.
- Newsletter, app, and social prompts: `sign up for our newsletter`, `subscribe to our newsletter`, `download our app`, `follow us on Instagram`.
- Ad and sponsored fragments: isolated `Advertisement`, `Sponsored content`, `Paid post`, affiliate disclosures.
- Code or style leftovers: `<script`, `window.`, `document.`, CSS declaration-heavy text, pure URLs, or URL-heavy paragraphs.
- Pure metadata fragments when the entire paragraph is short metadata: `By ...`, datelines, copyright notices, image credits.
- Obvious Chinese boilerplate: `阅读全文`, `点击查看全文`, `订阅`, `登录后继续`, `广告`, `分享本文`.

The predicate must not reject solely because a paragraph is short. These examples remain valid:

- `Prices rose.`
- `Buyers cited demand.`
- `The Row opened a showroom.`
- `Miu Miu named a CEO.`
- `Zendaya wore Margaux.`
- `Sales rose 8%.`
- `品牌发布了新系列。`
- Existing fallback/editorial text such as `Summary` and `Editorial`.

## Fallback Behavior

No new fallback state is needed. If filtering causes extracted paragraphs to be empty, existing `_build_story_local_article()` logic should continue into `_fallback_story_summary_article()` with `reason="no_publishable_paragraphs"`.

If fallback summary text itself is terse, it should still be kept unless it matches high-confidence boilerplate. Stage 340 should not turn fallback summaries into skipped articles through a broad length or entity rule.

## Safety Invariants

- Low-quality paragraphs do not consume `max_chars`.
- Paragraph filtering happens before content-section paragraph indices are computed.
- `paragraphs_zh` length remains aligned with `paragraphs`.
- Existing `details/*.html#local-article-paragraph-N` and `articles/<story-id>.html#local-article-paragraph-N` anchors continue to point to rendered paragraphs.
- `body_source="extracted"` remains when at least one extracted paragraph survives filtering.
- `body_source="summary_fallback"` remains when extracted text has no publishable paragraphs and story summary fallback is available.
- App/runtime/manifest schemas and contract versions remain unchanged.

## Testing Strategy

Tests should verify:

- `text_to_local_article_paragraphs()` filters cookie, newsletter, share, navigation, ad, code, URL-heavy, image-credit, RSS, and Chinese boilerplate fragments.
- Filtered fragments do not consume the character budget.
- Short valid English and Chinese fashion-news paragraphs survive.
- Mixed low-quality and valid extracted text still produces an extracted article.
- Low-quality-only extracted text falls back to the story summary article with `reason="no_publishable_paragraphs"`.
- Content-section paragraph indices align after a filtered preface paragraph is removed.
- Existing text cleaning behavior still strips generated prefixes, feed HTML, scripts/styles, duplicate sentences, and existing boilerplate.
- Stage 339 local article page/library render tests continue to pass.
- Documentation and workflow guards confirm Stage 340 is local article text cleanup only and does not create new contract artifacts.

## Documentation

Update:

- `README.md` stage history with Stage 340 boundaries.
- `docs/row-one.md` local article article-body quality notes.
- `tests/test_row_one_docs.py` with a Stage 340 boundary guard.
- `tests/test_workflows.py` with contract/artifact guard assertions.

## Definition of Done

Stage 340 is complete when:

- Saved local article bodies filter high-confidence extraction boilerplate before sidecar and HTML rendering.
- Short valid fashion-news paragraphs are preserved.
- Extracted-only boilerplate falls back through the existing summary fallback path.
- Paragraph indices and bilingual paragraph alignment remain correct.
- No JSON/app/runtime/manifest contract changes are introduced.
- Focused tests, full pytest, ruff, format check, lock check, secret scan, code review, commit, and push all pass.
