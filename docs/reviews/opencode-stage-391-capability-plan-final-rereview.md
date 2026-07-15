## Stage 391 Filesystem-Capability Amendment - Final Rereview

### Verification Of Requested Items

**1. Live-root descriptor safety - RESOLVED.** The mandate covers stage and live managed roots symmetrically: design `:157-170` ("every stage or live managed root and its `data` child can be opened and identity-checked"), `:175-176` ("never uses a pathname-only fallback for owner creation or stage/live owner and JSON reads"); plan `:1028-1037` ("bind any managed root and its `data/` child ... applies both to staging and to the same tree after it becomes live"). Consumers route through bound helpers: `_validate_published_row_one_site` uses `_read_owner_token_if_present(live)` (`plan:1238`) and bound `_read_json_object` (`plan:1245-1247`); `_read_owner_token_if_present` contract at `plan:1259-1265`; `_is_owned_live` reuses it (`plan:186`, `:1259`). RED coverage for symlinked `live/data` and symlinked live root at `plan:1209-1223`.

**2. Bound owner unlink - RESOLVED.** `_remove_owner_file_if_present` delegates to `_remove_owner_file_from_managed_root` (`plan:1524-1530`); contract at `plan:1550-1555` ("keep the verified managed-root and `data/` directory descriptors open from owner inspection through the relative unlink ... never performs a full-path unlink after releasing the bound directory"). Table entry at `plan:208`. RED requires reject-without-mutation (`plan:1217-1218`) plus a mid-operation `live/data` replacement TOCTOU test (`plan:1553-1555`).

**3. Exact `_SAFE_DIRECTORY_OPERATIONS_SUPPORTED` including `os.unlink` - RESOLVED.** Predicate at `plan:64-71` includes all four dir_fd functions `(os.open, os.stat, os.mkdir, os.unlink)` plus `O_DIRECTORY` and `O_NOFOLLOW`. Restated verbatim in the Filesystem Capability Contract (`plan:231-233`) and design (`:165-167`); tech stack names "descriptor-relative `open/stat/mkdir/unlink`" (`plan:23`). The `os.unlink` membership is what gates the bound owner deletion, closing the prior rereview's gap.

**4. Per-operation capability RED tests - RESOLVED.** `plan:1099-1102` parameterizes so "each required operation, including descriptor-relative `os.unlink`, can be absent independently" and states the key invariant: "A platform that can bind owner reads but cannot perform the required bound owner unlink must fail before commit, not during post-publish cleanup." Direct-helper defense-in-depth forces the whole predicate false (`plan:1219-1220`).

**5. `_commit_publish` attribution - RESOLVED.** Helper table `plan:203` reads "Task 3 Step 4"; dispatcher body at `plan:1251-1257` (Step 4), only called at orchestration. No stale Step 7 attribution.

**6. Fail-closed ordering - RESOLVED.** `_require_safe_directory_operations()` is the first statement of `publish_latest_row_one_site` (`plan:1571`), preceding resolve (`:1572`), parent mkdir (`:1573`), lock (`:1574`), recovery (`:1575`), staging (`:1581`), render (`:1583`). It sits outside the transaction try/except (`plan:1619-1621`). RED requires absent parent + zero artifacts + no render callback (`plan:1086-1097`); `latest_only=False` bypasses (`plan:1096-1097`).

**7. Windows feature boundary - RESOLVED.** Scoped to the latest-only staged feature, not the package: design `:92-96, 184-187, 293-298`; plan `:25-27, 2010-2013`. `msvcrt` lock retained in the portable contract but unreachable through the earlier gate. Docs phrase "ordinary non-latest build and preview rendering remains available" (`plan:1985`); checklist `plan:2479-2480`.

**8. Fixed interfaces - RESOLVED.** Table adds `_require_safe_directory_operations` (`plan:177`), `_read_owner_token_if_present` (`plan:186`), `_remove_owner_file_from_managed_root` (`plan:208`); corrects `_commit_publish` to Step 4 (`plan:203`). Every helper referenced in Tasks 1-6 appears in the table or an earlier step.

**9. Docs mapping - RESOLVED.** Three new normalized phrases (`plan:1983-1985`); Task 4 render capability test (`plan:1772-1776`); Task 4 CLI capability-false for build/preview/refresh (`plan:1796-1801`); Windows docs statement (`plan:2010-2013`); Task 6 checklist (`plan:2477-2480`); design acceptance criteria (`design:648-653`).

**10. Rollback/recovery invariants - RESOLVED (no regression).** The diff adds only an earlier gate and bound reads; no phase transition, rollback step, or recovery branch is modified. The `_validate_published_row_one_site` refactor preserves exact semantics (non-regular -> raise, mismatch -> raise, missing + `require_owner` -> raise, missing + not `require_owner` -> None) while upgrading to bound reads (`plan:1231-1248`). The `_remove_owner_file_if_present` delegation preserves missing -> no-op, present + unsafe/mismatch -> raise, present + match -> delete (`plan:1524-1555`). Recovery dispatch (`plan:1427-1435`) and both commit paths (`plan:1271-1353`) are untouched by this amendment.

### New Findings

None. `git diff --check` clean; placeholder scan exits 1. The depth-1 journal `Path.unlink()` deletions (`plan:1521, 1540`) are correctly out of scope - `os.unlink` does not follow symlinks, and the capability amendment is explicitly scoped to owner/JSON access below managed roots (`design:175-176`), not depth-1 siblings.

### Verdict

**APPROVED**
