## Verdict

I1-I3 are resolved. The new tests in `tests/test_row_one_articles.py`
directly pin the previously unpinned behaviors, and the negative short-sentence
test requested in I1 is also present. No Critical or Important items remain.

## I1

Resolved. Two tests now constrain cross-paragraph dedup scope:

- `test_text_to_local_article_paragraphs_dedupes_long_sentences_across_paragraphs`
  places the duplicated long sentence across a `\n\n` split and asserts a single
  surviving paragraph, which would fail if dedup were narrowed to per-paragraph.
- `test_text_to_local_article_paragraphs_keeps_repeated_short_sentences_across_paragraphs`
  is the requested negative test: a legitimately repeated short sentence across
  paragraphs survives, pinning the size-gated dedup boundary.

Whole-text `seen_sentences` behavior is now pinned in both directions.

## I2

Resolved. `test_text_to_local_article_paragraphs_strips_script_and_style_content`
feeds both an inline `<script>` block and a `<style>` block between legitimate
sentences and asserts the script/style content is dropped while surrounding text
is joined cleanly. The security-adjacent `_ignored_depth` path is now covered.

## I3

Resolved. `test_text_to_local_article_paragraphs_strips_chinese_prefix_and_boilerplate`
feeds `来源摘要：品牌发布了新系列。阅读全文。点击查看全文。` and asserts the output is
`["品牌发布了新系列。"]`. This single bilingual test pins the `来源摘要` prefix
match plus both `阅读全文。` and `点击查看全文。` boilerplate entries.

## Remaining Critical/Important

None. The prior Critical section was already empty, and all three prior
Important items are now closed by tests. The residual risks from the original
review are unchanged but remain acceptable, non-blocking test gaps rather than
Critical or Important findings.
