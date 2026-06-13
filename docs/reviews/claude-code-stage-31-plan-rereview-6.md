Verified against the current CLI surface:

1. **Command correction is accurate**
   - `import-signals` uses `--format`, not `--input-format`.
   - `import-signals-dir` also uses `--format`.
   - `community-signal-lint`, `community-signal-lint-dir`, `community-candidates`, and `community-candidates-dir` use `--input-format` for input format selection.
   - `--format` remains output-format selection for community lint/candidates where applicable.

2. **No runtime behavior or scope change**
   - This is only correcting the option name used by the installed-wheel smoke commands.
   - It does not change importer behavior, dry-run semantics, file scope, database writes, or community lint/candidate command contracts.

3. **No new Critical or Important issues introduced**
   - The correction aligns the smoke commands with the implemented Typer options.
   - Keeping community lint/candidates on `--input-format` avoids regressing their current CLI contract.

APPROVED FOR STAGE 31 RELEASE GATE
