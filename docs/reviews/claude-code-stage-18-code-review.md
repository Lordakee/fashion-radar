## Approval status

**Approved with no Critical or Important findings.**

Stage 18 appears ready for release checks, commit, and push, assuming the already-run verification remains current. I found only **Minor test-hardening suggestions**; nothing blocks release.

## Findings

### Critical

None.

### Important

None.

### Minor

1. **CLI-level non-recursive matching coverage could be stronger.**
   The importer-level tests cover non-recursive behavior and `**/*.csv` not recursing, and the CLI delegates directly to that function. Still, a CLI test with `top.csv` plus `nested/nested.csv` would better protect the user-facing command.

2. **CLI invalid-directory coverage does not separately cover “directory argument is a file.”**
   The importer-level test covers file path as invalid directory. The CLI covers missing directory. A CLI file-path case would be useful symmetry.

3. **Default table no-match output is not directly covered.**
   JSON no-match shape is tested. A simple table-output no-match CLI test could assert nonzero exit, no traceback, and visible `no_matching_files`.

4. **No-artifact behavior is covered for key paths but not every error branch.**
   Success, unreadable directory, and no-`--dry-run` paths are covered for no artifacts. File-failure/no-match artifact assertions would further harden this invariant.

These are polish/coverage-hardening suggestions, not blockers.

---

## Explicit review answers

### 1. Does the implementation require `--dry-run` before reading files?

**Yes.**

In `src/fashion_radar/cli.py`, `import_signals_dir_command()` checks:

```python
if not dry_run:
    typer.echo("Directory import is not implemented; rerun with --dry-run.", err=True)
    raise typer.Exit(1)
```

This happens before calling `dry_run_manual_signal_directory(...)`, so no directory inspection or file reading occurs without `--dry-run`.

### 2. Does it avoid SQLite, data/config/report directory creation, import writes, collectors, reports, dashboard, matching, scoring, and digest behavior?

**Yes.**

The directory dry-run path only:

- validates the directory;
- lists direct children;
- filters files by `fnmatch`;
- calls the existing manual signal row loader;
- aggregates counts/findings;
- prints table or JSON.

It does **not** call `store_manual_signal_rows()`, repositories, database engines, report generation, matching/scoring, dashboard, digest, collectors, or config/data/report directory setup.

The CLI command also intentionally omits `--data-dir`, `--config-dir`, `--reports-dir`, and `--imported-at`.

### 3. Does it preserve non-recursive direct-child matching and deterministic order?

**Yes.**

`dry_run_manual_signal_directory(...)` uses:

```python
children = list(directory.iterdir())
...
if is_regular_file and fnmatch.fnmatch(path.name, pattern):
    paths.append(path)
paths = sorted(paths, key=lambda path: str(path))
```

This satisfies the requested behavior:

- `directory.iterdir()` only;
- `path.is_file()`;
- `fnmatch.fnmatch(path.name, pattern)`;
- no `glob`/`rglob`;
- deterministic sorting by `str(path)`.

Tests also inspect the implementation to ensure `.glob(` and `.rglob(` are absent.

### 4. Are directory-level messages stable for missing/non-directory, unreadable, and no-match cases?

**Yes.**

The directory-level messages are fixed strings:

- missing or not a directory:
  `"Manual signal directory does not exist or is not a directory."`

- unreadable directory:
  `"Could not read manual signal directory."`

- no matching files:
  `"No regular files matched the pattern in the directory."`

The unreadable-directory branch catches `OSError` without exposing platform-specific exception text, which keeps output stable.

### 5. Does JSON output preserve the planned stable shape?

**Yes.**

The result models use `ConfigDict(extra="forbid")`, and CLI JSON output uses:

```python
typer.echo(result.model_dump_json(indent=2))
```

The top-level JSON shape is stable and tested as:

```text
directory
input_format
pattern
file_count
valid_file_count
row_count
error_count
source_name_counts
platform_counts
files
findings
```

File findings also include stable fields:

```text
severity
code
message
path
```

### 6. Do tests cover success, file failure, invalid directory, no-match, unreadable directory, no-`--dry-run`, non-recursive matching, no glob/rglob, and no-artifact behavior?

**Yes, substantially.**

Covered:

- success:
  - importer aggregate success;
  - CLI table success;
  - CLI JSON success.
- file failure:
  - importer mixed clean/invalid files;
  - CLI JSON failure shape.
- invalid directory:
  - importer missing directory;
  - importer file-path-as-directory;
  - CLI missing directory.
- no-match:
  - importer no-match;
  - CLI JSON no-match shape.
- unreadable directory:
  - importer unreadable mocked `Path.iterdir`;
  - CLI unreadable without artifacts.
- no `--dry-run`:
  - CLI exits before reading files / validating missing directory.
- non-recursive matching:
  - importer direct-child-only test;
  - importer `**/*.csv` does not recurse.
- no `glob`/`rglob`:
  - source-inspection test on `dry_run_manual_signal_directory`.
- no-artifact behavior:
  - success;
  - unreadable directory;
  - no-`--dry-run`.

Minor hardening opportunities remain for CLI-level non-recursive behavior, file-path-as-directory through CLI, default table no-match output, and no-artifact assertions on no-match/file-failure branches.

### 7. Do docs keep the distinction between strict `community-signal-lint-dir` and importer-model `import-signals-dir --dry-run` clear?

**Yes.**

Docs consistently describe:

- `community-signal-lint-dir` as the stricter community handoff linter;
- `import-signals-dir --dry-run` as broader manual importer-model validation that remains backward-compatible with extra columns/fields.

This distinction is clear in the manual import docs, community signal import docs, quality docs, README, architecture notes, and source boundary docs.

### 8. Do docs avoid scraping/platform/source-acquisition/account automation, authorization verification, compliance/audit, or policy workflow product features?

**Yes.**

The reviewed docs use those concepts only as explicit exclusions or boundary statements. I did not find product-facing additions for:

- scraping/crawling;
- browser automation;
- platform APIs/search;
- account automation;
- source acquisition workflows;
- authorization verification;
- compliance/audit/policy workflows;
- collectors/source packs/background jobs.

### 9. Is Stage 18 ready for release checks, commit, and push after fixing any Critical/Important findings?

**Yes.**

There are **no Critical or Important findings to fix** from this review. Stage 18 is ready for release checks, commit, and push. The Minor test additions above would improve long-term regression protection but are not release blockers.
