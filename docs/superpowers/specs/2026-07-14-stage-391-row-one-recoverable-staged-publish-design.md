# Stage 391 ROW ONE Recoverable Staged Publish Design

## Status

Approved by the user after a read-only CodeGraph audit, parallel runtime and
architecture reviews, and a Claude Code `--effort max` design review against
clean commit `67d26c6`. An implementation-time filesystem-capability amendment
was accepted through the OpenCode GLM 5.2 max fallback after Claude Code failed
the primary call and protocol retry; the amendment addresses Task 2 proof that
pathname-only fallback operations cannot enforce the owner marker's no-follow
boundary.

## Goal

Prevent a failed latest-only ROW ONE refresh from destroying the previously
published website.

Stage 391 makes `render_row_one_site(..., latest_only=True)` render and validate
a complete candidate site before it changes the live output. If a handled
publish operation fails after the live output moves, the publisher restores the
previous site. If the process terminates during a publish, the next invocation
uses an owned journal to recover a safe site before starting another render.

This is a failure-safe, recoverable publish design. It is not described as a
fully atomic or zero-downtime release mechanism.

The recoverable latest-only path requires safe directory-relative filesystem
operations. On a platform where Python does not expose that capability, the
publisher fails before creating the output parent, lock, journal, stage, or any
other transaction artifact. Ordinary `latest_only=False` in-place rendering
remains available.

## Verified Defect

The current `render_row_one_site` implementation performs this sequence when
`latest_only=True`:

1. validate story routes;
2. call `clean_row_one_site_children(output_dir)`;
3. write `.row-one-site`;
4. write assets, pages, and JSON artifacts.

`row-one refresh` always uses this latest-only path while `row-one serve`
directly serves the same output directory. A fault injected into `_write_assets`
after cleanup removed the previous `index.html` and `data/runtime.json` and left
only the site marker. Disk exhaustion, an interrupted process, a template
exception, or a later page or JSON write can therefore turn a valid published
site into a missing or mixed site.

## Selected Approach

Use a same-filesystem staging directory, an owned backup, an atomically written
journal, a single-publisher operating-system lock, validation before and after
the publish rename, old-version-first recovery, and a mutation-free platform
capability gate before publication begins.

This approach preserves current URLs, direct filesystem paths, static-server
configuration, systemd units, generated contracts, and the existing rule that
unrelated top-level output files survive latest-only refreshes.

### Alternatives Rejected For This Stage

1. Versioned release directories plus an atomically replaced `current` symlink
   provide a stronger Linux commit point and eliminate the two-rename gap. They
   also change physical-path behavior, migration, direct-path inspection,
   Windows symlink behavior, and retention semantics. This remains the preferred
   future design if strict zero-gap publication becomes a requirement.
2. Per-file temporary writes plus `os.replace` prevent a partially written
   individual file but cannot commit a multi-file website as one version. A
   process failure can still expose mixed pages, assets, and JSON.
3. Keeping the current delete-then-render flow and retaining a copied archive
   elsewhere does not protect readers during a failed render and makes rollback
   a separate manual operation.
4. A Windows native-handle backend could provide directory-handle-relative
   owner and staged-JSON access without following reparse points. Python's
   documented `os` API does not expose the required Windows primitives, and a
   new `ctypes`/NT implementation would require a separate design, Windows CI,
   and recovery test matrix. Stage 391 therefore fails closed instead of using
   a race-prone pathname fallback.

## Scope

The staged publisher applies only when `latest_only=True`. This includes:

- `row-one refresh`;
- `row-one build --latest-only`;
- `row-one preview --latest-only`;
- direct internal calls to `render_row_one_site(..., latest_only=True)`.

The ordinary `latest_only=False` in-place rendering behavior remains unchanged.
Its partial-write risk is an explicit residual risk and must be pinned by a
regression test so this stage does not silently widen its contract.

The staged publisher is capability-gated. Standard Python builds on platforms
without safe directory-relative handles, including current Windows builds, get
a concise mutation-free `RowOnePublishError` from the latest-only path. This is
a feature-level capability boundary, not a claim that the rest of the package
is platform-specific.

## Public Compatibility

Stage 391 preserves:

- the `render_row_one_site` call signature;
- `RowOneRenderResult` fields;
- logical `output_dir` and `index_path` return values;
- `index.html`, `details/`, `articles/`, `assets/`, and `data/` URLs;
- `.row-one-site` as the public generated-site marker;
- `row-one-app/v7`, `row-one-manifest/v1`, and `row-one-runtime/v1`;
- schemas and generated JSON shapes;
- `row-one serve`, `row-one status`, `row-one ops-check`, and systemd paths;
- output-directory safety rules and unrelated top-level file preservation.

These compatibility guarantees apply when the safe directory-operation
capability gate passes. On an unsupported platform, latest-only publication
does not fall back to delete-and-render or partially create transaction state.

No staging, backup, token, or physical symlink-target path may appear in a
returned `RowOneRenderResult` or generated public artifact.

## Module Boundaries

Add `src/fashion_radar/row_one/publish.py` for filesystem transaction behavior.
It owns publish paths, locking, journal parsing and writing, unrelated-child
copying, staging validation, rename operations, rollback, recovery, and cleanup.

Keep rendering in `src/fashion_radar/row_one/render.py`:

- extract the current write body into a private in-place renderer;
- keep `render_row_one_site` as the public dispatcher;
- dispatch `latest_only=False` directly to the in-place renderer;
- dispatch `latest_only=True` through the publisher using a callback that
  invokes the in-place renderer against the staging directory;
- construct the final result with logical live paths only after commit.

`src/fashion_radar/workflows.py` and CLI callers retain their current API usage.
The transaction does not belong in the CLI because direct renderer callers must
receive the same latest-only protection.

## Logical And Physical Output Paths

The user-provided `output_dir` is the logical output and remains the returned
and documented path.

When the logical output is a symbolic link, the publisher resolves its physical
target and performs the staging, backup, and rename operations beside that
target. It does not replace the logical symlink itself. A symlink loop or a
target that is an existing non-directory fails before live mutation. A dangling
symlink is allowed when its resolved target parent can be created safely.

For a normal output directory, logical and physical outputs are the same.

The platform capability gate runs before the physical parent directory is
created. After the gate passes, the physical parent directory is created before
lock acquisition and staging.
Stage and backup directories must be siblings of the physical output so each
publish rename remains on one filesystem.

## Filesystem Capability Boundary

The owner marker and generated JSON live below a managed root while staging and
after staging becomes live. A final-component `O_NOFOLLOW` check is insufficient
because a pathname open can still traverse a replaced root or `data/` ancestor.
The publisher therefore requires all of the following before latest-only
publication starts:

- `os.open`, `os.stat`, `os.mkdir`, and `os.unlink` support
  descriptor-relative `dir_fd` operations;
- directory opens support `O_DIRECTORY` and `O_NOFOLLOW`;
- every stage or live managed root and its `data` child can be opened and
  identity-checked as actual directories before owner or generated JSON files
  are accessed.

If any capability is unavailable, publication raises exactly
`ROW ONE safe directory handles are unsupported on this platform` before
creating the physical output parent, stable lock, journal, stage, backup, or
owner marker and before invoking the render callback. The publisher never uses
a pathname-only fallback for owner creation or stage/live owner and JSON reads.

The resolved physical output parent is the local transaction root. Stage 391
protects every transaction entry and managed descendant below that root with
no-follow metadata and ownership checks. Concurrent hostile replacement of an
already resolved ancestor above that transaction root is outside this local,
single-user publisher's threat model.

The package remains OS-independent overall. Non-latest in-place build and
preview paths remain available on platforms that fail this gate. A future
Windows native-handle publisher may remove the capability restriction without
changing the public site contracts.

## Managed And Unrelated Children

The managed generated children remain exactly:

```text
index.html
.row-one-site
details/
assets/
data/
articles/
```

The publisher performs the current marker safety check without deletion:

- generated-looking children plus no `.row-one-site` marker fail before stage
  creation;
- an absent output is allowed;
- an unmarked output containing only unrelated children is allowed;
- a marked generated output is allowed.

The existing mutating `clean_row_one_site_children` remains available for the
in-place behavior. Its check logic is extracted into a private read-only helper
used by both cleanup and staged publication.

Before rendering, every unrelated top-level child of an existing physical
output is copied into staging:

- regular files use metadata-preserving copy;
- directories use recursive metadata-preserving copy;
- symbolic links are recreated from `os.readlink` and are never followed;
- sockets, FIFOs, devices, and other special files fail before the first live
  rename;
- generated-directory contents are not copied, matching current latest-only
  cleanup semantics.

The publisher captures the physical output root's ordinary mode and timestamp
metadata before rendering. After rendering and staged integrity validation, it
reapplies that metadata to staging immediately before the `ready` phase is
written. Applying it after rendering is required because creation of generated
top-level children changes the staging root timestamp, and applying a read-only
root mode before rendering could prevent the renderer from completing. This
does not change the generated-child replacement rules.

Path and content preservation are required. Inode identity, every filesystem
ACL or extended attribute, and concurrent edits by a non-publisher during the
short transaction are not promised.

## Transaction Paths And Ownership

The physical output parent contains these private operational paths:

```text
.<output-name>.row-one-publish.lock
.<output-name>.row-one-publish.json
.<output-name>.row-one-stage-<token>/
.<output-name>.row-one-backup-<token>/
```

The lock file is stable and may remain after a successful publish. It contains
a small contract marker and the normalized physical output path, and consumes
negligible space. After acquiring the operating-system lock, the publisher
validates this ownership metadata before using an existing lock file. An
empty regular lock file is treated as recoverable creation-crash residue and is
initialized only after the publisher successfully acquires its OS lock. An
unrecognized nonempty lock file fails without being overwritten. The lock file
is not deleted because unlinking it can allow different processes to lock
different inodes under the same pathname.

The journal records the normalized physical output path, token, staging path,
backup path, whether an old live output directory existed, whether its public
site marker existed, whether its index existed, and phase. Recording these as
separate facts preserves the existing case where an unmarked directory contains
only unrelated user files and is therefore a valid first-publish target. Paths
loaded from a journal are accepted only when they remain direct siblings of the
expected physical output, match the expected tokenized names, and do not alias
the live path, lock, or journal.

Staging contains a private `data/.row-one-publish-owner.json` marker carrying
the same token. It lives inside the managed `data/` tree so it cannot collide
with an unrelated top-level user file that latest-only refresh promises to
preserve. The marker moves with staging if staging becomes live and is removed
before a successful result is returned. It is not a public site artifact.

An unrecognized journal, malformed journal, path mismatch, owner-token mismatch,
or unjournaled sibling matching a ROW ONE stage or backup prefix is ambiguous.
The publisher fails without deleting anything and reports the exact paths that
need operator inspection. This fail-fast behavior prevents accidental deletion
and silent disk accumulation.

## Single-Publisher Lock

Use a separate, stable lock file rather than locking the journal. Journal phase
writes replace the journal inode, so a lock attached to that inode would not
protect later opens of the replacement pathname.

The lock is non-blocking:

- POSIX uses `fcntl.flock(LOCK_EX | LOCK_NB)`;
- Windows uses the standard-library `msvcrt` non-blocking byte-range lock;
- an unsupported lock implementation fails with a clear error before staging;
- a live competing publisher fails immediately and does not inspect or recover
  its transaction;
- operating-system lock release on process termination removes the need for PID
  reuse or stale PID heuristics.

The Windows `msvcrt` lock implementation remains defined and tested, but the
current staged publisher's earlier safe-directory capability gate prevents it
from being reached on a standard Windows Python build. It remains part of the
portable lock contract for a future native-handle staging backend.

Lock, journal, temporary journal, and owner paths are inspected with no-follow
filesystem metadata. A symlink, directory, special file, or other non-regular
object in a file role is ambiguous and is never followed, overwritten, or
deleted. The lock opener uses `O_NOFOLLOW` where available and verifies lstat
and fstat identity on fallback platforms. The Windows byte-range lock may cover
one byte beyond the current end of an empty file; the publisher does not write a
sentinel byte before acquiring the lock.

Recovery and cleanup occur only while this lock is held.

## Atomic Journal Writes

Every journal phase write uses this sequence:

1. serialize a complete JSON object to a unique sibling temporary file;
2. flush and `fsync` the temporary file where supported;
3. atomically replace the deterministic journal path with `os.replace`;
4. best-effort `fsync` the parent directory where supported;
5. remove a leftover temporary journal on handled failure.

The publisher never edits the journal in place. A malformed journal is still
treated as ambiguous and is preserved for manual inspection.

Temporary journal recovery is deterministic under the publisher lock:

- when the canonical journal is valid, a temporary journal with the same token
  is stale and may be removed after the canonical state is recovered;
- when the canonical journal is absent and exactly one temporary journal is a
  complete, safe object, atomically promote it to the canonical journal and
  recover that state;
- a mismatched, malformed, unsafe, or non-unique temporary journal set is
  ambiguous and is preserved without mutation.

The design targets process-crash recovery. It does not claim complete durability
through sudden power loss on every filesystem.

## Journal Phases

The journal uses these explicit phases:

1. `staging`: the token and owned paths exist or are about to be created;
2. `ready`: staging rendered and passed pre-publish validation;
3. `live_moving`: an existing live output is about to move to backup;
4. `live_backed_up`: the old live output is in the owned backup;
5. `published`: staging moved to live and the live output passed validation.

The phase is written before a destructive transition and again after a
successful transition. Recovery combines phase with actual owned path presence;
it never trusts phase alone.

## Staging And Validation

The staged render sequence is:

1. require safe directory-relative filesystem operations without mutation;
2. create the physical parent and acquire the single-publisher lock;
3. recover or reject any prior transaction state;
4. perform the read-only live marker safety check;
5. atomically write a `staging` journal;
6. create the owned staging directory and owner marker;
7. copy unrelated top-level children;
8. call the in-place renderer against staging with cleanup disabled;
9. validate staging;
10. reapply the captured live-root mode and timestamp metadata to staging;
11. atomically write the `ready` phase.

Validation reads what was actually written to disk. It does not reuse an
in-memory app payload as a substitute for disk validation.

The staged validator:

- calls `validate_row_one_site_dir`, which requires `.row-one-site` and
  `index.html`;
- explicitly confirms that the private owner token matches the journal;
- reads `data/edition.json`, `data/manifest.json`, and `data/runtime.json` as
  JSON objects;
- passes the parsed `data/edition.json` object to
  `validate_row_one_generated_site_integrity`;
- confirms the staged render result refers to the staging directory before it
  is rebased;
- propagates any validation exception as a pre-publish failure.

Before unrelated directories are copied, the publisher recursively scans their
entries without following symbolic links and rejects nested sockets, FIFOs,
devices, or other special files. This prevents a recursive copy from blocking
or reading an untrusted special path.

Any stage creation, copy, render, JSON read, or validation failure leaves the
live output untouched. Owned staging and journal data are removed on handled
failure unless preserving them is required to explain an ambiguous state.
An unsupported filesystem capability fails earlier and creates no output
parent, lock, journal, stage, backup, owner marker, or render side effect.

## Commit And Rollback

### First Publish

When no physical live output exists:

1. move staging to the physical live path with one rename;
2. validate the physical live output;
3. write `published`;
4. remove the private owner marker and journal;
5. return a result rebased to the logical output.

If the move fails, no partial live directory is accepted. If post-move
validation or the `published` journal write fails, rename the token-owned new
live directory back to its owned staging path. A successful rollback removes
the owned stage and journal and re-raises the original failure. If that rename
or owned cleanup fails, preserve the token-owned live or staging path and
journal as an explicit rollback or cleanup-pending state. Neither case returns
a successful publish result.

### Existing Publish

When a physical live output exists:

1. write `live_moving`;
2. rename live to the owned backup;
3. write `live_backed_up`;
4. rename staging to live;
5. validate live;
6. write `published`;
7. remove the private owner marker;
8. remove backup and journal;
9. return a result rebased to the logical output.

If the first rename fails, the old live output remains in place. If writing the
`live_backed_up` phase, performing the second rename, validating the new live,
or writing the `published` phase fails, immediately restore the old output in
the same invocation. When a token-owned new live exists, first rename it back
to its owned staging path and then rename backup back to live. A successful
rollback removes the owned stage and journal, revalidates the restored prior
state, and re-raises the original publish failure. If moving the token-owned
new live aside, restoring the backup, or cleaning owned rollback state fails,
keep journal, backup, staging or token-owned live state and raise a rollback or
cleanup-pending error containing every recovery path.

There is a short interval between the two directory renames when the physical
live pathname is absent. Eliminating that interval requires the deferred
versioned-symlink architecture and is not a Stage 391 promise.

## Recovery Matrix

Recovery always runs under the publisher lock and favors the previous version
when a backup exists and the transaction is not durably marked `published`.

| Journal and paths | Recovery |
| --- | --- |
| No journal and no matching owned artifacts | Start normally. |
| No journal plus matching stage/backup artifacts | Fail ambiguous; delete nothing. |
| `staging` or `ready`, old live present, no backup | Keep old live; remove token-owned stage and journal after validation. |
| `live_moving`, old live present, no backup | The live-to-backup rename did not complete; keep and validate old live, then remove token-owned stage and journal. |
| `live_moving`, live missing, backup present | Restore backup to live; remove token-owned stage and journal. |
| `live_backed_up`, backup present | Remove only a token-owned new live if present, then restore and validate backup. |
| Pre-`published`, new token-owned live and backup present | Restore the old backup, even when the new live validates. |
| First publish, token-owned live validates, no backup | Keep the valid live, mark published, remove owner marker and journal. |
| `published`, valid live, backup present | Keep live; remove backup, owner marker, and journal. |
| `published`, invalid live, valid backup present | Restore backup and report failed commit validation. |
| Any state with malformed metadata, mismatched token, unsafe path, or multiple interpretations | Fail ambiguous and report all paths; delete nothing. |

Recovery validates the chosen live site before starting a new render.
When the journal proves the prior output was an unrelated-only unmarked
directory, recovery instead validates that the directory and its unrelated
children were restored; it does not require ROW ONE marker or index files that
did not previously exist. A marker-only prior output remains repairable under
the existing safety rule because the marker itself is not treated as an
unmarked generated child. An index-only prior output is restored byte-for-byte
but remains an unsafe unmarked generated target; recovery reports it and a new
publish refuses to overwrite it. Recovery never bypasses the marker guard.

The `published` recovery path accepts a missing private owner marker because a
process may terminate after removing that marker but before deleting the backup
and journal. It still validates the complete live site and journal-owned paths.
If an owner path remains, it must be a regular file with the matching token.
Every phase before `published` continues to require the owner marker when a
token-owned new live or staging directory must be identified.

## Cleanup Semantics

Before the first cleanup mutation, the publisher validates the canonical
journal, owner state, stage or live ownership, backup object, and the complete
set of matching temporary journals as one preflight. If any object is unsafe,
unowned, malformed, or inconsistent, cleanup deletes nothing. Once preflight
passes, later I/O failure may leave a partial but still journal-owned cleanup
state for the next invocation.

Successful publication removes the owned stage, backup, private owner marker,
journal, and temporary journal files. The stable lock file may remain.

Pre-commit cleanup failure leaves the old live site untouched and reports the
owned path. Post-commit cleanup failure does not roll back a valid new live
site. It raises a dedicated cleanup-pending error containing the live, backup,
journal, and stage paths; the next invocation performs recovery cleanup before
rendering.

No successful or failed transaction keeps a second historical website after
recovery completes. This preserves latest-only bounded storage.

## Result Semantics

The in-place staging renderer may produce an internal result whose paths point
at staging. That internal result is not returned to the caller.

After the live rename and validation succeed, the public dispatcher constructs
a new `RowOneRenderResult` with:

- `output_dir` set to the original logical output path;
- `index_path` set to the logical `output_dir / "index.html"`;
- story count, edition, and local article metrics copied from the staged render
  result.

No result is returned before commit.

## Error Behavior

Errors must distinguish these cases in concise messages:

- publish already in progress;
- unsafe unmarked live output;
- unsupported unrelated filesystem child;
- stage creation, copy, render, or validation failure with live untouched;
- first or second rename failure;
- publish failure followed by successful rollback;
- rollback failure with retained recovery paths;
- ambiguous or unowned transaction state;
- valid new live with cleanup pending.

No error message includes credentials, article bodies, or unrelated file
contents. Ordinary handled stage creation, copy, render, validation, rename, or
successful-rollback failures use concise public messages and retain the
original exception only as `__cause__`; they do not expose tokenized staging,
backup, or physical-target paths. Rollback, cleanup-pending, and ambiguous-state
errors deliberately include the retained recovery paths needed for an operator
to recover safely.

## Test Design

Use direct tests for the new publisher plus integration tests through
`render_row_one_site(..., latest_only=True)`. Fault injection targets focused
module helpers rather than globally patching `Path.rename`, `Path.replace`, or
`os.replace`, so each transition can be identified reliably.

Required RED or strengthened regression coverage:

1. `_write_assets` failure preserves old index, runtime, assets, and unrelated
   files byte-for-byte.
2. stage-directory creation failure leaves live untouched.
3. unrelated regular-file, directory, and symlink copy failure leaves live
   untouched.
4. staged marker absence, malformed JSON, and integrity failure leave live
   untouched and perform no live rename.
5. unexpected validator exceptions, including `OSError`, have the same
   pre-publish behavior.
6. first-publish rename failure leaves no accepted partial live site.
7. existing live-to-backup rename failure is non-destructive.
8. staging-to-live rename failure restores and validates the old site.
9. post-rename validation failure restores the old site.
10. rollback failure retains sufficient journal and owned paths for the next
    invocation to recover.
11. each journal phase has an old-version-first recovery test.
12. malformed journal, unsafe journal paths, token mismatch, and unjournaled
    lookalike siblings fail without deletion.
13. a concurrent publisher holding the OS lock causes a fast failure before
    recovery or staging, while an empty regular lock left by a creation crash is
    initialized only after acquiring that same OS lock.
14. output root regular files, directories, symlinks, and metadata survive a
    successful transaction; old generated children do not.
15. special unrelated files fail before live mutation on platforms that can
    create representative fixtures.
16. normal output, existing output symlink, and safely creatable dangling
    symlink target cases preserve logical return paths.
17. success, handled pre-commit failure, successful rollback, and completed
    recovery leave no stage, backup, journal, owner marker, or temporary
    journal. The stable lock file is allowed.
18. post-commit cleanup failure keeps the valid new live site and is recovered
    on the next invocation.
19. `latest_only=False` bypasses the publisher and retains current in-place
    behavior.
20. CLI build, preview, and refresh continue to print logical output paths and
    return nonzero on publisher errors.

Existing route, app contract, manifest, runtime, article, rendering, cleanup,
server, status, ops, first-run, packaging, and systemd tests remain part of the
integration surface.

## Verification

The implementation stage must run fresh verification from the integrated tree:

- focused publisher, render, workflow, CLI, server, status, ops, and scheduling
  tests;
- the full pytest suite;
- Ruff check and format check;
- release hygiene;
- public lockfile and locked-sync checks;
- source-checkout first-run smoke;
- wheel and sdist archive validation;
- installed CLI/module help, `init`, `doctor`, first-run, package-resource, and
  ROW ONE smoke checks;
- generated user-systemd unit verification where available;
- Claude Code `--effort max` code and release reviews of stable snapshots.

## Non-Goals

Stage 391 does not add or change:

- zero-downtime or fully atomic symlink releases;
- indefinite release history or manual rollback commands;
- power-loss durability guarantees on every filesystem;
- concurrent edits to unrelated output files by non-publisher processes;
- transactional `latest_only=False` rendering;
- transactional systemd unit installation;
- `ops-check` status, `ok`, strict mode, or exit semantics;
- recent-item publication-time correctness;
- RSS item-age filtering or source-pack composition;
- overseas workers, proxies, remote transport, or deployment;
- collection, extraction, matching, scoring, ranking, or trend formulas;
- translation, image generation, or model calls;
- app, manifest, runtime, database, report, or source schemas;
- dependencies or `uv.lock`.

## Follow-Up Order

After this node is released, the recommended independent follow-ups are:

1. correct `row-one ops-check` health derivation and add a strict exit mode;
2. show true item publication time while retaining observed-at selection order;
3. design opt-in RSS item-age filtering;
4. verify foreign sources from the overseas node before source-pack changes;
5. add source-paragraph provenance before expanding person/designer heat
   evidence;
6. design a real optional translation provider.

## Acceptance Criteria

Stage 391 is complete only when:

- a render or staged-validation exception cannot change an existing live site;
- handled publish failures restore a valid old site or retain explicit owned
  recovery state when rollback itself fails;
- the next invocation recovers every specified process-crash phase;
- unrelated top-level output children retain their current preservation
  contract;
- generated URLs, schemas, CLI paths, systemd paths, and public result paths do
  not change;
- latest-only storage remains bounded after successful recovery and cleanup;
- no unknown or unowned path is deleted;
- an unsupported safe-directory capability fails before every filesystem
  mutation and render callback, with the documented concise error;
- public documentation identifies the capability-gated latest-only boundary
  and the unchanged non-latest fallback;
- the full release verification and required Claude Code reviews pass.
