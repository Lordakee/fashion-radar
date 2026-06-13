# Claude Code Stage 24 Code Rereview Prompt

You previously reviewed Stage 24 and found one Important issue:

- `render_imported_review_workflow_table()` sanitized `step.command`, changing
  copyable shell arguments such as `--source-name 'Community | Tool Export'`
  into `--source-name 'Community / Tool Export'`.

Fix applied:

- `src/fashion_radar/imported_review_workflow.py` now preserves `step.command`
  verbatim in the `Command` column while still sanitizing display fields such as
  step name, purpose, data dir, config dir, and source name.
- Tests were updated so:
  - module renderer tests require command values containing `|` to remain
    unchanged;
  - CLI table tests require `--source-name 'Community | Tool Export'` in the
    command output while the display `Source name:` line remains sanitized.

Verification after fix:

```bash
.venv/bin/python -m pytest tests/test_imported_review_workflow.py tests/test_cli.py -q -k "imported_review_workflow or imported_entity_deltas or imported_signals"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

All passed.

Please rereview the current working tree in read-only mode and confirm whether
the Important finding is resolved. Also check for any new Critical or Important
issues introduced by the fix.

Return either:

1. `APPROVED FOR COMMIT` if there are no Critical or Important issues; or
2. A findings list with severity, file/line, issue, and concrete fix.

Do not edit files.
