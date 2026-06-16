# Stage 59 Directory Example Discovery Design

## Goal

Expose the checked-in external community tool export directory examples through
the existing machine-readable producer contracts, so external tools can discover
both single-file handoff examples and directory-shaped handoff examples without
reading prose docs.

## Context

The repository already has:

- `community-signal-profile --format json`, a print-only producer contract for
  external/local tools.
- `community-handoff-manifest --format json`, a print-only manifest for one
  planned local handoff directory.
- Single-file handoff examples listed in `example_paths`.
- Sanitized directory examples under
  `examples/community-tool-handoff-directory.example/`.

The current gap is discoverability. `example_paths` intentionally points to
importable single-file examples, while directory examples are only linked in
README/docs/checklist prose. External tools should be able to read the JSON
profile or manifest and discover the directory example paths directly.

## Recommended Approach

Add a new field named `directory_example_paths` to both producer contract models:

- `CommunitySignalProducerProfile.directory_example_paths`
- `CommunityHandoffManifest.directory_example_paths`

Keep `example_paths` unchanged as the existing single-file import examples. This
preserves old contract meaning and avoids mixing file-level and directory-layout
examples. The new field is a static list of relative repo paths:

- `examples/community-tool-handoff-directory.example/README.md`
- `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`
- `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`
- `examples/community-tool-handoff-directory.example/json/community-tool-a.json`
- `examples/community-tool-handoff-directory.example/json/community-tool-b.json`

The profile builder will copy this static list into the Pydantic model. The
manifest builder will copy it from the profile, just as it already copies
`example_paths`, schema paths, field notes, field rules, and unsupported
capabilities.

## Alternatives Considered

1. Add `directory_example_paths` to profile and manifest.

   This is the recommended option. It is a small contract addition, does not
   change workflow order, and directly helps external tools discover local export
   layouts.

2. Add `community-handoff-check-dir` to the printed community handoff workflow.

   This was rejected for this node. Stage 56 intentionally kept that aggregate
   readiness command independent from the canonical producer workflow, and adding
   it now would change the workflow contract rather than improving
   discoverability.

3. Add only more docs/tests for directory examples.

   This is safer but less useful. The examples already have prose links and test
   coverage; the missing piece is a machine-readable pointer for external tools.

## Scope

In scope:

- Add `directory_example_paths` to the producer profile model and table output.
- Add `directory_example_paths` to the handoff manifest model and table output.
- Update `examples/community-signal-profile.example.json` deterministically.
- Update tests for stable JSON key order, table output, CLI JSON output, docs
  drift, and existing directory example paths.
- Update user docs and changelog so the new field is discoverable.

Out of scope:

- No new CLI command.
- No new source/platform connector.
- No scraping, browser automation, account login, cookies, sessions, platform
  APIs, source acquisition, media downloading, monitoring, or scheduling.
- No schema migration, database access, or dependency change.
- No dashboard, report, digest, or workflow artifact writes.
- No change to `recommended_commands` or `community-handoff-workflow` step order.
- No directory reads in `build_community_signal_profile()` or
  `build_community_handoff_manifest()`; the new field is static metadata only.

## Data Model

`CommunitySignalProducerProfile` adds:

```python
directory_example_paths: list[str]
```

`CommunityHandoffManifest` adds:

```python
directory_example_paths: list[str]
```

Stable JSON key placement:

- In `CommunitySignalProducerProfile`, put `directory_example_paths` immediately
  after `example_paths`.
- In `CommunityHandoffManifest`, put `directory_example_paths` immediately after
  `example_paths`.

## Rendering

Profile table output adds:

```text
Directory example paths: examples/community-tool-handoff-directory.example/README.md, ...
```

Manifest table output adds the same style line after `Example paths`.

The renderer remains pure formatting. It must not check whether the paths exist.

## Testing

Tests should prove:

- The new fields exist in model JSON with stable key order.
- The new profile field exactly matches the checked-in directory example paths.
- The manifest field copies the profile value.
- CLI JSON output includes the field for both commands.
- Table output includes `Directory example paths`.
- The profile example JSON remains byte-for-byte deterministic.
- Directory example tests assert every profile-discoverable directory example
  path exists, and the CSV/JSON files remain lintable/dry-runnable through the
  existing local commands.
- Docs drift tests assert README/import docs/checklist mention
  `directory_example_paths` and the same relative paths.

## Review And Release Gates

Before implementation, submit this design and the implementation plan to local
`opencode` using model `zhipuai-coding-plan/glm-5.2`.

Before commit/push:

- Run targeted tests for profile, manifest, CLI docs, and directory examples.
- Run full `pytest -q`.
- Run `ruff check .` and `ruff format --check .`.
- Run lock/sync hygiene with `UV_NO_CONFIG=1`.
- Ensure `uv.lock` and `pyproject.toml` are unchanged.
- Run release hygiene and first-run smoke.
- Run opencode release review and fix Critical/Important findings.
