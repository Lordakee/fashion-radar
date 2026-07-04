## Verdict

Approve with one Important finding. Shared text helper extraction preserves
Stage 293 article behavior; render-time cleaning is correctly scoped to the four
static HTML summary surfaces and leaves `edition.summary`,
`build_row_one_app_payload`, `data/edition.json`, article sidecars, and SQLite
untouched. Output escaping keeps the new code safe, but the literal-angle
preservation feature added beyond the original plan has an over-broad match
pattern that captures real HTML tags, not just literal tokens, and lacks a
regression test for that case.

## Critical

None.

## Important

1. **Literal-angle protection regex matches real HTML tags.**
`ROW_ONE_LITERAL_ANGLE_RE` matches every bare `<word>` token, including real HTML
tag names that appear without attributes such as `<p>`, `<b>`, `<i>`, `<em>`,
`<strong>`, `<br>`, `<li>`, and table tags. These occur in RSS/Atom summaries.
For a summary like `<p>The Row expanded.</p>`, protection converts the opening
`<p>` into a placeholder, the HTML parser no longer sees the start tag, the
closing `</p>` is stripped, and restore emits visible literal `<p>` text.
Suggested fix: skip any match whose captured name is an HTML tag known to the
cleaner, or narrow the regex with a negative lookahead on that set.

2. **No regression test for real HTML tag interaction with the angle guard.**
The render test exercises `<angle>` and a custom feed tag with attributes, but
does not cover real bare tags such as `<p>`, `<b>`, or `<br>`. Add a render test
that asserts such summaries flatten to plain text with no surviving `&lt;p&gt;`
or `&lt;b&gt;` tokens.

## Residual Risks

- `_display_summary_text` intentionally falls back to normalized raw text when
  cleaning yields no sentences. Call-site escaping keeps this safe, but purely
  boilerplate summaries may still display imperfect text.
- Local article cleanup does not preserve literal `<angle>` tokens; that
  preserves Stage 293 behavior and is intentionally different from static
  summary display.
- `_display_summary_text` constructs a parser per call. This is acceptable for
  current edition sizes but could be optimized if editions become much larger.
- The generated-site acceptance scan does not include `<p>` / `<b>` / `<br>`;
  the new regression test should cover that specific issue.
