# Stage 391 ROW ONE Recoverable Staged Publish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make latest-only ROW ONE publication render, validate, commit, and
recover a complete site without destroying the previously published site when
a handled refresh or process crash interrupts publication.

**Architecture:** Add a focused `row_one/publish.py` filesystem transaction
module with a stable OS lock, atomically replaced journal, same-filesystem stage
and backup directories, validation before and after commit, rollback, and
old-version-first recovery. Keep `render_row_one_site` as the public dispatcher,
move its current write body into an in-place helper, and route only
`latest_only=True` through the publisher while preserving logical output paths,
URLs, schemas, and unrelated top-level files.

**Tech Stack:** Python 3.11+, standard-library `pathlib`, `os`, `json`, `secrets`,
`shutil`, `stat`, `contextlib`, POSIX `fcntl`, Windows `msvcrt`, existing ROW ONE
validators and models, pytest fault injection, Ruff, uv, Git.

**Core product gap closed:** The report/publish end of the
collect -> match -> report pipeline currently destroys the live ROW ONE site
before a replacement has rendered successfully. This stage makes a failed daily
report refresh preserve or restore the prior published report.

---

## Fixed Interface Contract

Workers must use these exact public-to-module names. Private helper internals may
be tightened during review, but no worker may rename or widen these contracts
without a reviewed plan amendment.

Create `src/fashion_radar/row_one/publish.py` with:

```python
from __future__ import annotations

import json
import os
import secrets
import shutil
import stat
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO, NoReturn, Protocol, TypeVar


ROW_ONE_PUBLISH_CONTRACT_VERSION = "row-one-publish/v1"
ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION = "row-one-publish-lock/v1"
ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION = "row-one-publish-owner/v1"
ROW_ONE_PUBLISH_OWNER_PATH = Path("data/.row-one-publish-owner.json")
GENERATED_CHILDREN = (
    "index.html",
    ".row-one-site",
    "details",
    "assets",
    "data",
    "articles",
)


class RowOnePublishError(RuntimeError):
    pass


class RowOnePublishBusyError(RowOnePublishError):
    pass


class RowOnePublishAmbiguousStateError(RowOnePublishError):
    pass


class RowOnePublishRollbackError(RowOnePublishError):
    pass


class RowOnePublishCleanupPendingError(RowOnePublishError):
    pass


class RowOnePublishPreservedError(RowOnePublishError):
    pass


class RowOnePublishRestoredError(RowOnePublishError):
    pass


class RowOnePublishPhase(StrEnum):
    STAGING = "staging"
    READY = "ready"
    LIVE_MOVING = "live_moving"
    LIVE_BACKED_UP = "live_backed_up"
    PUBLISHED = "published"


@dataclass(frozen=True)
class RowOnePublishTarget:
    logical_output: Path
    physical_output: Path
    lock_path: Path
    journal_path: Path


@dataclass(frozen=True)
class RowOnePublishTransaction:
    target: RowOnePublishTarget
    token: str
    stage_path: Path
    backup_path: Path
    had_live_output: bool
    had_site_marker: bool
    had_index: bool
    phase: RowOnePublishPhase


class StagedRowOneRenderResult(Protocol):
    output_dir: Path
    index_path: Path


RenderResultT = TypeVar("RenderResultT", bound=StagedRowOneRenderResult)


def publish_latest_row_one_site(
    output_dir: Path,
    *,
    render: Callable[[Path], RenderResultT],
) -> RenderResultT:
    """Publish a latest-only site and return the callback's internal result.

    The returned result's output_dir and index_path identify the staging paths
    used for validation and no longer exist after commit. The public renderer
    must rebase those fields to the logical output before exposing its result.
    """
```

Private helper signatures used across tasks are fixed by this table so later
steps do not invent incompatible names:

| Helper | Signature | First implementation |
| --- | --- | --- |
| `_resolve_publish_target` | `(output_dir: Path) -> RowOnePublishTarget` | Task 1 Step 3 |
| `_new_transaction` | `(target: RowOnePublishTarget, *, token: str | None = None) -> RowOnePublishTransaction` | Task 1 Step 3 |
| `_validate_token` | `(token: str) -> None` | Task 1 Step 3 |
| `_journal_payload` | `(transaction: RowOnePublishTransaction) -> dict[str, object]` | Task 1 Step 4 |
| `_load_journal` | `(target: RowOnePublishTarget) -> RowOnePublishTransaction | None` | Task 1 Step 4 |
| `_write_journal` | `(transaction: RowOnePublishTransaction) -> None` | Task 1 Step 4 |
| `_recover_temporary_journals` | `(target: RowOnePublishTarget) -> None` | Task 1 Step 4 |
| `_fsync_directory` | `(path: Path) -> None` | Task 1 Step 4 |
| `_acquire_publish_lock` | `(target: RowOnePublishTarget) -> Iterator[None]` context manager | Task 1 Step 6 |
| `_open_lock_file` | `(target: RowOnePublishTarget) -> BinaryIO` | Task 1 Step 6 |
| `_try_lock_handle` | `(handle: BinaryIO) -> None` | Task 1 Step 6 |
| `_unlock_handle` | `(handle: BinaryIO) -> None` | Task 1 Step 6 |
| `_validate_or_initialize_lock_metadata` | `(handle: BinaryIO, target: RowOnePublishTarget) -> None` | Task 1 Step 6 |
| `_validate_live_publish_target` | `(target: RowOnePublishTarget) -> None` | Task 2 Step 3 |
| `_validate_unrelated_tree` | `(path: Path) -> None` | Task 2 Step 3 |
| `_copy_unrelated_children` | `(source: Path, stage: Path) -> None` | Task 2 Step 3 |
| `_apply_live_root_metadata` | `(transaction: RowOnePublishTransaction) -> None` | Task 2 Step 3 |
| `_read_json_object` | `(path: Path, *, label: str) -> dict[str, object]` | Task 2 Step 5 |
| `_read_owner_token` | `(directory: Path) -> str` | Task 2 Step 5 |
| `_write_owner_file` | `(stage: Path, transaction: RowOnePublishTransaction) -> None` | Task 2 Step 5 |
| `_validate_staged_row_one_site` | `(transaction: RowOnePublishTransaction, result: StagedRowOneRenderResult) -> None` | Task 2 Step 5 |
| `_move_publish_path` | `(source: Path, destination: Path) -> None` | Task 3 Step 1 |
| `_remove_publish_path` | `(path: Path) -> None` | Task 3 Step 1 |
| `_replace_phase` | `(transaction: RowOnePublishTransaction, phase: RowOnePublishPhase) -> RowOnePublishTransaction` | Task 3 Step 1 |
| `_validate_published_row_one_site` | `(transaction: RowOnePublishTransaction, *, require_owner: bool = True) -> None` | Task 3 Step 4 |
| `_commit_first_publish` | `(transaction: RowOnePublishTransaction) -> RowOnePublishTransaction` | Task 3 Step 4 |
| `_commit_existing_publish` | `(transaction: RowOnePublishTransaction) -> RowOnePublishTransaction` | Task 3 Step 4 |
| `_rollback_existing_publish` | `(transaction: RowOnePublishTransaction, publish_error: BaseException) -> NoReturn` | Task 3 Step 4 |
| `_recover_interrupted_publish` | `(target: RowOnePublishTarget) -> None` | Task 3 Step 6 |
| `_reject_unowned_publish_artifacts` | `(target: RowOnePublishTarget) -> None` | Task 3 Step 6 |
| `_is_owned_live` | `(transaction: RowOnePublishTransaction) -> bool` | Task 3 Step 6 |
| `_restore_previous_output` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 6 |
| `_finish_published_recovery` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 6 |
| `_finish_valid_first_publish_recovery` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 6 |
| `_clean_precommit_stage_after_preserving_old_output` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 6 |
| `_begin_staging` | `(transaction: RowOnePublishTransaction) -> RowOnePublishTransaction` | Task 3 Step 7 |
| `_copy_unrelated_children_if_present` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 7 |
| `_commit_publish` | `(transaction: RowOnePublishTransaction) -> RowOnePublishTransaction` | Task 3 Step 7 |
| `_cleanup_after_handled_failure` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 7 |
| `_cleanup_after_published` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 7 |
| `_preflight_cleanup_artifacts` | `(transaction: RowOnePublishTransaction, *, published: bool) -> None` | Task 3 Step 7 |
| `_remove_owner_file_if_present` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 7 |
| `_remove_owned_backup_if_present` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 7 |
| `_remove_matching_temporary_journals` | `(transaction: RowOnePublishTransaction) -> None` | Task 3 Step 7 |

The journal JSON keys are exact and stable for Stage 391 local recovery:

```python
{
    "contract_version": "row-one-publish/v1",
    "token": "<32 lowercase hexadecimal characters>",
    "physical_output": "/absolute/output/path",
    "stage_path": "/absolute/.site.row-one-stage-<token>",
    "backup_path": "/absolute/.site.row-one-backup-<token>",
    "had_live_output": True,
    "had_site_marker": True,
    "had_index": True,
    "phase": "ready",
}
```

Use these deterministic sibling names for a physical output named `site`:

```text
.site.row-one-publish.lock
.site.row-one-publish.json
.site.row-one-publish.<token>.<nonce>.tmp
.site.row-one-stage-<token>/
.site.row-one-backup-<token>/
```

The stable lock file is allowed to remain after success. Stage, backup, journal,
temporary journal, and private owner files are not allowed after a fully cleaned
success.

## File Map

- Create: `src/fashion_radar/row_one/publish.py` - target resolution, ownership,
  OS lock, journal, copying, validation, commit, rollback, recovery, cleanup.
- Create: `tests/test_row_one_publish.py` - focused state-machine and filesystem
  tests.
- Modify: `src/fashion_radar/row_one/render.py` - in-place helper extraction and
  latest-only dispatcher.
- Modify: `src/fashion_radar/cli.py` - accurate `--latest-only` help text while
  retaining command behavior and error prefixes.
- Modify: `tests/test_row_one_render.py` - real-render integration, result path,
  user-file, validation, and in-place regression coverage.
- Modify: `tests/test_workflows.py` - workflow-level latest-only failure and
  successful refresh integration.
- Modify: `tests/test_row_one_cli.py` - build, preview, and refresh error/returned
  logical-path contracts.
- Modify: `scripts/check_first_run_smoke.py` - successful first-run denies
  transaction debris and accepts the stable lock file.
- Modify: `tests/test_first_run_smoke.py` - first-run transaction-debris
  validation.
- Modify: `scripts/check_package_archives.py` and
  `tests/test_package_archives.py` - require `publish.py` in wheel and sdist.
- Modify: `README.md`, `docs/row-one.md`, `docs/first-run.md`,
  `docs/cli-reference.md`, `docs/architecture.md`, and `CHANGELOG.md` - public
  behavior, limits, recovery, help, and follow-up boundaries.
- Modify: `tests/test_row_one_docs.py`, `tests/test_first_run_docs.py`,
  `tests/test_cli_docs.py`, and `tests/test_architecture_boundary_docs.py` -
  documentation contracts.
- Modify: `docs/superpowers/specs/2026-07-14-stage-391-row-one-recoverable-staged-publish-design.md`
  only for review-driven corrections; do not silently change the approved scope.
- Create: `docs/reviews/claude-code-stage-391-plan-review.md` when Claude returns
  one complete primary review.
- Create: `docs/reviews/opencode-stage-391-plan-review.md` for the required
  OpenCode revision after Claude, or as the formal fallback if Claude is
  unavailable after the protocol retry.
- Create if required: `docs/reviews/claude-code-stage-391-plan-rereview.md` and
  `docs/reviews/opencode-stage-391-plan-rereview.md`.
- Create: `docs/reviews/claude-code-stage-391-code-review.md` and any required
  rereview.
- Create: `docs/reviews/claude-code-stage-391-release-review.md`, or the matching
  OpenCode fallback record only when the protocol permits fallback.

No dependency, schema, source configuration, or `uv.lock` file is in scope.

## Parallel Ownership And Order

- Coordinator owns Task 0, the approved spec and plan, integration, cross-file
  result semantics, review records, final verification, conflict resolution,
  commits, and publication.
- Worker A owns `src/fashion_radar/row_one/publish.py` and
  `tests/test_row_one_publish.py` for Tasks 1 through 3.
- Coordinator owns `src/fashion_radar/row_one/render.py` and
  `tests/test_row_one_render.py` for Task 4 because this is the shared integration
  boundary with more than one hundred existing render callers.
- Worker B owns `scripts/check_first_run_smoke.py`,
  `tests/test_first_run_smoke.py`, `scripts/check_package_archives.py`, and
  `tests/test_package_archives.py` for Task 5A.
- Worker C owns `README.md`, `docs/row-one.md`, `docs/architecture.md`,
  `docs/first-run.md`, `docs/cli-reference.md`, `CHANGELOG.md`,
  `tests/test_row_one_docs.py`, `tests/test_first_run_docs.py`,
  `tests/test_cli_docs.py`, and `tests/test_architecture_boundary_docs.py` for
  Task 5B.
- Coordinator owns `tests/test_workflows.py` and `tests/test_row_one_cli.py`
  after Task 4 fixes the integration API.

Task 0 must pass before implementation. Worker A starts first. Once Task 1 fixes
the module interface, Worker B and Worker C may start in parallel because their
write sets are disjoint. Task 4 begins after Worker A completes Task 3. No agent
may edit another owner's files, stage another owner's changes, or commit while a
different worker has staged content. The coordinator reconciles every worker's
changed-file list, tests, unresolved work, and terminal state before reusing its
slot. Workers A, B, and C do not run `git add` or `git commit`; only the
coordinator stages reconciled files and creates commits.

## Task 0: Formal Plan Review And Acceptance

**Owner:** Coordinator

**Files:**

- Create: `docs/reviews/claude-code-stage-391-plan-review.md`
- Create: `docs/reviews/opencode-stage-391-plan-review.md`
- Modify if required: the Stage 391 design and this plan
- Create rereview records only when a review-driven diff requires them

- [ ] **Step 1: Self-review the plan against every design requirement**

Run:

```bash
git diff --check
rg -n '\b([T]ODO|[T]BD|[F]IXME|[P]LACEHOLDER)\b' \
  docs/superpowers/specs/2026-07-14-stage-391-row-one-recoverable-staged-publish-design.md \
  docs/superpowers/plans/2026-07-14-stage-391-row-one-recoverable-staged-publish-plan.md
```

Expected: `git diff --check` exits zero. The placeholder scan prints nothing and
exits with `rg` status `1`; status `0` means a placeholder was found and every
status above `1` is an unreadable-scan failure.
Confirm every spec acceptance criterion maps to a task and every function name
used in later tasks appears in the Fixed Interface Contract or an earlier step.

- [ ] **Step 2: Request the primary Claude Code plan review**

Run Claude Code with max effort, read-only plan mode, no persistent session, and
only Read, Grep, Glob, LS, and Bash:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review the approved Stage 391 recoverable staged publish design and implementation plan in this worktree. Verify journal and lock correctness, symlink target handling, unrelated-file preservation, staged integrity validation, every recovery phase, rollback and cleanup semantics, exact worker ownership, TDD ordering, no dependency/schema/URL drift, and release coverage. Findings first by severity. Return one coherent verdict and list every Critical or Important correction required before implementation. Do not edit files."
```

Capture only the complete coherent review body in
`docs/reviews/claude-code-stage-391-plan-review.md`. Do not commit a timeout,
tool-status text, duplicate output, truncated review, live-capture stub, or
credential material. Retry once with a narrower prompt if the first invocation
does not return a complete body.

- [ ] **Step 3: Request the required OpenCode plan revision**

After Claude's review, run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar/.worktrees/stage-388-release-documentation-consistency \
  "Revise and independently verify the current Stage 391 design and plan after the Claude plan review. Focus on filesystem transaction correctness, cross-platform locking, journal crash states, safe-path ownership, first publish, unrelated-only target rollback, symlink targets, tests, and worker write sets. Findings first and one verdict. Do not modify files."
```

Store one coherent body in `docs/reviews/opencode-stage-391-plan-review.md`.

- [ ] **Step 4: Resolve every Critical and Important finding**

Amend the spec and plan with `apply_patch`. Re-run Step 1. If any review-driven
plan text changes, request a fresh Claude max rereview and OpenCode max rereview
as required by `docs/REVIEW_PROTOCOL.md`. Tasks 1 through 6 remain blocked until
the active plan has no Critical or Important finding.

- [ ] **Step 5: Commit the accepted plan gate**

```bash
git add \
  docs/superpowers/specs/2026-07-14-stage-391-row-one-recoverable-staged-publish-design.md \
  docs/superpowers/plans/2026-07-14-stage-391-row-one-recoverable-staged-publish-plan.md \
  docs/reviews/claude-code-stage-391-plan-review.md \
  docs/reviews/opencode-stage-391-plan-review.md
git commit -m "docs: accept Stage 391 recoverable publish plan"
```

Include rereview files in the same commit when created. Expected: one plan-gate
commit and a clean worktree.

## Task 1: Publish Models, Safe Paths, OS Lock, And Atomic Journal

**Owner:** Worker A

**Files:**

- Create: `tests/test_row_one_publish.py`
- Create: `src/fashion_radar/row_one/publish.py`

- [ ] **Step 1: Write RED target, phase, path, symlink, and journal tests**

Start `tests/test_row_one_publish.py` with these shared helpers. Later task
snippets use these exact names; when a later RED step introduces another direct
helper reference, add that helper to this import block in the same RED change:

```python
import json
import os
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

import fashion_radar.row_one.publish as publish_module
from fashion_radar.row_one.publish import (
    ROW_ONE_PUBLISH_CONTRACT_VERSION,
    ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION,
    ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION,
    ROW_ONE_PUBLISH_OWNER_PATH,
    RowOnePublishAmbiguousStateError,
    RowOnePublishBusyError,
    RowOnePublishCleanupPendingError,
    RowOnePublishError,
    RowOnePublishPhase,
    RowOnePublishPreservedError,
    RowOnePublishRestoredError,
    RowOnePublishRollbackError,
    RowOnePublishTransaction,
    _acquire_publish_lock,
    _copy_unrelated_children,
    _load_journal,
    _new_transaction,
    _resolve_publish_target,
    _validate_live_publish_target,
    _validate_staged_row_one_site,
    _write_journal,
    publish_latest_row_one_site,
)


@dataclass(frozen=True)
class FakeStagedResult:
    output_dir: Path
    index_path: Path


def _transaction_fixture(
    tmp_path: Path,
    *,
    phase: RowOnePublishPhase = RowOnePublishPhase.STAGING,
    create_live: bool = True,
) -> RowOnePublishTransaction:
    output = tmp_path / "site"
    if create_live:
        output.mkdir(parents=True, exist_ok=True)
        (output / ".row-one-site").write_text(
            "ROW ONE generated site\n", encoding="utf-8"
        )
        (output / "index.html").write_text("old", encoding="utf-8")
    transaction = _new_transaction(
        _resolve_publish_target(output),
        token="a" * 32,
    )
    return replace(transaction, phase=phase)


def _write_owner(transaction: RowOnePublishTransaction) -> None:
    payload = {
        "contract_version": ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION,
        "physical_output": str(transaction.target.physical_output),
        "token": transaction.token,
    }
    owner_path = transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH
    owner_path.parent.mkdir(parents=True, exist_ok=True)
    owner_path.write_text(
        json.dumps(payload, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _owned_stage_fixture(tmp_path: Path) -> RowOnePublishTransaction:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    transaction.stage_path.mkdir(parents=True)
    _write_owner(transaction)
    return transaction


def _write_minimal_staged_files(
    stage: Path,
    *,
    edition: dict[str, object] | None = None,
) -> None:
    (stage / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (stage / "index.html").write_text("new", encoding="utf-8")
    data = stage / "data"
    data.mkdir(parents=True, exist_ok=True)
    for name, payload in (
        ("edition.json", edition or {"contract_version": "row-one-app/v7", "stories": []}),
        ("manifest.json", {"contract_version": "row-one-manifest/v1"}),
        ("runtime.json", {"contract_version": "row-one-runtime/v1"}),
    ):
        (data / name).write_text(
            json.dumps(payload, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _valid_old_site_fixture(output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old index", encoding="utf-8")
    data = output / "data"
    data.mkdir()
    (data / "runtime.json").write_text('{"old": true}\n', encoding="utf-8")
    return output


def _assert_no_transaction_debris(output: Path) -> None:
    parent = output.resolve(strict=False).parent
    name = output.resolve(strict=False).name
    forbidden = [
        path
        for path in parent.iterdir()
        if path.name == f".{name}.row-one-publish.json"
        or path.name.startswith(f".{name}.row-one-stage-")
        or path.name.startswith(f".{name}.row-one-backup-")
        or (
            path.name.startswith(f".{name}.row-one-publish.")
            and path.name.endswith(".tmp")
        )
    ]
    assert forbidden == []
```

Create focused tests with these exact names:

```python
def test_publish_target_uses_logical_output_and_resolved_physical_target(tmp_path: Path) -> None:
    physical = tmp_path / "physical" / "site"
    logical = tmp_path / "logical-site"
    physical.parent.mkdir()
    logical.symlink_to(physical, target_is_directory=True)

    target = _resolve_publish_target(logical)

    assert target.logical_output == logical
    assert target.physical_output == physical.resolve()
    assert target.lock_path == physical.parent / ".site.row-one-publish.lock"
    assert target.journal_path == physical.parent / ".site.row-one-publish.json"


def test_new_transaction_records_preexisting_unrelated_only_output(tmp_path: Path) -> None:
    output = tmp_path / "site"
    output.mkdir()
    (output / "keep.txt").write_text("keep", encoding="utf-8")
    target = _resolve_publish_target(output)

    transaction = _new_transaction(target, token="a" * 32)

    assert transaction.had_live_output is True
    assert transaction.had_site_marker is False
    assert transaction.had_index is False
    assert transaction.phase is RowOnePublishPhase.STAGING


def test_atomic_journal_round_trip_preserves_exact_contract(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path, phase=RowOnePublishPhase.READY)

    _write_journal(transaction)
    loaded = _load_journal(transaction.target)

    assert loaded == transaction
    assert json.loads(transaction.target.journal_path.read_text(encoding="utf-8")) == {
        "contract_version": "row-one-publish/v1",
        "token": transaction.token,
        "physical_output": str(transaction.target.physical_output),
        "stage_path": str(transaction.stage_path),
        "backup_path": str(transaction.backup_path),
        "had_live_output": True,
        "had_site_marker": True,
        "had_index": True,
        "phase": "ready",
    }
```

Add a platform-neutral test that `_resolve_publish_target(Path(tmp_path.anchor))`
rejects the filesystem root before deriving lock, journal, stage, or backup
siblings. No root path may reach a rename helper.

Also add parameterized invalid-payload tests for unknown keys, missing keys,
unsafe token, wrong contract version, relative paths, non-sibling paths, stage
equal to backup, and output mismatch. Every invalid payload must raise
`RowOnePublishAmbiguousStateError` without deleting the journal.

Add lstat-based tests requiring lock, canonical journal, and matching temporary
journal paths that are symlinks, directories, FIFOs, or other non-regular files
to fail without opening, following, promoting, overwriting, or deleting those
paths. Include a temporary-journal FIFO test behind `hasattr(os, "mkfifo")` so
recovery proves it inspects metadata before reading content. Lock opening uses
`O_NOFOLLOW` where the platform exposes it and an lstat/fstat identity check
otherwise.

- [ ] **Step 2: Run the contract tests and verify RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_publish.py -k \
  'publish_target or new_transaction or journal'
```

Expected: collection or import fails because `fashion_radar.row_one.publish`
does not exist.

- [ ] **Step 3: Add exact models, target resolution, and path validation**

Implement the Fixed Interface Contract. Use this target logic:

```python
def _resolve_publish_target(output_dir: Path) -> RowOnePublishTarget:
    logical_output = output_dir
    try:
        physical_output = output_dir.resolve(strict=False)
    except RuntimeError as exc:
        raise RowOnePublishError(f"ROW ONE output path cannot be resolved: {output_dir}") from exc
    if physical_output == physical_output.parent or not physical_output.name:
        raise RowOnePublishError(
            f"ROW ONE output cannot be a filesystem root: {logical_output}"
        )
    if physical_output.exists() and not physical_output.is_dir():
        raise RowOnePublishError(
            f"ROW ONE physical output is not a directory: {physical_output}"
        )
    parent = physical_output.parent
    name = physical_output.name
    return RowOnePublishTarget(
        logical_output=logical_output,
        physical_output=physical_output,
        lock_path=parent / f".{name}.row-one-publish.lock",
        journal_path=parent / f".{name}.row-one-publish.json",
    )


def _new_transaction(
    target: RowOnePublishTarget,
    *,
    token: str | None = None,
) -> RowOnePublishTransaction:
    publish_token = token or secrets.token_hex(16)
    _validate_token(publish_token)
    output = target.physical_output
    return RowOnePublishTransaction(
        target=target,
        token=publish_token,
        stage_path=output.parent / f".{output.name}.row-one-stage-{publish_token}",
        backup_path=output.parent / f".{output.name}.row-one-backup-{publish_token}",
        had_live_output=output.exists(),
        had_site_marker=(output / ".row-one-site").is_file(),
        had_index=(output / "index.html").is_file(),
        phase=RowOnePublishPhase.STAGING,
    )
```

Journal parsing must rebuild a target from the current requested output, not
trust a serialized logical path. Validate exact sibling names and absolute
physical paths before constructing the transaction.

- [ ] **Step 4: Implement atomic journal writes and temporary-journal recovery**

Use one complete JSON serialization, an exclusive temporary file, file flush,
`os.fsync`, and `os.replace`:

```python
def _write_journal(transaction: RowOnePublishTransaction) -> None:
    target = transaction.target
    nonce = secrets.token_hex(8)
    temp_path = target.journal_path.with_name(
        f".{target.physical_output.name}.row-one-publish."
        f"{transaction.token}.{nonce}.tmp"
    )
    payload = _journal_payload(transaction)
    created_identity: tuple[int, int] | None = None
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(temp_path, flags, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE temporary journal is not regular: {temp_path}"
                )
            created_identity = (opened.st_dev, opened.st_ino)
            json.dump(payload, handle, ensure_ascii=True, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            destination_mode = target.journal_path.lstat().st_mode
        except FileNotFoundError:
            destination_mode = None
        if destination_mode is not None and not stat.S_ISREG(destination_mode):
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE journal path is unsafe: {target.journal_path}"
            )
        os.replace(temp_path, target.journal_path)
        _fsync_directory(target.physical_output.parent)
    finally:
        if created_identity is not None:
            try:
                remaining = temp_path.lstat()
            except FileNotFoundError:
                remaining = None
            if remaining is not None:
                remaining_identity = (remaining.st_dev, remaining.st_ino)
                if not stat.S_ISREG(remaining.st_mode) or remaining_identity != created_identity:
                    raise RowOnePublishAmbiguousStateError(
                        f"ROW ONE temporary journal identity changed: {temp_path}"
                    )
                temp_path.unlink()
```

Implement `_fsync_directory` by opening the directory read-only with
`O_DIRECTORY` when available, calling `os.fsync`, and always closing the file
descriptor. Directory open/fsync `OSError` is deliberately best-effort and may
be ignored because some supported filesystems/platforms reject directory
fsync; journal-file fsync and `os.replace` failures are not ignored.

Implement `_recover_temporary_journals` exactly as the design specifies:
canonical valid plus same-token temporary is stale; no canonical plus exactly
one complete safe temporary promotes it; every mismatch or non-unique set raises
ambiguous state and deletes nothing. Enumerate candidates with no-follow
metadata, require every matching candidate to be a regular file before opening
any candidate, and validate the canonical journal path as missing or regular
before `os.replace`; a symlink, directory, FIFO, socket, or device is preserved
and reported as ambiguous.

- [ ] **Step 5: Add RED single-publisher lock tests**

Add:

```python
def test_publish_lock_rejects_a_concurrent_owner(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.physical_output.parent.mkdir(parents=True, exist_ok=True)

    with _acquire_publish_lock(target):
        with pytest.raises(RowOnePublishBusyError, match="already in progress"):
            with _acquire_publish_lock(target):
                pytest.fail("the second publisher must not acquire the lock")


def test_publish_lock_rejects_unrecognized_existing_metadata(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.lock_path.write_text("not a ROW ONE lock\n", encoding="utf-8")

    with pytest.raises(RowOnePublishAmbiguousStateError, match="lock file"):
        with _acquire_publish_lock(target):
            pytest.fail("unowned lock metadata must fail")

    assert target.lock_path.read_text(encoding="utf-8") == "not a ROW ONE lock\n"


def test_publish_lock_recovers_preexisting_empty_file(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.lock_path.touch()

    with _acquire_publish_lock(target):
        payload = json.loads(target.lock_path.read_text(encoding="utf-8"))

    assert payload == {
        "contract_version": ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION,
        "physical_output": str(target.physical_output),
    }
```

- [ ] **Step 6: Implement the separate stable OS lock**

Use one stable file, acquire before validating or initializing its metadata, and
never unlink it. The implementation branches on `os.name`:

```python
@contextmanager
def _acquire_publish_lock(target: RowOnePublishTarget) -> Iterator[None]:
    target.physical_output.parent.mkdir(parents=True, exist_ok=True)
    with _open_lock_file(target) as handle:
        _try_lock_handle(handle)
        try:
            _validate_or_initialize_lock_metadata(handle, target)
            yield
        finally:
            _unlock_handle(handle)
```

On POSIX, `_try_lock_handle` uses `fcntl.flock(handle.fileno(),
fcntl.LOCK_EX | fcntl.LOCK_NB)` and maps `BlockingIOError` to
`RowOnePublishBusyError`. On Windows, seek to byte zero and use
`msvcrt.locking(..., msvcrt.LK_NBLCK, 1)`; Windows permits the locked region to
extend one byte beyond EOF, so do not write a sentinel before locking an empty
file. Map the platform lock error to the same busy exception. Do not lock the
atomically replaced journal inode.

`_open_lock_file` uses no-follow regular-file checks and creates the stable file
when absent. After the OS lock is held, `_validate_or_initialize_lock_metadata`
initializes a zero-length regular file whether it was created by this invocation
or left by a process that terminated between file creation and metadata write.
It accepts only the exact complete contract object for a nonempty file. An
unrecognized nonempty file remains ambiguous and is never overwritten.

The exact UTF-8 lock metadata object is:

```python
{
    "contract_version": ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION,
    "physical_output": str(target.physical_output),
}
```

Acquire the OS lock before reading, validating, or initializing this object.
`_open_lock_file` must reject an existing non-regular path and must not follow a
symbolic link. Use `os.open` with `O_NOFOLLOW` when available; otherwise lstat
before open, fstat after open, and require the same regular-file identity before
returning the binary handle.

- [ ] **Step 7: Run Task 1 GREEN tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_publish.py -k \
  'publish_target or new_transaction or journal or publish_lock'
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --no-cache \
  src/fashion_radar/row_one/publish.py tests/test_row_one_publish.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/publish.py tests/test_row_one_publish.py
```

Expected: all selected tests and both Ruff commands pass.

## Task 2: Read-Only Live Safety, Unrelated Copying, Ownership, And Stage Validation

**Owner:** Worker A

**Files:**

- Modify: `src/fashion_radar/row_one/publish.py`
- Modify: `tests/test_row_one_publish.py`

- [ ] **Step 1: Write RED live-target safety tests**

Add tests proving:

```python
def test_live_preflight_rejects_unmarked_generated_children_without_mutation(
    tmp_path: Path,
) -> None:
    output = tmp_path / "site"
    generated = output / "assets" / "manual.css"
    generated.parent.mkdir(parents=True)
    generated.write_text("manual", encoding="utf-8")

    with pytest.raises(RowOnePublishError, match="not marked"):
        _validate_live_publish_target(_resolve_publish_target(output))

    assert generated.read_text(encoding="utf-8") == "manual"


def test_live_preflight_allows_unmarked_unrelated_only_directory(tmp_path: Path) -> None:
    output = tmp_path / "site"
    output.mkdir()
    keep = output / "keep.txt"
    keep.write_text("keep", encoding="utf-8")

    _validate_live_publish_target(_resolve_publish_target(output))

    assert keep.read_text(encoding="utf-8") == "keep"
```

The publisher and renderer must share one read-only helper for the exact
`GENERATED_CHILDREN` contract. To avoid a circular import, move the tuple and
read-only check to `publish.py`; import them into `render.py` when Task 4
integrates cleanup.

- [ ] **Step 2: Write RED unrelated-copy and owner tests**

Create regular file, nested directory, and relative symlink fixtures. Require
staging to preserve content and the symlink's raw target. Add FIFO coverage
behind `hasattr(os, "mkfifo")` and require rejection before any live rename.
Place a FIFO inside a nested unrelated directory as a separate case so recursive
copy cannot enter `shutil.copytree` before the entire unrelated tree passes a
no-follow lstat pre-scan. Add an owner-path symlink/non-regular-file case and
require validation to fail without following it.

```python
def test_copy_unrelated_children_preserves_file_directory_and_symlink(tmp_path: Path) -> None:
    output = tmp_path / "site"
    stage = tmp_path / "stage"
    output.mkdir()
    stage.mkdir()
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old", encoding="utf-8")
    (output / "keep.txt").write_text("keep", encoding="utf-8")
    (output / "notes").mkdir()
    (output / "notes" / "daily.txt").write_text("daily", encoding="utf-8")
    (output / "latest-note").symlink_to("notes/daily.txt")

    _copy_unrelated_children(output, stage)

    assert (stage / "keep.txt").read_text(encoding="utf-8") == "keep"
    assert (stage / "notes" / "daily.txt").read_text(encoding="utf-8") == "daily"
    assert (stage / "latest-note").is_symlink()
    assert os.readlink(stage / "latest-note") == "notes/daily.txt"
    assert not (stage / "index.html").exists()
    assert not (stage / ".row-one-site").exists()
```

- [ ] **Step 3: Implement read-only safety and copy-by-file-type**

Use `Path.lstat()` and `stat.S_ISREG`, `S_ISDIR`, and `S_ISLNK`. Recreate
symlinks with `os.readlink` plus `os.symlink`; never call `resolve` on an
unrelated child. Use `shutil.copy2(..., follow_symlinks=False)` for regular
files, `shutil.copytree(..., symlinks=True, copy_function=shutil.copy2)` for
directories. Raise `RowOnePublishError` naming only the unsupported path and
type for special files.

Before any copy, recursively validate the complete unrelated tree with
`os.scandir` plus `entry.stat(follow_symlinks=False)`. Recurse only into actual
directories, accept symbolic links without opening their targets, and reject
every non-regular/non-directory/non-symlink entry.

Implement `_apply_live_root_metadata` separately with
`shutil.copystat(live, stage, follow_symlinks=False)` when
`transaction.had_live_output` is true and as a no-op for first publish. It is
called only after the renderer and staged validator finish, so a restrictive
prior root mode cannot make staging unwritable and generated top-level writes
cannot change the restored mtime afterward. Add a full successful-publication
test that fixes the old live root mode and nanosecond mtime, has the render
callback create new top-level children, and requires the final physical live
directory to preserve both values where the platform supports `copystat`. A
staging-only assertion is not sufficient.

- [ ] **Step 4: Write RED stage-validation tests**

Add tests for missing owner marker, mismatched token, missing public marker,
malformed edition/manifest/runtime JSON, staged result path mismatch, and an
`OSError` from the integrity validator. Use a small `FakeStagedResult` dataclass
with `output_dir` and `index_path`.

Patch only the integrity validator for focused unit tests; Task 4 must exercise
the real validator with a real rendered site.

```python
def test_validate_staged_site_reads_edition_from_disk(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _owned_stage_fixture(tmp_path)
    expected = {"contract_version": "row-one-app/v7", "stories": []}
    _write_minimal_staged_files(transaction.stage_path, edition=expected)
    captured: dict[str, object] = {}

    def capture(*, site_dir: Path, edition: dict[str, object]) -> object:
        captured["site_dir"] = site_dir
        captured["edition"] = edition
        return object()

    monkeypatch.setattr(publish_module, "validate_row_one_generated_site_integrity", capture)
    result = FakeStagedResult(
        output_dir=transaction.stage_path,
        index_path=transaction.stage_path / "index.html",
    )

    _validate_staged_row_one_site(transaction, result)

    assert captured == {"site_dir": transaction.stage_path, "edition": expected}
```

- [ ] **Step 5: Implement disk-backed staged validation**

Implement `_read_json_object`, `_read_owner_token`, and:

The private owner file uses this exact object and rejects missing or extra keys:

```python
{
    "contract_version": ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION,
    "physical_output": str(transaction.target.physical_output),
    "token": transaction.token,
}
```

```python
def _validate_staged_row_one_site(
    transaction: RowOnePublishTransaction,
    result: StagedRowOneRenderResult,
) -> None:
    stage = transaction.stage_path
    if result.output_dir != stage or result.index_path != stage / "index.html":
        raise RowOnePublishError("ROW ONE staged render returned unexpected paths")
    validate_row_one_site_dir(stage)
    if _read_owner_token(stage) != transaction.token:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE stage owner token mismatch: {stage}"
        )
    edition = _read_json_object(stage / "data" / "edition.json", label="edition")
    _read_json_object(stage / "data" / "manifest.json", label="manifest")
    _read_json_object(stage / "data" / "runtime.json", label="runtime")
    validate_row_one_generated_site_integrity(site_dir=stage, edition=edition)
```

`validate_row_one_site_dir` supplies the explicit public marker and index check.
Do not substitute an in-memory app payload.

- [ ] **Step 6: Run Task 2 GREEN tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_publish.py -k \
  'live_preflight or unrelated or owner or validate_staged'
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --no-cache \
  src/fashion_radar/row_one/publish.py tests/test_row_one_publish.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/publish.py tests/test_row_one_publish.py
```

Expected: all selected tests and Ruff checks pass.

## Task 3: Commit, Rollback, Recovery, Cleanup, And Publisher Orchestration

**Owner:** Worker A

**Files:**

- Modify: `src/fashion_radar/row_one/publish.py`
- Modify: `tests/test_row_one_publish.py`

- [ ] **Step 1: Add focused filesystem-operation injection points**

Declare these helpers so tests can distinguish each transition without patching
global `os.replace` or `Path.rename`:

```python
def _move_publish_path(source: Path, destination: Path) -> None:
    os.replace(source, destination)


def _remove_publish_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE publish path has unsupported file type: {path}"
        )


def _replace_phase(
    transaction: RowOnePublishTransaction,
    phase: RowOnePublishPhase,
) -> RowOnePublishTransaction:
    updated = replace(transaction, phase=phase)
    _write_journal(updated)
    return updated
```

- [ ] **Step 2: Write RED pre-commit preservation tests**

Add exact tests for stage creation failure, render failure, validation failure,
owner-marker write failure, and first-publish move failure. Each uses a real old
index/runtime fixture and asserts bytes are unchanged. A handled owner write
failure must remove the exclusively created, still-empty stage and let outer
cleanup remove the journal; an injected failure removing that stage must raise
cleanup-pending and retain its paths. The render failure test must inject at the
render callback, not at journal code:

```python
def test_prerender_failure_preserves_live_and_cleans_owned_stage(tmp_path: Path) -> None:
    output = _valid_old_site_fixture(tmp_path / "site")
    old_index = (output / "index.html").read_bytes()
    old_runtime = (output / "data" / "runtime.json").read_bytes()

    def fail_render(stage: Path) -> FakeStagedResult:
        raise OSError("injected render failure")

    with pytest.raises(
        RowOnePublishError,
        match="staged publish failed before commit",
    ) as error:
        publish_latest_row_one_site(output, render=fail_render)

    assert (output / "index.html").read_bytes() == old_index
    assert (output / "data" / "runtime.json").read_bytes() == old_runtime
    assert isinstance(error.value.__cause__, OSError)
    assert "row-one-stage" not in str(error.value)
    _assert_no_transaction_debris(output)
```

- [ ] **Step 3: Write RED rename, rollback, and cleanup tests**

Add tests that inject `_move_publish_path` failures by call index:

- call 1 (`live -> backup`) fails: old live stays;
- call 2 (`stage -> live`) fails: call 3 restores backup;
- post-move validation fails: new live moves back to stage, then backup restores;
- first-publish validation with a missing, non-regular, or mismatched live owner
  preserves live and journal, performs no rollback rename, and raises ambiguous
  state with every retained recovery path;
- rollback move fails: journal, backup, and owned paths remain and the raised
  `RowOnePublishRollbackError` names each path;
- cleanup after `PUBLISHED` fails: valid new live remains and
  `RowOnePublishCleanupPendingError` is raised.
- handled cleanup with an unsafe temporary-journal symlink or FIFO preserves
  the owned stage, owner, canonical journal, and unsafe object;
- published cleanup with an unsafe backup object or temporary journal preserves
  the live owner, backup, canonical journal, and every temporary object because
  all artifacts are preflighted before the first deletion.
- `KeyboardInterrupt` during the first live rename is re-raised unchanged,
  leaves the `live_moving` journal for recovery, and does not attempt a phase
  rollback that could demote the control-flow exception.

Also inject `_write_journal` failure separately while writing
`live_backed_up` and `published`. Existing-publish cases must restore the old
index/runtime in the same invocation. The first-publish `published` write case
must move the new live back to its owned stage, remove the owned stage and
journal through handled cleanup, and leave no live output. No test may rely on
a later invocation to repair a handled journal-write failure.

Use a call-recording function:

```python
moves: list[tuple[Path, Path]] = []

def fail_second_move(source: Path, destination: Path) -> None:
    moves.append((source, destination))
    if len(moves) == 2:
        raise OSError("injected stage move failure")
    os.replace(source, destination)
```

- [ ] **Step 4: Implement first and existing publish commit paths**

Implement `_commit_first_publish` and `_commit_existing_publish` with the exact
phase order in the design. The existing path must use:

```python
def _validate_published_row_one_site(
    transaction: RowOnePublishTransaction,
    *,
    require_owner: bool = True,
) -> None:
    live = transaction.target.physical_output
    validate_row_one_site_dir(live)
    owner_path = live / ROW_ONE_PUBLISH_OWNER_PATH
    try:
        owner_mode = owner_path.lstat().st_mode
    except FileNotFoundError:
        owner_mode = None
    if owner_mode is not None and not stat.S_ISREG(owner_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published owner path is not a regular file: {owner_path}"
        )
    if owner_mode is not None and _read_owner_token(live) != transaction.token:
        raise RowOnePublishAmbiguousStateError(f"ROW ONE published owner token mismatch: {live}")
    if require_owner and owner_mode is None:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published owner marker is missing: {owner_path}"
        )
    edition = _read_json_object(live / "data" / "edition.json", label="edition")
    _read_json_object(live / "data" / "manifest.json", label="manifest")
    _read_json_object(live / "data" / "runtime.json", label="runtime")
    validate_row_one_generated_site_integrity(site_dir=live, edition=edition)


def _commit_publish(
    transaction: RowOnePublishTransaction,
) -> RowOnePublishTransaction:
    if transaction.had_live_output:
        return _commit_existing_publish(transaction)
    return _commit_first_publish(transaction)
```

The existing path must keep every post-backup operation inside the rollback
boundary, including both phase writes:

```python
def _commit_existing_publish(
    transaction: RowOnePublishTransaction,
) -> RowOnePublishTransaction:
    transaction = _replace_phase(transaction, RowOnePublishPhase.LIVE_MOVING)
    try:
        _move_publish_path(
            transaction.target.physical_output,
            transaction.backup_path,
        )
    except BaseException as move_error:
        if isinstance(move_error, (KeyboardInterrupt, SystemExit)):
            raise
        try:
            transaction = _replace_phase(transaction, RowOnePublishPhase.READY)
        except BaseException as journal_error:
            raise RowOnePublishCleanupPendingError(
                "ROW ONE live move failed with journal cleanup pending; "
                f"live={transaction.target.physical_output}; "
                f"stage={transaction.stage_path}; "
                f"journal={transaction.target.journal_path}"
            ) from journal_error
        _cleanup_after_handled_failure(transaction)
        raise RowOnePublishPreservedError(
            "ROW ONE could not move the live site; the previous site remains available"
        ) from move_error

    try:
        transaction = _replace_phase(
            transaction,
            RowOnePublishPhase.LIVE_BACKED_UP,
        )
        _move_publish_path(
            transaction.stage_path,
            transaction.target.physical_output,
        )
        _validate_published_row_one_site(transaction)
        transaction = _replace_phase(
            transaction,
            RowOnePublishPhase.PUBLISHED,
        )
    except BaseException as publish_error:
        _rollback_existing_publish(transaction, publish_error)
    return transaction
```

This means a failed `live_backed_up` write and a failed `published` write are
handled failures that restore the previous live site immediately; they are not
deferred to the next invocation.

The first-publish branch uses one publish rename and moves a token-owned new
live back to staging when either validation or the `published` write fails:

```python
def _commit_first_publish(
    transaction: RowOnePublishTransaction,
) -> RowOnePublishTransaction:
    live = transaction.target.physical_output
    _move_publish_path(transaction.stage_path, live)
    try:
        _validate_published_row_one_site(transaction)
        return _replace_phase(transaction, RowOnePublishPhase.PUBLISHED)
    except BaseException as publish_error:
        if not _is_owned_live(transaction):
            raise RowOnePublishAmbiguousStateError(
                "ROW ONE first publish failed after live ownership changed; "
                f"live={live}; stage={transaction.stage_path}; "
                f"journal={transaction.target.journal_path}"
            ) from publish_error
        try:
            _move_publish_path(live, transaction.stage_path)
        except BaseException as rollback_error:
            raise RowOnePublishRollbackError(
                f"ROW ONE first publish validation and rollback failed; "
                f"live={live}; stage={transaction.stage_path}; "
                f"journal={transaction.target.journal_path}"
            ) from rollback_error
        _cleanup_after_handled_failure(transaction)
        if isinstance(publish_error, (KeyboardInterrupt, SystemExit)):
            raise
        raise RowOnePublishRestoredError(
            "ROW ONE first publish failed; no site was published"
        ) from publish_error
```

`_is_owned_live` returns true only for a directory whose owner path is a
no-follow regular file with the matching token and physical output. A missing
live or owner returns false; a non-regular, malformed, or mismatched owner raises
`RowOnePublishAmbiguousStateError`. Therefore an ownership-validation failure
never triggers a rename or cleanup.

`_rollback_existing_publish` moves a token-owned new live back to the owned stage
when present, restores backup to live, verifies the restored pre-publish marker
and index facts, removes the token-owned stage and canonical journal after a
successful restore, and re-raises `KeyboardInterrupt`/`SystemExit` unchanged or
a concise `RowOnePublishRestoredError` chained from an ordinary original error. The
concise message states that the previous site was restored and does not expose
the stage token or physical recovery paths. If any rollback step fails, it
removes nothing further and raises `RowOnePublishRollbackError` with all
retained paths. Catch `BaseException` so a handled `KeyboardInterrupt` also
attempts rollback; `SIGKILL` remains a recovery case.

Before its first rollback move, the helper validates the canonical journal,
backup directory, complete temporary-journal set, and any new live owner as one
read-only preflight. It calls `_is_owned_live` before moving a present new live;
a missing, malformed, non-regular, or mismatched owner raises ambiguous state
and preserves live, backup, stage, journal, and temporary paths. Before deleting
owned rollback debris after restoration, it preflights that full cleanup set;
the canonical journal is removed last.

- [ ] **Step 5: Write RED recovery-matrix tests**

Parameterize every phase and physical state from the design recovery table.
Required named cases:

```text
test_recovery_keeps_old_live_before_backup_move
test_recovery_keeps_old_live_when_live_moving_rename_failed
test_recovery_restores_backup_when_live_is_missing
test_recovery_prefers_backup_before_published_phase
test_recovery_keeps_valid_first_publish_without_backup
test_recovery_keeps_valid_published_live_and_cleans_backup
test_recovery_keeps_published_live_after_owner_was_removed_before_cleanup
test_recovery_restores_backup_when_published_live_is_invalid
test_recovery_restores_unrelated_only_directory_without_site_validation
test_recovery_allows_marker_only_output_to_be_repaired
test_recovery_preserves_and_rejects_index_only_unmarked_output
test_recovery_rejects_unowned_or_unsafe_paths_without_deletion
```

The `live_moving` rename-failed case must seed the old live in place, no backup,
an owned stage, and a `live_moving` journal. Recovery keeps and validates the old
live, then removes only the owned stage, same-token temporary journals, and
canonical journal.

The unrelated-only case must create `keep.txt`, set all prior site facts false,
interrupt after backup creation, recover, and assert the restored directory is
not forced through ROW ONE site validation.

The marker-only case must recover, pass the ordinary read-only target check,
and proceed into a new staged render. The index-only case must recover the index
byte-for-byte, then fail the ordinary unmarked-generated-target check before a
new transaction or staging directory is created. Recovery must not add a marker
or use a one-time bypass.

The owner-removed published case must set phase `published`, keep a valid new
live plus backup and journal, remove only `data/.row-one-publish-owner.json`, and
require recovery to validate with `require_owner=False`, keep the new live, and
clean backup and journal. Earlier phases never relax owner validation.

- [ ] **Step 6: Implement old-version-first recovery**

Implement `_recover_interrupted_publish(target)` as a pure phase/state dispatcher
over a validated journal. It must run under the lock, call temporary-journal
recovery first, reject unknown sibling artifacts, and use these invariants:

```python
if transaction.phase is not RowOnePublishPhase.PUBLISHED and backup.exists():
    _restore_previous_output(transaction)
elif transaction.phase is RowOnePublishPhase.PUBLISHED:
    _finish_published_recovery(transaction)
elif not transaction.had_live_output and _is_owned_live(transaction):
    _finish_valid_first_publish_recovery(transaction)
else:
    _clean_precommit_stage_after_preserving_old_output(transaction)
```

Each branch verifies actual path state and ownership before moving or deleting.
Ambiguous combinations raise and preserve every path.

- [ ] **Step 7: Implement high-level orchestration and bounded cleanup**

Implement the orchestration helpers before the public function:

```python
def _begin_staging(
    transaction: RowOnePublishTransaction,
) -> RowOnePublishTransaction:
    _write_journal(transaction)
    transaction.stage_path.mkdir(parents=False, exist_ok=False)
    try:
        _write_owner_file(transaction.stage_path, transaction)
    except BaseException:
        try:
            _remove_publish_path(transaction.stage_path)
        except BaseException as cleanup_error:
            raise RowOnePublishCleanupPendingError(
                "ROW ONE stage owner write failed with cleanup pending; "
                f"stage={transaction.stage_path}; "
                f"journal={transaction.target.journal_path}"
            ) from cleanup_error
        raise
    return transaction


def _copy_unrelated_children_if_present(
    transaction: RowOnePublishTransaction,
) -> None:
    live = transaction.target.physical_output
    if live.is_dir():
        _copy_unrelated_children(live, transaction.stage_path)


```

Implement `_preflight_cleanup_artifacts(transaction, *, published)` as one
complete read-only pass. Before either cleanup function mutates anything, it
must:

- require the canonical journal to be a regular file equal to `transaction`;
- require phase `published` exactly when `published=True`, otherwise require
  only `staging` or `ready`;
- enumerate the complete matching temporary-journal set with no-follow metadata
  and require every candidate to be a regular, fully parsed same-token journal;
- reject every extra matching stage/backup sibling not named by the journal;
- for handled cleanup, require an existing stage to be a directory with the
  matching regular owner marker, require backup to be absent, and reject a
  token-owned live path as cleanup-pending rather than deleting its journal;
- for published cleanup, require a complete valid live site, accept only a
  missing or matching regular owner marker, require stage to be absent, and
  require any backup to be the exact journal-owned directory;
- raise ambiguous or cleanup-pending before the first mutation when any check
  fails.

After defining that preflight, implement cleanup as:

```python


def _cleanup_after_handled_failure(
    transaction: RowOnePublishTransaction,
) -> None:
    if _load_journal(transaction.target) is None:
        _reject_unowned_publish_artifacts(transaction.target)
        return
    _preflight_cleanup_artifacts(transaction, published=False)
    try:
        stage_mode = transaction.stage_path.lstat().st_mode
    except FileNotFoundError:
        stage_mode = None
    if stage_mode is not None:
        if not stat.S_ISDIR(stage_mode):
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE owned stage path is unsafe: {transaction.stage_path}"
            )
        if _read_owner_token(transaction.stage_path) != transaction.token:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE stage owner token mismatch: {transaction.stage_path}"
            )
        _remove_publish_path(transaction.stage_path)
    _remove_matching_temporary_journals(transaction)
    transaction.target.journal_path.unlink()


def _remove_owner_file_if_present(
    transaction: RowOnePublishTransaction,
) -> None:
    owner_path = transaction.target.physical_output / ROW_ONE_PUBLISH_OWNER_PATH
    try:
        owner_mode = owner_path.lstat().st_mode
    except FileNotFoundError:
        return
    if not stat.S_ISREG(owner_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published owner path is unsafe: {owner_path}"
        )
    if _read_owner_token(transaction.target.physical_output) != transaction.token:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published owner token mismatch: {owner_path}"
        )
    owner_path.unlink()


def _cleanup_after_published(transaction: RowOnePublishTransaction) -> None:
    live = transaction.target.physical_output
    try:
        _preflight_cleanup_artifacts(transaction, published=True)
        _remove_owner_file_if_present(transaction)
        _remove_owned_backup_if_present(transaction)
        _remove_matching_temporary_journals(transaction)
        transaction.target.journal_path.unlink()
    except OSError as exc:
        raise RowOnePublishCleanupPendingError(
            f"ROW ONE publish committed with cleanup pending; live={live}; "
            f"backup={transaction.backup_path}; "
            f"journal={transaction.target.journal_path}; "
            f"stage={transaction.stage_path}"
        ) from exc
```

`_remove_owned_backup_if_present` validates the canonical journal token and
exact backup path before removal. `_cleanup_after_handled_failure` must not erase
a rollback error, ambiguous state, committed state, unowned stage path, or
token-owned live path. Every owner, journal, and temporary-journal deletion is
preceded by no-follow regular-file validation; unknown objects are preserved.

Implement `publish_latest_row_one_site` in this exact order:

```python
def publish_latest_row_one_site(
    output_dir: Path,
    *,
    render: Callable[[Path], RenderResultT],
) -> RenderResultT:
    target = _resolve_publish_target(output_dir)
    target.physical_output.parent.mkdir(parents=True, exist_ok=True)
    with _acquire_publish_lock(target):
        _recover_interrupted_publish(target)
        _reject_unowned_publish_artifacts(target)
        _validate_live_publish_target(target)
        transaction = _new_transaction(target)
        commit_started = False
        try:
            transaction = _begin_staging(transaction)
            _copy_unrelated_children_if_present(transaction)
            result = render(transaction.stage_path)
            _validate_staged_row_one_site(transaction, result)
            _apply_live_root_metadata(transaction)
            transaction = _replace_phase(transaction, RowOnePublishPhase.READY)
            commit_started = True
            transaction = _commit_publish(transaction)
        except (
            RowOnePublishAmbiguousStateError,
            RowOnePublishRollbackError,
            RowOnePublishCleanupPendingError,
            RowOnePublishPreservedError,
            RowOnePublishRestoredError,
        ):
            raise
        except (KeyboardInterrupt, SystemExit):
            if not commit_started:
                _cleanup_after_handled_failure(transaction)
            raise
        except BaseException as publish_error:
            _cleanup_after_handled_failure(transaction)
            raise RowOnePublishError(
                "ROW ONE staged publish failed before commit; "
                "the live site was preserved"
            ) from publish_error
        _cleanup_after_published(transaction)
        return result
```

The helper cleanup functions must inspect the current journal phase before
deleting. Only intentional path-bearing recovery errors and the already
sanitized successful-rollback error bypass ordinary wrapping. A base
`RowOnePublishError` from copy, render, or validation is still wrapped, so an
untrusted callback cannot smuggle stage or physical paths into ordinary CLI
output. A rollback failure, ambiguous state, or cleanup-pending state is never
erased by the outer exception handler.

- [ ] **Step 8: Run all publisher tests and module quality gates**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_publish.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --no-cache \
  src/fashion_radar/row_one/publish.py tests/test_row_one_publish.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/publish.py tests/test_row_one_publish.py
```

Expected: all tests and quality checks pass with no transaction debris under
pytest temporary directories after handled success/failure cases.

- [ ] **Step 9: Commit the publisher core**

Worker A reports its changed files and checks without staging or committing.
After coordinator reconciliation and while no other worker has staged content,
the coordinator runs:

```bash
git add src/fashion_radar/row_one/publish.py tests/test_row_one_publish.py
git commit -m "feat: add recoverable ROW ONE publisher"
```

## Task 4: Integrate Latest-Only Publishing With The Renderer

**Owner:** Coordinator

**Files:**

- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Write RED real-render failure-preservation test**

Extend the latest-only tests with a valid old generated site plus `keep.txt`,
patch `fashion_radar.row_one.render._write_assets` to raise, and call the public
renderer. Import `RowOnePublishError` from `fashion_radar.row_one.publish` for
the public failure contract:

```python
def test_render_row_one_site_latest_only_failure_preserves_published_site(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_result = render_row_one_site(_edition(), tmp_path)
    old_index = old_result.index_path.read_bytes()
    old_runtime = (tmp_path / "data" / "runtime.json").read_bytes()
    keep = tmp_path / "keep.txt"
    keep.write_text("keep", encoding="utf-8")

    def fail_assets(output_dir: Path) -> None:
        raise OSError("injected asset failure")

    monkeypatch.setattr("fashion_radar.row_one.render._write_assets", fail_assets)

    with pytest.raises(
        RowOnePublishError,
        match="staged publish failed before commit",
    ) as error:
        render_row_one_site(_edition(), tmp_path, latest_only=True)

    assert (tmp_path / "index.html").read_bytes() == old_index
    assert (tmp_path / "data" / "runtime.json").read_bytes() == old_runtime
    assert keep.read_text(encoding="utf-8") == "keep"
    assert isinstance(error.value.__cause__, OSError)
    assert "row-one-stage" not in str(error.value)
```

Run it and expect old `index.html` to be missing under current behavior.

- [ ] **Step 2: Mechanically extract the in-place renderer**

Rename the current write body to:

```python
def _render_row_one_site_in_place(
    edition: RowOneEdition,
    output_dir: Path,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneRenderResult:
```

Move current lines that create the output directory, marker, assets, payloads,
pages, JSON, sidecars, and result into that helper unchanged. Remove only the
current `latest_only` cleanup branch from the helper. Keep route validation in
the public dispatcher so it runs before any transaction artifact is created.

- [ ] **Step 3: Add the public latest-only dispatcher and result rebasing**

Import `GENERATED_CHILDREN`, the shared read-only target check used by cleanup,
and `publish_latest_row_one_site` from `row_one.publish`. Replace the public
function with:

```python
def render_row_one_site(
    edition: RowOneEdition,
    output_dir: Path,
    *,
    latest_only: bool = False,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle] | None = None,
) -> RowOneRenderResult:
    _validate_unique_story_routes(edition)
    articles = local_articles_by_story_id or {}
    if not latest_only:
        return _render_row_one_site_in_place(
            edition,
            output_dir,
            local_articles_by_story_id=articles,
        )

    staged_result = publish_latest_row_one_site(
        output_dir,
        render=lambda stage: _render_row_one_site_in_place(
            edition,
            stage,
            local_articles_by_story_id=articles,
        ),
    )
    return RowOneRenderResult(
        output_dir=output_dir,
        index_path=output_dir / "index.html",
        story_count=staged_result.story_count,
        edition=staged_result.edition,
        local_article_metrics=staged_result.local_article_metrics,
    )
```

Update `clean_row_one_site_children` to call the shared read-only marker safety
helper and then retain its existing deletion loop. Do not route non-latest
rendering through the publisher. Add a succinct docstring stating that this
mutating function remains a public explicit-cleanup utility for callers even
though the staged publisher does not invoke it.

- [ ] **Step 4: Strengthen real integration tests**

Update or add tests proving:

- latest-only success replaces all six generated children;
- unrelated regular files/directories/symlinks survive;
- the final physical live directory preserves the prior root mode and
  nanosecond mtime after real renderer writes;
- result paths remain the logical symlink path when output is a symlink;
- no owner marker, stage, backup, journal, or temp journal survives success;
- the stable lock file may exist beside physical output;
- the real `validate_row_one_generated_site_integrity` accepts the staged site;
- `latest_only=False` does not call `publish_latest_row_one_site`;
- an unmarked generated target fails before `_write_assets` runs.

- [ ] **Step 5: Add workflow and CLI fault propagation tests**

In `tests/test_workflows.py`, seed a valid old site, inject a render failure into
`write_row_one_site_files(..., latest_only=True)`, and require the old site to
remain. In `tests/test_row_one_cli.py`, require build, preview, and refresh to
return nonzero and print their existing exact prefixes `ROW ONE build failed:`,
`ROW ONE preview failed:`, and `ROW ONE refresh failed:` when the publisher
raises. For each command, inject an underlying exception whose message contains
the actual tokenized stage path, physical target, and token. Assert the CLI
output contains the exact command prefix and concise preserved/failed wording,
but contains none of the stage basename, token, physical target, or underlying
message. Then inject `RowOnePublishRollbackError` and
`RowOnePublishAmbiguousStateError` and assert their explicit retained recovery
paths remain visible. This verifies that ordinary failures are wrapped by the
publisher while recovery errors are not sanitized. Successful commands continue
printing logical output paths.

Update the build and preview `--latest-only` help text in
`src/fashion_radar/cli.py` so it describes a staged, validated replacement that
preserves unrelated top-level children. Remove any help wording that says the
command deletes the current generated site before rendering.

- [ ] **Step 6: Run focused integration tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_publish.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_cli.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --no-cache \
  src/fashion_radar/row_one/publish.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/cli.py \
  tests/test_row_one_publish.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_cli.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/publish.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/cli.py \
  tests/test_row_one_publish.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_cli.py
```

Expected: all focused tests and quality checks pass.

- [ ] **Step 7: Commit renderer integration**

```bash
git add \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/cli.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_cli.py
git commit -m "fix: publish latest ROW ONE site recoverably"
```

## Task 5A: Harden First-Run Smoke And Package Archives

**Owner:** Worker B

**Files:**

- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Write RED debris-rejection tests**

Add one fixture case for each forbidden sibling after successful first-run:

```text
.site.row-one-publish.json
.site.row-one-stage-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
.site.row-one-backup-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
.site.row-one-publish.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.nonce.tmp
```

Add a separate fixture for the forbidden private live-site owner marker:

```text
site/data/.row-one-publish-owner.json
```

The existing stable `.site.row-one-publish.lock` must be accepted. Failure
messages name only the unexpected path.

- [ ] **Step 2: Run the focused smoke tests and verify RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_first_run_smoke.py -k 'row_one and publish'
```

Expected: the new debris fixtures are not rejected yet.

- [ ] **Step 3: Add a bounded sibling-debris validator**

After successful ROW ONE refresh validation, inspect only the output's direct
parent and only names derived from the exact physical output basename. Permit
the stable lock name; reject canonical journal, stage prefix, backup prefix, and
temporary journal prefix. Separately inspect only the exact
`output/data/.row-one-publish-owner.json` path and reject it when present. Do
not recursively scan any other output or unrelated directory and do not delete
anything.

- [ ] **Step 4: Run first-run smoke tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_first_run_smoke.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --no-cache \
  scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
```

Expected: all first-run smoke tests and quality checks pass.

- [ ] **Step 5: Write RED wheel and sdist membership tests**

Extend archive fixtures so one wheel omits
`fashion_radar/row_one/publish.py` and one sdist omits
`src/fashion_radar/row_one/publish.py`. Require the validator to name the exact
missing member for each archive type.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_package_archives.py -k 'publish or required_paths'
```

Expected: RED because the required member sets do not include the new module.

- [ ] **Step 6: Require the publisher module in both archive formats**

Add these exact required paths to the existing wheel and sdist sets:

```python
"fashion_radar/row_one/publish.py"
"src/fashion_radar/row_one/publish.py"
```

Keep each path in the correct archive-specific set; do not allow either format
to satisfy the other format's path.

- [ ] **Step 7: Run all first-run and archive checks**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_first_run_smoke.py tests/test_package_archives.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --no-cache \
  scripts/check_first_run_smoke.py scripts/check_package_archives.py \
  tests/test_first_run_smoke.py tests/test_package_archives.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  scripts/check_first_run_smoke.py scripts/check_package_archives.py \
  tests/test_first_run_smoke.py tests/test_package_archives.py
```

Expected: all checks pass.

## Task 5B: Document Recoverable Publication And Its Limits

**Owner:** Worker C

**Files:**

- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/first-run.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_first_run_docs.py`
- Modify: `tests/test_cli_docs.py`
- Modify: `tests/test_architecture_boundary_docs.py`

- [ ] **Step 1: Write RED documentation contract tests**

Require the current public documentation to state all of these normalized
phrases in the appropriate ROW ONE refresh/architecture sections:

```text
renders and validates a same-filesystem staging site before changing the live output
restores the previous output after a handled publish failure
recovers an interrupted owned transaction before the next latest-only render
preserves unrelated top-level output children
keeps the public output path and generated URLs unchanged
does not claim zero-downtime publication or power-loss durability
the stable sibling lock file may remain after a successful refresh
```

Also require the Unreleased changelog to name Stage 391 and explicitly deny
schema, dependency, source, collection, scoring, translation, and remote-worker
changes.

- [ ] **Step 2: Run documentation tests and verify RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_docs.py tests/test_first_run_docs.py \
  tests/test_cli_docs.py tests/test_architecture_boundary_docs.py
```

Expected: failures because current docs describe delete-and-rebuild latest-only
cleanup and do not describe staged publication.

- [ ] **Step 3: Update public documentation without rewriting history**

Add current Stage 391 behavior to README, `docs/row-one.md`, `docs/first-run.md`,
`docs/cli-reference.md`, architecture, and Unreleased changelog. Align CLI docs
with the revised `--latest-only` help text. Do not edit historical Stage 329,
330, 389, or 390 specs and review records. Keep terminology exact:
`failure-safe recoverable publish`, not `fully atomic`, `zero downtime`, or
`transactional power-loss durability`.

- [ ] **Step 4: Run documentation GREEN tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_docs.py \
  tests/test_first_run_docs.py \
  tests/test_cli_docs.py \
  tests/test_architecture_boundary_docs.py \
  tests/test_review_protocol_docs.py
```

Expected: all documentation tests pass, including existing roadmap/review
phrases.

## Task 6: Integrate Workers, Verify, Review, Commit, And Publish

**Owner:** Coordinator

**Files:** All Stage 391 files and review records

- [ ] **Step 1: Reconcile every worker before closing it**

For each worker, record changed files, exact tests and results, unresolved work,
partial writes, and whether its worktree is clean outside owned files. Review
the actual integrated diff. Do not rely on worker summaries as final evidence.

- [ ] **Step 2: Run targeted integrated verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q -p no:cacheprovider \
  tests/test_row_one_publish.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_cli.py \
  tests/test_first_run_smoke.py \
  tests/test_package_archives.py \
  tests/test_row_one_docs.py \
  tests/test_first_run_docs.py \
  tests/test_cli_docs.py \
  tests/test_architecture_boundary_docs.py \
  tests/test_row_one_ops_check.py \
  tests/test_row_one_local_article_route_health.py \
  tests/test_row_one_local_article_content_health.py \
  tests/test_scheduling.py
```

Expected: all selected tests pass.

- [ ] **Step 3: Run full source-tree verification**

Define `public_uv` in the same shell so inherited mirror and project-environment
variables cannot influence public lock or verification behavior:

```bash
public_uv() {
  env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL \
    -u UV_PROJECT_ENVIRONMENT -u UV_INDEX -u UV_FIND_LINKS \
    -u PIP_INDEX_URL -u PIP_EXTRA_INDEX_URL \
    UV_NO_CONFIG=1 uv "$@"
}
public_uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then
  echo "refusing a mirror-bound public lockfile" >&2
  exit 1
else
  mirror_scan_status=$?
fi
case "$mirror_scan_status" in
  1) ;;
  *)
    echo "refusing to continue after an unreadable lockfile mirror scan" >&2
    exit "$mirror_scan_status"
    ;;
esac
unset mirror_scan_status
public_uv --no-config run --frozen pytest -q -p no:cacheprovider
public_uv --no-config run --frozen ruff check --no-cache .
public_uv --no-config run --frozen ruff format --check .
git diff --check
PYTHONDONTWRITEBYTECODE=1 public_uv --no-config run --frozen \
  python scripts/check_release_hygiene.py --repo-root .
```

Expected: the full suite, Ruff, formatting, diff, release hygiene, and public
lockfile checks pass. `uv.lock` must remain byte-for-byte unchanged.

- [ ] **Step 4: Request Claude Code max code review**

Review one stable integrated snapshot. The prompt must cover the exact Stage 391
diff, journal and lock correctness, safe paths, symlink behavior, user-file
preservation, all crash phases, rollback/cleanup, public path compatibility,
tests, docs, and non-goals. Store one coherent review body in
`docs/reviews/claude-code-stage-391-code-review.md`.

Fix every Critical and Important finding, rerun affected and full verification,
and request `claude-code-stage-391-code-rereview.md` when the reviewed diff
changes. OpenCode GLM 5.2 max is fallback only under the review protocol.

- [ ] **Step 5: Commit reviewed implementation and documentation**

After the final code review approves the exact diff, stage the implementation,
documentation, Stage 391 plan/design amendments, and whichever primary,
fallback, or rereview code-review records actually exist:

```bash
git add \
  src/fashion_radar/row_one/publish.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/cli.py \
  tests/test_row_one_publish.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_cli.py \
  scripts/check_first_run_smoke.py \
  scripts/check_package_archives.py \
  tests/test_first_run_smoke.py \
  tests/test_package_archives.py \
  README.md docs/row-one.md docs/first-run.md docs/cli-reference.md \
  docs/architecture.md CHANGELOG.md \
  tests/test_row_one_docs.py tests/test_first_run_docs.py tests/test_cli_docs.py \
  tests/test_architecture_boundary_docs.py \
  docs/superpowers/specs/2026-07-14-stage-391-row-one-recoverable-staged-publish-design.md \
  docs/superpowers/plans/2026-07-14-stage-391-row-one-recoverable-staged-publish-plan.md
for review_path in \
  docs/reviews/claude-code-stage-391-code-review.md \
  docs/reviews/claude-code-stage-391-code-rereview.md \
  docs/reviews/opencode-stage-391-code-review.md \
  docs/reviews/opencode-stage-391-code-rereview.md
do
  if [ -e "$review_path" ]; then
    git add -- "$review_path"
  fi
done
unset review_path
staged_code_review_count="$(
  git diff --cached --name-only | \
    awk '/^docs\/reviews\/(claude-code|opencode)-stage-391-code-(review|rereview)\.md$/ {count += 1} END {print count + 0}'
)"
if [ "$staged_code_review_count" -lt 1 ]; then
  echo "refusing to commit without a Stage 391 code-review record" >&2
  exit 1
fi
unset staged_code_review_count
git diff --quiet || {
  echo "refusing to commit with unstaged implementation changes" >&2
  exit 1
}
untracked_paths="$(git ls-files --others --exclude-standard)" || {
  echo "refusing to determine untracked paths" >&2
  exit 1
}
if [ -n "$untracked_paths" ]; then
  echo "refusing to commit with untracked paths" >&2
  exit 1
fi
unset untracked_paths
git diff --cached --check
git diff --cached --quiet -- uv.lock || {
  echo "Stage 391 must not modify uv.lock" >&2
  exit 1
}
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL \
  -u UV_PROJECT_ENVIRONMENT -u UV_INDEX -u UV_FIND_LINKS \
  -u PIP_INDEX_URL -u PIP_EXTRA_INDEX_URL \
  UV_NO_CONFIG=1 uv --no-config run --frozen \
  python scripts/check_release_hygiene.py --repo-root .
git commit -m "Stage 391: publish ROW ONE site recoverably"
implementation_head="$(git rev-parse HEAD)"
test "$(git status --porcelain=v1 --untracked-files=all)" = ""
```

Keep `implementation_head` in the same protected release terminal through final
validation and publication. Do not stage unrelated files.

- [ ] **Step 6: Run clean committed-snapshot release verification**

Define these helpers in that protected terminal. `public_uv` removes every
supported inherited index/project override. The lockfile scan is fail-closed:
status `1` means no match, status `0` blocks for mirror content, and every other
status blocks because the scan was unreadable.

```bash
public_uv() {
  env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL \
    -u UV_PROJECT_ENVIRONMENT -u UV_INDEX -u UV_FIND_LINKS \
    -u PIP_INDEX_URL -u PIP_EXTRA_INDEX_URL \
    UV_NO_CONFIG=1 uv "$@"
}

require_clean_stage_391_snapshot() {
  worktree_status="$(git status --porcelain=v1 --untracked-files=all)" || {
    echo "refusing to determine Stage 391 worktree status" >&2
    exit 1
  }
  if [ -n "$worktree_status" ]; then
    echo "refusing to validate a dirty Stage 391 snapshot" >&2
    exit 1
  fi
  unset worktree_status
}

run_stage_391_release_validation() (
  set -e
  public_uv lock --check
  if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then
    echo "refusing a mirror-bound public lockfile" >&2
    exit 1
  else
    mirror_scan_status=$?
  fi
  case "$mirror_scan_status" in
    1) ;;
    *)
      echo "refusing to continue after an unreadable lockfile mirror scan" >&2
      exit "$mirror_scan_status"
      ;;
  esac
  unset mirror_scan_status

  public_uv sync --locked --dev
  public_uv sync --locked --dev --check
  public_uv --no-config run --frozen pytest -q -p no:cacheprovider
  public_uv --no-config run --frozen ruff check --no-cache .
  public_uv --no-config run --frozen ruff format --check .
  PYTHONDONTWRITEBYTECODE=1 public_uv --no-config run --frozen \
    python scripts/check_release_hygiene.py --repo-root .
  PYTHONDONTWRITEBYTECODE=1 public_uv --no-config run --frozen \
    python scripts/check_first_run_smoke.py --repo-root .
  git diff --check

  tmp_build="$(mktemp -d)"
  tmp_env="$(mktemp -d)"
  tmp_dash="$(mktemp -d)"
  tmp_units="$(mktemp -d)"
  trap 'rm -rf "$tmp_build" "$tmp_env" "$tmp_dash" "$tmp_units"' EXIT
  public_uv --no-config build --out-dir "$tmp_build"
  public_uv --no-config run --frozen \
    python scripts/check_package_archives.py "$tmp_build"
  wheel="$(find "$tmp_build" -maxdepth 1 -type f -name '*.whl' -print)"
  sdist="$(find "$tmp_build" -maxdepth 1 -type f -name '*.tar.gz' -print)"
  test -f "$wheel"
  test -f "$sdist"

  public_uv venv "$tmp_env/venv"
  public_uv pip install --python "$tmp_env/venv/bin/python" "$wheel"
  installed_cli="$tmp_env/venv/bin/fashion-radar"
  env -u PYTHONPATH "$installed_cli" --help
  env -u PYTHONPATH "$tmp_env/venv/bin/python" -m fashion_radar --help
  env -u PYTHONPATH "$installed_cli" row-one build --help
  env -u PYTHONPATH "$installed_cli" row-one preview --help
  env -u PYTHONPATH "$installed_cli" row-one refresh --help
  env -u PYTHONPATH "$installed_cli" row-one status --help
  env -u PYTHONPATH "$installed_cli" row-one ops-check --help
  env -u PYTHONPATH "$installed_cli" row-one serve --help
  env -u PYTHONPATH "$tmp_env/venv/bin/python" \
    scripts/check_first_run_smoke.py \
    --repo-root . \
    --python "$tmp_env/venv/bin/python" \
    --installed
  env -u PYTHONPATH "$tmp_env/venv/bin/python" -c \
    "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"

  env -u PYTHONPATH "$installed_cli" row-one install-local \
    --project-dir "$PWD" \
    --config-dir "$tmp_units/config" \
    --data-dir "$tmp_units/data" \
    --reports-dir "$tmp_units/reports" \
    --output-dir "$tmp_units/site" \
    --unit-dir "$tmp_units/units" \
    --force
  if command -v systemd-analyze >/dev/null 2>&1; then
    systemd-analyze --user verify \
      "$tmp_units/units/row-one-refresh.service" \
      "$tmp_units/units/row-one-refresh.timer" \
      "$tmp_units/units/row-one-serve.service"
  fi

  public_uv venv "$tmp_dash/venv"
  public_uv pip install --python "$tmp_dash/venv/bin/python" "$wheel[dashboard]"
  env -u PYTHONPATH "$tmp_dash/venv/bin/python" -c \
    "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
)

test "$(git rev-parse HEAD)" = "$implementation_head"
require_clean_stage_391_snapshot
run_stage_391_release_validation
require_clean_stage_391_snapshot
```

Use mirror-backed `UV_DEFAULT_INDEX` only for an initial frozen local install
before entering this public sequence when needed. The public sequence itself
must use `public_uv` and never write a mirror URL into `uv.lock`. The installed
first-run smoke is the executable build/preview/refresh/status/serve validation;
the explicit installed help calls include `ops-check`, and installed units are
verified where `systemd-analyze` is available.

- [ ] **Step 7: Request release review of the committed SHA**

Request Claude Code `--effort max` release review pinned to
`implementation_head`. The prompt must require inspection of committed Git
objects with `git diff "$implementation_head^" "$implementation_head"` and
`git show "$implementation_head:<path>"`, or an equivalent detached clean
worktree, and must include the complete Step 6 outcomes. Store one coherent body
in `docs/reviews/claude-code-stage-391-release-review.md`; use the matching
OpenCode GLM 5.2 max path only when the review protocol permits fallback.

Resolve every Critical and Important finding. If a finding changes shipped
implementation, tests, or docs, commit the correction together with the
CHANGES-REQUIRED review record, replace `implementation_head` with that new
commit SHA, rerun the complete Step 6 function, and request a SHA-pinned release
rereview. Never review a mutable worktree as the release snapshot.

- [ ] **Step 8: Commit only the clean release record delta**

```bash
for review_path in \
  docs/reviews/claude-code-stage-391-release-review.md \
  docs/reviews/claude-code-stage-391-release-rereview.md \
  docs/reviews/opencode-stage-391-release-review.md \
  docs/reviews/opencode-stage-391-release-rereview.md
do
  if [ -e "$review_path" ]; then
    git add -- "$review_path"
  fi
done
git add \
  docs/superpowers/specs/2026-07-14-stage-391-row-one-recoverable-staged-publish-design.md \
  docs/superpowers/plans/2026-07-14-stage-391-row-one-recoverable-staged-publish-plan.md
unset review_path
staged_release_review_count="$(
  git diff --cached --name-only | \
    awk '/^docs\/reviews\/(claude-code|opencode)-stage-391-release-(review|rereview)\.md$/ {count += 1} END {print count + 0}'
)"
if [ "$staged_release_review_count" -lt 1 ]; then
  echo "refusing to commit without a Stage 391 release-review record" >&2
  exit 1
fi
unset staged_release_review_count
git diff --quiet || {
  echo "refusing to commit a release record with unstaged changes" >&2
  exit 1
}
untracked_paths="$(git ls-files --others --exclude-standard)" || {
  echo "refusing to determine untracked paths" >&2
  exit 1
}
if [ -n "$untracked_paths" ]; then
  echo "refusing to commit a release record with untracked paths" >&2
  exit 1
fi
unset untracked_paths
git diff --cached --check
git diff --cached --quiet -- uv.lock || {
  echo "Stage 391 release records must not modify uv.lock" >&2
  exit 1
}
PYTHONDONTWRITEBYTECODE=1 public_uv --no-config run --frozen \
  python scripts/check_release_hygiene.py --repo-root .
git commit -m "Stage 391: record release review"
```

At least one release-review record must be staged; unchanged plan/design paths
add nothing. Expected: one record commit and a clean worktree.

- [ ] **Step 9: Revalidate the exact final HEAD and release-record delta**

Define and run the exact allowlist before and after repeating the complete
release function:

```bash
verify_stage_391_release_record_delta() {
  test -n "${implementation_head:-}" || {
    echo "refusing to validate without the SHA-pinned implementation head" >&2
    exit 1
  }
  git cat-file -e "$implementation_head^{commit}" || {
    echo "refusing to validate an unknown implementation head" >&2
    exit 1
  }
  git merge-base --is-ancestor "$implementation_head" HEAD || {
    echo "refusing to validate outside the reviewed implementation history" >&2
    exit 1
  }
  release_record_paths="$(git diff --name-only "$implementation_head" HEAD)" || {
    echo "refusing to determine the Stage 391 release-record delta" >&2
    exit 1
  }
  if [ -z "$release_record_paths" ]; then
    echo "refusing to validate a missing Stage 391 release-record commit" >&2
    exit 1
  fi
  while IFS= read -r release_record_path; do
    case "$release_record_path" in
      docs/reviews/claude-code-stage-391-release-*|docs/reviews/opencode-stage-391-release-*|docs/superpowers/plans/2026-07-14-stage-391-row-one-recoverable-staged-publish-plan.md|docs/superpowers/specs/2026-07-14-stage-391-row-one-recoverable-staged-publish-design.md) ;;
      *)
        echo "refusing to publish an unreviewed non-record path" >&2
        exit 1
        ;;
    esac
  done <<EOF
$release_record_paths
EOF
  unset release_record_path release_record_paths
}

require_clean_stage_391_snapshot
verify_stage_391_release_record_delta
run_stage_391_release_validation
require_clean_stage_391_snapshot
verify_stage_391_release_record_delta
release_head="$(git rev-parse HEAD)"
```

- [ ] **Step 10: Push only the verified immutable SHA**

Confirm the remote URL contains no embedded credential, fetch `origin`, verify
the local branch contains current `origin/main`, and push the reviewed final
commit to `main` without force:

```bash
(
  set -e
  require_clean_stage_391_snapshot
  test "$(git rev-parse HEAD)" = "$release_head"
  origin_url="$(git remote get-url origin)"
  case "$origin_url" in
    https://github.com/Lordakee/fashion-radar.git|git@github.com:Lordakee/fashion-radar.git) ;;
    *) echo "origin is not the authorized Fashion Radar remote" >&2; exit 1 ;;
  esac
  unset origin_url
  git fetch --no-tags origin refs/heads/main
  remote_before="$(git rev-parse FETCH_HEAD)"
  git merge-base --is-ancestor "$remote_before" "$release_head"
  git push origin "$release_head:refs/heads/main"
  remote_after_raw="$(git ls-remote --exit-code origin refs/heads/main)"
  remote_after="$(printf '%s\n' "$remote_after_raw" | awk '{print $1}')"
  test -n "$remote_after"
  test "$remote_after" = "$release_head"
)
```

Never print, persist, or commit a token, and do not publish packages or any
artifact beyond the authorized Git branch.

## Plan Self-Review Checklist

- [ ] Every approved design requirement maps to Tasks 1 through 6.
- [ ] Every function/type referenced by later tasks is defined in the fixed
  contract or an earlier task.
- [ ] Preexisting unrelated-only output is distinct from a valid old site in
  journal and recovery tests.
- [ ] Lock and atomically replaced journal use different files/inodes.
- [ ] Staged validation reads disk JSON and checks the public marker/index.
- [ ] Every destructive rename has RED failure and rollback coverage.
- [ ] Every journal phase has recovery coverage.
- [ ] Unknown paths, malformed state, and ownership mismatches delete nothing.
- [ ] Temporary journal, canonical journal, lock, and owner non-regular paths
  have no-follow tests that preserve the unexpected object.
- [ ] Final live root mode and mtime are asserted after real renderer writes.
- [ ] Ordinary CLI failures hide tokenized recovery paths while rollback,
  cleanup-pending, and ambiguous errors retain required operator paths.
- [ ] Latest-only success leaves bounded disk state and logical result paths.
- [ ] `public_uv`, the fail-closed mirror scan, immutable
  `implementation_head`, exact release-record allowlist, and complete final-HEAD
  rerun are executable rather than prose.
- [ ] Non-latest behavior, URLs, contracts, systemd paths, schemas, dependencies,
  source behavior, scoring, translation, and remote networking stay unchanged.

## Handoff Summary Contract

At the end of every development node, report only:

- repository branch, HEAD, and remote-main relationship;
- completed Claude/OpenCode review gates;
- exact verification commands with concise pass/fail outcomes;
- uncommitted or untracked files;
- next task, owner, and non-overlapping write set.

Do not paste large diffs, raw reviewer logs, credentials, private URLs, or
generated data.
