Review Fashion Radar Stage 262 before commit.

Repo: /home/ubuntu/fashion-radar

This is a read-only code and documentation review. Do not edit files.

Review the current uncommitted Stage 262 implementation and artifacts:
- docs/row-one.md
- src/fashion_radar/row_one/templates.py
- tests/test_row_one_cli.py
- tests/test_row_one_docs.py
- tests/test_row_one_render.py
- docs/superpowers/specs/2026-07-02-stage-262-row-one-reader-orientation-design.md
- docs/superpowers/plans/2026-07-02-stage-262-row-one-reader-orientation-plan.md
- docs/reviews/claude-code-stage-262-plan-review.md
- docs/reviews/claude-code-stage-262-plan-rereview.md
- docs/reviews/claude-code-stage-262-plan-final-review.md
- docs/REVIEW_PROTOCOL.md
- AGENTS.md

Objective: Stage 262 adds a deterministic reader-orientation layer to ROW ONE: homepage edition contents, section jump links, story counts, story-card orientation metadata, detail-page back-to-section links, and documentation/tests for the presentation-only boundary.

Boundaries: implementation must stay in the ROW ONE presentation layer and use existing RowOneEdition/RowOneSection/RowOneStory data only. It must not change collection, matching, ranking, scoring, story IDs, JSON payload shape, server behavior, cleanup behavior, deployment, translation, LLM calls, platform APIs, demand proof, platform coverage verification, or compliance product behavior. Preserve unsafe URL omission and detail-path validation.

Verification already passed:
- git diff --check
- uv --no-config run --frozen pytest tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py -q
- uv --no-config run --frozen ruff check src/fashion_radar/row_one src/fashion_radar/cli.py tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py
- uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py

Review focus:
- correctness of homepage contents nav, story-card orientation, and detail back-to-section links;
- tests for empty sections, unsafe evidence URLs, undated stories, bilingual labels, CLI smoke behavior, docs boundary language;
- no duplicate source-only card metadata;
- unsafe evidence URLs are not counted as reader-facing evidence links;
- existing ROW ONE JSON contract and generated-site behavior remain unchanged;
- review artifacts are coherent enough to commit after fixes.

Return one coherent review body only:
- Verdict: accept / accept with fixes / reject
- Critical findings
- Important findings
- Minor findings
- Notes
- State whether Stage 262 is acceptable to commit after verification gates pass.

Use file and line references where possible. Do not modify files.
