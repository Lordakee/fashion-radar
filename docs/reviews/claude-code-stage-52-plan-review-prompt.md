Please review this Stage 52 plan before implementation. Use a code-review
stance and report Critical/Important issues first.

Objective:
Add `fashion-radar community-handoff-manifest DIRECTORY`, a local print-only
producer manifest for external tools that write sanitized community signal
directory files.

Technology and implementation approach:
- Python 3.11+, Typer, Pydantic.
- New focused module `src/fashion_radar/community_handoff_manifest.py`.
- Reuse existing `community_signal_profile` constants for field/schema contract.
- Reuse existing `build_community_handoff_workflow()` for command workflow.
- Add CLI command with table/json output.
- No new dependencies and no `uv.lock` change.

Hard boundaries:
- Do not add scraping/crawling/browser automation/account login/cookies/sessions
  /platform API/source acquisition/scheduling/monitoring/connectors.
- Do not add any compliance-review feature.
- The command must be print-only and must not inspect the supplied directory,
  read handoff files, execute commands, open SQLite, or create artifacts.

Files to review:
- `docs/superpowers/specs/2026-06-16-stage-52-community-handoff-manifest-design.md`
- `docs/superpowers/plans/2026-06-16-stage-52-community-handoff-manifest-plan.md`

Review questions:
1. Does the manifest fill a real gap beyond `community-signal-profile` and
   `community-handoff-workflow`, or is the scope duplicative?
2. Are the planned model fields stable and useful for an external local producer?
3. Are there any planned behaviors that violate the local-only/free-first
   boundaries in `AGENTS.md` or `docs/source-boundaries.md`?
4. Does the `manifest_storage_note` adequately prevent external tools from
   saving the manifest where `community-signal-lint-dir`,
   `community-candidates-dir`, or `import-signals-dir` would treat it as a
   signal file?
5. Are tests sufficient for print-only/no-side-effect behavior, JSON key order,
   docs synchronization, invalid timestamp handling, and public command help?
6. Are any CLI naming, option reuse, or documentation updates missing before
   implementation?
