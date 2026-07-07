Review Stage 337 changes in /home/ubuntu/fashion-radar.

Goal: add a generated-site-only ROW ONE Saved Article Reference Atlas inside articles/index.html. It aggregates existing RowOneReference chips from saved local article content organization into Brands / People / Products / Source Context buckets.

Boundary:
- No app/runtime/manifest/schema/JSON contract changes.
- No data/saved-article-reference-atlas.json.
- No source collection, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, social/community, or compliance product behavior.
- No outbound article URLs in the atlas.
- Links must be internal validated detail anchors only: #local-article-content-section-N and optional #local-article-paragraph-N.

Please inspect the diff and relevant files:
- src/fashion_radar/row_one/saved_article_reference_atlas.py
- src/fashion_radar/row_one/render.py
- src/fashion_radar/row_one/templates.py
- tests/test_row_one_saved_article_reference_atlas.py
- tests/test_row_one_render.py
- tests/test_row_one_docs.py
- README.md
- docs/row-one.md
- docs/superpowers/specs/2026-07-08-stage-337-row-one-saved-article-reference-atlas-design.md

Prior focused verification passed:
- pytest tests/test_row_one_saved_article_reference_atlas.py -q
- pytest tests/test_row_one_render.py -q -k "reference_atlas or theme_digest or saved_signal_index or saved_article_library"
- pytest tests/test_row_one_docs.py -q -k "stage_337 or saved_article_reference_atlas"
- ruff check on touched code/test files

Return findings only, grouped by Critical / Important / Nice-to-have. Focus on correctness, boundary violations, unsafe links, missing tests, contract pollution, and maintainability. If no Critical/Important issues, say so explicitly.
