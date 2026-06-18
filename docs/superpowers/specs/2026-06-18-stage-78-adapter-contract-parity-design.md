# Stage 78 Adapter Contract Parity Gate Design

## Goal

Add a focused parity gate proving the external/community tool adapter surfaces
stay aligned with the community signal handoff contract across every built-in
adapter.

## Context

Fashion Radar now has several local-only producer-facing surfaces:

- `external-tool-adapters`
- `external-tool-template`
- `external-tool-workflow`
- `external-tool-readiness`
- `community-signal-profile`
- directory lint/check/import workflow commands

These surfaces are designed for user-controlled external/community tools that
write sanitized CSV/JSON local handoff rows. They must stay in sync as the
project prepares for future handoff data from social/community tools. The risk
is not missing runtime collection behavior; the risk is contract drift between
metadata, template rows, workflow commands, and readiness guidance.

## Scope

In scope:

- Add a test-only adapter contract parity gate covering all seven current
  adapter IDs.
- Prove each adapter's `field_mappings` match the producer
  `community-signal-profile` allowed and required fields.
- Prove each adapter's template model mirrors registry metadata and command
  guidance, while rendered JSON/CSV remains importable rows only.
- Prove every adapter template renders CSV/JSON rows that lint cleanly with
  `community-signal-lint`.
- Prove workflow/readiness command steps stay aligned with the adapter
  recommended command list and preserve dry-run versus real-import separation.
- Prove adapter/workflow/readiness command guidance does not include platform
  acquisition verbs or unsupported platform-operation commands.
- Document the parity guarantee in `docs/community-signal-import.md`.
- Add a changelog entry and stage-local `opencode` review artifacts.

Out of scope:

- Runtime behavior changes.
- Adding or changing adapters.
- Scraping, browser automation, platform APIs, login/session/cookie/token/proxy
  behavior, media downloads, monitoring, scheduling, source acquisition, demand
  proof, ranking, platform coverage verification, or compliance-review product
  features.
- Public dependency or lockfile changes. The current local `uv.lock` mirror
  rewrite remains unrelated and must not be staged.

## Design

Create one new test file:

```text
tests/test_external_tool_contract_parity.py
```

The file should use public builders only:

- `build_community_signal_profile`
- `build_external_tool_adapter_registry`
- `build_external_tool_template`
- `build_external_tool_workflow`
- `build_external_tool_readiness`
- `render_external_tool_template_json`
- `render_external_tool_template_csv`
- `lint_community_signal_file`

Avoid importing private helpers such as `_recommended_commands`. The point of
the gate is to verify the public model outputs that users and CLI renderers rely
on.

Use deterministic inputs:

```python
DIRECTORY = Path("./exports")
CONFIG_DIR = Path("./configs")
DATA_DIR = Path("./data")
AS_OF = "2026-06-13T12:00:00Z"
```

Readiness tests must pass `which=lambda _command: None` so PATH contents do not
change the expected model.

The parity tests should:

1. Compare adapter field mapping order, required flags, and notes to the
   community signal profile.
2. Compare template metadata, field mappings, and recommended commands to the
   registry adapter for every adapter.
3. Render every template as JSON and CSV into temporary files, then lint the
   files with `lint_community_signal_file`.
4. Compare named workflow steps back to the matching adapter recommended
   command indexes.
5. Compare named readiness steps back to the matching adapter recommended
   command indexes.
6. Assert `dry_run_directory_import` includes `--dry-run`, while
   `import_directory_signals` does not.
7. Parse every generated command with `shlex.split` and reject unsupported
   command tokens such as `scrape`, `crawl`, `download`, `watch`, `monitor`,
   `schedule`, `login`, `api`, `playwright`, `browser`, `cookie`, `session`,
   `token`, and `proxy`.

The command-token ban should be scoped to Fashion Radar generated command
strings, not documentation prose. It must not reject legitimate boundary text
that says "no scraping" or install hints that mention upstream tools; those
belong in other docs/readiness tests.

## Documentation

Add a short subsection to `docs/community-signal-import.md`, near the external
tool adapter/template/workflow sections, explaining that the adapter registry,
template models, workflow, and readiness guidance are tested as one local
contract. The wording should emphasize:

- field mappings are derived from `community-signal-profile`;
- JSON/CSV template output remains importable rows only;
- generated guidance is local handoff guidance, not platform collection;
- parity tests guard command drift and dry-run separation.
- dry-run import guidance remains separate from real import guidance;
- the parity gate does not add connectors, prove demand, rank sources, or verify
  platform coverage.

Add a docs drift test in `tests/test_cli_docs.py` to keep this subsection
anchored without over-constraining prose.

## Acceptance Criteria

- New parity tests pass across all seven adapters:
  `rednote_mcp`, `xiaohongshu_crawler`, `instaloader`, `tiktok_api`, `yt_dlp`,
  `x_search_export`, and `generic_community_export`.
- Template JSON and CSV rendered for every adapter lint cleanly and contain only
  community signal row fields.
- Workflow and readiness steps reuse the same command guidance as the adapter
  registry for shared steps.
- Dry-run import guidance remains separate from real import guidance.
- Generated Fashion Radar command guidance contains no unsupported acquisition
  or platform-operation command tokens.
- Docs describe the parity gate as local contract protection only.
- No `src/`, dependency manifest, or public `uv.lock` changes are required.
