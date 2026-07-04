## Verdict

Approve. Both prior Important findings are resolved. The literal-angle guard now
excludes known HTML tags via `ROW_ONE_KNOWN_HTML_TAGS`, so real bare tags such
as `<p>`, `<b>`, `<br>`, and `<i>` reach `PlainTextHTMLParser` and flatten
normally instead of being turned into visible escaped tag text, while genuine
literal tokens like `<angle>` are still preserved as escaped display text.

## Prior Findings

1. **Literal-angle protection regex matched real HTML tags.** Resolved.
   `protect_literal_angle_tokens` now checks whether the token is in known
   block, inline, void, script, or style tags and leaves those matches unchanged
   for the HTML parser.
2. **Missing regression test for real HTML tag interaction with the angle
   guard.** Resolved. `test_render_row_one_site_cleans_story_summary_display_without_changing_payload`
   now feeds bare `<p><b>` alongside `<angle>` and asserts real tags are absent
   while `&lt;angle&gt;` is retained in index, detail, and meta output.

## Remaining Critical/Important

None.

The order of operations in `_display_summary_text` is protect, clean, then
restore, and each call site escapes output after restore. The raw fallback is
also escaped at call sites, so it remains safe though it may be cosmetically
imperfect for pathological all-boilerplate summaries.
