## Stage 18 Plan Rereview Findings

### Critical

None found.

### Important

None found.

### Minor / Optional Hardening

1. **Static guard is described as module-level but only inspects one function.**
   The plan says it adds a “module-level static guard,” but the planned test only checks:

   ```python
   source = inspect.getsource(dry_run_manual_signal_directory)
   ```

   This is likely sufficient if all enumeration stays inside `dry_run_manual_signal_directory`, but it would not catch a future helper such as `_iter_manual_signal_directory_files()` accidentally using `Path.glob()` / `rglob()`. For stronger alignment with the wording, inspect the whole `manual_signals` module or explicitly inspect the enumeration helper too. This is not blocking because the implementation plan itself prescribes `iterdir()` + `fnmatch`, and the behavioral tests cover non-recursion including `**/*.csv`.

2. **The no-`--dry-run` test proves early directory validation avoidance, not file-read avoidance directly.**
   The planned CLI test uses a missing directory and confirms the command exits with the `--dry-run` requirement message before producing `invalid_directory`. That covers the important control-flow requirement. If desired, it could be hardened by monkeypatching `Path.iterdir` or `load_manual_signal_rows` to fail if reached. Not blocking because the planned implementation checks `if not dry_run` before invoking `dry_run_manual_signal_directory`.

### Previous Important Findings Status

1. **CLI failure coverage for no-match and unreadable-directory cases** — Fixed.
   The plan now includes JSON no-match coverage and unreadable-directory nonzero/no-traceback/no-artifact coverage.

2. **Guard against accidental `Path.glob()` / `rglob()` use** — Fixed enough for approval, with optional hardening noted above.
   Behavioral non-recursive tests plus the static source check address the concern.

3. **Post-acceptance commit/push marked outside implementation** — Fixed.
   The “Post-Acceptance Release And Upload” section clearly says it is an operator/maintainer checklist after implementation and code review approval, not part of Stage 18 product implementation.

4. **Exact stable directory-level messages enumerated** — Fixed.
   The design and plan both enumerate exact stable messages for missing/not-directory, unreadable, and no-match cases.

5. **No-`--dry-run` no-artifact coverage** — Fixed.
   The plan includes a CLI test confirming missing `--dry-run` exits before directory validation and creates no config/data/report artifacts.

### Scope Review

The current planning artifacts remain within Stage 18 scope:

- local-only directory dry-run validation;
- `--dry-run` required;
- no SQLite writes or row import;
- no data/config/report directory creation;
- no scraping, crawling, browser automation, account automation, or platform APIs;
- no source acquisition instructions;
- no product-facing compliance/audit/policy workflow feature.

The planned implementation reuses `load_manual_signal_rows()` and keeps the new command as a read-only aggregate validation layer, which matches the intended architecture.

Approved for Stage 18 implementation
