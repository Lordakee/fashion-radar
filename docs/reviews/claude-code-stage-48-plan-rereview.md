Prior Important finding is resolved.

The updated spec and plan now explicitly close both parts of the source-contamination gap:

- Installed mode removes inherited `repo_root/src` from `PYTHONPATH` before command execution.
- Installed mode adds an import-origin preflight using the target Python.
- The preflight fails if `fashion_radar.__file__` resolves inside `repo_root/src`.
- The plan adds regression tests for installed-mode removal of repo `src` from `PYTHONPATH`.
- `run_cli()` is planned to use `context.source_checkout`, so the mode propagates into actual smoke command execution.
- CI/docs/release verification still run the real wheel in a fresh venv.

I do not see any remaining Critical or Important blockers in the Stage 48 plan.

Minor non-blocking notes only:

- The exact-string docs/CI assertions may remain brittle, but that matches the repo’s existing drift-test style and is acceptable.
- The import-origin preflight test coverage focuses on `assert_installed_import_origin()` rather than fully mocking `installed_import_origin()` subprocess behavior, but the real installed-wheel verification covers the end-to-end path.
- The `remove_pythonpath_entry()` helper filters empty `PYTHONPATH` entries; that is acceptable and arguably safer for installed mode.

APPROVED FOR STAGE 48 INSTALLED-WHEEL FIRST-RUN SMOKE
