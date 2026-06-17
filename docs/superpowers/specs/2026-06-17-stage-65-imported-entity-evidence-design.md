# Stage 65 Imported Entity Evidence Design

## Goal

Add a local read-only `imported-entity-evidence` CLI command that shows the
retained `manual_import` rows behind one matched imported entity, such as a
brand, product, category, trend, bag, or shoe. This closes the drilldown gap
after `imported-entity-deltas`: users can see that "The Row" or a product moved
in imported community/social handoff data, then inspect which retained local
rows explain that movement.

## Scope

Stage 65 is a narrow evidence drilldown.

In scope:

- Query an existing local SQLite database in read-only mode.
- Join `items` and `item_entities` for retained `manual_import` rows.
- Filter by exact `entity_name`, exact `entity_type`, optional exact
  `source_name`, and current/baseline collected-at windows.
- Deduplicate by `items.id` so duplicate aliases or duplicate stored matches for
  the same requested entity do not inflate evidence rows.
- Print table and JSON output.
- Include only privacy-safe retained item fields:
  `window`, `id`, `source_name`, `title`, `url`, `published_at`, and
  `collected_at`.
- Reuse the same window semantics as `imported-entity-deltas`:
  - baseline: `baseline_window_start < collected_at <= current_window_start`
  - current: `current_window_start < collected_at <= as_of`
- Update the imported review workflow to print this evidence command as an
  optional example step for a supplied entity name/type.
- Update README, CLI reference, source-boundary, architecture, quality, upload
  checklist, AGENTS, and CHANGELOG docs.
- Add package/first-run smoke coverage where useful.

Out of scope:

- No scraping, browser automation, social platform API calls, account/cookie
  behavior, media download, monitoring, scheduling, source acquisition, demand
  proof, ranking, coverage verification, or compliance-review product feature.
- No schema migration.
- No matching refresh or `match` execution.
- No raw summaries, full post bodies, raw comments, handles, profile URLs,
  media URLs, account IDs, source file paths, importer internals, match reasons,
  aliases, confidence values, or context terms in this first version.
- No dashboard evidence browser.
- No changes to heat scoring or trend semantics.
- No adapter readiness metadata changes in this stage.

## User Flow

The expected flow is:

```bash
uv run fashion-radar imported-entity-deltas \
  --data-dir "$PWD/data" \
  --as-of "$AS_OF" \
  --format json

uv run fashion-radar imported-entity-evidence \
  --data-dir "$PWD/data" \
  --as-of "$AS_OF" \
  --entity-name "The Row" \
  --entity-type brand \
  --source-name "Community Tool Export" \
  --format json
```

The first command shows aggregate imported entity movement. The second command
shows the retained local rows behind one selected entity. The evidence command
does not explain total `heat-movers` output by itself, because `heat-movers`
can include configured RSS/GDELT/web sources plus imported rows. It explains
only retained imported `manual_import` rows.

## Data Model

Create `src/fashion_radar/imported_entity_evidence.py`.

Models:

- `ImportedEntityEvidenceRow`
  - `id: int`
  - `window: Literal["current", "baseline"]`
  - `source_name: str`
  - `title: str`
  - `url: str`
  - `published_at: str`
  - `collected_at: str`
- `ImportedEntityEvidenceReview`
  - `database: str`
  - `as_of: str`
  - `entity_name: str`
  - `entity_type: str`
  - `current_window_start: str`
  - `baseline_window_start: str`
  - `current_days: int = 7`
  - `baseline_days: int = 7`
  - `source_type: Literal["manual_import"] = "manual_import"`
  - `source_name: str | None = None`
  - `limit: int | None = 20`
  - `row_count: int = 0`
  - `total_count: int = 0`
  - `current_mentions: int = 0`
  - `baseline_mentions: int = 0`
  - `distinct_sources: int = 0`
  - `evidence: list[ImportedEntityEvidenceRow]`

The JSON key order must be stable and tested.

## Query Semantics

`query_imported_entity_evidence(db_path, *, as_of, entity_name, entity_type,
current_days=7, baseline_days=7, source_name=None, limit=20)`:

- Rejects `current_days < 1`, `baseline_days < 1`, and negative `limit`.
- Strips `entity_name`, `entity_type`, and `source_name`.
- Rejects blank `entity_name` or `entity_type`.
- Returns an empty review without creating directories if `db_path` does not
  exist.
- Opens SQLite through `create_readonly_sqlite_engine`.
- Calls `verify_imported_signals_schema`.
- Selects from `items` joined to `item_entities` where:
  - `items.source_type == "manual_import"`
  - `item_entities.entity_name == entity_name`
  - `item_entities.entity_type == entity_type`
  - optional `items.source_name == source_name`
- Ignores rows outside `(baseline_window_start, as_of]`.
- Classifies row windows in Python using the same boundary behavior as
  `imported-entity-deltas`.
- Deduplicates by item id after filtering the requested entity. If one item has
  two `item_entities` rows for `"The Row"`/`brand`, the evidence output includes
  that item once.
- Sorts current rows first, then newer `collected_at`, then higher item id.
- Applies `limit` only to visible evidence rows; `total_count`,
  `current_mentions`, `baseline_mentions`, and `distinct_sources` remain based
  on all matching rows. `limit=None` means no visible-row limit.

## Rendering

Table output:

- Starts with `Imported manual entity evidence from local SQLite.`
- States that evidence rows are retained `manual_import` rows whose stored
  matched entity equals the requested entity.
- Prints entity name/type, current and baseline window bounds, source filter,
  row counts, current mentions, baseline mentions, and distinct current sources.
- Prints `Window | ID | Collected At | Source | Title | URL`.
- Sanitizes cells the same way other table renderers do: replace pipes and line
  breaks, collapse whitespace.

JSON output:

- Emits `ImportedEntityEvidenceReview.model_dump_json(indent=2)`.
- Does not include match internals or raw content fields.

## CLI

Add `fashion-radar imported-entity-evidence`.

Options:

- `--data-dir`: shared data directory option.
- `--as-of`: default should reuse the imported review fixed timestamp convention
  used by nearby imported review commands.
- `--entity-name`: required, must not be blank.
- `--entity-type`: required, must not be blank.
- `--source-name`: optional exact stored source name filter.
- `--current-days`: integer, min 1, default 7.
- `--baseline-days`: integer, min 1, default 7.
- `--limit`: integer or none, min 0, default 20.
- `--format`: `table` or `json`, default `table`.

Error messages should follow existing CLI patterns:

- Invalid date: `Could not review imported entity evidence: invalid --as-of: ...`
- Blank entity: `Could not review imported entity evidence: invalid --entity-name: entity name must not be blank`
- Blank type: `Could not review imported entity evidence: invalid --entity-type: entity type must not be blank`
- Query errors: `Could not review imported entity evidence: ...`

## Imported Review Workflow

`imported-review-workflow` should include a new read-only step after
`compare_imported_entities`:

- name: `review_imported_entity_evidence`
- purpose: print the entity drilldown command for one reviewed entity
- command: `fashion-radar imported-entity-evidence --data-dir ... --as-of ... --entity-name "The Row" --entity-type brand ...`
- suggested effect: `read_only`

Because the workflow is print-only and cannot know which entity the user will
choose, this step uses a documented example entity (`The Row`, `brand`).
It should still quote paths and source names correctly. If `--source-name` is
provided to the workflow, the evidence step includes the same source filter.

This changes the workflow step count and first-run smoke fake payload, so tests
must be updated. The workflow remains print-only and does not execute the
evidence command.

## Documentation

Update:

- `README.md`: command examples and local/read-only description near existing
  imported review commands.
- `docs/cli-reference.md`: command reference.
- `docs/community-signal-import.md`: post-import review flow.
- `docs/source-boundaries.md`: imported evidence is local read-only and
  imported-only.
- `docs/architecture.md`: add the drilldown to the local import review layer.
- `docs/community-signal-quality.md`: clarify privacy-safe evidence fields.
- `docs/dashboard.md`: heat movers are aggregate; use CLI entity evidence for
  imported row drilldown.
- `docs/github-upload-checklist.md`: installed-wheel smoke includes help and
  JSON/table checks.
- `AGENTS.md`: future work must keep this command local/read-only.
- `CHANGELOG.md`: Stage 65 entry.

## Tests

New tests:

- `tests/test_imported_entity_evidence.py`:
  - missing database returns empty without creating parent directories
  - filters manual rows, entity name/type, source name, and windows
  - blank source name means no source filter
  - duplicate matches for one item dedupe to one evidence row
  - current/baseline boundary timestamps match imported entity delta semantics
  - `limit=0` preserves counts while hiding visible rows
  - negative limit/current/baseline days and blank entity fields fail
  - table rendering sanitizes pipes and newlines
  - output omits match internals and raw summaries

Extended tests:

- `tests/test_cli.py`:
  - help lists options
  - JSON output works and has stable keys
  - table output works
  - blank entity name/type rejected before query
  - invalid date rejected before query
  - query errors are reported without traceback
- `tests/test_imported_review_workflow.py`:
  - step list includes `review_imported_entity_evidence`
  - command includes example entity name/type and optional source filter
- `tests/test_first_run_smoke.py` and `scripts/check_first_run_smoke.py`:
  - workflow fake payload and validator include the new step
  - first-run flow may include installed help coverage if appropriate
- `tests/test_cli_docs.py`:
  - docs mention the new command and local/read-only/imported-only boundaries

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_imported_entity_evidence.py -q
uv --no-config run --frozen pytest tests/test_cli.py -q -k "imported_entity_evidence"
uv --no-config run --frozen pytest tests/test_imported_review_workflow.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
```

Full gate:

```bash
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Package gate:

```bash
tmp_build="$(mktemp -d)"
tmp_env="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
python3 scripts/check_package_archives.py "$tmp_build"
uv --no-config venv "$tmp_env/venv"
uv --no-config pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" imported-entity-evidence --help
"$tmp_env/venv/bin/fashion-radar" imported-entity-evidence \
  --data-dir "$tmp_env/data" \
  --as-of 2026-06-13T12:00:00Z \
  --entity-name "The Row" \
  --entity-type brand \
  --format json | "$tmp_env/venv/bin/python" -m json.tool >/dev/null
```

Security/release scans:

```bash
rg -n "ghp_[A-Za-z0-9_]{20,}" .
rg -n "mirrors|tuna|aliyun|ustc|pypi.tuna|pypi.mirrors|index-url" uv.lock
```

## Deferred Candidates

The Stage 65 exploration also identified two good follow-up nodes:

- Adapter readiness notes for external tool registry entries.
- First-run smoke guards for repo-local generated config artifacts.

Both are deliberately deferred to keep this node focused on user-visible
entity evidence drilldown.
