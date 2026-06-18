# Stage 85 Plan Review Prompt

Review the Stage 85 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-85-suggested-platform-labels-design.md`
- `docs/superpowers/plans/2026-06-18-stage-85-suggested-platform-labels-plan.md`
- Current `src/fashion_radar/community_signal_profile.py`
- Current `src/fashion_radar/community_handoff_manifest.py`
- Current `src/fashion_radar/external_tool_adapters.py`
- Current `tests/test_community_signal_profile.py`
- Current `tests/test_community_handoff_manifest.py`
- Current `tests/test_external_tool_contract_parity.py`
- Current `tests/test_cli_docs.py`
- Current `docs/community-signal-import.md`
- Current `docs/community-signal-quality.md`

## Intended Goal

Add advisory `suggested_platform_labels` to the local producer profile and
directory handoff manifest so user-controlled external/community tools can
choose stable local provenance labels for sanitized handoff rows. The exact
label list is:

```python
["rednote", "xiaohongshu", "instagram", "tiktok", "media", "x", "community"]
```

## Scope Constraints

Allowed changes:

- producer profile model/build/render and deterministic example JSON
- directory manifest model/build/render
- focused tests and docs drift tests
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- Stage 85 spec/plan/review artifacts

Disallowed changes:

- `schemas/community-signals.schema.json`
- import/lint validation behavior
- external adapter/template/workflow/readiness command generation
- dependency manifests or `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

Do not propose adding scraping, connectors, browser automation, platform APIs,
login/cookie/session/token behavior, media downloads, monitoring, scheduling,
source acquisition, demand proof, ranking, coverage verification, schema enums,
new linter restrictions, or compliance-review product features.

## Review Questions

1. Does the plan expose useful machine-readable local provenance guidance
   without turning labels into schema/validation rules?
2. Are the profile and manifest insertion points compatible with existing
   stable key-order tests and table renderers?
3. Does adapter parity coverage catch current/future adapter label drift
   without creating a circular import?
4. Are docs/test updates scoped enough and worded as advisory, not platform
   support or coverage?
5. Are verification commands sufficient?
6. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
