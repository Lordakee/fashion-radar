# Stage 175 Entity-Pack Quality Sample Parity Design

## Objective

Keep `docs/entity-pack-quality.md` synchronized with the current
`entity-pack-lint` output for the checked-in starter watchlist pack, without
changing runtime lint behavior.

## Current Gap

`docs/entity-pack-quality.md` documents table and JSON examples for:

```bash
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json
```

The table sample currently matches the current renderer prefix, but no test
guards that parity. The JSON sample is more problematic: it documents the same
top-level shape as the runtime payload, but several count maps are abbreviated
and the single example finding is not explicitly described as a shortened
excerpt. That makes the docs easy to drift from the actual
`lint_entity_pack(...)` output.

Current runtime output for the starter watchlist pack includes:

- `entity_count`: `28`
- `alias_count`: `45`
- `type_counts`: `brand=10`, `category=5`, `celebrity=2`, `designer=2`,
  `product=6`, `trend=3`
- `tag_counts`: 16 configured tag lanes
- `category_tag_counts`: 9 configured category tag lanes
- matcher-gate counters:
  - `accepted_without_context_aliases`: `22`
  - `context_gated_aliases`: `4`
  - `safe_aliases`: `7`
  - `product_parent_gated_aliases`: `12`
- findings: `0` errors, `16` warnings, `61` info

The docs should keep the count fields exact while avoiding a huge 77-finding
JSON dump. The JSON example should explicitly say it is an abbreviated
representative excerpt and should show the first current finding from the real
lint output.

## Scope

In scope:

- Add docs/runtime parity tests in `tests/test_entity_pack_quality_docs.py`.
- Parse the `docs/entity-pack-quality.md` table sample and compare it with the
  current `render_entity_pack_lint_table(lint_entity_pack(...))` prefix.
- Parse the JSON sample and compare stable count fields to
  `lint_entity_pack(configs/entity-packs/fashion-watchlist.example.yaml)`.
- Require the JSON docs to state that the sample is an abbreviated
  representative excerpt, with one representative finding rather than the full
  findings list.
- Update `docs/entity-pack-quality.md` JSON sample count maps and first finding
  so the tested fields match current runtime output.

Out of scope:

- No changes to `src/fashion_radar/entity_packs.py`.
- No changes to `src/fashion_radar/cli.py`.
- No changes to entity pack YAML config.
- No changes to matcher behavior, scoring behavior, runtime lint payload shape,
  renderer behavior, CLI exit behavior, install hints, mirror hints, dependency
  manifests, or `uv.lock`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification, or
  compliance-review product feature.

## Architecture

Modify only:

```text
tests/test_entity_pack_quality_docs.py
docs/entity-pack-quality.md
```

The tests should follow the Stage 168 source-pack docs/runtime parity pattern:
read the Markdown file, extract a fenced code block, parse JSON with the Python
standard library, and use the production linter as the source of truth for
current counts.

Add constants:

```python
WATCHLIST_ENTITY_PACK = ROOT / "configs" / "entity-packs" / "fashion-watchlist.example.yaml"
```

The table sample documents the relative path used in the CLI examples, so the
table parity test must pass `WATCHLIST_ENTITY_PACK.relative_to(ROOT)` into
`lint_entity_pack(...)`. The JSON test can use the absolute constant for file
location and compare the documented path with
`WATCHLIST_ENTITY_PACK.relative_to(ROOT).as_posix()`.

Add helpers:

- `_fenced_block_after(text, marker, language)` for extracting the first fenced
  block after a marker.
- `_entity_pack_quality_table_sample()` for the table sample under
  `## Table Output`.
- `_entity_pack_quality_json_sample()` for the JSON sample under
  `## JSON Output`.
- `_json_ready_first_finding(result)` to compare the already-computed first
  finding using Pydantic's JSON-mode serialization.

Add two tests:

1. `test_entity_pack_quality_table_sample_matches_watchlist_lint_prefix`
   compares the documented table sample with the first N lines of
   `render_entity_pack_lint_table(lint_entity_pack(relative_pack_path))`, where
   `relative_pack_path` is `WATCHLIST_ENTITY_PACK.relative_to(ROOT)`.
2. `test_entity_pack_quality_json_sample_matches_watchlist_lint_counts`
   compares:
   - `path`
   - `entity_count`
   - `alias_count`
   - `type_counts`
   - `tag_counts`
   - `category_tag_counts`
   - the four matcher-gate counters
   - a single representative finding equal to the current first finding
   - prose that says the findings list is abbreviated and not the full findings
     list

The tests should not run CLI commands, open SQLite, match entities, score
entities, fetch sources, or create artifacts.

## Tech Stack

- Python standard library `json`.
- Existing `fashion_radar.entity_packs.lint_entity_pack`.
- Existing `fashion_radar.entity_packs.render_entity_pack_lint_table`.
- Pytest.
- Markdown docs.
- `uv --no-config run --frozen`.
- Local opencode reviews with `zhipuai-coding-plan/glm-5.2 --variant max`.

## Implementation Method

Use TDD:

1. Add the JSON/table docs parity tests first.
2. Run the new JSON parity test and confirm it fails against current docs because
   the documented JSON count maps are abbreviated and the representative finding
   does not match the current first finding.
3. Update only `docs/entity-pack-quality.md` so the JSON sample's tested fields
   match current linter output and the prose clearly says the findings list is
   abbreviated.
4. Re-run the focused tests and lint checks.
5. Run opencode code review, release gate, opencode release review, commit, and
   push.

## Expected Behavior

- The entity-pack quality table sample remains synchronized with the current
  public starter watchlist lint table prefix.
- The JSON sample's stable count fields match current `lint_entity_pack(...)`
  output for the checked-in starter watchlist pack.
- The JSON sample stays readable by showing one representative finding rather
  than the full findings list.
- The docs explicitly state that the JSON finding list is abbreviated.
- Runtime behavior remains unchanged.

## Risks

- Requiring the full 77-finding JSON payload in docs would make the guide noisy
  and harder to maintain. The design avoids that by testing exact counts plus
  one representative first finding.
- Over-generalizing from the starter watchlist could imply live fashion demand
  coverage. The docs should keep the existing local configuration quality
  boundary.
- Changing runtime linter output would expand the node unnecessarily and is out
  of scope.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py::test_entity_pack_quality_json_sample_matches_watchlist_lint_counts -q
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_entity_pack_lint.py tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_entity_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_entity_pack_quality_docs.py
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```
