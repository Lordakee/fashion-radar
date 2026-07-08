Review current uncommitted Stage 341 diff in /home/ubuntu/fashion-radar.

Goal: generated-site-only Local Article Information Panel on `articles/<story-id>.html`.

Inspect:
- src/fashion_radar/row_one/templates.py
- tests/test_row_one_render.py
- README.md, docs/row-one.md, tests/test_row_one_docs.py, tests/test_workflows.py

Focus:
- No redefinition/breakage of existing `_local_article_body_source_label(article) -> str`.
- Panel uses `_local_article_body_source_label_localized()` and `_local_article_rendered_paragraph_indices(article)` with `_strict_valid_local_article_paragraph_indices()`.
- All panel hrefs are same-page `#local-article-*` links; no outbound URLs.
- Escaping, dedupe, caps, and invalid paragraph-index filtering are sound.
- No schema/model/render.py/JSON contract/artifact drift.

Already run:
- focused render: 6 passed
- docs/workflows: 75 passed
- render+docs+workflows: 280 passed
- ruff check/format check/diff check passed for touched files

Reply only:
Approved/Not approved
Critical findings
Important findings
Minor findings
Recommended fixes before commit
