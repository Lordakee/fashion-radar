# Opencode Stage 55 Plan Review Prompt

You are reviewing the Stage 55 implementation plan for the `fashion-radar`
repository before implementation begins.

Required review mode:

- Review model: GLM 5.2 via local opencode
  (`zhipuai-coding-plan/glm-5.2`).
- This is a plan review only.
- Do not edit files.
- Do not narrate tool usage or file-reading steps.
- Keep the response concise.
- Treat Critical and Important findings as blocking.

## Goal

Add checked-in external community tool export directory examples so future
user-controlled tools can copy a complete local CSV or JSON directory layout and
run existing directory handoff commands.

The intended checked-in layout has two one-row files per format:

```text
examples/community-tool-handoff-directory.example/
  README.md
  csv/
    community-tool-a.csv
    community-tool-b.csv
  json/
    community-tool-a.json
    community-tool-b.json
```

## Files To Review

- `docs/superpowers/specs/2026-06-16-stage-55-community-tool-directory-examples-design.md`
- `docs/superpowers/plans/2026-06-16-stage-55-community-tool-directory-examples-plan.md`
- Current related files:
  - `examples/community-tool-handoff.example.csv`
  - `examples/community-tool-handoff.example.json`
  - `src/fashion_radar/community_handoff_manifest.py`
  - `src/fashion_radar/community_handoff_workflow.py`
  - `docs/community-signal-import.md`
  - `tests/test_cli.py`
  - `tests/test_cli_docs.py`
  - `scripts/check_package_archives.py`
  - `tests/test_package_archives.py`

## Required Boundaries

The plan must not add:

- new CLI commands;
- schema changes;
- dependency or lockfile changes;
- source acquisition;
- scraping/crawling;
- browser automation;
- platform API clients;
- account login/cookies/sessions/tokens;
- monitoring, scheduling, or watching;
- media download;
- demand proof;
- platform/community coverage verification;
- source ranking;
- compliance-review, legal-review, approval UI, or policy workflow features.

The plan must also avoid adding directory paths to the existing profile
`example_paths` field and must not add an `example_directory_paths` field in
this stage.

## Review Questions

1. Is a checked-in `examples/community-tool-handoff-directory.example/{csv,json}/`
   layout with two matched files per format the right next step after
   single-file templates?
2. Are the planned examples sanitized and limited to the existing community
   signal fields?
3. Do the planned tests cover the sample directories through existing local
   directory commands without adding runtime behavior?
4. Do package/archive and docs drift tests cover the new files and stale
   manifest example risk?
5. Is the verification/upload plan sufficient and mirror-safe?

## Required Output

Respond with:

- `## Critical Findings`
- `## Important Findings`
- `## Minor Findings`
- `## Verdict`

If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 55 COMMUNITY TOOL DIRECTORY EXAMPLES
```
