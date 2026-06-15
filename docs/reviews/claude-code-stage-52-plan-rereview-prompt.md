Please re-review the revised Stage 52 plan after the first plan review.

Original review file:
- `docs/reviews/claude-code-stage-52-plan-review.md`

Revised files:
- `docs/superpowers/specs/2026-06-16-stage-52-community-handoff-manifest-design.md`
- `docs/superpowers/plans/2026-06-16-stage-52-community-handoff-manifest-plan.md`

Changes made in response to Important findings:
1. Manifest now includes profile-derived producer fields:
   `producer_contract_version`, `supported_input_formats`, `prohibited_fields`,
   `field_notes`, `field_rules`, and `unsupported_capabilities`, using
   `build_community_signal_profile()` instead of duplicating constants.
2. `manifest_storage_note` now explicitly warns about the `--pattern "*.json"`
   case and says not to save a `.json` manifest inside the handoff directory.
3. No-side-effect CLI test now guards `directory`, `config_dir`, and `data_dir`.
4. JSON tests now assert nested `workflow` and `workflow.steps[]` key order.
5. The unused `COMMUNITY_SIGNAL_CONTRACT_VERSION` import was removed from the
   implementation sketch.
6. `matched_file_rule` wording now describes downstream lint/preview/import
   commands, not the manifest command itself.
7. Docs plan now includes the `docs/source-boundaries.md` README Requirements
   bullet, not only the boundary paragraph.

Please check whether all prior Critical/Important concerns are resolved and
whether any new Critical/Important issues were introduced. Keep review focused
on plan readiness before implementation.
