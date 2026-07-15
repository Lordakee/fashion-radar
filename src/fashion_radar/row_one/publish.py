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

from fashion_radar.row_one.server import validate_row_one_site_dir
from fashion_radar.row_one.status_integrity import validate_row_one_generated_site_integrity

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

_JOURNAL_KEYS = frozenset(
    {
        "contract_version",
        "token",
        "physical_output",
        "stage_path",
        "backup_path",
        "had_live_output",
        "had_site_marker",
        "had_index",
        "phase",
    }
)
_OWNER_KEYS = frozenset({"contract_version", "physical_output", "token"})


def _safe_directory_operations_supported() -> bool:
    return (
        all(function in os.supports_dir_fd for function in (os.open, os.stat, os.mkdir, os.unlink))
        and hasattr(os, "O_DIRECTORY")
        and hasattr(os, "O_NOFOLLOW")
    )


_SAFE_DIRECTORY_OPERATIONS_SUPPORTED = _safe_directory_operations_supported()


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


def _require_safe_directory_operations() -> None:
    if not _SAFE_DIRECTORY_OPERATIONS_SUPPORTED:
        raise RowOnePublishError("ROW ONE safe directory handles are unsupported on this platform")


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


def _resolve_publish_target(output_dir: Path) -> RowOnePublishTarget:
    logical_output = output_dir
    try:
        physical_output = output_dir.resolve(strict=False)
        try:
            output_dir.resolve(strict=True)
        except FileNotFoundError:
            pass
    except (OSError, RuntimeError) as exc:
        raise RowOnePublishError(f"ROW ONE output path cannot be resolved: {output_dir}") from exc
    if physical_output == physical_output.parent or not physical_output.name:
        raise RowOnePublishError(f"ROW ONE output cannot be a filesystem root: {logical_output}")
    if physical_output.exists() and not physical_output.is_dir():
        raise RowOnePublishError(f"ROW ONE physical output is not a directory: {physical_output}")
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


def _validate_token(token: str) -> None:
    if (
        not isinstance(token, str)
        or len(token) != 32
        or any(character not in "0123456789abcdef" for character in token)
    ):
        raise RowOnePublishError(
            "ROW ONE publish token must be 32 lowercase hexadecimal characters"
        )


def _validate_live_publish_target(target: RowOnePublishTarget) -> None:
    output = target.physical_output
    try:
        output_metadata = output.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISDIR(output_metadata.st_mode):
        raise RowOnePublishError(f"ROW ONE physical output is not a directory: {output}")

    marker_metadata: os.stat_result | None = None
    generated_child_exists = False
    for child_name in GENERATED_CHILDREN:
        child = output / child_name
        try:
            child_metadata = child.lstat()
        except FileNotFoundError:
            continue
        generated_child_exists = True
        if child_name == ".row-one-site":
            marker_metadata = child_metadata
    if generated_child_exists and (
        marker_metadata is None or not stat.S_ISREG(marker_metadata.st_mode)
    ):
        raise RowOnePublishError(f"ROW ONE output directory is not marked as generated: {output}")


def _validate_unrelated_tree(path: Path) -> None:
    try:
        root_metadata = path.lstat()
    except FileNotFoundError as exc:
        raise RowOnePublishError(
            f"ROW ONE unrelated path disappeared during validation: {path}"
        ) from exc
    if stat.S_ISREG(root_metadata.st_mode) or stat.S_ISLNK(root_metadata.st_mode):
        return
    if not stat.S_ISDIR(root_metadata.st_mode):
        raise RowOnePublishError(f"ROW ONE unrelated path is a special object: {path}")

    try:
        with os.scandir(path) as iterator:
            entries = list(iterator)
    except OSError as exc:
        raise RowOnePublishError(
            f"ROW ONE unrelated directory cannot be inspected: {path}"
        ) from exc
    for entry in entries:
        entry_path = path / entry.name
        try:
            metadata = entry.stat(follow_symlinks=False)
        except OSError as exc:
            raise RowOnePublishError(
                f"ROW ONE unrelated path changed during validation: {entry_path}"
            ) from exc
        if stat.S_ISDIR(metadata.st_mode):
            _validate_unrelated_tree(entry_path)
        elif not (stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode)):
            raise RowOnePublishError(f"ROW ONE unrelated path is a special object: {entry_path}")


def _copy_unrelated_children(source: Path, stage: Path) -> None:
    _require_directory_without_following(source, label="live output")
    _require_directory_without_following(stage, label="stage output")
    _validate_source_owner_path(source)

    try:
        with os.scandir(source) as iterator:
            entries = list(iterator)
    except OSError as exc:
        raise RowOnePublishError(f"ROW ONE live output cannot be inspected: {source}") from exc

    unrelated: list[tuple[str, int]] = []
    for entry in entries:
        if entry.name in GENERATED_CHILDREN:
            continue
        path = source / entry.name
        try:
            metadata = entry.stat(follow_symlinks=False)
        except OSError as exc:
            raise RowOnePublishError(
                f"ROW ONE unrelated path changed during validation: {path}"
            ) from exc
        mode = metadata.st_mode
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_ISLNK(mode)):
            raise RowOnePublishError(f"ROW ONE unrelated path is a special object: {path}")
        _validate_unrelated_tree(path)
        unrelated.append((entry.name, mode))

    for name, mode in unrelated:
        source_path = source / name
        destination = stage / name
        if stat.S_ISREG(mode):
            shutil.copy2(source_path, destination, follow_symlinks=False)
        elif stat.S_ISDIR(mode):
            shutil.copytree(
                source_path,
                destination,
                symlinks=True,
                copy_function=shutil.copy2,
            )
        else:
            os.symlink(os.readlink(source_path), destination)


def _require_directory_without_following(path: Path, *, label: str) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise RowOnePublishError(f"ROW ONE {label} is missing: {path}") from exc
    if not stat.S_ISDIR(metadata.st_mode):
        raise RowOnePublishError(f"ROW ONE {label} is not a directory: {path}")


def _directory_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _close_descriptor(
    descriptor: int,
    *,
    primary_error: BaseException | None,
    label: str,
    path: Path,
) -> None:
    try:
        os.close(descriptor)
    except BaseException as close_error:
        if primary_error is None:
            raise
        primary_error.add_note(
            f"ROW ONE {label} close also failed for {path}: "
            f"{type(close_error).__name__}: {close_error}"
        )


def _directory_metadata(path: Path, *, label: str) -> os.stat_result:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} is missing: {path}") from exc
    except OSError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} cannot be inspected safely: {path}"
        ) from exc
    if not stat.S_ISDIR(metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} is not an actual directory: {path}"
        )
    return metadata


@contextmanager
def _open_verified_directory(path: Path, *, label: str) -> Iterator[int]:
    if not _SAFE_DIRECTORY_OPERATIONS_SUPPORTED:
        raise RowOnePublishError("ROW ONE safe directory handles are unsupported on this platform")
    before = _directory_metadata(path, label=label)

    descriptor: int | None = None
    try:
        descriptor = os.open(path, _directory_open_flags())
        opened = os.fstat(descriptor)
        current = _directory_metadata(path, label=label)
        if (
            not stat.S_ISDIR(opened.st_mode)
            or _identity(opened) != _identity(before)
            or _identity(current) != _identity(before)
        ):
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE {label} identity changed while opening: {path}"
            )
    except OSError as exc:
        primary_error = RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} cannot be opened safely: {path}"
        )
        if descriptor is not None:
            _close_descriptor(
                descriptor,
                primary_error=primary_error,
                label=label,
                path=path,
            )
        raise primary_error from exc
    except BaseException as primary_error:
        if descriptor is not None:
            _close_descriptor(
                descriptor,
                primary_error=primary_error,
                label=label,
                path=path,
            )
        raise

    body_primary: BaseException | None = None
    try:
        yield descriptor
    except BaseException as exc:
        body_primary = exc
        raise
    finally:
        _close_descriptor(
            descriptor,
            primary_error=body_primary,
            label=label,
            path=path,
        )


def _directory_entry_metadata(
    directory_descriptor: int,
    directory: Path,
    name: str,
    *,
    label: str,
    allow_missing: bool,
) -> os.stat_result | None:
    path = directory / name
    try:
        return os.stat(name, dir_fd=directory_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        if allow_missing:
            return None
        raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} is missing: {path}") from None
    except OSError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} cannot be inspected safely: {path}"
        ) from exc


@contextmanager
def _open_verified_child_directory(
    parent_descriptor: int,
    parent: Path,
    name: str,
    *,
    label: str,
) -> Iterator[int]:
    path = parent / name
    before = _directory_entry_metadata(
        parent_descriptor,
        parent,
        name,
        label=label,
        allow_missing=False,
    )
    if before is None:
        raise AssertionError("required directory metadata unexpectedly missing")
    if not stat.S_ISDIR(before.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} is not an actual directory: {path}"
        )
    descriptor: int | None = None
    try:
        descriptor = os.open(name, _directory_open_flags(), dir_fd=parent_descriptor)
        opened = os.fstat(descriptor)
        current = _directory_entry_metadata(
            parent_descriptor,
            parent,
            name,
            label=label,
            allow_missing=False,
        )
        if current is None:
            raise AssertionError("required directory metadata unexpectedly missing")
        if (
            not stat.S_ISDIR(opened.st_mode)
            or _identity(opened) != _identity(before)
            or _identity(current) != _identity(before)
        ):
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE {label} identity changed while opening: {path}"
            )
    except OSError as exc:
        primary_error = RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} cannot be opened safely: {path}"
        )
        if descriptor is not None:
            _close_descriptor(
                descriptor,
                primary_error=primary_error,
                label=label,
                path=path,
            )
        raise primary_error from exc
    except BaseException as primary_error:
        if descriptor is not None:
            _close_descriptor(
                descriptor,
                primary_error=primary_error,
                label=label,
                path=path,
            )
        raise

    body_primary: BaseException | None = None
    try:
        yield descriptor
    except BaseException as exc:
        body_primary = exc
        raise
    finally:
        _close_descriptor(
            descriptor,
            primary_error=body_primary,
            label=label,
            path=path,
        )


def _ensure_child_directory(
    parent_descriptor: int,
    parent: Path,
    name: str,
    *,
    label: str,
) -> None:
    metadata = _directory_entry_metadata(
        parent_descriptor,
        parent,
        name,
        label=label,
        allow_missing=True,
    )
    if metadata is None:
        try:
            os.mkdir(name, dir_fd=parent_descriptor)
        except FileExistsError:
            pass
        except OSError as exc:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE {label} cannot be created safely: {parent / name}"
            ) from exc
        metadata = _directory_entry_metadata(
            parent_descriptor,
            parent,
            name,
            label=label,
            allow_missing=False,
        )
    if metadata is None or not stat.S_ISDIR(metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} is not an actual directory: {parent / name}"
        )


def _validate_source_owner_path(source: Path) -> None:
    data_path = source / "data"
    try:
        data_metadata = data_path.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISDIR(data_metadata.st_mode):
        return
    _regular_file_metadata(
        source / ROW_ONE_PUBLISH_OWNER_PATH,
        label="publish owner file",
        allow_missing=True,
    )


def _apply_live_root_metadata(transaction: RowOnePublishTransaction) -> None:
    if not transaction.had_live_output:
        return
    shutil.copystat(
        transaction.target.physical_output,
        transaction.stage_path,
        follow_symlinks=False,
    )


def _read_json_object(path: Path, *, label: str) -> dict[str, object]:
    managed_root = path.parent.parent
    with _open_verified_directory(
        managed_root,
        label=f"{label} managed root directory",
    ) as root_descriptor:
        with _open_verified_child_directory(
            root_descriptor,
            managed_root,
            path.parent.name,
            label=f"{label} parent directory",
        ) as parent_descriptor:
            return _read_json_object_at(parent_descriptor, path, label=label)


def _read_json_object_at(
    directory_descriptor: int,
    path: Path,
    *,
    label: str,
) -> dict[str, object]:
    metadata = _directory_entry_metadata(
        directory_descriptor,
        path.parent,
        path.name,
        label=label,
        allow_missing=False,
    )
    if metadata is None:
        raise AssertionError("required JSON metadata unexpectedly missing")
    if not stat.S_ISREG(metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} path is unsafe: {path}")
    expected_identity = _identity(metadata)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    descriptor: int | None = None
    primary_error: BaseException | None = None
    try:
        try:
            descriptor = os.open(path.name, flags, dir_fd=directory_descriptor)
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode) or _identity(opened) != expected_identity:
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE {label} identity changed while reading: {path}"
                )
            current = _directory_entry_metadata(
                directory_descriptor,
                path.parent,
                path.name,
                label=label,
                allow_missing=False,
            )
            if current is None:
                raise AssertionError("required JSON metadata unexpectedly missing")
            if not stat.S_ISREG(current.st_mode) or _identity(current) != expected_identity:
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE {label} identity changed while reading: {path}"
                )
            with os.fdopen(descriptor, "rb") as handle:
                descriptor = None
                payload = json.load(handle, object_pairs_hook=_unique_json_object)
        except RowOnePublishAmbiguousStateError:
            raise
        except OSError as exc:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE {label} cannot be read safely: {path}"
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
            raise RowOnePublishError(f"ROW ONE {label} is not valid JSON: {path}") from exc
    except BaseException as exc:
        primary_error = exc
        raise
    finally:
        if descriptor is not None:
            _close_descriptor(
                descriptor,
                primary_error=primary_error,
                label=f"{label} JSON descriptor",
                path=path,
            )
    if not isinstance(payload, dict):
        raise RowOnePublishError(f"ROW ONE {label} must contain a JSON object: {path}")
    return payload


def _write_owner_file(stage: Path, transaction: RowOnePublishTransaction) -> None:
    owner_path = stage / ROW_ONE_PUBLISH_OWNER_PATH
    payload = {
        "contract_version": ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION,
        "physical_output": str(transaction.target.physical_output),
        "token": transaction.token,
    }
    with _open_verified_directory(stage, label="publish stage directory") as stage_descriptor:
        _ensure_child_directory(
            stage_descriptor,
            stage,
            "data",
            label="publish data directory",
        )
        with _open_verified_child_directory(
            stage_descriptor,
            stage,
            "data",
            label="publish data directory",
        ) as data_descriptor:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor: int | None = None
            primary_error: BaseException | None = None
            try:
                try:
                    descriptor = os.open(
                        owner_path.name,
                        flags,
                        0o600,
                        dir_fd=data_descriptor,
                    )
                    opened = os.fstat(descriptor)
                    if not stat.S_ISREG(opened.st_mode):
                        raise RowOnePublishAmbiguousStateError(
                            f"ROW ONE publish owner file is not regular: {owner_path}"
                        )
                    current = _directory_entry_metadata(
                        data_descriptor,
                        owner_path.parent,
                        owner_path.name,
                        label="publish owner",
                        allow_missing=False,
                    )
                    if current is None or _identity(current) != _identity(opened):
                        raise RowOnePublishAmbiguousStateError(
                            f"ROW ONE publish owner identity changed while opening: {owner_path}"
                        )
                    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                        descriptor = None
                        json.dump(payload, handle, ensure_ascii=True, sort_keys=True)
                        handle.write("\n")
                except FileExistsError as exc:
                    raise RowOnePublishAmbiguousStateError(
                        f"ROW ONE publish owner path already exists: {owner_path}"
                    ) from exc
                except RowOnePublishError:
                    raise
                except OSError as exc:
                    raise RowOnePublishError(
                        f"ROW ONE publish owner cannot be written: {owner_path}"
                    ) from exc
            except BaseException as exc:
                primary_error = exc
                raise
            finally:
                if descriptor is not None:
                    _close_descriptor(
                        descriptor,
                        primary_error=primary_error,
                        label="publish owner file",
                        path=owner_path,
                    )


def _validated_owner(directory: Path) -> tuple[str, Path]:
    owner_path = directory / ROW_ONE_PUBLISH_OWNER_PATH
    with _open_verified_directory(
        directory,
        label="publish stage directory",
    ) as stage_descriptor:
        with _open_verified_child_directory(
            stage_descriptor,
            directory,
            "data",
            label="publish data directory",
        ) as data_descriptor:
            return _validated_owner_at(data_descriptor, owner_path)


def _validated_owner_at(
    data_descriptor: int,
    owner_path: Path,
) -> tuple[str, Path]:
    try:
        payload = _read_json_object_at(data_descriptor, owner_path, label="publish owner")
    except RowOnePublishAmbiguousStateError:
        raise
    except RowOnePublishError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE publish owner is invalid: {owner_path}"
        ) from exc
    if set(payload) != _OWNER_KEYS:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE publish owner keys do not match the contract: {owner_path}"
        )
    if payload["contract_version"] != ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE publish owner contract version is not recognized: {owner_path}"
        )

    physical_output_value = payload["physical_output"]
    if not isinstance(physical_output_value, str):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE publish owner physical output is not a string: {owner_path}"
        )
    physical_output = Path(physical_output_value)
    if not physical_output.is_absolute():
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE publish owner physical output is not absolute: {owner_path}"
        )

    token = payload["token"]
    if not isinstance(token, str):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE publish owner token is not a string: {owner_path}"
        )
    try:
        _validate_token(token)
    except RowOnePublishError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE publish owner token is unsafe: {owner_path}"
        ) from exc
    return token, physical_output


def _read_owner_token(directory: Path) -> str:
    token, _physical_output = _validated_owner(directory)
    return token


def _read_owner_token_if_present(directory: Path) -> str | None:
    _require_safe_directory_operations()
    owner_path = directory / ROW_ONE_PUBLISH_OWNER_PATH
    with _open_verified_directory(
        directory,
        label="published live directory",
    ) as root_descriptor:
        with _open_verified_child_directory(
            root_descriptor,
            directory,
            "data",
            label="published data directory",
        ) as data_descriptor:
            metadata = _directory_entry_metadata(
                data_descriptor,
                owner_path.parent,
                owner_path.name,
                label="publish owner",
                allow_missing=True,
            )
            if metadata is None:
                return None
            token, physical_output = _validated_owner_at(data_descriptor, owner_path)
            if physical_output != directory:
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE publish owner physical output mismatch: {owner_path}"
                )
            return token


def _validate_published_row_one_site(
    transaction: RowOnePublishTransaction,
    *,
    require_owner: bool = True,
) -> None:
    _require_safe_directory_operations()
    live = transaction.target.physical_output
    owner_token = _read_owner_token_if_present(live)
    if owner_token is not None and owner_token != transaction.token:
        raise RowOnePublishAmbiguousStateError(f"ROW ONE published owner token mismatch: {live}")
    if require_owner and owner_token is None:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published owner marker is missing: {live / ROW_ONE_PUBLISH_OWNER_PATH}"
        )
    _validate_published_row_one_content(live)


def _validate_published_row_one_content(live: Path) -> None:
    validate_row_one_site_dir(live)
    edition = _read_json_object(live / "data" / "edition.json", label="edition")
    _read_json_object(live / "data" / "manifest.json", label="manifest")
    _read_json_object(live / "data" / "runtime.json", label="runtime")
    validate_row_one_generated_site_integrity(site_dir=live, edition=edition)


def _is_owned_live(transaction: RowOnePublishTransaction) -> bool:
    _require_safe_directory_operations()
    live = transaction.target.physical_output
    try:
        metadata = live.lstat()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published live path cannot be inspected safely: {live}"
        ) from exc
    if not stat.S_ISDIR(metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published live path is not an actual directory: {live}"
        )
    data = live / "data"
    try:
        data_metadata = data.lstat()
    except FileNotFoundError:
        return False
    if not stat.S_ISDIR(data_metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published data path is not an actual directory: {data}"
        )
    owner_token = _read_owner_token_if_present(live)
    if owner_token is None:
        return False
    if owner_token != transaction.token:
        raise RowOnePublishAmbiguousStateError(f"ROW ONE published owner token mismatch: {live}")
    return True


def _remove_owner_file_from_managed_root(
    directory: Path,
    *,
    expected_token: str,
) -> None:
    _require_safe_directory_operations()
    owner_path = directory / ROW_ONE_PUBLISH_OWNER_PATH
    with _open_verified_directory(
        directory,
        label="published live directory",
    ) as root_descriptor:
        with _open_verified_child_directory(
            root_descriptor,
            directory,
            "data",
            label="published data directory",
        ) as data_descriptor:
            metadata = _directory_entry_metadata(
                data_descriptor,
                owner_path.parent,
                owner_path.name,
                label="publish owner",
                allow_missing=True,
            )
            if metadata is None:
                return
            expected_identity = _identity(metadata)
            token, physical_output = _validated_owner_at(data_descriptor, owner_path)
            if token != expected_token:
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE published owner token mismatch: {directory}"
                )
            if physical_output != directory:
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE publish owner physical output mismatch: {owner_path}"
                )
            current = _directory_entry_metadata(
                data_descriptor,
                owner_path.parent,
                owner_path.name,
                label="publish owner",
                allow_missing=False,
            )
            if current is None or _identity(current) != expected_identity:
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE publish owner identity changed before removal: {owner_path}"
                )
            try:
                os.unlink(owner_path.name, dir_fd=data_descriptor)
            except FileNotFoundError:
                remaining = _directory_entry_metadata(
                    data_descriptor,
                    owner_path.parent,
                    owner_path.name,
                    label="publish owner",
                    allow_missing=True,
                )
                if remaining is None:
                    return
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE publish owner changed during removal: {owner_path}"
                ) from None


def _remove_owner_file_if_present(transaction: RowOnePublishTransaction) -> None:
    _remove_owner_file_from_managed_root(
        transaction.target.physical_output,
        expected_token=transaction.token,
    )


def _validate_staged_row_one_site(
    transaction: RowOnePublishTransaction,
    result: StagedRowOneRenderResult,
) -> None:
    stage = transaction.stage_path
    if result.output_dir != stage:
        raise RowOnePublishError(
            f"ROW ONE staged render result output_dir does not match stage: {result.output_dir}"
        )
    expected_index = stage / "index.html"
    if result.index_path != expected_index:
        raise RowOnePublishError(
            f"ROW ONE staged render result index_path does not match stage: {result.index_path}"
        )
    data_dir = stage / "data"
    with _open_verified_directory(stage, label="publish stage directory") as stage_descriptor:
        with _open_verified_child_directory(
            stage_descriptor,
            stage,
            "data",
            label="publish data directory",
        ) as data_descriptor:
            try:
                validate_row_one_site_dir(stage)
            except FileNotFoundError as exc:
                raise RowOnePublishError(str(exc)) from exc

            owner_token, owner_physical_output = _validated_owner_at(
                data_descriptor,
                stage / ROW_ONE_PUBLISH_OWNER_PATH,
            )
            if owner_token != transaction.token:
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE publish owner token does not match transaction: {stage}"
                )
            if owner_physical_output != transaction.target.physical_output:
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE publish owner physical output does not match transaction: {stage}"
                )

            edition = _read_json_object_at(
                data_descriptor,
                data_dir / "edition.json",
                label="edition",
            )
            _read_json_object_at(
                data_descriptor,
                data_dir / "manifest.json",
                label="manifest",
            )
            _read_json_object_at(
                data_descriptor,
                data_dir / "runtime.json",
                label="runtime",
            )
    try:
        validate_row_one_generated_site_integrity(site_dir=stage, edition=edition)
    except ValueError as exc:
        raise RowOnePublishError(f"ROW ONE staged site integrity validation failed: {exc}") from exc


def _journal_payload(transaction: RowOnePublishTransaction) -> dict[str, object]:
    _validate_token(transaction.token)
    return {
        "contract_version": ROW_ONE_PUBLISH_CONTRACT_VERSION,
        "token": transaction.token,
        "physical_output": str(transaction.target.physical_output),
        "stage_path": str(transaction.stage_path),
        "backup_path": str(transaction.backup_path),
        "had_live_output": transaction.had_live_output,
        "had_site_marker": transaction.had_site_marker,
        "had_index": transaction.had_index,
        "phase": transaction.phase.value,
    }


def _read_canonical_journal(
    target: RowOnePublishTarget,
) -> RowOnePublishTransaction | None:
    journal_metadata = _regular_file_metadata(
        target.journal_path,
        label="journal",
        allow_missing=True,
    )
    if journal_metadata is None:
        return None
    payload = _read_journal_json_object(
        target.journal_path,
        label="journal",
        expected_identity=_identity(journal_metadata),
    )
    return _transaction_from_payload(
        target,
        payload,
        label=f"journal at {target.journal_path}",
    )


def _load_journal(target: RowOnePublishTarget) -> RowOnePublishTransaction | None:
    _recover_temporary_journals(target)
    return _read_canonical_journal(target)


def _write_journal(transaction: RowOnePublishTransaction) -> None:
    target = transaction.target
    nonce = secrets.token_hex(8)
    temp_path = target.journal_path.with_name(
        f".{target.physical_output.name}.row-one-publish.{transaction.token}.{nonce}.tmp"
    )
    payload = _journal_payload(transaction)
    created_identity: tuple[int, int] | None = None
    descriptor: int | None = None
    primary_error: BaseException | None = None
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(temp_path, flags, 0o600)
        except FileExistsError as exc:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE temporary journal path already exists: {temp_path}"
            ) from exc
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = None
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE temporary journal is not regular: {temp_path}"
                )
            created_identity = _identity(opened)
            json.dump(payload, handle, ensure_ascii=True, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        _regular_file_metadata(
            target.journal_path,
            label="journal",
            allow_missing=True,
        )
        if created_identity is None:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE temporary journal identity is unavailable: {temp_path}"
            )
        _require_identity(
            temp_path,
            expected_identity=created_identity,
            label="temporary journal",
        )
        os.replace(temp_path, target.journal_path)
        _require_identity(
            target.journal_path,
            expected_identity=created_identity,
            label="promoted journal",
        )
        _fsync_directory(target.physical_output.parent)
    except BaseException as local_primary:
        primary_error = local_primary
        raise
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except BaseException as cleanup_error:
                if primary_error is None:
                    raise
                primary_error.add_note(
                    "ROW ONE temporary journal descriptor cleanup also failed: "
                    f"{type(cleanup_error).__name__}: {cleanup_error}"
                )
        if created_identity is not None:
            try:
                try:
                    remaining = temp_path.lstat()
                except FileNotFoundError:
                    remaining = None
                if remaining is not None:
                    if (
                        not stat.S_ISREG(remaining.st_mode)
                        or _identity(remaining) != created_identity
                    ):
                        raise RowOnePublishAmbiguousStateError(
                            f"ROW ONE temporary journal identity changed: {temp_path}"
                        )
                    temp_path.unlink()
            except BaseException as cleanup_error:
                if primary_error is None:
                    raise
                primary_error.add_note(
                    f"ROW ONE temporary journal cleanup also failed for {temp_path}: "
                    f"{type(cleanup_error).__name__}: {cleanup_error}"
                )


def _recover_temporary_journals(target: RowOnePublishTarget) -> None:
    canonical_metadata = _regular_file_metadata(
        target.journal_path,
        label="journal",
        allow_missing=True,
    )
    candidates = _temporary_journal_candidates(target)
    if len(candidates) > 1:
        paths = ", ".join(str(path) for path, _metadata in candidates)
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE temporary journal set is not unique: {paths}"
        )

    canonical: RowOnePublishTransaction | None = None
    if canonical_metadata is not None:
        canonical_payload = _read_journal_json_object(
            target.journal_path,
            label="journal",
            expected_identity=_identity(canonical_metadata),
        )
        canonical = _transaction_from_payload(
            target,
            canonical_payload,
            label=f"journal at {target.journal_path}",
        )
    if not candidates:
        return

    temp_path, temp_metadata = candidates[0]
    temp_payload = _read_journal_json_object(
        temp_path,
        label="temporary journal",
        expected_identity=_identity(temp_metadata),
    )
    temporary = _transaction_from_payload(
        target,
        temp_payload,
        label=f"temporary journal at {temp_path}",
    )
    _validate_temporary_journal_name(temp_path, target, temporary.token)

    if canonical is not None:
        if temporary.token != canonical.token:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE temporary journal token does not match canonical journal: {temp_path}"
            )
        _unlink_if_identity_matches(
            temp_path,
            expected_identity=_identity(temp_metadata),
            label="temporary journal",
        )
        _fsync_directory(target.physical_output.parent)
        return

    current_canonical = _regular_file_metadata(
        target.journal_path,
        label="journal",
        allow_missing=True,
    )
    if current_canonical is not None:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE journal appeared during temporary recovery: {target.journal_path}"
        )
    _require_identity(
        temp_path,
        expected_identity=_identity(temp_metadata),
        label="temporary journal",
    )
    os.replace(temp_path, target.journal_path)
    _require_identity(
        target.journal_path,
        expected_identity=_identity(temp_metadata),
        label="promoted journal",
    )
    _fsync_directory(target.physical_output.parent)


def _fsync_directory(path: Path) -> None:
    descriptor: int | None = None
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            flags |= os.O_DIRECTORY
        descriptor = os.open(path, flags)
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


@contextmanager
def _acquire_publish_lock(target: RowOnePublishTarget) -> Iterator[None]:
    target.physical_output.parent.mkdir(parents=True, exist_ok=True)
    with _open_lock_file(target) as handle:
        _try_lock_handle(handle)
        primary_error: BaseException | None = None
        try:
            _validate_or_initialize_lock_metadata(handle, target)
            yield
        except BaseException as local_primary:
            primary_error = local_primary
            raise
        finally:
            try:
                _unlock_handle(handle)
            except BaseException as release_error:
                if primary_error is None:
                    raise
                primary_error.add_note(
                    f"ROW ONE publish lock release also failed for {target.lock_path}: "
                    f"{type(release_error).__name__}: {release_error}"
                )


def _open_lock_file(target: RowOnePublishTarget) -> BinaryIO:
    path = target.lock_path
    for _attempt in range(2):
        try:
            before = path.lstat()
        except FileNotFoundError:
            flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            try:
                descriptor = os.open(path, flags, 0o600)
            except FileExistsError:
                continue
            return _verified_lock_handle(path, descriptor, expected_identity=None)

        if not stat.S_ISREG(before.st_mode):
            raise RowOnePublishAmbiguousStateError(f"ROW ONE lock file path is unsafe: {path}")
        flags = os.O_RDWR
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        if hasattr(os, "O_NONBLOCK"):
            flags |= os.O_NONBLOCK
        try:
            descriptor = os.open(path, flags)
        except OSError as exc:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE lock file cannot be opened safely: {path}"
            ) from exc
        return _verified_lock_handle(
            path,
            descriptor,
            expected_identity=_identity(before),
        )
    raise RowOnePublishAmbiguousStateError(
        f"ROW ONE lock file changed while it was being opened: {path}"
    )


def _verified_lock_handle(
    path: Path,
    descriptor: int,
    *,
    expected_identity: tuple[int, int] | None,
) -> BinaryIO:
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise RowOnePublishAmbiguousStateError(f"ROW ONE lock file is not regular: {path}")
        opened_identity = _identity(opened)
        if expected_identity is not None and opened_identity != expected_identity:
            raise RowOnePublishAmbiguousStateError(f"ROW ONE lock file identity changed: {path}")
        try:
            current = path.lstat()
        except FileNotFoundError as exc:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE lock file disappeared after opening: {path}"
            ) from exc
        if not stat.S_ISREG(current.st_mode) or _identity(current) != opened_identity:
            raise RowOnePublishAmbiguousStateError(f"ROW ONE lock file identity changed: {path}")
        return os.fdopen(descriptor, "r+b")
    except BaseException as primary_error:
        _close_descriptor(
            descriptor,
            primary_error=primary_error,
            label="lock file descriptor",
            path=path,
        )
        raise


def _try_lock_handle(handle: BinaryIO) -> None:
    if os.name == "posix":
        import errno
        import fcntl

        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if isinstance(exc, BlockingIOError) or exc.errno in {errno.EACCES, errno.EAGAIN}:
                raise RowOnePublishBusyError(
                    "ROW ONE publish is already in progress for this output"
                ) from exc
            raise RowOnePublishError("ROW ONE publish lock could not be acquired") from exc
        return
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise RowOnePublishBusyError(
                "ROW ONE publish is already in progress for this output"
            ) from exc
        return
    raise RowOnePublishError(f"ROW ONE publish locking is unsupported on platform: {os.name}")


def _unlock_handle(handle: BinaryIO) -> None:
    if os.name == "posix":
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return
    raise RowOnePublishError(f"ROW ONE publish unlocking is unsupported on platform: {os.name}")


def _validate_or_initialize_lock_metadata(
    handle: BinaryIO,
    target: RowOnePublishTarget,
) -> None:
    opened = os.fstat(handle.fileno())
    try:
        current = target.lock_path.lstat()
    except FileNotFoundError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE lock file disappeared while locked: {target.lock_path}"
        ) from exc
    if (
        not stat.S_ISREG(opened.st_mode)
        or not stat.S_ISREG(current.st_mode)
        or _identity(opened) != _identity(current)
    ):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE lock file identity changed while locked: {target.lock_path}"
        )

    expected = {
        "contract_version": ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION,
        "physical_output": str(target.physical_output),
    }
    handle.seek(0)
    raw = handle.read()
    if not raw:
        encoded = (json.dumps(expected, ensure_ascii=True, sort_keys=True) + "\n").encode()
        handle.seek(0)
        handle.write(encoded)
        handle.truncate()
        handle.flush()
        os.fsync(handle.fileno())
        return
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_object)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE lock file metadata is invalid: {target.lock_path}"
        ) from exc
    if payload != expected or not isinstance(payload, dict) or set(payload) != set(expected):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE lock file metadata is not recognized: {target.lock_path}"
        )


def _temporary_journal_candidates(
    target: RowOnePublishTarget,
) -> list[tuple[Path, os.stat_result]]:
    parent = target.physical_output.parent
    prefix = f".{target.physical_output.name}.row-one-publish."
    suffix = ".tmp"
    try:
        with os.scandir(parent) as iterator:
            entries = list(iterator)
    except FileNotFoundError:
        return []

    candidates: list[tuple[Path, os.stat_result]] = []
    unsafe: list[Path] = []
    for entry in entries:
        if not entry.name.startswith(prefix) or not entry.name.endswith(suffix):
            continue
        path = parent / entry.name
        try:
            metadata = entry.stat(follow_symlinks=False)
        except FileNotFoundError as exc:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE temporary journal changed during inspection: {path}"
            ) from exc
        if not stat.S_ISREG(metadata.st_mode):
            unsafe.append(path)
        candidates.append((path, metadata))
    if unsafe:
        paths = ", ".join(str(path) for path in sorted(unsafe))
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE temporary journal path is not regular: {paths}"
        )
    return sorted(candidates, key=lambda candidate: candidate[0].name)


def _transaction_from_payload(
    target: RowOnePublishTarget,
    payload: dict[str, object],
    *,
    label: str,
) -> RowOnePublishTransaction:
    if set(payload) != _JOURNAL_KEYS:
        _invalid_journal(label, "keys do not match the contract")
    if payload["contract_version"] != ROW_ONE_PUBLISH_CONTRACT_VERSION:
        _invalid_journal(label, "contract version is not recognized")

    token = payload["token"]
    if not isinstance(token, str):
        _invalid_journal(label, "token is not a string")
    try:
        _validate_token(token)
    except RowOnePublishError as exc:
        raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} token is unsafe") from exc

    physical_output = _absolute_payload_path(payload["physical_output"], label=label)
    stage_path = _absolute_payload_path(payload["stage_path"], label=label)
    backup_path = _absolute_payload_path(payload["backup_path"], label=label)
    if physical_output != target.physical_output:
        _invalid_journal(label, "physical output does not match the requested target")

    expected_stage = physical_output.parent / f".{physical_output.name}.row-one-stage-{token}"
    expected_backup = physical_output.parent / f".{physical_output.name}.row-one-backup-{token}"
    if stage_path != expected_stage:
        _invalid_journal(label, "stage path is not the exact token-owned sibling")
    if backup_path != expected_backup:
        _invalid_journal(label, "backup path is not the exact token-owned sibling")
    if stage_path == backup_path:
        _invalid_journal(label, "stage and backup paths alias")

    flags: list[bool] = []
    for key in ("had_live_output", "had_site_marker", "had_index"):
        value = payload[key]
        if type(value) is not bool:
            _invalid_journal(label, f"{key} is not boolean")
        flags.append(value)
    phase_value = payload["phase"]
    if not isinstance(phase_value, str):
        _invalid_journal(label, "phase is not a string")
    try:
        phase = RowOnePublishPhase(phase_value)
    except ValueError as exc:
        raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} phase is not recognized") from exc
    return RowOnePublishTransaction(
        target=target,
        token=token,
        stage_path=stage_path,
        backup_path=backup_path,
        had_live_output=flags[0],
        had_site_marker=flags[1],
        had_index=flags[2],
        phase=phase,
    )


def _absolute_payload_path(value: object, *, label: str) -> Path:
    if not isinstance(value, str):
        _invalid_journal(label, "path value is not a string")
    path = Path(value)
    if not path.is_absolute():
        _invalid_journal(label, f"path is not absolute: {value}")
    return path


def _read_journal_json_object(
    path: Path,
    *,
    label: str,
    expected_identity: tuple[int, int],
) -> dict[str, object]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    descriptor: int | None = None
    primary_error: BaseException | None = None
    try:
        descriptor = os.open(path, flags)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or _identity(opened) != expected_identity:
            raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} identity changed: {path}")
        try:
            current = path.lstat()
        except FileNotFoundError as exc:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE {label} identity changed: {path}"
            ) from exc
        if not stat.S_ISREG(current.st_mode) or _identity(current) != expected_identity:
            raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} identity changed: {path}")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            payload = json.load(handle, object_pairs_hook=_unique_json_object)
    except RowOnePublishAmbiguousStateError as exc:
        primary_error = exc
        raise
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        RecursionError,
        ValueError,
    ) as exc:
        primary_error = RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} is not valid JSON: {path}"
        )
        raise primary_error from exc
    except BaseException as exc:
        primary_error = exc
        raise
    finally:
        if descriptor is not None:
            _close_descriptor(
                descriptor,
                primary_error=primary_error,
                label=f"{label} descriptor",
                path=path,
            )
    if not isinstance(payload, dict):
        _invalid_journal(f"{label} at {path}", "payload is not an object")
    return payload


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate JSON key: {key}")
        payload[key] = value
    return payload


def _regular_file_metadata(
    path: Path,
    *,
    label: str,
    allow_missing: bool,
) -> os.stat_result | None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        if allow_missing:
            return None
        raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} is missing: {path}") from None
    if not stat.S_ISREG(metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} path is unsafe: {path}")
    return metadata


def _validate_temporary_journal_name(
    path: Path,
    target: RowOnePublishTarget,
    token: str,
) -> None:
    prefix = f".{target.physical_output.name}.row-one-publish."
    suffix = ".tmp"
    middle = path.name.removeprefix(prefix).removesuffix(suffix)
    parts = middle.split(".")
    if len(parts) != 2 or parts[0] != token:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE temporary journal name does not match its token: {path}"
        )
    nonce = parts[1]
    if len(nonce) != 16 or any(character not in "0123456789abcdef" for character in nonce):
        raise RowOnePublishAmbiguousStateError(f"ROW ONE temporary journal nonce is unsafe: {path}")


def _unlink_if_identity_matches(
    path: Path,
    *,
    expected_identity: tuple[int, int],
    label: str,
) -> None:
    _require_identity(path, expected_identity=expected_identity, label=label)
    path.unlink()


def _require_identity(
    path: Path,
    *,
    expected_identity: tuple[int, int],
    label: str,
) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE {label} disappeared during inspection: {path}"
        ) from exc
    if not stat.S_ISREG(metadata.st_mode) or _identity(metadata) != expected_identity:
        raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} identity changed: {path}")


def _commit_first_publish(
    transaction: RowOnePublishTransaction,
) -> RowOnePublishTransaction:
    live = transaction.target.physical_output
    _move_publish_path(transaction.stage_path, live)
    try:
        _validate_published_row_one_site(transaction)
        return _replace_phase(transaction, RowOnePublishPhase.PUBLISHED)
    except BaseException as publish_error:
        try:
            owned_live = _is_owned_live(transaction)
        except RowOnePublishAmbiguousStateError:
            raise RowOnePublishAmbiguousStateError(
                "ROW ONE first publish failed after live ownership changed; "
                f"live={live}; stage={transaction.stage_path}; "
                f"journal={transaction.target.journal_path}"
            ) from publish_error
        if not owned_live:
            raise RowOnePublishAmbiguousStateError(
                "ROW ONE first publish failed after live ownership changed; "
                f"live={live}; stage={transaction.stage_path}; "
                f"journal={transaction.target.journal_path}"
            ) from publish_error
        try:
            _move_publish_path(live, transaction.stage_path)
        except BaseException as rollback_error:
            raise RowOnePublishRollbackError(
                "ROW ONE first publish validation and rollback failed; "
                f"live={live}; stage={transaction.stage_path}; "
                f"journal={transaction.target.journal_path}"
            ) from rollback_error
        _cleanup_after_handled_failure(transaction)
        if isinstance(publish_error, (KeyboardInterrupt, SystemExit)):
            raise publish_error
        raise RowOnePublishRestoredError(
            "ROW ONE first publish failed; no site was published"
        ) from publish_error


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


def _validate_previous_output_facts(transaction: RowOnePublishTransaction) -> None:
    live = transaction.target.physical_output
    try:
        live_metadata = live.lstat()
    except FileNotFoundError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE restored live path is missing: {live}"
        ) from exc
    if not stat.S_ISDIR(live_metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(f"ROW ONE restored live path is unsafe: {live}")

    facts: list[tuple[Path, bool, str]] = [
        (live / ".row-one-site", transaction.had_site_marker, "site marker"),
        (live / "index.html", transaction.had_index, "index"),
    ]
    for path, expected, label in facts:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            present = False
        else:
            if not stat.S_ISREG(metadata.st_mode):
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE restored {label} path is unsafe: {path}"
                )
            present = True
        if present is not expected:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE restored {label} fact does not match the journal: {path}"
            )


def _cleanup_after_rollback_restore(transaction: RowOnePublishTransaction) -> None:
    canonical = _read_canonical_journal(transaction.target)
    if canonical != transaction:
        raise RowOnePublishAmbiguousStateError(
            "ROW ONE canonical journal does not match restored rollback transaction: "
            f"{transaction.target.journal_path}"
        )
    if transaction.phase not in {
        RowOnePublishPhase.LIVE_MOVING,
        RowOnePublishPhase.LIVE_BACKED_UP,
    }:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE journal phase is unsafe after rollback: {transaction.phase.value}"
        )
    _validated_temporary_journals(transaction)
    _reject_extra_transaction_siblings(transaction)
    if _validate_owned_backup_if_present(transaction, required=False):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE backup remains after rollback restore: {transaction.backup_path}"
        )
    _validate_owned_stage_if_present(transaction, allow_missing=True)
    _validate_previous_output_facts(transaction)
    if _is_owned_live(transaction):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE restored live path is still transaction-owned: "
            f"{transaction.target.physical_output}"
        )

    if transaction.stage_path.exists():
        _remove_publish_path(transaction.stage_path)
    _remove_matching_temporary_journals(transaction)
    _remove_canonical_journal(transaction)


def _rollback_existing_publish(
    transaction: RowOnePublishTransaction,
    publish_error: BaseException,
) -> NoReturn:
    _preflight_rollback_artifacts(transaction)
    live = transaction.target.physical_output
    try:
        if live.exists() or live.is_symlink():
            _move_publish_path(live, transaction.stage_path)
        _move_publish_path(transaction.backup_path, live)
        _validate_previous_output_facts(transaction)
        _cleanup_after_rollback_restore(transaction)
    except BaseException as rollback_error:
        raise RowOnePublishRollbackError(
            "ROW ONE publish and rollback failed; retained recovery paths: "
            f"live={live}; stage={transaction.stage_path}; "
            f"backup={transaction.backup_path}; "
            f"journal={transaction.target.journal_path}"
        ) from rollback_error
    if isinstance(publish_error, (KeyboardInterrupt, SystemExit)):
        raise publish_error
    raise RowOnePublishRestoredError(
        "ROW ONE publish failed; the previous site was restored"
    ) from publish_error


def _commit_publish(
    transaction: RowOnePublishTransaction,
) -> RowOnePublishTransaction:
    if transaction.had_live_output:
        return _commit_existing_publish(transaction)
    return _commit_first_publish(transaction)


def _path_exists_without_following(path: Path) -> bool:
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    return True


def _validate_previous_output_facts_at(
    transaction: RowOnePublishTransaction,
    directory: Path,
) -> None:
    try:
        directory_metadata = directory.lstat()
    except FileNotFoundError as exc:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE previous output is missing: {directory}"
        ) from exc
    if not stat.S_ISDIR(directory_metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(f"ROW ONE previous output is unsafe: {directory}")
    facts: list[tuple[Path, bool, str]] = [
        (directory / ".row-one-site", transaction.had_site_marker, "site marker"),
        (directory / "index.html", transaction.had_index, "index"),
    ]
    for path, expected, label in facts:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            present = False
        else:
            if not stat.S_ISREG(metadata.st_mode):
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE previous {label} path is unsafe: {path}"
                )
            present = True
        if present is not expected:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE previous {label} fact does not match the journal: {path}"
            )


def _validate_recovered_previous_output(transaction: RowOnePublishTransaction) -> None:
    _validate_previous_output_facts(transaction)
    if transaction.had_site_marker and transaction.had_index:
        _validate_published_row_one_site(transaction, require_owner=False)


def _published_live_owner_preflight(transaction: RowOnePublishTransaction) -> str | None:
    live = transaction.target.physical_output
    try:
        live_metadata = live.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISDIR(live_metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published live path is unsafe during recovery: {live}"
        )
    data = live / "data"
    try:
        data_metadata = data.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISDIR(data_metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published data path is unsafe during recovery: {data}"
        )
    owner_token = _read_owner_token_if_present(live)
    if owner_token is not None and owner_token != transaction.token:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published owner token mismatch during recovery: {live}"
        )
    return owner_token


def _validate_recovery_common(transaction: RowOnePublishTransaction) -> None:
    canonical = _read_canonical_journal(transaction.target)
    if canonical != transaction:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE canonical journal changed during recovery: {transaction.target.journal_path}"
        )
    _validated_temporary_journals(transaction)
    _reject_extra_transaction_siblings(transaction)


def _validate_recovery_stage(
    transaction: RowOnePublishTransaction,
    *,
    allow_missing_owner: bool,
) -> None:
    stage = transaction.stage_path
    try:
        metadata = stage.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISDIR(metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(f"ROW ONE recovery stage path is unsafe: {stage}")
    if not allow_missing_owner:
        _validate_owned_stage_if_present(transaction, allow_missing=False)
        return
    data = stage / "data"
    try:
        data_metadata = data.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISDIR(data_metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE recovery stage data path is unsafe: {data}"
        )
    owner = stage / ROW_ONE_PUBLISH_OWNER_PATH
    try:
        owner_metadata = owner.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISREG(owner_metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE recovery stage owner path is unsafe: {owner}"
        )
    token, physical_output = _validated_owner(stage)
    if token != transaction.token or physical_output != transaction.target.physical_output:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE recovery stage owner does not match the transaction: {stage}"
        )


def _cleanup_after_recovery_restore(
    transaction: RowOnePublishTransaction,
    *,
    allow_missing_stage_owner: bool,
) -> None:
    _validate_recovery_common(transaction)
    if _validate_owned_backup_if_present(transaction, required=False):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE backup remains after recovery restore: {transaction.backup_path}"
        )
    _validate_recovery_stage(
        transaction,
        allow_missing_owner=allow_missing_stage_owner,
    )
    _validate_recovered_previous_output(transaction)
    if _is_owned_live(transaction):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE recovered previous output is transaction-owned: "
            f"{transaction.target.physical_output}"
        )
    if _path_exists_without_following(transaction.stage_path):
        _remove_publish_path(transaction.stage_path)
    _remove_matching_temporary_journals(transaction)
    _remove_canonical_journal(transaction)


def _restore_previous_output(transaction: RowOnePublishTransaction) -> None:
    _validate_recovery_common(transaction)
    _validate_owned_backup_if_present(transaction, required=True)
    _validate_previous_output_facts_at(transaction, transaction.backup_path)
    live = transaction.target.physical_output
    live_exists = _path_exists_without_following(live)
    stage_exists = _path_exists_without_following(transaction.stage_path)
    allow_missing_stage_owner = False

    if stage_exists:
        _validate_owned_stage_if_present(transaction, allow_missing=False)
    if live_exists:
        if stage_exists:
            raise RowOnePublishAmbiguousStateError(
                "ROW ONE recovery found both live and stage transaction outputs; "
                f"live={live}; stage={transaction.stage_path}"
            )
        if transaction.phase is RowOnePublishPhase.PUBLISHED:
            allow_missing_stage_owner = _published_live_owner_preflight(transaction) is None
        elif not _is_owned_live(transaction):
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE recovery live path is not transaction-owned: {live}"
            )

    try:
        if live_exists:
            _move_publish_path(live, transaction.stage_path)
        _move_publish_path(transaction.backup_path, live)
        _validate_recovered_previous_output(transaction)
        _cleanup_after_recovery_restore(
            transaction,
            allow_missing_stage_owner=allow_missing_stage_owner,
        )
    except BaseException as recovery_error:
        raise RowOnePublishRollbackError(
            "ROW ONE recovery could not restore the previous output; retained paths: "
            f"live={live}; stage={transaction.stage_path}; "
            f"backup={transaction.backup_path}; "
            f"journal={transaction.target.journal_path}"
        ) from recovery_error


def _finish_published_recovery(transaction: RowOnePublishTransaction) -> None:
    _validate_recovery_common(transaction)
    if transaction.phase is not RowOnePublishPhase.PUBLISHED:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published recovery has the wrong phase: {transaction.phase.value}"
        )
    if _path_exists_without_following(transaction.stage_path):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE published recovery still has a stage: {transaction.stage_path}"
        )
    backup_present = _validate_owned_backup_if_present(transaction, required=False)
    live_present = _path_exists_without_following(transaction.target.physical_output)
    if live_present:
        _published_live_owner_preflight(transaction)
    try:
        if not live_present:
            raise FileNotFoundError(transaction.target.physical_output)
        _validate_published_row_one_content(transaction.target.physical_output)
    except Exception as content_error:
        if backup_present:
            _restore_previous_output(transaction)
            return
        raise RowOnePublishAmbiguousStateError(
            "ROW ONE published live site is invalid and no backup is available; "
            f"live={transaction.target.physical_output}; "
            f"journal={transaction.target.journal_path}"
        ) from content_error
    _cleanup_after_published(transaction)


def _finish_valid_first_publish_recovery(
    transaction: RowOnePublishTransaction,
) -> None:
    _validate_recovery_common(transaction)
    if transaction.phase is not RowOnePublishPhase.READY:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE first-publish recovery has the wrong phase: {transaction.phase.value}"
        )
    if _path_exists_without_following(transaction.stage_path):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE first-publish recovery still has a stage: {transaction.stage_path}"
        )
    if _validate_owned_backup_if_present(transaction, required=False):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE first-publish recovery unexpectedly has a backup: {transaction.backup_path}"
        )
    if not _is_owned_live(transaction):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE first-publish live path is not transaction-owned: "
            f"{transaction.target.physical_output}"
        )
    _validate_published_row_one_site(transaction)
    transaction = _replace_phase(transaction, RowOnePublishPhase.PUBLISHED)
    _cleanup_after_published(transaction)


def _clean_precommit_stage_after_preserving_old_output(
    transaction: RowOnePublishTransaction,
) -> None:
    _validate_recovery_common(transaction)
    if transaction.phase not in {
        RowOnePublishPhase.STAGING,
        RowOnePublishPhase.READY,
        RowOnePublishPhase.LIVE_MOVING,
    }:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE precommit recovery has the wrong phase: {transaction.phase.value}"
        )
    if _validate_owned_backup_if_present(transaction, required=False):
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE precommit recovery unexpectedly has a backup: {transaction.backup_path}"
        )
    _validate_owned_stage_if_present(transaction, allow_missing=True)
    live = transaction.target.physical_output
    live_exists = _path_exists_without_following(live)
    if transaction.had_live_output:
        if not live_exists:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE previous live output is missing during recovery: {live}"
            )
        _validate_recovered_previous_output(transaction)
        if _is_owned_live(transaction):
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE precommit live output is transaction-owned: {live}"
            )
    elif live_exists:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE unexpected live output appeared during first-publish recovery: {live}"
        )
    if _path_exists_without_following(transaction.stage_path):
        _remove_publish_path(transaction.stage_path)
    _remove_matching_temporary_journals(transaction)
    _remove_canonical_journal(transaction)


def _recover_interrupted_publish(target: RowOnePublishTarget) -> None:
    transaction = _load_journal(target)
    if transaction is None:
        _reject_unowned_publish_artifacts(target)
        return
    _reject_extra_transaction_siblings(transaction)
    backup_present = _path_exists_without_following(transaction.backup_path)
    if transaction.phase is not RowOnePublishPhase.PUBLISHED and backup_present:
        _restore_previous_output(transaction)
    elif transaction.phase is RowOnePublishPhase.PUBLISHED:
        _finish_published_recovery(transaction)
    elif not transaction.had_live_output and _is_owned_live(transaction):
        _finish_valid_first_publish_recovery(transaction)
    else:
        _clean_precommit_stage_after_preserving_old_output(transaction)


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


def _matching_sibling_paths(target: RowOnePublishTarget, *, kind: str) -> list[Path]:
    parent = target.physical_output.parent
    prefix = f".{target.physical_output.name}.row-one-{kind}-"
    try:
        with os.scandir(parent) as iterator:
            return sorted(
                (parent / entry.name for entry in iterator if entry.name.startswith(prefix)),
                key=lambda path: path.name,
            )
    except FileNotFoundError:
        return []


def _reject_extra_transaction_siblings(transaction: RowOnePublishTransaction) -> None:
    expected = {
        "stage": transaction.stage_path,
        "backup": transaction.backup_path,
    }
    extras: list[Path] = []
    for kind, expected_path in expected.items():
        extras.extend(
            path
            for path in _matching_sibling_paths(transaction.target, kind=kind)
            if path != expected_path
        )
    if extras:
        paths = ", ".join(str(path) for path in sorted(extras))
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE unowned publish sibling artifacts are present: {paths}"
        )


def _validated_temporary_journals(
    transaction: RowOnePublishTransaction,
) -> list[tuple[Path, os.stat_result]]:
    candidates = _temporary_journal_candidates(transaction.target)
    for path, metadata in candidates:
        payload = _read_journal_json_object(
            path,
            label="temporary journal",
            expected_identity=_identity(metadata),
        )
        temporary = _transaction_from_payload(
            transaction.target,
            payload,
            label=f"temporary journal at {path}",
        )
        _validate_temporary_journal_name(path, transaction.target, temporary.token)
        if temporary.token != transaction.token:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE temporary journal token does not match canonical journal: {path}"
            )
    return candidates


def _validate_owned_stage_if_present(
    transaction: RowOnePublishTransaction,
    *,
    allow_missing: bool,
) -> None:
    stage = transaction.stage_path
    try:
        metadata = stage.lstat()
    except FileNotFoundError:
        if allow_missing:
            return
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE owned stage path is missing: {stage}"
        ) from None
    if not stat.S_ISDIR(metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(f"ROW ONE owned stage path is unsafe: {stage}")
    token, physical_output = _validated_owner(stage)
    if token != transaction.token or physical_output != transaction.target.physical_output:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE owned stage marker does not match the transaction: {stage}"
        )


def _validate_owned_backup_if_present(
    transaction: RowOnePublishTransaction,
    *,
    required: bool,
) -> bool:
    backup = transaction.backup_path
    try:
        metadata = backup.lstat()
    except FileNotFoundError:
        if required:
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE owned backup path is missing: {backup}"
            ) from None
        return False
    if not stat.S_ISDIR(metadata.st_mode):
        raise RowOnePublishAmbiguousStateError(f"ROW ONE owned backup path is unsafe: {backup}")
    return True


def _preflight_cleanup_artifacts(
    transaction: RowOnePublishTransaction,
    *,
    published: bool,
) -> None:
    canonical = _read_canonical_journal(transaction.target)
    if canonical != transaction:
        raise RowOnePublishAmbiguousStateError(
            "ROW ONE canonical journal does not match cleanup transaction: "
            f"{transaction.target.journal_path}"
        )
    expected_phases = (
        {RowOnePublishPhase.PUBLISHED}
        if published
        else {RowOnePublishPhase.STAGING, RowOnePublishPhase.READY}
    )
    if transaction.phase not in expected_phases:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE journal phase is unsafe for cleanup: {transaction.phase.value}"
        )
    _validated_temporary_journals(transaction)
    _reject_extra_transaction_siblings(transaction)
    if published:
        _validate_owned_stage_if_present(transaction, allow_missing=True)
        if transaction.stage_path.exists():
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE published transaction still has a stage: {transaction.stage_path}"
            )
        _validate_owned_backup_if_present(transaction, required=False)
        _validate_published_row_one_site(transaction, require_owner=False)
        return

    _validate_owned_stage_if_present(transaction, allow_missing=True)
    _validate_owned_backup_if_present(transaction, required=False)
    if transaction.backup_path.exists() or transaction.backup_path.is_symlink():
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE handled transaction unexpectedly has a backup: {transaction.backup_path}"
        )
    if _is_owned_live(transaction):
        raise RowOnePublishCleanupPendingError(
            "ROW ONE handled transaction has a token-owned live site; "
            f"live={transaction.target.physical_output}; "
            f"stage={transaction.stage_path}; "
            f"journal={transaction.target.journal_path}"
        )


def _preflight_rollback_artifacts(transaction: RowOnePublishTransaction) -> None:
    canonical = _read_canonical_journal(transaction.target)
    if canonical != transaction:
        raise RowOnePublishAmbiguousStateError(
            "ROW ONE canonical journal does not match rollback transaction: "
            f"{transaction.target.journal_path}"
        )
    if transaction.phase not in {
        RowOnePublishPhase.LIVE_MOVING,
        RowOnePublishPhase.LIVE_BACKED_UP,
    }:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE journal phase is unsafe for rollback: {transaction.phase.value}"
        )
    _validated_temporary_journals(transaction)
    _reject_extra_transaction_siblings(transaction)
    _validate_owned_backup_if_present(transaction, required=True)
    _validate_owned_stage_if_present(transaction, allow_missing=True)
    live = transaction.target.physical_output
    stage_present = _path_exists_without_following(transaction.stage_path)
    live_present = _path_exists_without_following(live)
    if stage_present and live_present:
        raise RowOnePublishAmbiguousStateError(
            "ROW ONE rollback found both live and stage transaction outputs; "
            f"live={live}; stage={transaction.stage_path}; "
            f"backup={transaction.backup_path}; "
            f"journal={transaction.target.journal_path}"
        )
    if live_present:
        if not _is_owned_live(transaction):
            raise RowOnePublishAmbiguousStateError(
                f"ROW ONE rollback live path is not transaction-owned: {live}"
            )


def _remove_matching_temporary_journals(transaction: RowOnePublishTransaction) -> None:
    canonical = _read_canonical_journal(transaction.target)
    if canonical != transaction:
        raise RowOnePublishAmbiguousStateError(
            "ROW ONE canonical journal changed before temporary cleanup: "
            f"{transaction.target.journal_path}"
        )
    for path, metadata in _validated_temporary_journals(transaction):
        _unlink_if_identity_matches(
            path,
            expected_identity=_identity(metadata),
            label="temporary journal",
        )


def _remove_owned_backup_if_present(transaction: RowOnePublishTransaction) -> None:
    canonical = _read_canonical_journal(transaction.target)
    if canonical != transaction:
        raise RowOnePublishAmbiguousStateError(
            "ROW ONE canonical journal changed before backup cleanup: "
            f"{transaction.target.journal_path}"
        )
    if _validate_owned_backup_if_present(transaction, required=False):
        _remove_publish_path(transaction.backup_path)


def _remove_canonical_journal(transaction: RowOnePublishTransaction) -> None:
    canonical = _read_canonical_journal(transaction.target)
    if canonical != transaction:
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE canonical journal changed before removal: {transaction.target.journal_path}"
        )
    metadata = _regular_file_metadata(
        transaction.target.journal_path,
        label="journal",
        allow_missing=False,
    )
    if metadata is None:
        raise AssertionError("required canonical journal metadata unexpectedly missing")
    _unlink_if_identity_matches(
        transaction.target.journal_path,
        expected_identity=_identity(metadata),
        label="journal",
    )


def _cleanup_after_handled_failure(
    transaction: RowOnePublishTransaction,
) -> None:
    canonical = _read_canonical_journal(transaction.target)
    if canonical is None:
        _reject_unowned_publish_artifacts(transaction.target)
        return
    _preflight_cleanup_artifacts(transaction, published=False)
    try:
        try:
            stage_mode = transaction.stage_path.lstat().st_mode
        except FileNotFoundError:
            stage_mode = None
        if stage_mode is not None:
            if not stat.S_ISDIR(stage_mode):
                raise RowOnePublishAmbiguousStateError(
                    f"ROW ONE owned stage path is unsafe: {transaction.stage_path}"
                )
            _remove_publish_path(transaction.stage_path)
        _remove_matching_temporary_journals(transaction)
        _remove_canonical_journal(transaction)
    except OSError as exc:
        raise RowOnePublishCleanupPendingError(
            "ROW ONE staged publish cleanup is pending; "
            f"stage={transaction.stage_path}; "
            f"journal={transaction.target.journal_path}"
        ) from exc


def _cleanup_after_published(transaction: RowOnePublishTransaction) -> None:
    live = transaction.target.physical_output
    try:
        _preflight_cleanup_artifacts(transaction, published=True)
        _remove_owner_file_if_present(transaction)
        _remove_owned_backup_if_present(transaction)
        _remove_matching_temporary_journals(transaction)
        _remove_canonical_journal(transaction)
    except OSError as exc:
        raise RowOnePublishCleanupPendingError(
            f"ROW ONE publish committed with cleanup pending; live={live}; "
            f"backup={transaction.backup_path}; "
            f"journal={transaction.target.journal_path}; "
            f"stage={transaction.stage_path}"
        ) from exc


def _reject_unowned_publish_artifacts(target: RowOnePublishTarget) -> None:
    artifacts = [
        *_matching_sibling_paths(target, kind="stage"),
        *_matching_sibling_paths(target, kind="backup"),
        *(path for path, _metadata in _temporary_journal_candidates(target)),
    ]
    if artifacts:
        paths = ", ".join(str(path) for path in sorted(artifacts))
        raise RowOnePublishAmbiguousStateError(
            f"ROW ONE unowned publish artifacts are present: {paths}"
        )


def _identity(metadata: os.stat_result) -> tuple[int, int]:
    return metadata.st_dev, metadata.st_ino


def _invalid_journal(label: str, reason: str) -> None:
    raise RowOnePublishAmbiguousStateError(f"ROW ONE {label} is invalid: {reason}")


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
    _require_safe_directory_operations()
    target = _resolve_publish_target(output_dir)
    target.physical_output.parent.mkdir(parents=True, exist_ok=True)
    with _acquire_publish_lock(target):
        _recover_interrupted_publish(target)
        _reject_unowned_publish_artifacts(target)
        _validate_live_publish_target(target)
        transaction = _new_transaction(target)
        commit_started = False
        trusted_validation_wrapper: RowOnePublishError | None = None
        try:
            transaction = _begin_staging(transaction)
            _copy_unrelated_children_if_present(transaction)
            result = render(transaction.stage_path)
            try:
                _validate_staged_row_one_site(transaction, result)
            except RowOnePublishError as validation_error:
                if type(validation_error) is RowOnePublishError and validation_error.__cause__:
                    trusted_validation_wrapper = validation_error
                raise
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
            direct_cause = publish_error
            if publish_error is trusted_validation_wrapper:
                direct_cause = publish_error.__cause__ or publish_error
            raise RowOnePublishError(
                "ROW ONE staged publish failed before commit; the live site was preserved"
            ) from direct_cause
        _cleanup_after_published(transaction)
        return result
