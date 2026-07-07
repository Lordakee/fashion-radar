Review Stage 323 ROW ONE Local-First Reading implementation.

Return a complete, concise review under 80 lines. Lead with Critical and
Important findings only. If there are no unresolved Critical or Important
findings, state that clearly.

Repo: /home/ubuntu/fashion-radar
Branch: main
Base commit before this node: da95a41

Implemented scope:
- Generated ROW ONE HTML/CSS only.
- `render_row_one_site()` passes the existing local article map into
  `render_index_html()` as a private render argument.
- Homepage lead/story CTAs become `Read saved article / 阅读本地正文` and link to
  `details/<story>.html#local-article` when the story has usable saved local
  paragraphs.
- Detail pages render a local-first action before the external source action
  when the local article section exists.
- Saved article content-organization cards are now `<article>` containers with
  standalone organized-section links.
- Saved content-organization cards expose capped, deduped, safe evidence
  paragraph links from existing `card.paragraph_indices`.
- External source links remain provenance.
- No app/runtime/manifest JSON contract fields were added.

Files changed:
- `src/fashion_radar/row_one/templates.py`
- `src/fashion_radar/row_one/render.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 323 spec/plan/review artifacts

Hard boundaries:
- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not add `local_first_read`, `local_read_path`, `saved_article_cta`,
  `evidence_paragraph_trail`, `paragraph_trail`, `evidence_paragraph_chips`,
  or `saved_article_content_organization_evidence` to app/runtime/manifest
  payloads.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not add source collection, article fetching, extraction behavior, scoring,
  matching, ranking, LLM calls, translation calls, image generation,
  connectors, deployment behavior, scheduling behavior, or compliance-review
  product features.
- Do not rename story IDs, detail routes, local article anchors, paragraph
  anchors, or content-section anchors.
- Do not add dependencies.

Verification already run:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "saved_article_reading or saved_article_action or local_first or saved_article_content_organization or local_article_content or editorial_brief or stage_323" -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k row_one -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q`
- `UV_NO_CONFIG=1 uv lock --check`
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`
- `git diff --check`

Please review for:
- correctness and technical reasonableness
- href safety
- no nested anchors
- local-first action eligibility
- no JSON contract/schema/artifact mutation
- docs/test coverage
- any Critical or Important findings that must be fixed before push
