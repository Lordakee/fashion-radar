# Opencode Stage 54 Plan Review Prompt

You are reviewing the Stage 54 implementation plan for the `fashion-radar`
repository before implementation continues.

Required review mode:

- Review model: GLM 5.2 via local opencode
  (`zhipuai-coding-plan/glm-5.2`).
- This is a plan review only.
- Do not edit files.
- Do not inspect the repository; review only the self-contained context below.
- Do not narrate tool usage or file-reading steps.
- Treat Critical and Important findings as blocking.

## Goal

Add sanitized, importable external tool handoff templates for future
user-controlled community/social tools. The templates let outside tools write
local CSV/JSON files that Fashion Radar can lint, preview, dry-run import, and
import through the existing community signal boundary.

## Required Boundaries

Stage 54 must not add:

- a new CLI command;
- schema changes;
- dependencies or lockfile changes;
- scraping, crawling, browser automation, account login, cookies, sessions,
  tokens, platform API clients, source acquisition, monitoring, scheduling,
  media download, connector code, demand proof, platform coverage verification,
  source ranking, compliance review, legal review, approval UI, or policy
  workflow.

Fashion Radar remains the consumer of local sanitized files only. External
community/social producers remain outside this repo.

## Planned Technical Approach

The existing producer surfaces already exist:

- `community-signal-profile` prints the producer contract.
- `community-handoff-manifest` prints a directory manifest and workflow.
- `community-handoff-workflow` prints the local lint, preview, dry-run import,
  import, and post-import review sequence.
- The existing importer/linter/candidate preview commands operate on local
  files only.

Stage 54 will reuse those surfaces and add static examples only:

- Add `examples/community-tool-handoff.example.csv`.
- Add `examples/community-tool-handoff.example.json`.
- Update `src/fashion_radar/community_signal_profile.py` so
  `COMMUNITY_SIGNAL_EXAMPLE_PATHS` becomes:

  ```python
  [
      "examples/community-signals.example.csv",
      "examples/community-signals.example.json",
      "examples/community-tool-handoff.example.csv",
      "examples/community-tool-handoff.example.json",
  ]
  ```

- Regenerate `examples/community-signal-profile.example.json` so profile and
  derived manifest output expose the two new paths.
- Update frozen profile/manifest/CLI tests to expect those four example paths.
- Update package archive checks so the new examples must ship in sdists.
- Update docs and docs drift tests so the handoff template is discoverable and
  clearly bounded as sanitized CSV/JSON local file handoff.

## Planned Template Fields

Both new templates must use only existing community signal schema fields:

- `url`
- `title`
- `published_at`
- `summary`
- `source_name`
- `platform`
- `source_weight`
- `collected_at`

The JSON template must use the already supported envelope:

```json
{
  "items": [
    {
      "url": "https://example.com/community-tool/ballet-flat-signal",
      "title": "Ballet flat observed signal",
      "published_at": "2026-06-12T12:00:00Z",
      "summary": "Synthetic sanitized observation about ballet flats from a user-controlled tool.",
      "source_name": "External Community Tool",
      "platform": "community",
      "source_weight": 1.2,
      "collected_at": "2026-06-12T12:10:00Z"
    }
  ]
}
```

The CSV template will use the same fields and synthetic `example.com` rows.

## Planned Tests

Update or add coverage in:

- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_community_signal_profile.py`
- `tests/test_community_handoff_manifest.py`
- `tests/test_cli.py`
- `tests/test_package_archives.py`
- `tests/test_cli_docs.py`

The tests should verify:

- all four importable community examples use only schema fields;
- all four examples lint cleanly;
- dry-run import accepts all four examples without writing artifacts;
- profile and manifest `example_paths` include all four examples;
- CLI JSON output keeps stable keys and the new paths;
- the new examples are required in package archives;
- docs mention both new template paths;
- docs describe the template as sanitized CSV/JSON local file handoff;
- docs do not imply platform connectors or platform collection.

## Planned Verification

Targeted tests:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_handoff_manifest_command_prints_json_with_stable_keys -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py tests/test_cli_docs.py -q
```

Full release verification:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
uv build plus package archive check and installed-wheel smoke
```

## Review Questions

1. Is reusing `COMMUNITY_SIGNAL_EXAMPLE_PATHS` for the two new importable
   templates technically appropriate?
2. Are the planned template fields valid and sufficiently sanitized?
3. Does the plan avoid runtime behavior changes and new CLI/API/scraping
   behavior?
4. Are the planned tests and package checks sufficient for this static-template
   change?
5. Is the verification plan sufficient, including mirror-free `uv.lock` checks?
6. Is the node-specific switch to local opencode review represented clearly
   without rewriting historical `claude-code-*` records?

## Required Output

Respond with:

- `## Critical Findings`
- `## Important Findings`
- `## Minor Findings`
- `## Verdict`

If and only if the plan is acceptable to execute, include this exact phrase in
the verdict:

```text
APPROVED FOR STAGE 54 EXTERNAL TOOL HANDOFF TEMPLATES
```
