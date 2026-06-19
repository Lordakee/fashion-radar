Review the updated Stage 117 plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Review scope:
- `docs/superpowers/specs/2026-06-19-stage-117-discoverability-links-design.md`
- `docs/superpowers/plans/2026-06-19-stage-117-discoverability-links-plan.md`
- `docs/reviews/opencode-stage-117-plan-review.md`
- Current docs/test targets:
  - `README.md`
  - `docs/cli-reference.md`
  - `docs/first-run.md`
  - `docs/github-upload-checklist.md`
  - `tests/test_cli_docs.py`

Focus only on whether the updated Stage 117 plan resolves the prior Important
findings from `docs/reviews/opencode-stage-117-plan-review.md`:

1. README and first-run planned text must include `generic_community_export`.
2. CLI planned text must use full `external-tool-readiness` and
   `external-tool-workflow` command names.
3. CLI/test link expectations must use the correct sibling-doc target
   `community-signal-import.md#external-tool-export-directory-examples`.
4. first-run planned text must include CSV, JSON, and
   `generic_community_export`.
5. upload checklist planned text must be exact enough and include
   `generic_community_export`, `external-tool-readiness`, and
   `external-tool-workflow`.

Also verify that the plan still keeps Stage 117 docs/tests-only and does not
introduce source acquisition, scraping, scheduling, monitoring, connector, API,
account-cookie, compliance/audit, or ranking behavior.

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any remaining Critical or
  Important blockers before implementation.
