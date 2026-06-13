- **Important — `src/fashion_radar/imported_review_workflow.py:158` / `src/fashion_radar/imported_review_workflow.py:173`**
  - **Issue:** Table rendering changes the copyable shell command. `render_imported_review_workflow_table()` passes `step.command` through `_table_cell()`, which replaces `|` with `/` and collapses whitespace. For a source name like `Community | Tool Export`, the builder correctly produces:
    ```sh
    --source-name 'Community | Tool Export'
    ```
    but the table output prints:
    ```sh
    --source-name 'Community / Tool Export'
    ```
    That changes the argument a user would copy and run, so the table command is no longer equivalent to the JSON command or the intended deterministic shell command.
  - **Concrete fix:** Preserve `step.command` verbatim in user-copyable output. Either render commands outside the pipe-delimited table, or introduce command-specific rendering that does not alter shell argument content. Update `tests/test_cli.py:2448` to expect the original `|` in the command output. It is fine to keep sanitizing non-copyable display fields like `Source name:` if desired.
