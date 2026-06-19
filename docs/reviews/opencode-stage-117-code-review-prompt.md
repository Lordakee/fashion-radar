Review the Stage 117 implementation in `/home/ubuntu/fashion-radar`.

Focus only on the current docs/test changes for the external community tool
directory discoverability node:

- `README.md`
- `docs/cli-reference.md`
- `docs/first-run.md`
- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`

Also check the stage review artifacts if useful:
- `docs/superpowers/specs/2026-06-19-stage-117-discoverability-links-design.md`
- `docs/superpowers/plans/2026-06-19-stage-117-discoverability-links-plan.md`
- `docs/reviews/opencode-stage-117-plan-review.md`
- `docs/reviews/opencode-stage-117-plan-rereview.md`

What to verify:
1. The docs now point to the checked-in `examples/community-tool-handoff-directory.example/README.md`.
2. The docs mention the `generic_community_export` CSV/JSON preflight examples.
3. The docs reference `external-tool-readiness` and `external-tool-workflow`.
4. The CLI reference uses the correct sibling-relative link to
   `community-signal-import.md#external-tool-export-directory-examples`.
5. The new test in `tests/test_cli_docs.py` is correctly section-scoped and
   fails for the right reason if the pointers are removed.
6. No scope violations were introduced, especially no `uv.lock` or `pyproject.toml`
   edits, and no connector/scraping/scheduling/monitoring/ranking behavior.

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final statement on whether the Stage 117 change is ready to ship.
