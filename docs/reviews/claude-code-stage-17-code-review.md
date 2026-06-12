Approval status: **Changes requested — one Important finding.**
I found **no Critical issues**, but I would not approve release/commit/push until the unreadable-directory diagnostic message is made stable.

## Findings

### Critical

None found.

### Important

1. **Unreadable-directory error message is not stable**
   **File:** `src/fashion_radar/community_signals.py:206-218`

   In the `OSError` branch of `lint_community_signal_directory()`, the finding message embeds the exception text:

   ```python
   message=f"Could not read community signal directory: {exc}",
   ```

   That can vary by OS, Python, permissions model, path rendering, monkeypatch behavior, locale, or errno text. Stage 17 asks for invalid/unreadable directory handling to return **stable directory-level findings without tracebacks**. The finding code is stable (`invalid_directory`) and there is no traceback, but the message itself is not stable.

   Recommended fix: use a fixed message such as:

   ```python
   message="Could not read community signal directory."
   ```

   If detailed diagnostics are needed later, keep them out of the contract-shaped finding message.

### Minor

1. **Architecture summary slightly under-describes the new directory wrapper**
   **File:** `docs/architecture.md`

   The later architecture section documents `community-signal-lint-dir`, but an earlier component summary still describes community signal quality primarily as linting “one community signal CSV/JSON file.” This is not a scope violation and not release-blocking, but it would be cleaner to mention the non-recursive directory wrapper in the summary too.

2. **Some CLI coverage is stronger for JSON/API than for table output**
   Existing tests cover sorted file order at the API level and JSON CLI level, but table CLI order is only indirectly covered because rendering uses `result.files`. This is not blocking given the implementation, but adding a two-file table test would make the regression net tighter.

---

## Explicit answers

1. **Does the implementation preserve non-recursive direct-child matching?**
   **Yes.** It uses `directory.iterdir()`, filters with `path.is_file()`, matches with `fnmatch.fnmatch(path.name, pattern)`, and sorts by `str(path)`. I did not see `Path.glob()` or `rglob()` used for directory matching.

2. **Does invalid/unreadable directory handling return stable directory-level findings without tracebacks?**
   **Partially.** It returns directory-level findings and avoids tracebacks. Missing/non-directory handling has a stable message. The unreadable-directory branch has stable code/severity but an unstable message because it includes `{exc}`. This is the Important finding.

3. **Does no-match return `no_matching_files` as an error?**
   **Yes.** No-match appends a directory-level `CommunitySignalFinding` with severity `error` and code `no_matching_files`.

4. **Do aggregate severity counts include per-file findings?**
   **Yes.** `error_count`, `warning_count`, and `info_count` add directory-level finding counts plus sums from all per-file results.

5. **Does CLI strict/non-strict exit behavior match the plan?**
   **Yes.** The CLI prints table/JSON first, then exits non-zero when `result.error_count` is non-zero, or when `--strict` is set and aggregate `result.warning_count` is non-zero.

6. **Do tests cover JSON success and failure shape, sorted file order, warning-only behavior, and no-artifact behavior?**
   **Mostly yes.**
   - Directory JSON success shape: covered.
   - Directory JSON failure shape: covered for missing directory and no-match.
   - Sorted file order: covered at lower-level directory lint and directory JSON CLI.
   - Warning-only behavior: covered for strict and non-strict directory CLI.
   - No-artifact behavior: covered for directory lint default/table output and unreadable-directory case.

   Minor possible additions: unreadable-directory JSON shape, table sorted-order CLI, JSON no-artifact path.

7. **Do docs avoid adding social/platform acquisition, scraping, account automation, platform coverage, authorization verification, compliance/audit, or policy workflow product features?**
   **Yes.** The docs consistently frame the command as local, read-only, non-recursive diagnostics over sanitized CSV/JSON handoff files. Boundary text explicitly excludes fetching URLs, collecting sources, platform/community acquisition, authorization verification, scraping/monitoring-like behavior, matching/scoring, reports, and policy/compliance workflows.

8. **Is the code ready for release checks, commit, and push after fixing any Critical/Important findings?**
   **Yes, after fixing the unstable unreadable-directory message.** Once that Important issue is fixed and the existing full verification/release checks pass again, I would consider Stage 17 ready for release checks, commit, and push.
