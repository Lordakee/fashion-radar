Review the current uncommitted changes in /home/ubuntu/fashion-radar for Stage 285.

Scope implemented:
- Add existing why_it_matters and signal_context to ROW ONE contentCard payload/schema/tests/docs.
- Add a static detail-information-map after article contents and before summary in ROW ONE detail HTML, derived only from existing RowOneStory fields.
- Update tests/docs/review records.

Constraints:
No dependencies, no source collection/connectors/social platform work, no browser automation, no account/cookie behavior, no LLM/image generation, no scoring/ranking/sorting/story ID/cleanup/scheduler/server/deployment/contract-version changes.

Verification already run:
- UV_NO_CONFIG=1 uv --no-config run python -m json.tool schemas/row-one-app.schema.json >/dev/null
- UV_NO_CONFIG=1 uv --no-config run pytest tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py -q => 152 passed
- UV_NO_CONFIG=1 uv --no-config run ruff check . => passed
- UV_NO_CONFIG=1 uv --no-config run ruff format --check . => passed
- UV_NO_CONFIG=1 uv --no-config run pytest -q => 1860 passed
- UV_NO_CONFIG=1 uv --no-config lock --check => passed
- git diff --check => passed
- git diff --exit-code -- uv.lock pyproject.toml => passed

Return APPROVED or NOT APPROVED. List only Critical/Important findings with file/line references. Focus on correctness, schema contract risk, escaping/XSS risk, tests, docs accuracy, and scope creep. Do not edit files.
