## Stage 391 Filesystem-Capability Amendment Rereview

### Prior Findings - Resolution Verification

**I-1 (IMPORTANT) - Live-root no-follow/descriptor-relative mandate - RESOLVED.**

The amendment now extends the mandate to both stage and live managed roots:
- Design `2026-07-14-stage-391-...-design.md:159` ("below a managed root while staging and **after staging becomes live**"), `:168-170` ("every **stage or live** managed root and its `data` child can be opened and identity-checked"), `:175-176` ("never uses a pathname-only fallback for owner creation or **stage/live** owner and JSON reads").
- Plan `:1023-1028` ("must bind **any managed root** and its `data/` child ... applies both to staging and to the same tree after it becomes live for post-publish validation, ownership checks, cleanup, rollback, and recovery").

Each named consumer is covered:
- **`_validate_published_row_one_site`** (`plan:1221-1238`) reads the live owner via `_read_owner_token_if_present` and live JSON via `_read_json_object`; both bind root + `data/` (`plan:1249-1252`). RED: `plan:1199-1204` (symlinked `live/data` -> reject before integrity validator, external bytes preserved).
- **`_is_owned_live`** (`plan:1345-1349`) uses `_read_owner_token_if_present` (`plan:1253`). RED: `plan:1205-1207`.
- **Recovery** dispatch (`plan:1416-1428`) routes through `_is_owned_live` / `_validate_published_row_one_site(require_owner=False)` / bound cleanup; `plan:1212-1213` states the `published` owner relaxation does not relax ancestry/JSON-read safety.
- **Owner deletion bound through unlink** - `_remove_owner_file_from_managed_root` (`plan:1540-1545`) "must keep the verified managed-root and `data/` directory descriptors open from owner inspection through the relative unlink ... never performs a full-path unlink after releasing the bound directory. Tests inject a `live/data` replacement between inspection and unlink and require zero external mutation." RED: `plan:1207-1208`.

Capability-false defense-in-depth is enforced per direct helper (`plan:1209-1210`), and both a symlinked live root and symlinked `live/data` child are covered (`plan:1211`). Confirmed `validate_row_one_site_dir` (`server.py:53-59`) only does depth-1 marker/index `exists()` checks and does not read into `data/`, so it cannot reintroduce a depth-2 pathname gap; the composite validators still reject via the bound helpers.

**M-1 (MINOR) - `_commit_publish` table attribution - RESOLVED.** Helper table `plan:200` now reads "Task 3 Step 4"; the dispatcher body is at `plan:1241-1247` (Step 4) and is only *called* at `plan:1578` (Step 7). No stale "Step 7" attribution remains.

**M-2 (MINOR) - Exact capability predicate - RESOLVED.** `_SAFE_DIRECTORY_OPERATIONS_SUPPORTED` is defined exactly in the Fixed Interface Contract code block at `plan:64-68` (`os.open/os.stat/os.mkdir in os.supports_dir_fd` and `hasattr(os,"O_DIRECTORY")` and `hasattr(os,"O_NOFOLLOW")`), referenced as "shown above" at `plan:228-229`, used in `_require_safe_directory_operations` at `plan:235`, and in the RED gate test at `plan:1209`. Reproducible, no longer prose-only.

### Other Requested Items - All PASS

- **Fail-closed ordering** - `_require_safe_directory_operations()` is the first statement of `publish_latest_row_one_site` (`plan:1561`), preceding `_resolve_publish_target` (`:1562`), parent `mkdir` (`:1563`), lock (`:1564`), recovery (`:1565`), staging (`:1571`), and `render` (`:1573`); it sits outside the transaction try/except so the capability error is not re-wrapped (`plan:1609-1611`). RED requires absent parent + zero artifacts + no render callback (`plan:1079-1095`); `latest_only=False` bypasses the gate (`plan:1091-1092`).
- **Windows feature boundary** - Scoped to the latest-only staged feature, not the package (design `:92-96, 182-187, 293-298`; plan `:25-27, 2000-2003`). `msvcrt` lock remains in the portable contract but unreachable through the earlier gate.
- **Task/test/docs mapping** - Tasks 1-6 cover every design section and acceptance criterion (design `:636-652`); Task 3 RED-GREEN per component, Task 4 real-render failure-first, Task 5A debris+archives, Task 5B 10 normalized phrases + changelog denials, Task 6 release gates.
- **Rollback/recovery invariants** - Same-invocation restore for `live_backed_up` / second-rename / validation / `published`-write failures (`plan:1261-1304`); recovery matrix 12 named cases (`plan:1376-1388`); old-version-first dispatch (`plan:1416-1428`). Amendment adds only an earlier gate and bound reads - no phase transition, rollback step, or recovery branch weakened.
- **Fixed interfaces** - Public function, Protocol, TypeVar, dataclasses, phases, error hierarchy, constants, and helper-signature table are internally consistent; every helper referenced in Tasks 1-6 appears in the table or an earlier step. `git diff --check` clean; placeholder scan exits 1 (none found).

No new Critical, Important, or Minor findings introduced by the fixes.

### Verdict

**APPROVED**
