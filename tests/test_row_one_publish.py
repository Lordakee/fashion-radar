from __future__ import annotations

import errno
import inspect
import json
import os
import socket
import stat
import sys
import tempfile
import types
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

import pytest

import fashion_radar.row_one.publish as publish_module
from fashion_radar.row_one.publish import (
    GENERATED_CHILDREN,
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
    _journal_payload,
    _load_journal,
    _new_transaction,
    _open_lock_file,
    _recover_temporary_journals,
    _resolve_publish_target,
    _try_lock_handle,
    _unlock_handle,
    _validate_token,
    _write_journal,
)

_SYMLINK_UNAVAILABLE_ERRNOS = frozenset(
    getattr(errno, name)
    for name in ("EACCES", "EPERM", "ENOSYS", "ENOTSUP", "EOPNOTSUPP")
    if hasattr(errno, name)
)

_SPECIAL_FILE_UNAVAILABLE_ERRNOS = frozenset(
    getattr(errno, name)
    for name in ("EACCES", "EPERM", "EROFS", "ENOSYS", "ENOTSUP", "EOPNOTSUPP")
    if hasattr(errno, name)
)
_SOCKET_UNAVAILABLE_ERRNOS = _SPECIAL_FILE_UNAVAILABLE_ERRNOS | frozenset(
    getattr(errno, name) for name in ("EAFNOSUPPORT", "EPROTONOSUPPORT") if hasattr(errno, name)
)


def _symlink_to(
    path: Path,
    target: Path,
    *,
    target_is_directory: bool = False,
) -> None:
    try:
        path.symlink_to(target, target_is_directory=target_is_directory)
    except NotImplementedError:
        pytest.skip("symbolic links are unsupported on this platform")
    except OSError as exc:
        if exc.errno in _SYMLINK_UNAVAILABLE_ERRNOS or getattr(exc, "winerror", None) == 1314:
            pytest.skip(f"symbolic links are unavailable without platform privilege: {exc}")
        raise


def _assert_file_descriptors_closed(descriptors: list[int]) -> None:
    assert descriptors
    for descriptor in descriptors:
        with pytest.raises(OSError) as exc_info:
            os.fstat(descriptor)
        assert exc_info.value.errno == errno.EBADF


def _make_fifo(path: Path) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO files are unavailable on this platform")
    try:
        os.mkfifo(path)
    except OSError as exc:
        if exc.errno in _SPECIAL_FILE_UNAVAILABLE_ERRNOS:
            pytest.skip(f"FIFO files are unavailable on this filesystem: {exc}")
        raise


def _make_unix_socket(path: Path) -> socket.socket:
    if not hasattr(socket, "AF_UNIX"):
        pytest.skip("Unix-domain sockets are unavailable on this platform")
    try:
        handle = socket.socket(socket.AF_UNIX)
    except OSError as exc:
        if exc.errno in _SOCKET_UNAVAILABLE_ERRNOS:
            pytest.skip(f"Unix-domain sockets are unavailable on this platform: {exc}")
        raise
    try:
        handle.bind(str(path))
    except OSError as exc:
        handle.close()
        path_too_long = exc.errno == getattr(errno, "ENAMETOOLONG", None) or (
            exc.errno is None and "path too long" in str(exc).lower()
        )
        if path_too_long:
            raise AssertionError(f"Unix-domain socket test path is too long: {path}") from exc
        if exc.errno in _SOCKET_UNAVAILABLE_ERRNOS:
            pytest.skip(f"Unix-domain sockets are unavailable on this filesystem: {exc}")
        raise
    return handle


def _transaction_fixture(
    tmp_path: Path,
    *,
    phase: RowOnePublishPhase = RowOnePublishPhase.STAGING,
    create_live: bool = True,
) -> RowOnePublishTransaction:
    output = tmp_path / "site"
    if create_live:
        output.mkdir(parents=True, exist_ok=True)
        (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
        (output / "index.html").write_text("old", encoding="utf-8")
    transaction = _new_transaction(
        _resolve_publish_target(output),
        token="a" * 32,
    )
    return replace(transaction, phase=phase)


def _write_payload(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def _temporary_journal_path(
    transaction: RowOnePublishTransaction,
    *,
    token: str | None = None,
    nonce: str = "b" * 16,
) -> Path:
    output = transaction.target.physical_output
    return output.parent / (
        f".{output.name}.row-one-publish.{token or transaction.token}.{nonce}.tmp"
    )


def _create_nonregular_path(path: Path, kind: str) -> socket.socket | None:
    if kind == "symlink":
        target = path.with_name("outside-journal.json")
        target.write_text("outside\n", encoding="utf-8")
        _symlink_to(path, target)
        return None
    if kind == "directory":
        path.mkdir()
        return None
    if kind == "fifo":
        _make_fifo(path)
        return None
    if kind == "socket":
        return _make_unix_socket(path)
    raise AssertionError(f"unknown nonregular test kind: {kind}")


def test_publish_target_contract_models_errors_and_phases_are_fixed() -> None:
    assert ROW_ONE_PUBLISH_CONTRACT_VERSION == "row-one-publish/v1"
    assert ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION == "row-one-publish-lock/v1"
    assert ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION == "row-one-publish-owner/v1"
    assert ROW_ONE_PUBLISH_OWNER_PATH == Path("data/.row-one-publish-owner.json")
    assert GENERATED_CHILDREN == (
        "index.html",
        ".row-one-site",
        "details",
        "assets",
        "data",
        "articles",
    )
    assert [phase.value for phase in RowOnePublishPhase] == [
        "staging",
        "ready",
        "live_moving",
        "live_backed_up",
        "published",
    ]
    for error_type in (
        RowOnePublishBusyError,
        RowOnePublishAmbiguousStateError,
        RowOnePublishRollbackError,
        RowOnePublishCleanupPendingError,
        RowOnePublishPreservedError,
        RowOnePublishRestoredError,
    ):
        assert issubclass(error_type, RowOnePublishError)


def test_journal_reader_exposes_the_dedicated_journal_reader() -> None:
    assert hasattr(publish_module, "_read_journal_json_object")


def test_public_publish_docstring_describes_internal_staging_paths_and_rebasing() -> None:
    assert inspect.getdoc(publish_module.publish_latest_row_one_site) == (
        "Publish a latest-only site and return the callback's internal result.\n\n"
        "The returned result's output_dir and index_path identify the staging paths\n"
        "used for validation and no longer exist after commit. The public renderer\n"
        "must rebase those fields to the logical output before exposing its result."
    )


def test_special_file_skip_allowlists_exclude_resource_collision_and_bad_path_errors() -> None:
    excluded_names = (
        "EMFILE",
        "ENFILE",
        "EADDRINUSE",
        "ENOENT",
        "ENOTDIR",
        "EINVAL",
        "EBADF",
    )
    for name in excluded_names:
        if hasattr(errno, name):
            error_number = getattr(errno, name)
            assert error_number not in _SPECIAL_FILE_UNAVAILABLE_ERRNOS
            assert error_number not in _SOCKET_UNAVAILABLE_ERRNOS


@pytest.mark.parametrize("error_number", sorted(_SPECIAL_FILE_UNAVAILABLE_ERRNOS))
def test_fifo_fixture_skips_only_explicit_capability_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
) -> None:
    failure = OSError(error_number, "FIFO capability unavailable")
    monkeypatch.setattr(
        os,
        "mkfifo",
        lambda _path: (_ for _ in ()).throw(failure),
        raising=False,
    )

    with pytest.raises(pytest.skip.Exception):
        _make_fifo(tmp_path / "fixture.fifo")


@pytest.mark.parametrize(
    "error_number",
    [
        getattr(errno, name)
        for name in ("EMFILE", "ENFILE", "EEXIST", "ENOENT", "ENOTDIR", "EINVAL")
        if hasattr(errno, name)
    ],
)
def test_fifo_fixture_propagates_resource_and_bad_path_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
) -> None:
    failure = OSError(error_number, "unexpected FIFO failure")
    monkeypatch.setattr(
        os,
        "mkfifo",
        lambda _path: (_ for _ in ()).throw(failure),
        raising=False,
    )

    with pytest.raises(OSError) as exc_info:
        _make_fifo(tmp_path / "fixture.fifo")

    assert exc_info.value is failure


@pytest.mark.parametrize(
    "error_number",
    [getattr(errno, name) for name in ("EMFILE", "ENFILE") if hasattr(errno, name)],
)
def test_socket_fixture_propagates_descriptor_exhaustion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
) -> None:
    failure = OSError(error_number, "socket descriptor exhaustion")
    monkeypatch.setattr(
        socket,
        "socket",
        lambda _family: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(OSError) as exc_info:
        _make_unix_socket(tmp_path / "fixture.sock")

    assert exc_info.value is failure


@pytest.mark.parametrize("error_number", sorted(_SOCKET_UNAVAILABLE_ERRNOS))
def test_socket_fixture_skips_explicit_capability_errors_and_closes_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
) -> None:
    failure = OSError(error_number, "socket capability unavailable")

    class FakeSocket:
        closed = False

        def bind(self, _path: str) -> None:
            raise failure

        def close(self) -> None:
            self.closed = True

    handle = FakeSocket()
    monkeypatch.setattr(socket, "socket", lambda _family: handle)

    with pytest.raises(pytest.skip.Exception):
        _make_unix_socket(tmp_path / "fixture.sock")

    assert handle.closed


@pytest.mark.parametrize(
    "error_number",
    [
        getattr(errno, name)
        for name in ("EADDRINUSE", "ENOENT", "ENOTDIR", "EINVAL", "EBADF")
        if hasattr(errno, name)
    ],
)
def test_socket_fixture_closes_handle_and_propagates_collision_or_bad_path_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
) -> None:
    failure = OSError(error_number, "unexpected socket bind failure")

    class FakeSocket:
        closed = False

        def bind(self, _path: str) -> None:
            raise failure

        def close(self) -> None:
            self.closed = True

    handle = FakeSocket()
    monkeypatch.setattr(socket, "socket", lambda _family: handle)

    with pytest.raises(OSError) as exc_info:
        _make_unix_socket(tmp_path / "fixture.sock")

    assert exc_info.value is failure
    assert handle.closed


def test_socket_fixture_fails_path_length_explicitly_and_closes_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = OSError("AF_UNIX path too long")

    class FakeSocket:
        closed = False

        def bind(self, _path: str) -> None:
            raise failure

        def close(self) -> None:
            self.closed = True

    handle = FakeSocket()
    monkeypatch.setattr(socket, "socket", lambda _family: handle)

    with pytest.raises(AssertionError, match="socket test path is too long") as exc_info:
        _make_unix_socket(tmp_path / "fixture.sock")

    assert exc_info.value.__cause__ is failure
    assert handle.closed


def test_socket_fixture_does_not_skip_an_unclassified_bind_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = OSError("mystery socket bind failure")

    class FakeSocket:
        closed = False

        def bind(self, _path: str) -> None:
            raise failure

        def close(self) -> None:
            self.closed = True

    handle = FakeSocket()
    monkeypatch.setattr(socket, "socket", lambda _family: handle)

    with pytest.raises(OSError) as exc_info:
        _make_unix_socket(tmp_path / "fixture.sock")

    assert exc_info.value is failure
    assert handle.closed


def test_publish_target_uses_logical_output_and_resolved_physical_target(
    tmp_path: Path,
) -> None:
    physical = tmp_path / "physical" / "site"
    logical = tmp_path / "logical-site"
    physical.parent.mkdir()
    _symlink_to(logical, physical, target_is_directory=True)

    target = _resolve_publish_target(logical)

    assert target.logical_output == logical
    assert target.physical_output == physical.resolve()
    assert target.lock_path == physical.parent / ".site.row-one-publish.lock"
    assert target.journal_path == physical.parent / ".site.row-one-publish.json"


def test_publish_target_allows_a_dangling_symlink_to_a_creatable_target(
    tmp_path: Path,
) -> None:
    physical = tmp_path / "physical" / "site"
    logical = tmp_path / "logical-site"
    _symlink_to(logical, physical, target_is_directory=True)

    target = _resolve_publish_target(logical)

    assert target.logical_output == logical
    assert target.physical_output == physical
    assert not physical.exists()


def test_publish_target_resolves_a_symlink_to_an_existing_directory(tmp_path: Path) -> None:
    physical = tmp_path / "physical" / "site"
    physical.mkdir(parents=True)
    logical = tmp_path / "logical-site"
    _symlink_to(logical, physical, target_is_directory=True)

    target = _resolve_publish_target(logical)

    assert target.logical_output == logical
    assert target.physical_output == physical.resolve()
    assert target.lock_path.parent == physical.parent


def test_publish_target_rejects_a_symlink_to_an_existing_regular_file(
    tmp_path: Path,
) -> None:
    physical = tmp_path / "physical-file"
    physical.write_text("keep", encoding="utf-8")
    logical = tmp_path / "logical-site"
    _symlink_to(logical, physical)

    with pytest.raises(RowOnePublishError, match="not a directory"):
        _resolve_publish_target(logical)

    assert logical.is_symlink()
    assert physical.read_text(encoding="utf-8") == "keep"


def test_publish_target_rejects_the_filesystem_root(tmp_path: Path) -> None:
    with pytest.raises(RowOnePublishError, match="filesystem root"):
        _resolve_publish_target(Path(tmp_path.anchor))


def test_publish_target_rejects_an_existing_non_directory(tmp_path: Path) -> None:
    output = tmp_path / "site"
    output.write_text("not a directory", encoding="utf-8")

    with pytest.raises(RowOnePublishError, match="not a directory"):
        _resolve_publish_target(output)

    assert output.read_text(encoding="utf-8") == "not a directory"


def test_publish_target_rejects_a_symlink_loop(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _symlink_to(first, second)
    _symlink_to(second, first)

    with pytest.raises(RowOnePublishError, match="cannot be resolved"):
        _resolve_publish_target(first)

    assert first.is_symlink()
    assert second.is_symlink()


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


def test_new_transaction_uses_exact_sibling_paths(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")

    transaction = _new_transaction(target, token="a" * 32)

    assert transaction.stage_path == tmp_path / f".site.row-one-stage-{'a' * 32}"
    assert transaction.backup_path == tmp_path / f".site.row-one-backup-{'a' * 32}"
    assert transaction.target == target


@pytest.mark.parametrize(
    "token",
    [
        "a" * 31,
        "a" * 33,
        "A" * 32,
        "g" * 32,
        "0" * 31 + "/",
        "0" * 31 + "-",
    ],
)
def test_new_transaction_rejects_unsafe_tokens(tmp_path: Path, token: str) -> None:
    target = _resolve_publish_target(tmp_path / "site")

    with pytest.raises(RowOnePublishError, match="token"):
        _new_transaction(target, token=token)


def test_new_transaction_token_validator_rejects_an_empty_token() -> None:
    with pytest.raises(RowOnePublishError, match="token"):
        _validate_token("")


def test_new_transaction_generates_a_safe_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(publish_module.secrets, "token_hex", lambda length: "c" * (length * 2))

    transaction = _new_transaction(_resolve_publish_target(tmp_path / "site"))

    assert transaction.token == "c" * 32
    _validate_token(transaction.token)


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
    assert _journal_payload(transaction) == json.loads(
        transaction.target.journal_path.read_text(encoding="utf-8")
    )


def _invalid_journal_payload(
    case: str,
    transaction: RowOnePublishTransaction,
) -> dict[str, object]:
    payload = _journal_payload(transaction)
    if case == "unknown_key":
        payload["unknown"] = True
    elif case == "missing_key":
        del payload["phase"]
    elif case == "unsafe_token":
        payload["token"] = "A" * 32
    elif case == "wrong_contract":
        payload["contract_version"] = "row-one-publish/v0"
    elif case == "relative_physical_output":
        payload["physical_output"] = "site"
    elif case == "relative_stage":
        payload["stage_path"] = ".site.row-one-stage-unsafe"
    elif case == "relative_backup":
        payload["backup_path"] = ".site.row-one-backup-unsafe"
    elif case == "non_sibling_stage":
        payload["stage_path"] = str(
            transaction.target.physical_output.parent / "nested" / transaction.stage_path.name
        )
    elif case == "non_sibling_backup":
        payload["backup_path"] = str(
            transaction.target.physical_output.parent / "nested" / transaction.backup_path.name
        )
    elif case == "stage_equals_backup":
        payload["stage_path"] = payload["backup_path"]
    elif case == "output_mismatch":
        payload["physical_output"] = str(transaction.target.physical_output.with_name("other-site"))
    elif case == "invalid_phase":
        payload["phase"] = "committing"
    elif case == "non_boolean_flag":
        payload["had_live_output"] = 1
    else:
        raise AssertionError(f"unknown journal case: {case}")
    return payload


@pytest.mark.parametrize(
    "case",
    [
        "unknown_key",
        "missing_key",
        "unsafe_token",
        "wrong_contract",
        "relative_physical_output",
        "relative_stage",
        "relative_backup",
        "non_sibling_stage",
        "non_sibling_backup",
        "stage_equals_backup",
        "output_mismatch",
        "invalid_phase",
        "non_boolean_flag",
    ],
)
def test_journal_rejects_invalid_payload_without_deleting_it(
    tmp_path: Path,
    case: str,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    payload = _invalid_journal_payload(case, transaction)
    _write_payload(transaction.target.journal_path, payload)
    original = transaction.target.journal_path.read_bytes()

    with pytest.raises(RowOnePublishAmbiguousStateError, match="journal") as exc_info:
        _load_journal(transaction.target)

    assert str(transaction.target.journal_path) in str(exc_info.value)
    assert transaction.target.journal_path.read_bytes() == original


def test_journal_rejects_duplicate_json_keys_without_deleting_it(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    payload = json.dumps(_journal_payload(transaction), sort_keys=True)
    duplicate_payload = payload[:-1] + ', "phase": "ready"}\n'
    transaction.target.journal_path.write_text(duplicate_payload, encoding="utf-8")

    with pytest.raises(RowOnePublishAmbiguousStateError, match="journal"):
        _load_journal(transaction.target)

    assert transaction.target.journal_path.read_text(encoding="utf-8") == duplicate_payload


def test_journal_non_object_diagnostic_includes_the_inspected_path(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    original = b"[]\n"
    transaction.target.journal_path.write_bytes(original)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="journal") as exc_info:
        _load_journal(transaction.target)

    assert str(transaction.target.journal_path) in str(exc_info.value)
    assert transaction.target.journal_path.read_bytes() == original


def test_journal_rejects_deeply_nested_json_and_closes_its_descriptor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    depth = sys.getrecursionlimit() * 10
    original = ('{"nested":' * depth + "null" + "}" * depth + "\n").encode()
    transaction.target.journal_path.write_bytes(original)
    opened_descriptors: list[int] = []
    real_open = os.open

    def record_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        descriptor = real_open(path, flags, mode)
        if Path(path) == transaction.target.journal_path:
            opened_descriptors.append(descriptor)
        return descriptor

    monkeypatch.setattr(publish_module.os, "open", record_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="journal") as exc_info:
        _load_journal(transaction.target)

    assert str(transaction.target.journal_path) in str(exc_info.value)
    assert transaction.target.journal_path.read_bytes() == original
    _assert_file_descriptors_closed(opened_descriptors)


@pytest.mark.parametrize("kind", ["symlink", "directory", "fifo", "socket"])
def test_journal_rejects_a_nonregular_canonical_path_without_mutation(
    tmp_path: Path,
    kind: str,
) -> None:
    short_root: tempfile.TemporaryDirectory[str] | None = None
    if kind == "socket":
        short_root = tempfile.TemporaryDirectory(prefix="r1-", dir=tempfile.gettempdir())
        transaction = _transaction_fixture(Path(short_root.name))
    else:
        transaction = _transaction_fixture(tmp_path)
    handle = _create_nonregular_path(transaction.target.journal_path, kind)
    before = transaction.target.journal_path.lstat()

    try:
        with pytest.raises(RowOnePublishAmbiguousStateError, match="journal"):
            _load_journal(transaction.target)

        after = transaction.target.journal_path.lstat()
        assert (after.st_dev, after.st_ino, after.st_mode) == (
            before.st_dev,
            before.st_ino,
            before.st_mode,
        )
    finally:
        if handle is not None:
            handle.close()
        if short_root is not None:
            short_root.cleanup()


@pytest.mark.parametrize("kind", ["symlink", "directory", "fifo", "socket"])
def test_journal_recovery_rejects_a_nonregular_temporary_path_without_mutation(
    tmp_path: Path,
    kind: str,
) -> None:
    short_root: tempfile.TemporaryDirectory[str] | None = None
    if kind == "socket":
        short_root = tempfile.TemporaryDirectory(prefix="r1-", dir=tempfile.gettempdir())
        transaction = _transaction_fixture(Path(short_root.name))
    else:
        transaction = _transaction_fixture(tmp_path)
    temp_path = _temporary_journal_path(transaction)
    handle = _create_nonregular_path(temp_path, kind)
    before = temp_path.lstat()

    try:
        with pytest.raises(RowOnePublishAmbiguousStateError, match="temporary journal"):
            _recover_temporary_journals(transaction.target)

        after = temp_path.lstat()
        assert (after.st_dev, after.st_ino, after.st_mode) == (
            before.st_dev,
            before.st_ino,
            before.st_mode,
        )
        assert not transaction.target.journal_path.exists()
    finally:
        if handle is not None:
            handle.close()
        if short_root is not None:
            short_root.cleanup()


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO files are unavailable")
def test_journal_recovery_preflights_fifo_before_opening_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    fifo = _temporary_journal_path(transaction)
    _make_fifo(fifo)
    opened: list[Path] = []
    real_open = os.open

    def record_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        if Path(path) == fifo:
            opened.append(Path(path))
        return real_open(path, flags, mode)

    monkeypatch.setattr(publish_module.os, "open", record_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="temporary journal"):
        _recover_temporary_journals(transaction.target)

    assert opened == []
    assert fifo.lstat()


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO files are unavailable")
def test_journal_recovery_preflights_mixed_set_before_reading_regular_candidate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    regular = _temporary_journal_path(transaction, nonce="b" * 16)
    fifo = _temporary_journal_path(transaction, nonce="c" * 16)
    _write_payload(regular, _journal_payload(transaction))
    _make_fifo(fifo)
    opened: list[Path] = []
    real_open = os.open

    def record_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        candidate = Path(path)
        if candidate in {regular, fifo}:
            opened.append(candidate)
        return real_open(path, flags, mode)

    monkeypatch.setattr(publish_module.os, "open", record_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="temporary journal"):
        _recover_temporary_journals(transaction.target)

    assert opened == []
    assert regular.exists()
    assert fifo.lstat()


def test_journal_recovery_rejects_changed_temporary_identity_before_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, phase=RowOnePublishPhase.READY)
    temp_path = _temporary_journal_path(transaction)
    _write_payload(temp_path, _journal_payload(transaction))
    replacement = tmp_path / "replacement-journal.json"
    replacement_transaction = replace(transaction, phase=RowOnePublishPhase.PUBLISHED)
    _write_payload(replacement, _journal_payload(replacement_transaction))
    replacement_bytes = replacement.read_bytes()
    real_open = os.open
    swapped = False

    def swap_before_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        nonlocal swapped
        if Path(path) == temp_path and not swapped:
            swapped = True
            os.replace(replacement, temp_path)
        return real_open(path, flags, mode)

    monkeypatch.setattr(publish_module.os, "open", swap_before_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="identity changed"):
        _recover_temporary_journals(transaction.target)

    assert temp_path.read_bytes() == replacement_bytes
    assert not transaction.target.journal_path.exists()


def test_journal_reader_fallback_rejects_inode_to_symlink_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    temp_path = _temporary_journal_path(transaction)
    _write_payload(temp_path, _journal_payload(transaction))
    expected_identity = (temp_path.lstat().st_dev, temp_path.lstat().st_ino)
    outside = tmp_path / "outside-journal.json"
    outside.write_text("outside\n", encoding="utf-8")
    symlink_probe = tmp_path / "symlink-probe"
    _symlink_to(symlink_probe, outside)
    symlink_probe.unlink()
    real_open = os.open
    swapped = False

    def swap_after_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        nonlocal swapped
        descriptor = real_open(path, flags, mode)
        if Path(path) == temp_path and not swapped:
            swapped = True
            temp_path.unlink()
            _symlink_to(temp_path, outside)
        return descriptor

    monkeypatch.delattr(publish_module.os, "O_NOFOLLOW", raising=False)
    monkeypatch.setattr(publish_module.os, "open", swap_after_open)
    reader = getattr(publish_module, "_read_journal_json_object", None)
    assert reader is not None

    with pytest.raises(RowOnePublishAmbiguousStateError, match="identity changed"):
        reader(
            temp_path,
            label="temporary journal",
            expected_identity=expected_identity,
        )

    assert temp_path.is_symlink()
    assert outside.read_text(encoding="utf-8") == "outside\n"


@pytest.mark.parametrize("primary_kind", ["identity", "unsafe", "control_flow"])
def test_journal_reader_preserves_primary_error_when_descriptor_close_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    primary_kind: str,
) -> None:
    path = tmp_path / "journal.json"
    path.write_text('{"value": true}\n', encoding="utf-8")
    metadata = path.lstat()
    expected_identity = (metadata.st_dev, metadata.st_ino)
    opened_descriptors: list[int] = []
    close_calls: list[int] = []
    close_failure = OSError("journal close failure")
    injected_primary: BaseException | None = None
    real_open = os.open
    real_close = os.close
    real_fstat = os.fstat
    real_lstat = Path.lstat

    def record_open(
        opened_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
    ) -> int:
        descriptor = real_open(opened_path, flags, mode)
        if Path(opened_path) == path:
            opened_descriptors.append(descriptor)
        return descriptor

    def fail_close(descriptor: int) -> None:
        if descriptor in opened_descriptors:
            close_calls.append(descriptor)
            raise close_failure
        real_close(descriptor)

    monkeypatch.setattr(publish_module.os, "open", record_open)
    monkeypatch.setattr(publish_module.os, "close", fail_close)

    if primary_kind == "identity":
        injected_primary = RowOnePublishAmbiguousStateError("injected journal identity failure")
        monkeypatch.setattr(
            publish_module,
            "_identity",
            lambda _metadata: (_ for _ in ()).throw(injected_primary),
        )
        expected_type: type[BaseException] = RowOnePublishAmbiguousStateError
    elif primary_kind == "unsafe":

        def report_directory(descriptor: int) -> os.stat_result:
            if descriptor in opened_descriptors:
                return tmp_path.lstat()
            return real_fstat(descriptor)

        monkeypatch.setattr(publish_module.os, "fstat", report_directory)
        expected_type = RowOnePublishAmbiguousStateError
    elif primary_kind == "control_flow":
        injected_primary = KeyboardInterrupt("stop journal verification")

        def stop_after_open(inspected: Path) -> os.stat_result:
            if inspected == path and opened_descriptors:
                raise injected_primary
            return real_lstat(inspected)

        monkeypatch.setattr(Path, "lstat", stop_after_open)
        expected_type = KeyboardInterrupt
    else:
        raise AssertionError(f"unknown primary kind: {primary_kind}")

    try:
        with pytest.raises(expected_type) as exc_info:
            publish_module._read_journal_json_object(
                path,
                label="journal",
                expected_identity=expected_identity,
            )
    finally:
        for descriptor in opened_descriptors:
            try:
                real_close(descriptor)
            except OSError as exc:
                if exc.errno != errno.EBADF:
                    raise

    if injected_primary is not None:
        assert exc_info.value is injected_primary
    else:
        assert type(exc_info.value) is RowOnePublishAmbiguousStateError
        assert "identity changed" in str(exc_info.value)
    notes = getattr(exc_info.value, "__notes__", ())
    assert len(notes) == 1
    assert "journal descriptor close also failed" in notes[0]
    assert f"OSError: {close_failure}" in notes[0]
    assert close_calls == opened_descriptors
    assert path.read_text(encoding="utf-8") == '{"value": true}\n'


def test_journal_reader_surfaces_close_only_failure_once_after_successful_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "journal.json"
    path.write_text('{"value": true}\n', encoding="utf-8")
    metadata = path.lstat()
    expected_identity = (metadata.st_dev, metadata.st_ino)
    opened_descriptors: list[int] = []
    close_calls: list[int] = []
    close_failure = OSError("journal close-only failure")
    real_open = os.open
    real_close = os.close

    def record_open(
        opened_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
    ) -> int:
        descriptor = real_open(opened_path, flags, mode)
        if Path(opened_path) == path:
            opened_descriptors.append(descriptor)
        return descriptor

    def fail_close(descriptor: int) -> None:
        if descriptor in opened_descriptors:
            close_calls.append(descriptor)
            raise close_failure
        real_close(descriptor)

    monkeypatch.setattr(publish_module.os, "open", record_open)
    monkeypatch.setattr(publish_module.os, "close", fail_close)

    try:
        with pytest.raises(OSError) as exc_info:
            publish_module._read_journal_json_object(
                path,
                label="journal",
                expected_identity=expected_identity,
            )
    finally:
        for descriptor in opened_descriptors:
            try:
                real_close(descriptor)
            except OSError as exc:
                if exc.errno != errno.EBADF:
                    raise

    assert exc_info.value is close_failure
    assert close_calls == opened_descriptors
    assert path.read_text(encoding="utf-8") == '{"value": true}\n'


def test_journal_recovery_promotes_one_complete_safe_temporary(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path, phase=RowOnePublishPhase.READY)
    temp_path = _temporary_journal_path(transaction)
    _write_payload(temp_path, _journal_payload(transaction))

    _recover_temporary_journals(transaction.target)

    assert not temp_path.exists()
    assert _load_journal(transaction.target) == transaction


def test_journal_recovery_rejects_temp_inode_swapped_during_promotion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, phase=RowOnePublishPhase.READY)
    temp_path = _temporary_journal_path(transaction)
    _write_payload(temp_path, _journal_payload(transaction))
    replacement = tmp_path / "promotion-replacement.json"
    replacement_transaction = replace(transaction, phase=RowOnePublishPhase.PUBLISHED)
    _write_payload(replacement, _journal_payload(replacement_transaction))
    replacement_bytes = replacement.read_bytes()
    real_replace = os.replace
    swapped = False

    def swap_during_replace(source: Path, destination: Path) -> None:
        nonlocal swapped
        if Path(source) == temp_path and Path(destination) == transaction.target.journal_path:
            assert not swapped
            swapped = True
            real_replace(replacement, temp_path)
        real_replace(source, destination)

    monkeypatch.setattr(publish_module.os, "replace", swap_during_replace)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="identity changed"):
        _recover_temporary_journals(transaction.target)

    assert swapped is True
    assert not temp_path.exists()
    assert transaction.target.journal_path.read_bytes() == replacement_bytes


def test_journal_recovery_removes_one_same_token_temporary_when_canonical_is_valid(
    tmp_path: Path,
) -> None:
    transaction = _transaction_fixture(tmp_path, phase=RowOnePublishPhase.READY)
    _write_payload(transaction.target.journal_path, _journal_payload(transaction))
    temp_transaction = replace(transaction, phase=RowOnePublishPhase.PUBLISHED)
    temp_path = _temporary_journal_path(transaction)
    _write_payload(temp_path, _journal_payload(temp_transaction))

    _recover_temporary_journals(transaction.target)

    assert not temp_path.exists()
    assert _load_journal(transaction.target) == transaction


def test_journal_recovery_preserves_nonunique_temporary_set(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    first = _temporary_journal_path(transaction, nonce="b" * 16)
    second = _temporary_journal_path(transaction, nonce="c" * 16)
    _write_payload(first, _journal_payload(transaction))
    _write_payload(second, _journal_payload(transaction))

    with pytest.raises(RowOnePublishAmbiguousStateError, match="temporary journal"):
        _recover_temporary_journals(transaction.target)

    assert first.exists()
    assert second.exists()
    assert not transaction.target.journal_path.exists()


def test_journal_recovery_preserves_a_mismatched_temporary(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    _write_payload(transaction.target.journal_path, _journal_payload(transaction))
    other = _new_transaction(transaction.target, token="c" * 32)
    temp_path = _temporary_journal_path(other)
    _write_payload(temp_path, _journal_payload(other))

    with pytest.raises(RowOnePublishAmbiguousStateError, match="temporary journal"):
        _recover_temporary_journals(transaction.target)

    assert temp_path.exists()
    assert transaction.target.journal_path.exists()


def test_journal_recovery_preserves_a_malformed_temporary(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    temp_path = _temporary_journal_path(transaction)
    temp_path.write_text("{not json\n", encoding="utf-8")

    with pytest.raises(RowOnePublishAmbiguousStateError, match="temporary journal"):
        _recover_temporary_journals(transaction.target)

    assert temp_path.read_text(encoding="utf-8") == "{not json\n"
    assert not transaction.target.journal_path.exists()


def test_journal_recovery_preserves_a_filename_token_mismatch(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    temp_path = _temporary_journal_path(transaction, token="c" * 32)
    _write_payload(temp_path, _journal_payload(transaction))

    with pytest.raises(RowOnePublishAmbiguousStateError, match="temporary journal"):
        _recover_temporary_journals(transaction.target)

    assert temp_path.exists()
    assert not transaction.target.journal_path.exists()


def test_atomic_journal_write_does_not_replace_a_symlink_destination(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text("outside\n", encoding="utf-8")
    _symlink_to(transaction.target.journal_path, outside)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="journal path is unsafe"):
        _write_journal(transaction)

    assert transaction.target.journal_path.is_symlink()
    assert outside.read_text(encoding="utf-8") == "outside\n"
    assert list(tmp_path.glob(".site.row-one-publish.*.tmp")) == []


def test_atomic_journal_write_fsyncs_the_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    fsynced_modes: list[int] = []

    def record_fsync(descriptor: int) -> None:
        fsynced_modes.append(os.fstat(descriptor).st_mode)

    monkeypatch.setattr(publish_module.os, "fsync", record_fsync)

    _write_journal(transaction)

    assert any(stat.S_ISREG(mode) for mode in fsynced_modes)


def test_atomic_journal_write_attempts_parent_directory_fsync_best_effort(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    directory_descriptor = -12345
    directory_open_flags: list[int] = []
    directory_fsync_attempts: list[int] = []
    closed_descriptors: list[int] = []
    real_open = os.open
    real_fsync = os.fsync
    real_close = os.close

    def record_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        if Path(path) == transaction.target.physical_output.parent:
            directory_open_flags.append(flags)
            return directory_descriptor
        return real_open(path, flags, mode)

    def fail_directory_fsync(descriptor: int) -> None:
        if descriptor == directory_descriptor:
            directory_fsync_attempts.append(descriptor)
            raise OSError("directory fsync unsupported")
        real_fsync(descriptor)

    def record_close(descriptor: int) -> None:
        if descriptor == directory_descriptor:
            closed_descriptors.append(descriptor)
            return
        real_close(descriptor)

    monkeypatch.setattr(publish_module.os, "open", record_open)
    monkeypatch.setattr(publish_module.os, "fsync", fail_directory_fsync)
    monkeypatch.setattr(publish_module.os, "close", record_close)

    _write_journal(transaction)

    assert directory_open_flags
    assert directory_descriptor in directory_fsync_attempts
    assert directory_descriptor in closed_descriptors
    assert transaction.target.journal_path.is_file()


def test_atomic_journal_write_uses_exclusive_create_and_preserves_temp_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    nonce = "b" * 16
    temp_path = _temporary_journal_path(transaction, nonce=nonce)
    original = b"preexisting temporary\n"
    temp_path.write_bytes(original)
    opened_flags: list[int] = []
    real_open = os.open

    def record_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        if Path(path) == temp_path:
            opened_flags.append(flags)
        return real_open(path, flags, mode)

    monkeypatch.setattr(publish_module.secrets, "token_hex", lambda _length: nonce)
    monkeypatch.setattr(publish_module.os, "open", record_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="already exists"):
        _write_journal(transaction)

    assert any(flags & os.O_CREAT and flags & os.O_EXCL for flags in opened_flags)
    assert temp_path.read_bytes() == original
    assert not transaction.target.journal_path.exists()


def test_atomic_journal_write_preserves_a_symlink_temp_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    nonce = "b" * 16
    temp_path = _temporary_journal_path(transaction, nonce=nonce)
    outside = tmp_path / "outside-temp.json"
    outside.write_text("outside\n", encoding="utf-8")
    _symlink_to(temp_path, outside)
    monkeypatch.setattr(publish_module.secrets, "token_hex", lambda _length: nonce)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="already exists"):
        _write_journal(transaction)

    assert temp_path.is_symlink()
    assert outside.read_text(encoding="utf-8") == "outside\n"
    assert not transaction.target.journal_path.exists()


def test_atomic_journal_write_rejects_temp_inode_swapped_during_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, phase=RowOnePublishPhase.READY)
    nonce = "b" * 16
    temp_path = _temporary_journal_path(transaction, nonce=nonce)
    replacement = tmp_path / "writer-replacement.json"
    replacement_transaction = replace(transaction, phase=RowOnePublishPhase.PUBLISHED)
    _write_payload(replacement, _journal_payload(replacement_transaction))
    replacement_bytes = replacement.read_bytes()
    real_replace = os.replace
    swapped = False

    def swap_during_replace(source: Path, destination: Path) -> None:
        nonlocal swapped
        if Path(source) == temp_path and Path(destination) == transaction.target.journal_path:
            assert not swapped
            swapped = True
            real_replace(replacement, temp_path)
        real_replace(source, destination)

    monkeypatch.setattr(publish_module.secrets, "token_hex", lambda _length: nonce)
    monkeypatch.setattr(publish_module.os, "replace", swap_during_replace)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="identity changed"):
        _write_journal(transaction)

    assert swapped is True
    assert not temp_path.exists()
    assert transaction.target.journal_path.read_bytes() == replacement_bytes


def test_atomic_journal_write_removes_its_temporary_when_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError(f"replace failed: {source} -> {destination}")

    monkeypatch.setattr(publish_module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        _write_journal(transaction)

    assert not transaction.target.journal_path.exists()
    assert list(tmp_path.glob(".site.row-one-publish.*.tmp")) == []


def test_atomic_journal_write_preserves_replace_failure_when_temp_unlink_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    nonce = "b" * 16
    temp_path = _temporary_journal_path(transaction, nonce=nonce)
    replace_error = OSError("replace failed")
    unlink_error = OSError("temporary unlink failed")
    real_unlink = Path.unlink

    def fail_replace(_source: Path, _destination: Path) -> None:
        raise replace_error

    def fail_temp_unlink(path: Path, missing_ok: bool = False) -> None:
        if path == temp_path:
            raise unlink_error
        real_unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(publish_module.secrets, "token_hex", lambda _length: nonce)
    monkeypatch.setattr(publish_module.os, "replace", fail_replace)
    monkeypatch.setattr(Path, "unlink", fail_temp_unlink)

    with pytest.raises(OSError, match="replace failed") as exc_info:
        _write_journal(transaction)

    assert exc_info.value is replace_error
    assert any(
        "temporary unlink failed" in note for note in getattr(exc_info.value, "__notes__", ())
    )
    assert temp_path.is_file()
    assert not transaction.target.journal_path.exists()


def test_atomic_journal_write_surfaces_cleanup_failure_without_a_primary_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    nonce = "b" * 16
    temp_path = _temporary_journal_path(transaction, nonce=nonce)
    cleanup_error = OSError("temporary cleanup inspection failed")
    real_lstat = Path.lstat

    def fail_cleanup_inspection(path: Path) -> os.stat_result:
        if path == temp_path and transaction.target.journal_path.exists():
            raise cleanup_error
        return real_lstat(path)

    monkeypatch.setattr(publish_module.secrets, "token_hex", lambda _length: nonce)
    monkeypatch.setattr(Path, "lstat", fail_cleanup_inspection)

    with pytest.raises(OSError, match="cleanup inspection failed") as exc_info:
        _write_journal(transaction)

    assert exc_info.value is cleanup_error
    assert transaction.target.journal_path.is_file()
    assert not temp_path.exists()


def test_atomic_journal_write_surfaces_cleanup_failure_inside_unrelated_except(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    nonce = "b" * 16
    temp_path = _temporary_journal_path(transaction, nonce=nonce)
    ambient_error = RuntimeError("unrelated caller failure")
    cleanup_error = OSError("temporary cleanup inspection failed")
    real_lstat = Path.lstat

    def fail_cleanup_inspection(path: Path) -> os.stat_result:
        if path == temp_path and transaction.target.journal_path.exists():
            raise cleanup_error
        return real_lstat(path)

    monkeypatch.setattr(publish_module.secrets, "token_hex", lambda _length: nonce)
    monkeypatch.setattr(Path, "lstat", fail_cleanup_inspection)

    try:
        raise ambient_error
    except RuntimeError as handled_error:
        assert handled_error is ambient_error
        with pytest.raises(OSError, match="cleanup inspection failed") as exc_info:
            _write_journal(transaction)

    assert exc_info.value is cleanup_error
    assert getattr(ambient_error, "__notes__", ()) == ()
    assert transaction.target.journal_path.is_file()
    assert not temp_path.exists()


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


def test_publish_lock_rejects_deeply_nested_metadata_and_closes_its_descriptor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    depth = sys.getrecursionlimit() * 10
    original = ('{"nested":' * depth + "null" + "}" * depth + "\n").encode()
    target.lock_path.write_bytes(original)
    opened_descriptors: list[int] = []
    real_open = os.open

    def record_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        descriptor = real_open(path, flags, mode)
        if Path(path) == target.lock_path:
            opened_descriptors.append(descriptor)
        return descriptor

    monkeypatch.setattr(publish_module.os, "open", record_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="lock file") as exc_info:
        with _acquire_publish_lock(target):
            pytest.fail("deeply nested metadata must not acquire the publish lock")

    assert str(target.lock_path) in str(exc_info.value)
    assert target.lock_path.read_bytes() == original
    _assert_file_descriptors_closed(opened_descriptors)


def test_publish_lock_recovers_preexisting_empty_file(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.lock_path.touch()

    with _acquire_publish_lock(target):
        payload = json.loads(target.lock_path.read_text(encoding="utf-8"))

    assert payload == {
        "contract_version": ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION,
        "physical_output": str(target.physical_output),
    }


def test_publish_lock_is_stable_across_acquisitions(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")

    with _acquire_publish_lock(target):
        first_identity = target.lock_path.lstat().st_ino
    with _acquire_publish_lock(target):
        second_identity = target.lock_path.lstat().st_ino

    assert second_identity == first_identity
    assert target.lock_path.is_file()


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"contract_version": ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION}, "lock file"),
        (
            {
                "contract_version": ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION,
                "physical_output": "/wrong/output",
            },
            "lock file",
        ),
    ],
)
def test_publish_lock_rejects_inexact_metadata_without_overwriting(
    tmp_path: Path,
    payload: dict[str, object],
    message: str,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    original = json.dumps(payload, sort_keys=True) + "\n"
    target.lock_path.write_text(original, encoding="utf-8")

    with pytest.raises(RowOnePublishAmbiguousStateError, match=message):
        with _acquire_publish_lock(target):
            pytest.fail("inexact metadata must fail")

    assert target.lock_path.read_text(encoding="utf-8") == original


def test_publish_lock_rejects_extra_key_with_otherwise_correct_metadata(
    tmp_path: Path,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    payload = {
        "contract_version": ROW_ONE_PUBLISH_LOCK_CONTRACT_VERSION,
        "physical_output": str(target.physical_output),
        "extra": True,
    }
    original = json.dumps(payload, sort_keys=True) + "\n"
    target.lock_path.write_text(original, encoding="utf-8")

    with pytest.raises(RowOnePublishAmbiguousStateError, match="lock file"):
        with _acquire_publish_lock(target):
            pytest.fail("extra lock metadata must fail")

    assert target.lock_path.read_text(encoding="utf-8") == original


@pytest.mark.parametrize("kind", ["symlink", "directory", "fifo", "socket"])
def test_publish_lock_rejects_a_nonregular_path_without_mutation(
    tmp_path: Path,
    kind: str,
) -> None:
    short_root: tempfile.TemporaryDirectory[str] | None = None
    if kind == "socket":
        short_root = tempfile.TemporaryDirectory(prefix="r1-", dir=tempfile.gettempdir())
        target = _resolve_publish_target(Path(short_root.name) / "site")
    else:
        target = _resolve_publish_target(tmp_path / "site")
    handle = _create_nonregular_path(target.lock_path, kind)
    before = target.lock_path.lstat()

    try:
        with pytest.raises(RowOnePublishAmbiguousStateError, match="lock file"):
            with _acquire_publish_lock(target):
                pytest.fail("a nonregular lock path must fail")

        after = target.lock_path.lstat()
        assert (after.st_dev, after.st_ino, after.st_mode) == (
            before.st_dev,
            before.st_ino,
            before.st_mode,
        )
    finally:
        if handle is not None:
            handle.close()
        if short_root is not None:
            short_root.cleanup()


def test_publish_lock_fallback_rejects_an_inode_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.lock_path.write_bytes(b"")
    replacement = tmp_path / "replacement.lock"
    replacement.write_text("replacement\n", encoding="utf-8")
    real_open = os.open
    swapped = False

    def swap_before_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        nonlocal swapped
        if Path(path) == target.lock_path and not swapped:
            swapped = True
            os.replace(replacement, target.lock_path)
        return real_open(path, flags, mode)

    monkeypatch.delattr(publish_module.os, "O_NOFOLLOW", raising=False)
    monkeypatch.setattr(publish_module.os, "open", swap_before_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="identity changed"):
        _open_lock_file(target)

    assert target.lock_path.read_text(encoding="utf-8") == "replacement\n"


def test_publish_lock_maps_post_open_path_disappearance_to_ambiguous_and_closes_descriptor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.lock_path.write_bytes(b"")
    opened_descriptors: list[int] = []
    real_open = os.open
    real_lstat = Path.lstat

    def record_open(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        descriptor = real_open(path, flags, mode)
        if Path(path) == target.lock_path:
            opened_descriptors.append(descriptor)
        return descriptor

    def disappear_after_open(path: Path) -> os.stat_result:
        if path == target.lock_path and opened_descriptors:
            raise FileNotFoundError(path)
        return real_lstat(path)

    monkeypatch.setattr(publish_module.os, "open", record_open)
    monkeypatch.setattr(Path, "lstat", disappear_after_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="lock file.*disappeared"):
        _open_lock_file(target)

    _assert_file_descriptors_closed(opened_descriptors)


@pytest.mark.parametrize("primary_kind", ["identity", "unsafe", "control_flow"])
def test_verified_lock_handle_preserves_primary_error_when_descriptor_close_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    primary_kind: str,
) -> None:
    path = tmp_path / "publish.lock"
    path.write_bytes(b"")
    descriptor = os.open(path, os.O_RDWR)
    metadata = path.lstat()
    expected_identity = (metadata.st_dev, metadata.st_ino)
    close_calls: list[int] = []
    close_failure = OSError("lock descriptor close failure")
    injected_primary: BaseException | None = None
    real_close = os.close
    real_fstat = os.fstat

    def fail_close(open_descriptor: int) -> None:
        if open_descriptor == descriptor:
            close_calls.append(open_descriptor)
            raise close_failure
        real_close(open_descriptor)

    monkeypatch.setattr(publish_module.os, "close", fail_close)

    if primary_kind == "identity":
        injected_primary = RowOnePublishAmbiguousStateError("injected lock identity failure")
        monkeypatch.setattr(
            publish_module,
            "_identity",
            lambda _metadata: (_ for _ in ()).throw(injected_primary),
        )
        expected_type: type[BaseException] = RowOnePublishAmbiguousStateError
    elif primary_kind == "unsafe":

        def report_directory(open_descriptor: int) -> os.stat_result:
            if open_descriptor == descriptor:
                return tmp_path.lstat()
            return real_fstat(open_descriptor)

        monkeypatch.setattr(publish_module.os, "fstat", report_directory)
        expected_type = RowOnePublishAmbiguousStateError
    elif primary_kind == "control_flow":
        injected_primary = SystemExit("stop lock verification")
        monkeypatch.setattr(
            publish_module.os,
            "fdopen",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(injected_primary),
        )
        expected_type = SystemExit
    else:
        raise AssertionError(f"unknown primary kind: {primary_kind}")

    try:
        with pytest.raises(expected_type) as exc_info:
            publish_module._verified_lock_handle(
                path,
                descriptor,
                expected_identity=expected_identity,
            )
    finally:
        try:
            real_close(descriptor)
        except OSError as exc:
            if exc.errno != errno.EBADF:
                raise

    if injected_primary is not None:
        assert exc_info.value is injected_primary
    else:
        assert type(exc_info.value) is RowOnePublishAmbiguousStateError
        assert "not regular" in str(exc_info.value)
    notes = getattr(exc_info.value, "__notes__", ())
    assert len(notes) == 1
    assert "lock file descriptor close also failed" in notes[0]
    assert f"OSError: {close_failure}" in notes[0]
    assert close_calls == [descriptor]


def test_publish_lock_acquires_os_lock_before_validating_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    calls: list[str] = []
    real_try_lock = publish_module._try_lock_handle
    real_validate = publish_module._validate_or_initialize_lock_metadata

    def record_lock(handle) -> None:
        calls.append("lock")
        real_try_lock(handle)

    def record_validate(handle, locked_target) -> None:
        calls.append("validate")
        real_validate(handle, locked_target)

    monkeypatch.setattr(publish_module, "_try_lock_handle", record_lock)
    monkeypatch.setattr(
        publish_module,
        "_validate_or_initialize_lock_metadata",
        record_validate,
    )

    with _acquire_publish_lock(target):
        assert calls == ["lock", "validate"]


def test_publish_lock_preserves_active_body_error_when_unlock_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    body_error = RuntimeError("publish body failed")
    unlock_error = OSError("unlock failed")

    def fail_unlock(_handle) -> None:
        raise unlock_error

    monkeypatch.setattr(publish_module, "_unlock_handle", fail_unlock)

    with pytest.raises(RuntimeError, match="publish body failed") as exc_info:
        with _acquire_publish_lock(target):
            raise body_error

    assert exc_info.value is body_error
    assert any("unlock failed" in note for note in getattr(exc_info.value, "__notes__", ()))


def test_publish_lock_surfaces_unlock_failure_without_an_active_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    unlock_error = OSError("unlock failed")

    def fail_unlock(_handle) -> None:
        raise unlock_error

    monkeypatch.setattr(publish_module, "_unlock_handle", fail_unlock)

    with pytest.raises(OSError, match="unlock failed") as exc_info:
        with _acquire_publish_lock(target):
            pass

    assert exc_info.value is unlock_error


def test_publish_lock_surfaces_unlock_failure_inside_unrelated_except(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    ambient_error = RuntimeError("unrelated caller failure")
    unlock_error = OSError("unlock failed")

    def fail_unlock(_handle) -> None:
        raise unlock_error

    monkeypatch.setattr(publish_module, "_unlock_handle", fail_unlock)

    try:
        raise ambient_error
    except RuntimeError as handled_error:
        assert handled_error is ambient_error
        with pytest.raises(OSError, match="unlock failed") as exc_info:
            with _acquire_publish_lock(target):
                pass

    assert exc_info.value is unlock_error
    assert getattr(ambient_error, "__notes__", ()) == ()


def test_publish_lock_uses_posix_nonblocking_exclusive_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_fcntl = types.ModuleType("fcntl")
    fake_fcntl.LOCK_EX = 2
    fake_fcntl.LOCK_NB = 4
    calls: list[tuple[int, int]] = []
    fake_fcntl.flock = lambda descriptor, operation: calls.append((descriptor, operation))
    monkeypatch.setitem(sys.modules, "fcntl", fake_fcntl)
    monkeypatch.setattr(publish_module.os, "name", "posix")

    class Handle:
        def fileno(self) -> int:
            return 17

    _try_lock_handle(Handle())  # type: ignore[arg-type]

    assert calls == [(17, fake_fcntl.LOCK_EX | fake_fcntl.LOCK_NB)]


def test_publish_lock_uses_windows_nonblocking_byte_range_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_msvcrt = types.ModuleType("msvcrt")
    fake_msvcrt.LK_NBLCK = 3
    fake_msvcrt.LK_UNLCK = 4
    calls: list[tuple[int, int, int]] = []
    fake_msvcrt.locking = lambda descriptor, operation, count: calls.append(
        (descriptor, operation, count)
    )
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(publish_module.os, "name", "nt")

    class Handle:
        def __init__(self) -> None:
            self.seeks: list[int] = []

        def fileno(self) -> int:
            return 23

        def seek(self, offset: int) -> None:
            self.seeks.append(offset)

    handle = Handle()
    _try_lock_handle(handle)  # type: ignore[arg-type]
    _unlock_handle(handle)  # type: ignore[arg-type]

    assert handle.seeks == [0, 0]
    assert calls == [
        (23, fake_msvcrt.LK_NBLCK, 1),
        (23, fake_msvcrt.LK_UNLCK, 1),
    ]


def test_publish_lock_maps_windows_lock_failure_to_busy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_msvcrt = types.ModuleType("msvcrt")
    fake_msvcrt.LK_NBLCK = 3

    def fail_lock(_descriptor: int, _operation: int, _count: int) -> None:
        raise OSError("locked")

    fake_msvcrt.locking = fail_lock
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(publish_module.os, "name", "nt")

    class Handle:
        def fileno(self) -> int:
            return 23

        def seek(self, _offset: int) -> None:
            pass

    with pytest.raises(RowOnePublishBusyError, match="already in progress"):
        _try_lock_handle(Handle())  # type: ignore[arg-type]


def _write_valid_owner_file(
    directory: Path,
    transaction: RowOnePublishTransaction,
    **overrides: object,
) -> Path:
    owner_path = directory / ROW_ONE_PUBLISH_OWNER_PATH
    owner_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "contract_version": ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION,
        "physical_output": str(transaction.target.physical_output),
        "token": transaction.token,
    }
    payload.update(overrides)
    _write_payload(owner_path, payload)
    return owner_path


def _staged_publish_fixture(
    tmp_path: Path,
) -> tuple[RowOnePublishTransaction, types.SimpleNamespace]:
    transaction = _transaction_fixture(tmp_path)
    stage = transaction.stage_path
    (stage / "data").mkdir(parents=True)
    (stage / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (stage / "index.html").write_text("new", encoding="utf-8")
    _write_payload(stage / "data" / "edition.json", {"stories": []})
    _write_payload(stage / "data" / "manifest.json", {"manifest": "disk"})
    _write_payload(stage / "data" / "runtime.json", {"runtime": "disk"})
    _write_valid_owner_file(stage, transaction)
    result = types.SimpleNamespace(
        output_dir=stage,
        index_path=stage / "index.html",
        edition={"stories": [{"id": "memory-only"}]},
    )
    return transaction, result


def _published_publish_fixture(tmp_path: Path) -> RowOnePublishTransaction:
    transaction = _transaction_fixture(tmp_path)
    live = transaction.target.physical_output
    data = live / "data"
    data.mkdir(parents=True, exist_ok=True)
    (live / "index.html").write_text("published", encoding="utf-8")
    _write_payload(data / "edition.json", {"stories": []})
    _write_payload(data / "manifest.json", {"manifest": "published"})
    _write_payload(data / "runtime.json", {"runtime": "published"})
    _write_valid_owner_file(live, transaction)
    return transaction


def _create_owned_stage(transaction: RowOnePublishTransaction) -> Path:
    stage = transaction.stage_path
    (stage / "data").mkdir(parents=True)
    _write_valid_owner_file(stage, transaction)
    return stage


def _write_transaction_journal(transaction: RowOnePublishTransaction) -> None:
    _write_payload(transaction.target.journal_path, _journal_payload(transaction))


def _write_transaction_temporary_journal(
    transaction: RowOnePublishTransaction,
    *,
    nonce: str = "b" * 16,
) -> Path:
    path = _temporary_journal_path(transaction, nonce=nonce)
    _write_payload(path, _journal_payload(transaction))
    return path


def _ready_commit_fixture(
    tmp_path: Path,
    *,
    had_live_output: bool,
) -> RowOnePublishTransaction:
    transaction = _transaction_fixture(tmp_path, create_live=had_live_output)
    stage = transaction.stage_path
    (stage / "data").mkdir(parents=True)
    (stage / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (stage / "index.html").write_text("new", encoding="utf-8")
    _write_payload(stage / "data" / "edition.json", {"stories": []})
    _write_payload(stage / "data" / "manifest.json", {"manifest": "new"})
    _write_payload(stage / "data" / "runtime.json", {"runtime": "new"})
    _write_valid_owner_file(stage, transaction)
    transaction = replace(transaction, phase=RowOnePublishPhase.READY)
    _write_transaction_journal(transaction)
    return transaction


def _patch_published_validators(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", lambda _path: None)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )


def _write_complete_recovery_site(
    directory: Path,
    *,
    index: str,
    transaction: RowOnePublishTransaction | None = None,
) -> None:
    data = directory / "data"
    data.mkdir(parents=True, exist_ok=True)
    (directory / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (directory / "index.html").write_text(index, encoding="utf-8")
    _write_payload(data / "edition.json", {"stories": []})
    _write_payload(data / "manifest.json", {"manifest": index})
    _write_payload(data / "runtime.json", {"runtime": index})
    if transaction is not None:
        _write_valid_owner_file(directory, transaction)


def _recovery_transaction(
    tmp_path: Path,
    *,
    phase: RowOnePublishPhase,
    had_live_output: bool,
    had_site_marker: bool,
    had_index: bool,
) -> RowOnePublishTransaction:
    target = _resolve_publish_target(tmp_path / "site")
    transaction = _new_transaction(target, token="a" * 32)
    return replace(
        transaction,
        phase=phase,
        had_live_output=had_live_output,
        had_site_marker=had_site_marker,
        had_index=had_index,
    )


def _render_valid_staged_site(
    stage: Path,
    *,
    index: str = "new",
) -> types.SimpleNamespace:
    data = stage / "data"
    data.mkdir(parents=True, exist_ok=True)
    (stage / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (stage / "index.html").write_text(index, encoding="utf-8")
    _write_payload(data / "edition.json", {"stories": []})
    _write_payload(data / "manifest.json", {"manifest": index})
    _write_payload(data / "runtime.json", {"runtime": index})
    return types.SimpleNamespace(output_dir=stage, index_path=stage / "index.html")


def _generated_site_bytes(directory: Path) -> dict[Path, bytes]:
    relative_paths = (
        Path(".row-one-site"),
        Path("index.html"),
        Path("data/edition.json"),
        Path("data/manifest.json"),
        Path("data/runtime.json"),
    )
    return {
        relative_path: (directory / relative_path).read_bytes() for relative_path in relative_paths
    }


def _assert_no_transaction_debris(output: Path) -> None:
    parent = output.resolve(strict=False).parent
    name = output.resolve(strict=False).name
    assert not (parent / f".{name}.row-one-publish.json").exists()
    assert list(parent.glob(f".{name}.row-one-publish.*.tmp")) == []
    assert list(parent.glob(f".{name}.row-one-stage-*")) == []
    assert list(parent.glob(f".{name}.row-one-backup-*")) == []
    if output.exists():
        assert not (output / ROW_ONE_PUBLISH_OWNER_PATH).exists()


def _install_full_path_swap_spy(
    monkeypatch: pytest.MonkeyPatch,
    *,
    final_path: Path,
    directory: Path,
    external_directory: Path,
) -> list[Path]:
    real_open = publish_module.os.open
    displaced = directory.with_name(f"{directory.name}-displaced")
    swaps: list[Path] = []

    def swap_before_full_path_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None and os.fspath(path) == os.fspath(final_path):
            directory.rename(displaced)
            _symlink_to(directory, external_directory, target_is_directory=True)
            swaps.append(directory)
        if dir_fd is None:
            return real_open(path, flags, mode)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(publish_module.os, "open", swap_before_full_path_open)
    return swaps


def _assert_safe_directory_handle_capability_error(
    exc_info: pytest.ExceptionInfo[RowOnePublishError],
) -> None:
    assert type(exc_info.value) is RowOnePublishError
    assert str(exc_info.value) == (
        "ROW ONE safe directory handles are unsupported on this platform"
    )


_REQUIRES_SAFE_DIRECTORY_OPERATIONS = pytest.mark.skipif(
    not publish_module._SAFE_DIRECTORY_OPERATIONS_SUPPORTED,
    reason="safe directory-relative operations are unavailable",
)


def _exercise_verified_directory_context(
    tmp_path: Path,
    context_kind: str,
    body: Callable[[int], None],
    *,
    close_parent: Callable[[int], None] = os.close,
) -> None:
    root = tmp_path / f"{context_kind}-root"
    root.mkdir()
    if context_kind == "root":
        with publish_module._open_verified_directory(
            root, label="test root directory"
        ) as descriptor:
            body(descriptor)
        return
    if context_kind != "child":
        raise AssertionError(f"unknown directory context kind: {context_kind}")
    (root / "data").mkdir()
    parent_descriptor = os.open(root, publish_module._directory_open_flags())
    try:
        with publish_module._open_verified_child_directory(
            parent_descriptor,
            root,
            "data",
            label="test child directory",
        ) as descriptor:
            body(descriptor)
    finally:
        close_parent(parent_descriptor)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("context_kind", ["root", "child"])
def test_verified_directory_open_preserves_identity_error_when_close_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    context_kind: str,
) -> None:
    root = tmp_path / f"{context_kind}-verification-root"
    child = root / "data"
    child.mkdir(parents=True)
    parent_descriptor: int | None = None
    opened_descriptors: list[int] = []
    primary_failure = RowOnePublishAmbiguousStateError("injected identity failure")
    close_failure = OSError(f"{context_kind} verification close failure")
    real_open = os.open
    real_close = os.close
    before = {
        path.relative_to(root): (path.lstat().st_dev, path.lstat().st_ino) for path in (root, child)
    }

    def record_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            descriptor = real_open(path, flags, mode)
        else:
            descriptor = real_open(path, flags, mode, dir_fd=dir_fd)
        opened_descriptors.append(descriptor)
        return descriptor

    def fail_identity(_metadata: os.stat_result) -> tuple[int, int]:
        raise primary_failure

    def fail_verified_descriptor_close(descriptor: int) -> None:
        if descriptor in opened_descriptors:
            raise close_failure
        real_close(descriptor)

    if context_kind == "child":
        parent_descriptor = real_open(root, publish_module._directory_open_flags())
    monkeypatch.setattr(publish_module.os, "open", record_open)
    monkeypatch.setattr(publish_module, "_identity", fail_identity)
    monkeypatch.setattr(publish_module.os, "close", fail_verified_descriptor_close)

    try:
        with pytest.raises(RowOnePublishAmbiguousStateError) as exc_info:
            if context_kind == "root":
                with publish_module._open_verified_directory(
                    root,
                    label="test root directory",
                ):
                    pytest.fail("identity verification must fail before yield")
            else:
                assert parent_descriptor is not None
                with publish_module._open_verified_child_directory(
                    parent_descriptor,
                    root,
                    child.name,
                    label="test child directory",
                ):
                    pytest.fail("identity verification must fail before yield")
    finally:
        for descriptor in opened_descriptors:
            try:
                real_close(descriptor)
            except OSError as exc:
                if exc.errno != errno.EBADF:
                    raise
        if parent_descriptor is not None:
            real_close(parent_descriptor)

    assert exc_info.value is primary_failure
    notes = getattr(primary_failure, "__notes__", ())
    assert len(notes) == 1
    assert "directory close also failed" in notes[0]
    assert f"OSError: {close_failure}" in notes[0]
    _assert_file_descriptors_closed(opened_descriptors)
    assert {
        path.relative_to(root): (path.lstat().st_dev, path.lstat().st_ino) for path in (root, child)
    } == before


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("context_kind", ["root", "child"])
def test_verified_directory_context_propagates_body_oserror_by_identity(
    tmp_path: Path,
    context_kind: str,
) -> None:
    failure = OSError("body disk failure")

    def fail_body(_descriptor: int) -> None:
        raise failure

    with pytest.raises(OSError) as exc_info:
        _exercise_verified_directory_context(tmp_path, context_kind, fail_body)

    assert exc_info.value is failure


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("context_kind", ["root", "child"])
def test_verified_directory_context_preserves_body_error_when_close_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    context_kind: str,
) -> None:
    body_failure = RuntimeError("body failure")
    close_failure = OSError("close failure")
    opened_descriptors: list[int] = []
    real_close = os.close

    def fail_body(descriptor: int) -> None:
        opened_descriptors.append(descriptor)
        raise body_failure

    def fail_body_descriptor_close(descriptor: int) -> None:
        if opened_descriptors and descriptor == opened_descriptors[0]:
            raise close_failure
        real_close(descriptor)

    monkeypatch.setattr(publish_module.os, "close", fail_body_descriptor_close)

    try:
        with pytest.raises(RuntimeError) as exc_info:
            _exercise_verified_directory_context(tmp_path, context_kind, fail_body)
    finally:
        if opened_descriptors:
            real_close(opened_descriptors[0])

    assert exc_info.value is body_failure
    notes = getattr(body_failure, "__notes__", ())
    assert len(notes) == 1
    assert "directory close also failed" in notes[0]
    assert "OSError: close failure" in notes[0]


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("context_kind", ["root", "child"])
def test_verified_directory_context_surfaces_close_error_after_successful_body(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    context_kind: str,
) -> None:
    close_failure = OSError("close failure")
    opened_descriptors: list[int] = []
    real_close = os.close

    def record_body(descriptor: int) -> None:
        opened_descriptors.append(descriptor)

    def fail_body_descriptor_close(descriptor: int) -> None:
        if opened_descriptors and descriptor == opened_descriptors[0]:
            raise close_failure
        real_close(descriptor)

    monkeypatch.setattr(publish_module.os, "close", fail_body_descriptor_close)

    try:
        with pytest.raises(OSError) as exc_info:
            _exercise_verified_directory_context(tmp_path, context_kind, record_body)
    finally:
        if opened_descriptors:
            real_close(opened_descriptors[0])

    assert exc_info.value is close_failure


def test_safe_directory_operations_supported_matches_exact_platform_contract() -> None:
    expected = (
        all(function in os.supports_dir_fd for function in (os.open, os.stat, os.mkdir, os.unlink))
        and hasattr(os, "O_DIRECTORY")
        and hasattr(os, "O_NOFOLLOW")
    )

    assert getattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", None) is expected


@pytest.mark.parametrize("missing_name", [None, "open", "stat", "mkdir", "unlink"])
def test_safe_directory_operations_supported_requires_all_directory_fd_operations(
    monkeypatch: pytest.MonkeyPatch,
    missing_name: str | None,
) -> None:
    required = {
        "open": publish_module.os.open,
        "stat": publish_module.os.stat,
        "mkdir": publish_module.os.mkdir,
        "unlink": publish_module.os.unlink,
    }
    supported = set(required.values())
    if missing_name is not None:
        supported.remove(required[missing_name])
    monkeypatch.setattr(publish_module.os, "supports_dir_fd", supported)
    monkeypatch.setattr(publish_module.os, "O_DIRECTORY", 1, raising=False)
    monkeypatch.setattr(publish_module.os, "O_NOFOLLOW", 2, raising=False)

    assert publish_module._safe_directory_operations_supported() is (missing_name is None)


@pytest.mark.parametrize("missing_flag", ["O_DIRECTORY", "O_NOFOLLOW"])
def test_safe_directory_operations_supported_requires_each_open_flag(
    monkeypatch: pytest.MonkeyPatch,
    missing_flag: str,
) -> None:
    monkeypatch.setattr(
        publish_module.os,
        "supports_dir_fd",
        {
            publish_module.os.open,
            publish_module.os.stat,
            publish_module.os.mkdir,
            publish_module.os.unlink,
        },
    )
    monkeypatch.setattr(publish_module.os, "O_DIRECTORY", 1, raising=False)
    monkeypatch.setattr(publish_module.os, "O_NOFOLLOW", 2, raising=False)
    monkeypatch.delattr(publish_module.os, missing_flag)

    assert publish_module._safe_directory_operations_supported() is False


def test_public_publish_gate_uses_import_time_capability_before_any_side_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "missing-parent" / "site"
    render_calls: list[Path] = []

    def redetection_is_forbidden() -> bool:
        raise AssertionError("public gate must use the import-time capability snapshot")

    def render(stage: Path) -> types.SimpleNamespace:
        render_calls.append(stage)
        return types.SimpleNamespace(output_dir=stage, index_path=stage / "index.html")

    monkeypatch.setattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", False)
    monkeypatch.setattr(
        publish_module,
        "_safe_directory_operations_supported",
        redetection_is_forbidden,
    )

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module.publish_latest_row_one_site(output, render=render)

    _assert_safe_directory_handle_capability_error(exc_info)
    assert not output.parent.exists()
    assert render_calls == []


def test_non_latest_renderer_bypasses_publish_capability_gate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fashion_radar.row_one.models import RowOneEdition
    from fashion_radar.row_one.render import render_row_one_site

    output = tmp_path / "site"
    edition = RowOneEdition.model_validate(
        {
            "generated_at": "2026-07-15T00:00:00Z",
            "edition_date": "2026-07-15T00:00:00Z",
            "summary": {"en": "Summary", "zh": "Summary"},
        }
    )
    monkeypatch.setattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", False)

    result = render_row_one_site(edition, output, latest_only=False)

    assert result.output_dir == output
    assert result.index_path == output / "index.html"
    assert result.index_path.is_file()


def test_move_publish_path_moves_source_to_destination(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    (source / "value.txt").write_text("new", encoding="utf-8")

    publish_module._move_publish_path(source, destination)

    assert not source.exists()
    assert (destination / "value.txt").read_text(encoding="utf-8") == "new"


@pytest.mark.parametrize("kind", ["file", "directory", "symlink"])
def test_remove_publish_path_removes_supported_path_types(
    tmp_path: Path,
    kind: str,
) -> None:
    path = tmp_path / "owned"
    if kind == "file":
        path.write_text("owned", encoding="utf-8")
    elif kind == "directory":
        path.mkdir()
        (path / "child.txt").write_text("owned", encoding="utf-8")
    else:
        target = tmp_path / "external.txt"
        target.write_text("external", encoding="utf-8")
        _symlink_to(path, target)

    publish_module._remove_publish_path(path)

    assert not path.exists()
    assert not path.is_symlink()
    if kind == "symlink":
        assert target.read_text(encoding="utf-8") == "external"


def test_remove_publish_path_rejects_unsupported_file_type_without_mutation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "owned.fifo"
    handle = _create_nonregular_path(path, "fifo")

    try:
        with pytest.raises(RowOnePublishAmbiguousStateError, match="unsupported file type"):
            publish_module._remove_publish_path(path)
    finally:
        if handle is not None:
            handle.close()

    assert path.exists()


def test_replace_phase_persists_and_returns_a_new_transaction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    writes: list[RowOnePublishTransaction] = []
    monkeypatch.setattr(publish_module, "_write_journal", writes.append)

    updated = publish_module._replace_phase(transaction, RowOnePublishPhase.READY)

    assert transaction.phase is RowOnePublishPhase.STAGING
    assert updated == replace(transaction, phase=RowOnePublishPhase.READY)
    assert writes == [updated]


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_live_owner_reader_returns_none_only_for_a_missing_final_owner(
    tmp_path: Path,
) -> None:
    transaction = _published_publish_fixture(tmp_path)
    live = transaction.target.physical_output
    owner = live / ROW_ONE_PUBLISH_OWNER_PATH

    assert publish_module._read_owner_token_if_present(live) == transaction.token

    owner.unlink()

    assert publish_module._read_owner_token_if_present(live) is None


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize(
    "helper_name",
    [
        "_read_owner_token_if_present",
        "_validate_published_row_one_site",
        "_is_owned_live",
        "_remove_owner_file_if_present",
    ],
)
def test_live_owner_consumers_reject_mismatched_embedded_physical_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    helper_name: str,
) -> None:
    transaction = _published_publish_fixture(tmp_path)
    live = transaction.target.physical_output
    owner = live / ROW_ONE_PUBLISH_OWNER_PATH
    _write_valid_owner_file(
        live,
        transaction,
        physical_output=str(live.parent / "different-site"),
    ).replace(owner)
    before = owner.read_bytes()
    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", lambda _path: None)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    helper = getattr(publish_module, helper_name)
    with pytest.raises(RowOnePublishAmbiguousStateError, match="physical output"):
        if helper_name == "_read_owner_token_if_present":
            helper(live)
        else:
            helper(transaction)

    assert owner.read_bytes() == before


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("ancestor", ["root", "data"])
@pytest.mark.parametrize(
    "helper_name",
    [
        "_read_owner_token_if_present",
        "_validate_published_row_one_site",
        "_is_owned_live",
        "_remove_owner_file_if_present",
    ],
)
def test_live_owner_consumers_reject_symlinked_ancestors_without_external_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ancestor: str,
    helper_name: str,
) -> None:
    transaction = _published_publish_fixture(tmp_path)
    live = transaction.target.physical_output
    external = tmp_path / f"external-{ancestor}-{helper_name}"
    external.mkdir()
    external_data = external / "data"
    external_data.mkdir()
    (external / ".row-one-site").write_text("external marker\n", encoding="utf-8")
    (external / "index.html").write_text("external index", encoding="utf-8")
    _write_payload(external_data / "edition.json", {"stories": []})
    _write_payload(external_data / "manifest.json", {"external": "manifest"})
    _write_payload(external_data / "runtime.json", {"external": "runtime"})
    external_owner = external_data / ROW_ONE_PUBLISH_OWNER_PATH.name
    _write_payload(
        external_owner,
        {
            "contract_version": ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION,
            "physical_output": str(live),
            "token": transaction.token,
        },
    )
    before = {
        path.relative_to(external): path.read_bytes()
        for path in external.rglob("*")
        if path.is_file()
    }

    if ancestor == "root":
        displaced = live.with_name("displaced-live")
        live.rename(displaced)
        _symlink_to(live, external, target_is_directory=True)
    else:
        displaced = live / "displaced-data"
        (live / "data").rename(displaced)
        _symlink_to(live / "data", external_data, target_is_directory=True)

    validator_calls: list[Path] = []

    def record_validator(path: Path) -> None:
        validator_calls.append(path)

    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", record_validator)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: pytest.fail("integrity validation must not inspect external data"),
    )

    helper = getattr(publish_module, helper_name)
    with pytest.raises(RowOnePublishAmbiguousStateError):
        if helper_name == "_read_owner_token_if_present":
            helper(live)
        else:
            helper(transaction)

    if helper_name == "_validate_published_row_one_site":
        assert validator_calls == []
    assert {
        path.relative_to(external): path.read_bytes()
        for path in external.rglob("*")
        if path.is_file()
    } == before


@pytest.mark.parametrize(
    "helper_name",
    [
        "_read_owner_token_if_present",
        "_validate_published_row_one_site",
        "_is_owned_live",
        "_remove_owner_file_if_present",
    ],
)
def test_live_owner_consumers_fail_closed_before_open_when_capability_is_unsupported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    helper_name: str,
) -> None:
    transaction = _published_publish_fixture(tmp_path)
    live = transaction.target.physical_output

    def forbidden_open(*_args: object, **_kwargs: object) -> int:
        raise AssertionError("unsupported helpers must fail before opening a child")

    monkeypatch.setattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", False)
    monkeypatch.setattr(publish_module.os, "open", forbidden_open)
    helper = getattr(publish_module, helper_name)

    with pytest.raises(RowOnePublishError) as exc_info:
        if helper_name == "_read_owner_token_if_present":
            helper(live)
        else:
            helper(transaction)

    _assert_safe_directory_handle_capability_error(exc_info)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_published_validation_reads_bound_json_and_passes_disk_edition_to_integrity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _published_publish_fixture(tmp_path)
    calls: list[tuple[Path, dict[str, object]]] = []
    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", lambda _path: None)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda *, site_dir, edition: calls.append((site_dir, edition)),
    )

    publish_module._validate_published_row_one_site(transaction)

    assert calls == [(transaction.target.physical_output, {"stories": []})]


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_is_owned_live_returns_false_for_missing_live_or_owner(tmp_path: Path) -> None:
    transaction = _published_publish_fixture(tmp_path)
    owner = transaction.target.physical_output / ROW_ONE_PUBLISH_OWNER_PATH
    owner.unlink()

    assert publish_module._is_owned_live(transaction) is False

    publish_module._remove_publish_path(transaction.target.physical_output)

    assert publish_module._is_owned_live(transaction) is False


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_bound_owner_removal_is_a_noop_when_the_final_owner_is_missing(
    tmp_path: Path,
) -> None:
    transaction = _published_publish_fixture(tmp_path)
    owner = transaction.target.physical_output / ROW_ONE_PUBLISH_OWNER_PATH
    owner.unlink()

    publish_module._remove_owner_file_if_present(transaction)

    assert not owner.exists()
    assert transaction.target.physical_output.is_dir()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_bound_owner_removal_retains_verified_data_descriptor_through_unlink_race(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _published_publish_fixture(tmp_path)
    live = transaction.target.physical_output
    data = live / "data"
    owner = data / ROW_ONE_PUBLISH_OWNER_PATH.name
    external_data = tmp_path / "external-data"
    external_data.mkdir()
    external_owner = external_data / owner.name
    external_owner.write_bytes(owner.read_bytes())
    external_before = external_owner.read_bytes()
    displaced_data = live / "displaced-data"
    real_unlink = os.unlink
    swaps: list[Path] = []

    def swap_data_before_relative_unlink(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        dir_fd: int | None = None,
    ) -> None:
        if dir_fd is not None and os.fspath(path) == owner.name and not swaps:
            data.rename(displaced_data)
            _symlink_to(data, external_data, target_is_directory=True)
            swaps.append(data)
        real_unlink(path, dir_fd=dir_fd)

    monkeypatch.setattr(publish_module.os, "unlink", swap_data_before_relative_unlink)

    publish_module._remove_owner_file_if_present(transaction)

    assert swaps == [data]
    assert not (displaced_data / owner.name).exists()
    assert external_owner.read_bytes() == external_before


def test_read_canonical_journal_missing_is_mutation_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    temporary = _write_transaction_temporary_journal(transaction)
    temporary_before = temporary.read_bytes()
    monkeypatch.setattr(
        publish_module,
        "_recover_temporary_journals",
        lambda _target: pytest.fail("canonical reads must not recover temporary journals"),
    )

    assert publish_module._read_canonical_journal(transaction.target) is None
    assert temporary.read_bytes() == temporary_before
    assert not transaction.target.journal_path.exists()


def test_read_canonical_journal_round_trips_without_inspecting_temporary_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    _write_transaction_journal(transaction)
    temporary = _write_transaction_temporary_journal(transaction)
    before = {
        transaction.target.journal_path: transaction.target.journal_path.read_bytes(),
        temporary: temporary.read_bytes(),
    }
    monkeypatch.setattr(
        publish_module,
        "_recover_temporary_journals",
        lambda _target: pytest.fail("canonical reads must not recover temporary journals"),
    )

    assert publish_module._read_canonical_journal(transaction.target) == transaction
    assert {path: path.read_bytes() for path in before} == before


@pytest.mark.parametrize("kind", ["malformed", "symlink"])
def test_read_canonical_journal_rejects_invalid_state_without_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    journal = transaction.target.journal_path
    if kind == "malformed":
        journal.write_text("{not-json\n", encoding="utf-8")
        inspected = journal
    else:
        external = tmp_path / "external-journal.json"
        external.write_text("external\n", encoding="utf-8")
        _symlink_to(journal, external)
        inspected = external
    before = inspected.read_bytes()
    monkeypatch.setattr(
        publish_module,
        "_recover_temporary_journals",
        lambda _target: pytest.fail("canonical reads must not recover temporary journals"),
    )

    with pytest.raises(RowOnePublishAmbiguousStateError):
        publish_module._read_canonical_journal(transaction.target)

    assert inspected.read_bytes() == before
    if kind == "symlink":
        assert journal.is_symlink()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_begin_staging_writes_journal_stage_and_owner(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)

    returned = publish_module._begin_staging(transaction)

    assert returned == transaction
    assert publish_module._read_canonical_journal(transaction.target) == transaction
    assert publish_module._read_owner_token(transaction.stage_path) == transaction.token


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_begin_staging_owner_failure_removes_empty_owned_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    failure = OSError("injected owner failure")
    monkeypatch.setattr(
        publish_module,
        "_write_owner_file",
        lambda _stage, _transaction: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(OSError) as exc_info:
        publish_module._begin_staging(transaction)

    assert exc_info.value is failure
    assert not transaction.stage_path.exists()
    assert transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_begin_staging_owner_failure_reports_cleanup_pending_when_stage_removal_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    monkeypatch.setattr(
        publish_module,
        "_write_owner_file",
        lambda _stage, _transaction: (_ for _ in ()).throw(OSError("owner failure")),
    )
    monkeypatch.setattr(
        publish_module,
        "_remove_publish_path",
        lambda _path: (_ for _ in ()).throw(OSError("cleanup failure")),
    )

    with pytest.raises(RowOnePublishCleanupPendingError) as exc_info:
        publish_module._begin_staging(transaction)

    assert str(transaction.stage_path) in str(exc_info.value)
    assert str(transaction.target.journal_path) in str(exc_info.value)
    assert transaction.stage_path.is_dir()
    assert transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_handled_cleanup_preflights_every_artifact_before_deleting_valid_temporary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    stage = _create_owned_stage(transaction)
    _write_transaction_journal(transaction)
    temporary = _write_transaction_temporary_journal(transaction)
    backup = transaction.backup_path
    external = tmp_path / "external-backup"
    external.mkdir()
    _symlink_to(backup, external, target_is_directory=True)
    before = {
        transaction.target.journal_path: transaction.target.journal_path.read_bytes(),
        temporary: temporary.read_bytes(),
        stage / ROW_ONE_PUBLISH_OWNER_PATH: (stage / ROW_ONE_PUBLISH_OWNER_PATH).read_bytes(),
    }
    monkeypatch.setattr(
        publish_module,
        "_recover_temporary_journals",
        lambda _target: pytest.fail("cleanup preflight must use the canonical reader"),
    )

    with pytest.raises(RowOnePublishAmbiguousStateError):
        publish_module._cleanup_after_handled_failure(transaction)

    assert {path: path.read_bytes() for path in before} == before
    assert stage.is_dir()
    assert backup.is_symlink()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("kind", ["symlink", "fifo"])
def test_handled_cleanup_preserves_owned_state_when_temporary_journal_is_unsafe(
    tmp_path: Path,
    kind: str,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    stage = _create_owned_stage(transaction)
    owner = stage / ROW_ONE_PUBLISH_OWNER_PATH
    _write_transaction_journal(transaction)
    temporary = _temporary_journal_path(transaction)
    handle = _create_nonregular_path(temporary, kind)
    before_owner = owner.read_bytes()
    before_journal = transaction.target.journal_path.read_bytes()
    before_temporary = temporary.lstat()

    try:
        with pytest.raises(RowOnePublishAmbiguousStateError, match="temporary journal"):
            publish_module._cleanup_after_handled_failure(transaction)
    finally:
        if handle is not None:
            handle.close()

    after_temporary = temporary.lstat()
    assert stage.is_dir()
    assert owner.read_bytes() == before_owner
    assert transaction.target.journal_path.read_bytes() == before_journal
    assert (after_temporary.st_dev, after_temporary.st_ino, after_temporary.st_mode) == (
        before_temporary.st_dev,
        before_temporary.st_ino,
        before_temporary.st_mode,
    )


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_published_cleanup_preflights_unsafe_backup_before_owner_or_temp_deletion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = replace(
        _published_publish_fixture(tmp_path),
        phase=RowOnePublishPhase.PUBLISHED,
    )
    live = transaction.target.physical_output
    owner = live / ROW_ONE_PUBLISH_OWNER_PATH
    _write_transaction_journal(transaction)
    temporary = _write_transaction_temporary_journal(transaction)
    external = tmp_path / "external-backup"
    external.mkdir()
    _symlink_to(transaction.backup_path, external, target_is_directory=True)
    before = {
        owner: owner.read_bytes(),
        temporary: temporary.read_bytes(),
        transaction.target.journal_path: transaction.target.journal_path.read_bytes(),
    }
    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", lambda _path: None)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    with pytest.raises(RowOnePublishAmbiguousStateError):
        publish_module._cleanup_after_published(transaction)

    assert {path: path.read_bytes() for path in before} == before
    assert transaction.backup_path.is_symlink()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_handled_cleanup_removes_only_owned_stage_temps_and_canonical_journal(
    tmp_path: Path,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    _create_owned_stage(transaction)
    _write_transaction_journal(transaction)
    temporary_one = _write_transaction_temporary_journal(transaction, nonce="b" * 16)
    temporary_two = _write_transaction_temporary_journal(transaction, nonce="c" * 16)

    publish_module._cleanup_after_handled_failure(transaction)

    assert not transaction.stage_path.exists()
    assert not temporary_one.exists()
    assert not temporary_two.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_published_cleanup_removes_owner_backup_temps_then_canonical_and_keeps_live(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = replace(
        _published_publish_fixture(tmp_path),
        phase=RowOnePublishPhase.PUBLISHED,
    )
    live = transaction.target.physical_output
    transaction.backup_path.mkdir()
    (transaction.backup_path / "old.txt").write_text("old", encoding="utf-8")
    _write_transaction_journal(transaction)
    temporary = _write_transaction_temporary_journal(transaction)
    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", lambda _path: None)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    publish_module._cleanup_after_published(transaction)

    assert live.is_dir()
    assert (live / "index.html").read_text(encoding="utf-8") == "published"
    assert not (live / ROW_ONE_PUBLISH_OWNER_PATH).exists()
    assert not transaction.backup_path.exists()
    assert not temporary.exists()
    assert not transaction.target.journal_path.exists()


def test_published_cleanup_calls_removal_helpers_in_contract_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = replace(
        _transaction_fixture(tmp_path, create_live=False),
        phase=RowOnePublishPhase.PUBLISHED,
    )
    calls: list[str] = []
    monkeypatch.setattr(
        publish_module,
        "_preflight_cleanup_artifacts",
        lambda _transaction, *, published: calls.append(f"preflight:{published}"),
    )
    monkeypatch.setattr(
        publish_module,
        "_remove_owner_file_if_present",
        lambda _transaction: calls.append("owner"),
    )
    monkeypatch.setattr(
        publish_module,
        "_remove_owned_backup_if_present",
        lambda _transaction: calls.append("backup"),
    )
    monkeypatch.setattr(
        publish_module,
        "_remove_matching_temporary_journals",
        lambda _transaction: calls.append("temporary"),
    )
    monkeypatch.setattr(
        publish_module,
        "_remove_canonical_journal",
        lambda _transaction: calls.append("canonical"),
    )

    publish_module._cleanup_after_published(transaction)

    assert calls == ["preflight:True", "owner", "backup", "temporary", "canonical"]


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_rollback_preflight_is_mutation_free_when_late_live_owner_is_invalid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = replace(
        _published_publish_fixture(tmp_path),
        phase=RowOnePublishPhase.LIVE_BACKED_UP,
    )
    transaction.backup_path.mkdir()
    _write_transaction_journal(transaction)
    temporary = _write_transaction_temporary_journal(transaction)
    owner = transaction.target.physical_output / ROW_ONE_PUBLISH_OWNER_PATH
    _write_valid_owner_file(
        transaction.target.physical_output,
        transaction,
        physical_output=str(tmp_path / "different-live"),
    ).replace(owner)
    before = {
        owner: owner.read_bytes(),
        temporary: temporary.read_bytes(),
        transaction.target.journal_path: transaction.target.journal_path.read_bytes(),
    }
    monkeypatch.setattr(
        publish_module,
        "_recover_temporary_journals",
        lambda _target: pytest.fail("rollback preflight must use the canonical reader"),
    )

    with pytest.raises(RowOnePublishAmbiguousStateError):
        publish_module._preflight_rollback_artifacts(transaction)

    assert {path: path.read_bytes() for path in before} == before
    assert transaction.backup_path.is_dir()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_commit_first_publish_moves_stage_validates_and_persists_published(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=False)
    _patch_published_validators(monkeypatch)

    published = publish_module._commit_first_publish(transaction)

    assert published.phase is RowOnePublishPhase.PUBLISHED
    assert published.target.physical_output.is_dir()
    assert not published.stage_path.exists()
    assert (published.target.physical_output / "index.html").read_text(encoding="utf-8") == "new"
    assert publish_module._read_canonical_journal(published.target) == published


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_commit_existing_publish_keeps_new_live_and_owned_backup_until_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=True)
    _patch_published_validators(monkeypatch)

    published = publish_module._commit_existing_publish(transaction)

    assert published.phase is RowOnePublishPhase.PUBLISHED
    assert (published.target.physical_output / "index.html").read_text(encoding="utf-8") == "new"
    assert (published.backup_path / "index.html").read_text(encoding="utf-8") == "old"
    assert publish_module._read_canonical_journal(published.target) == published


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_existing_live_to_backup_move_failure_preserves_old_live_and_cleans_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=True)
    live = transaction.target.physical_output
    old_index = (live / "index.html").read_bytes()
    monkeypatch.setattr(
        publish_module,
        "_move_publish_path",
        lambda _source, _destination: (_ for _ in ()).throw(OSError("first move failed")),
    )

    with pytest.raises(RowOnePublishPreservedError, match="previous site remains") as exc_info:
        publish_module._commit_existing_publish(transaction)

    assert isinstance(exc_info.value.__cause__, OSError)
    assert (live / "index.html").read_bytes() == old_index
    assert not transaction.stage_path.exists()
    assert not transaction.backup_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_existing_stage_to_live_move_failure_restores_old_live_same_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=True)
    live = transaction.target.physical_output
    old_index = (live / "index.html").read_bytes()
    real_move = publish_module._move_publish_path
    moves: list[tuple[Path, Path]] = []

    def fail_second_move(source: Path, destination: Path) -> None:
        moves.append((source, destination))
        if len(moves) == 2:
            raise OSError("second move failed")
        real_move(source, destination)

    monkeypatch.setattr(publish_module, "_move_publish_path", fail_second_move)

    with pytest.raises(RowOnePublishRestoredError, match="previous site was restored"):
        publish_module._commit_existing_publish(transaction)

    assert moves == [
        (live, transaction.backup_path),
        (transaction.stage_path, live),
        (transaction.backup_path, live),
    ]
    assert (live / "index.html").read_bytes() == old_index
    assert not transaction.stage_path.exists()
    assert not transaction.backup_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_existing_post_move_validation_failure_restores_old_live_same_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=True)
    live = transaction.target.physical_output
    old_index = (live / "index.html").read_bytes()
    failure = OSError("published validation failed")
    monkeypatch.setattr(
        publish_module,
        "_validate_published_row_one_site",
        lambda _transaction: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(RowOnePublishRestoredError) as exc_info:
        publish_module._commit_existing_publish(transaction)

    assert exc_info.value.__cause__ is failure
    assert (live / "index.html").read_bytes() == old_index
    assert not transaction.stage_path.exists()
    assert not transaction.backup_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize(
    "failed_phase", [RowOnePublishPhase.LIVE_BACKED_UP, RowOnePublishPhase.PUBLISHED]
)
def test_existing_phase_write_failure_restores_old_live_same_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failed_phase: RowOnePublishPhase,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=True)
    live = transaction.target.physical_output
    old_index = (live / "index.html").read_bytes()
    real_write = publish_module._write_journal
    failure = OSError(f"{failed_phase.value} journal failure")
    _patch_published_validators(monkeypatch)

    def fail_phase_write(updated: RowOnePublishTransaction) -> None:
        if updated.phase is failed_phase:
            raise failure
        real_write(updated)

    monkeypatch.setattr(publish_module, "_write_journal", fail_phase_write)

    with pytest.raises(RowOnePublishRestoredError) as exc_info:
        publish_module._commit_existing_publish(transaction)

    assert exc_info.value.__cause__ is failure
    assert (live / "index.html").read_bytes() == old_index
    assert not transaction.stage_path.exists()
    assert not transaction.backup_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_first_published_phase_write_failure_removes_new_live_same_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=False)
    real_write = publish_module._write_journal
    failure = OSError("published journal failure")
    _patch_published_validators(monkeypatch)

    def fail_published_write(updated: RowOnePublishTransaction) -> None:
        if updated.phase is RowOnePublishPhase.PUBLISHED:
            raise failure
        real_write(updated)

    monkeypatch.setattr(publish_module, "_write_journal", fail_published_write)

    with pytest.raises(RowOnePublishRestoredError) as exc_info:
        publish_module._commit_first_publish(transaction)

    assert exc_info.value.__cause__ is failure
    assert not transaction.target.physical_output.exists()
    assert not transaction.stage_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("owner_kind", ["missing", "mismatched", "symlink"])
def test_first_publish_validation_with_untrusted_live_owner_preserves_ambiguous_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    owner_kind: str,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=False)
    live = transaction.target.physical_output
    failure = OSError("validation failure")
    moves: list[tuple[Path, Path]] = []
    real_move = publish_module._move_publish_path

    def record_move(source: Path, destination: Path) -> None:
        moves.append((source, destination))
        real_move(source, destination)

    def fail_after_changing_owner(_transaction: RowOnePublishTransaction) -> None:
        owner = live / ROW_ONE_PUBLISH_OWNER_PATH
        if owner_kind == "missing":
            owner.unlink()
        elif owner_kind == "mismatched":
            _write_valid_owner_file(live, transaction, token="b" * 32).replace(owner)
        else:
            external = tmp_path / "external-owner.json"
            external.write_text("external\n", encoding="utf-8")
            owner.unlink()
            _symlink_to(owner, external)
        raise failure

    monkeypatch.setattr(publish_module, "_move_publish_path", record_move)
    monkeypatch.setattr(
        publish_module,
        "_validate_published_row_one_site",
        fail_after_changing_owner,
    )

    with pytest.raises(RowOnePublishAmbiguousStateError) as exc_info:
        publish_module._commit_first_publish(transaction)

    assert exc_info.value.__cause__ is failure
    assert moves == [(transaction.stage_path, live)]
    assert live.exists()
    assert transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_rollback_move_failure_retains_all_recovery_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=True)
    live = transaction.target.physical_output
    real_move = publish_module._move_publish_path
    moves: list[tuple[Path, Path]] = []
    failure = OSError("validation failure")

    def fail_restore_move(source: Path, destination: Path) -> None:
        moves.append((source, destination))
        if len(moves) == 4:
            raise OSError("restore move failed")
        real_move(source, destination)

    monkeypatch.setattr(publish_module, "_move_publish_path", fail_restore_move)
    monkeypatch.setattr(
        publish_module,
        "_validate_published_row_one_site",
        lambda _transaction: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(RowOnePublishRollbackError) as exc_info:
        publish_module._commit_existing_publish(transaction)

    message = str(exc_info.value)
    for path in (
        live,
        transaction.stage_path,
        transaction.backup_path,
        transaction.target.journal_path,
    ):
        assert str(path) in message
    assert transaction.stage_path.is_dir()
    assert transaction.backup_path.is_dir()
    assert transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_rollback_preflight_rejects_simultaneous_owned_live_and_stage_before_any_move(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_BACKED_UP,
        had_live_output=True,
        had_site_marker=True,
        had_index=True,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(live, index="new", transaction=transaction)
    _create_owned_stage(transaction)
    _write_complete_recovery_site(transaction.backup_path, index="old")
    _write_transaction_journal(transaction)
    moves: list[tuple[Path, Path]] = []
    monkeypatch.setattr(
        publish_module,
        "_move_publish_path",
        lambda source, destination: moves.append((source, destination)),
    )

    with pytest.raises(RowOnePublishAmbiguousStateError) as exc_info:
        publish_module._rollback_existing_publish(
            transaction,
            OSError("publish failed"),
        )

    message = str(exc_info.value)
    for path in (
        live,
        transaction.stage_path,
        transaction.backup_path,
        transaction.target.journal_path,
    ):
        assert str(path) in message
    assert moves == []
    assert live.is_dir()
    assert transaction.stage_path.is_dir()
    assert transaction.backup_path.is_dir()
    assert transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("control_type", [KeyboardInterrupt, SystemExit])
def test_control_flow_during_first_existing_live_move_is_reraised_without_phase_rollback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    control_type: type[BaseException],
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=True)
    control = control_type("stop")
    writes: list[RowOnePublishPhase] = []
    real_write = publish_module._write_journal

    def record_write(updated: RowOnePublishTransaction) -> None:
        writes.append(updated.phase)
        real_write(updated)

    monkeypatch.setattr(publish_module, "_write_journal", record_write)
    monkeypatch.setattr(
        publish_module,
        "_move_publish_path",
        lambda _source, _destination: (_ for _ in ()).throw(control),
    )

    with pytest.raises(control_type) as exc_info:
        publish_module._commit_existing_publish(transaction)

    assert exc_info.value is control
    assert writes == [RowOnePublishPhase.LIVE_MOVING]
    assert publish_module._read_canonical_journal(transaction.target).phase is (
        RowOnePublishPhase.LIVE_MOVING
    )
    assert transaction.target.physical_output.is_dir()
    assert transaction.stage_path.is_dir()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("control_type", [KeyboardInterrupt, SystemExit])
def test_control_flow_after_backup_move_restores_old_live_then_reraises_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    control_type: type[BaseException],
) -> None:
    transaction = _ready_commit_fixture(tmp_path, had_live_output=True)
    live = transaction.target.physical_output
    old_index = (live / "index.html").read_bytes()
    control = control_type("stop")
    monkeypatch.setattr(
        publish_module,
        "_validate_published_row_one_site",
        lambda _transaction: (_ for _ in ()).throw(control),
    )

    with pytest.raises(control_type) as exc_info:
        publish_module._commit_existing_publish(transaction)

    assert exc_info.value is control
    assert (live / "index.html").read_bytes() == old_index
    assert not transaction.stage_path.exists()
    assert not transaction.backup_path.exists()
    assert not transaction.target.journal_path.exists()


def test_commit_publish_dispatches_by_preexisting_live_fact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _transaction_fixture(tmp_path / "first", create_live=False)
    existing = _transaction_fixture(tmp_path / "existing", create_live=True)
    calls: list[tuple[str, RowOnePublishTransaction]] = []
    monkeypatch.setattr(
        publish_module,
        "_commit_first_publish",
        lambda transaction: calls.append(("first", transaction)) or transaction,
    )
    monkeypatch.setattr(
        publish_module,
        "_commit_existing_publish",
        lambda transaction: calls.append(("existing", transaction)) or transaction,
    )

    assert publish_module._commit_publish(first) == first
    assert publish_module._commit_publish(existing) == existing
    assert calls == [("first", first), ("existing", existing)]


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("phase", [RowOnePublishPhase.STAGING, RowOnePublishPhase.READY])
def test_recovery_keeps_old_live_before_backup_move(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    phase: RowOnePublishPhase,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=phase,
        had_live_output=True,
        had_site_marker=True,
        had_index=True,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(live, index="old")
    _create_owned_stage(transaction)
    _write_transaction_journal(transaction)
    _patch_published_validators(monkeypatch)

    publish_module._recover_interrupted_publish(transaction.target)

    assert (live / "index.html").read_text(encoding="utf-8") == "old"
    assert not transaction.stage_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_keeps_old_live_when_live_moving_rename_failed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_MOVING,
        had_live_output=True,
        had_site_marker=True,
        had_index=True,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(live, index="old")
    _create_owned_stage(transaction)
    temporary = _write_transaction_temporary_journal(transaction)
    _write_transaction_journal(transaction)
    _patch_published_validators(monkeypatch)

    publish_module._recover_interrupted_publish(transaction.target)

    assert (live / "index.html").read_text(encoding="utf-8") == "old"
    assert not transaction.stage_path.exists()
    assert not temporary.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_restores_backup_when_live_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_MOVING,
        had_live_output=True,
        had_site_marker=True,
        had_index=True,
    )
    _write_complete_recovery_site(transaction.backup_path, index="old")
    _create_owned_stage(transaction)
    _write_transaction_journal(transaction)
    _patch_published_validators(monkeypatch)

    publish_module._recover_interrupted_publish(transaction.target)

    assert (transaction.target.physical_output / "index.html").read_text(encoding="utf-8") == "old"
    assert not transaction.backup_path.exists()
    assert not transaction.stage_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_prefers_backup_before_published_phase(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_BACKED_UP,
        had_live_output=True,
        had_site_marker=True,
        had_index=True,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(live, index="new", transaction=transaction)
    _write_complete_recovery_site(transaction.backup_path, index="old")
    _write_transaction_journal(transaction)
    _patch_published_validators(monkeypatch)

    publish_module._recover_interrupted_publish(transaction.target)

    assert (live / "index.html").read_text(encoding="utf-8") == "old"
    assert not transaction.backup_path.exists()
    assert not transaction.stage_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_keeps_valid_first_publish_without_backup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.READY,
        had_live_output=False,
        had_site_marker=False,
        had_index=False,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(live, index="new", transaction=transaction)
    _write_transaction_journal(transaction)
    _patch_published_validators(monkeypatch)

    publish_module._recover_interrupted_publish(transaction.target)

    assert (live / "index.html").read_text(encoding="utf-8") == "new"
    assert not (live / ROW_ONE_PUBLISH_OWNER_PATH).exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_keeps_valid_published_live_and_cleans_backup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.PUBLISHED,
        had_live_output=True,
        had_site_marker=True,
        had_index=True,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(live, index="new", transaction=transaction)
    _write_complete_recovery_site(transaction.backup_path, index="old")
    _write_transaction_journal(transaction)
    _patch_published_validators(monkeypatch)

    publish_module._recover_interrupted_publish(transaction.target)

    assert (live / "index.html").read_text(encoding="utf-8") == "new"
    assert not transaction.backup_path.exists()
    assert not (live / ROW_ONE_PUBLISH_OWNER_PATH).exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_keeps_published_live_after_owner_was_removed_before_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.PUBLISHED,
        had_live_output=True,
        had_site_marker=True,
        had_index=True,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(live, index="new")
    _write_complete_recovery_site(transaction.backup_path, index="old")
    _write_transaction_journal(transaction)
    _patch_published_validators(monkeypatch)

    publish_module._recover_interrupted_publish(transaction.target)

    assert (live / "index.html").read_text(encoding="utf-8") == "new"
    assert not transaction.backup_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("had_live_output", [False, True])
@pytest.mark.parametrize("owner_present", [False, True])
def test_recovery_keeps_valid_published_live_without_backup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    had_live_output: bool,
    owner_present: bool,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.PUBLISHED,
        had_live_output=had_live_output,
        had_site_marker=had_live_output,
        had_index=had_live_output,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(
        live,
        index="new",
        transaction=transaction if owner_present else None,
    )
    temporary = _write_transaction_temporary_journal(transaction)
    _write_transaction_journal(transaction)
    _patch_published_validators(monkeypatch)

    publish_module._recover_interrupted_publish(transaction.target)

    assert (live / "index.html").read_text(encoding="utf-8") == "new"
    assert not (live / ROW_ONE_PUBLISH_OWNER_PATH).exists()
    assert not temporary.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_restores_backup_when_published_live_is_invalid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.PUBLISHED,
        had_live_output=True,
        had_site_marker=True,
        had_index=True,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(live, index="invalid", transaction=transaction)
    (live / "index.html").unlink()
    _write_complete_recovery_site(transaction.backup_path, index="old")
    _write_transaction_journal(transaction)

    def require_index(path: Path) -> None:
        if not (path / "index.html").is_file():
            raise FileNotFoundError(path / "index.html")

    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", require_index)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    publish_module._recover_interrupted_publish(transaction.target)

    assert (live / "index.html").read_text(encoding="utf-8") == "old"
    assert not transaction.backup_path.exists()
    assert not transaction.stage_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("had_live_output", [False, True])
@pytest.mark.parametrize("owner_present", [False, True])
def test_recovery_preserves_invalid_published_live_without_backup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    had_live_output: bool,
    owner_present: bool,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.PUBLISHED,
        had_live_output=had_live_output,
        had_site_marker=had_live_output,
        had_index=had_live_output,
    )
    live = transaction.target.physical_output
    _write_complete_recovery_site(
        live,
        index="invalid",
        transaction=transaction if owner_present else None,
    )
    (live / "index.html").unlink()
    _write_transaction_journal(transaction)
    journal_before = transaction.target.journal_path.read_bytes()
    owner = live / ROW_ONE_PUBLISH_OWNER_PATH
    owner_before = owner.read_bytes() if owner_present else None
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_site_dir",
        lambda _path: (_ for _ in ()).throw(FileNotFoundError("missing index")),
    )

    with pytest.raises(RowOnePublishAmbiguousStateError):
        publish_module._recover_interrupted_publish(transaction.target)

    assert live.is_dir()
    assert not (live / "index.html").exists()
    assert transaction.target.journal_path.read_bytes() == journal_before
    if owner_present:
        assert owner.read_bytes() == owner_before


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_restores_unrelated_only_directory_without_site_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_BACKED_UP,
        had_live_output=True,
        had_site_marker=False,
        had_index=False,
    )
    transaction.backup_path.mkdir()
    (transaction.backup_path / "keep.txt").write_text("keep", encoding="utf-8")
    _create_owned_stage(transaction)
    _write_transaction_journal(transaction)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_site_dir",
        lambda _path: pytest.fail("unrelated-only output is not a ROW ONE site"),
    )

    publish_module._recover_interrupted_publish(transaction.target)

    assert (transaction.target.physical_output / "keep.txt").read_text(encoding="utf-8") == "keep"
    assert not transaction.backup_path.exists()
    assert not transaction.stage_path.exists()
    assert not transaction.target.journal_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_allows_marker_only_output_to_be_repaired(tmp_path: Path) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_BACKED_UP,
        had_live_output=True,
        had_site_marker=True,
        had_index=False,
    )
    transaction.backup_path.mkdir()
    (transaction.backup_path / ".row-one-site").write_text(
        "ROW ONE generated site\n",
        encoding="utf-8",
    )
    _create_owned_stage(transaction)
    _write_transaction_journal(transaction)

    publish_module._recover_interrupted_publish(transaction.target)
    publish_module._validate_live_publish_target(transaction.target)

    assert (transaction.target.physical_output / ".row-one-site").is_file()
    assert not transaction.stage_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_preserves_and_rejects_index_only_unmarked_output(tmp_path: Path) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_BACKED_UP,
        had_live_output=True,
        had_site_marker=False,
        had_index=True,
    )
    transaction.backup_path.mkdir()
    (transaction.backup_path / "index.html").write_text("old index", encoding="utf-8")
    _create_owned_stage(transaction)
    _write_transaction_journal(transaction)

    publish_module._recover_interrupted_publish(transaction.target)

    live_index = transaction.target.physical_output / "index.html"
    assert live_index.read_text(encoding="utf-8") == "old index"
    with pytest.raises(RowOnePublishError, match="not marked as generated"):
        publish_module._validate_live_publish_target(transaction.target)
    assert not transaction.stage_path.exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_publish_recovers_marker_only_output_then_uses_a_new_real_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_BACKED_UP,
        had_live_output=True,
        had_site_marker=True,
        had_index=False,
    )
    transaction.backup_path.mkdir()
    (transaction.backup_path / ".row-one-site").write_text(
        "ROW ONE generated site\n",
        encoding="utf-8",
    )
    _create_owned_stage(transaction)
    _write_transaction_journal(transaction)
    rendered_stages: list[Path] = []
    _patch_published_validators(monkeypatch)
    monkeypatch.setattr(
        publish_module.secrets,
        "token_hex",
        lambda length: "b" * 32 if length == 16 else "c" * 16,
    )

    def render(stage: Path) -> types.SimpleNamespace:
        rendered_stages.append(stage)
        return _render_valid_staged_site(stage, index="new after recovery")

    result = publish_module.publish_latest_row_one_site(
        transaction.target.physical_output,
        render=render,
    )

    expected_stage = transaction.target.physical_output.parent / (
        f".{transaction.target.physical_output.name}.row-one-stage-{'b' * 32}"
    )
    assert rendered_stages == [expected_stage]
    assert rendered_stages[0] != transaction.stage_path
    assert (transaction.target.physical_output / "index.html").read_text(encoding="utf-8") == (
        "new after recovery"
    )
    assert result.output_dir == expected_stage
    assert not result.output_dir.exists()
    _assert_no_transaction_debris(transaction.target.physical_output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_publish_recovers_index_only_output_then_fails_before_new_transaction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.LIVE_BACKED_UP,
        had_live_output=True,
        had_site_marker=False,
        had_index=True,
    )
    transaction.backup_path.mkdir()
    old_index = b"old index\x00with exact bytes\n"
    (transaction.backup_path / "index.html").write_bytes(old_index)
    _create_owned_stage(transaction)
    _write_transaction_journal(transaction)
    token_requests: list[int] = []

    def reject_token(length: int) -> str:
        token_requests.append(length)
        pytest.fail("index-only recovery must fail before requesting a new token")

    monkeypatch.setattr(publish_module.secrets, "token_hex", reject_token)
    monkeypatch.setattr(
        publish_module,
        "_begin_staging",
        lambda _transaction: pytest.fail("index-only recovery must fail before staging"),
    )

    with pytest.raises(RowOnePublishError, match="not marked as generated"):
        publish_module.publish_latest_row_one_site(
            transaction.target.physical_output,
            render=lambda _stage: pytest.fail("index-only recovery must fail before render"),
        )

    live = transaction.target.physical_output
    assert token_requests == []
    assert not (live / ".row-one-site").exists()
    assert (live / "index.html").read_bytes() == old_index
    _assert_no_transaction_debris(live)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_recovery_rejects_unowned_or_unsafe_paths_without_deletion(
    tmp_path: Path,
) -> None:
    transaction = _recovery_transaction(
        tmp_path,
        phase=RowOnePublishPhase.STAGING,
        had_live_output=False,
        had_site_marker=False,
        had_index=False,
    )
    external = tmp_path / "external-stage"
    external.mkdir()
    (external / "keep.txt").write_text("keep", encoding="utf-8")
    _symlink_to(transaction.stage_path, external, target_is_directory=True)
    _write_transaction_journal(transaction)
    journal_before = transaction.target.journal_path.read_bytes()

    with pytest.raises(RowOnePublishAmbiguousStateError):
        publish_module._recover_interrupted_publish(transaction.target)

    assert transaction.stage_path.is_symlink()
    assert (external / "keep.txt").read_text(encoding="utf-8") == "keep"
    assert transaction.target.journal_path.read_bytes() == journal_before


def test_recovery_rejects_owned_lookalikes_without_a_journal(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    lookalike = target.physical_output.parent / (
        f".{target.physical_output.name}.row-one-stage-{'b' * 32}"
    )
    lookalike.mkdir()

    with pytest.raises(RowOnePublishAmbiguousStateError):
        publish_module._recover_interrupted_publish(target)

    assert lookalike.is_dir()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_publish_success_replaces_generated_site_preserves_unrelated_and_cleans(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "site"
    output.mkdir()
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old", encoding="utf-8")
    (output / "keep.txt").write_text("keep", encoding="utf-8")
    _patch_published_validators(monkeypatch)

    result = publish_module.publish_latest_row_one_site(
        output,
        render=lambda stage: _render_valid_staged_site(stage, index="new"),
    )

    assert (output / "index.html").read_text(encoding="utf-8") == "new"
    assert (output / "keep.txt").read_text(encoding="utf-8") == "keep"
    assert result.output_dir != output
    assert not result.output_dir.exists()
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize(
    "failure_point",
    [
        "stage",
        "render",
        "validation",
        "owner",
        "copy_regular",
        "copy_directory",
        "copy_symlink",
        "metadata",
    ],
)
def test_public_precommit_failures_preserve_existing_valid_site_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_point: str,
) -> None:
    output = tmp_path / "site"
    _write_complete_recovery_site(output, index="old")
    unrelated: Path | None = None
    external: Path | None = None
    if failure_point == "copy_regular":
        unrelated = output / "keep.txt"
        unrelated.write_bytes(b"regular bytes\x00\n")
    elif failure_point == "copy_directory":
        unrelated = output / "keep-dir"
        unrelated.mkdir()
        (unrelated / "nested.txt").write_bytes(b"directory bytes\x00\n")
    elif failure_point == "copy_symlink":
        unrelated = output / "keep-link"
        external = tmp_path / "external-keep.txt"
        external.write_bytes(b"external bytes\x00\n")
        _symlink_to(unrelated, external)

    before_generated = _generated_site_bytes(output)
    failure = OSError(f"injected {failure_point} failure")
    _patch_published_validators(monkeypatch)
    render: Callable[[Path], types.SimpleNamespace] = _render_valid_staged_site

    if failure_point == "stage":
        real_mkdir = Path.mkdir

        def fail_stage_mkdir(
            path: Path,
            mode: int = 0o777,
            parents: bool = False,
            exist_ok: bool = False,
        ) -> None:
            if ".row-one-stage-" in path.name:
                raise failure
            real_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

        monkeypatch.setattr(Path, "mkdir", fail_stage_mkdir)
    elif failure_point == "render":

        def fail_render(_stage: Path) -> types.SimpleNamespace:
            raise failure

        render = fail_render
    elif failure_point == "validation":
        monkeypatch.setattr(
            publish_module,
            "_validate_staged_row_one_site",
            lambda _transaction, _result: (_ for _ in ()).throw(failure),
        )
    elif failure_point == "owner":
        monkeypatch.setattr(
            publish_module,
            "_write_owner_file",
            lambda _stage, _transaction: (_ for _ in ()).throw(failure),
        )
    elif failure_point == "copy_regular":
        assert unrelated is not None
        real_copy2 = publish_module.shutil.copy2

        def fail_regular_copy(source, destination, *, follow_symlinks=True):
            if Path(source) == unrelated:
                raise failure
            return real_copy2(source, destination, follow_symlinks=follow_symlinks)

        monkeypatch.setattr(publish_module.shutil, "copy2", fail_regular_copy)
    elif failure_point == "copy_directory":
        assert unrelated is not None
        real_copytree = publish_module.shutil.copytree

        def fail_directory_copy(source, destination, *args, **kwargs):
            if Path(source) == unrelated:
                raise failure
            return real_copytree(source, destination, *args, **kwargs)

        monkeypatch.setattr(publish_module.shutil, "copytree", fail_directory_copy)
    elif failure_point == "copy_symlink":
        assert unrelated is not None
        real_symlink = publish_module.os.symlink

        def fail_symlink_copy(source, destination, *args, **kwargs):
            if Path(destination).name == unrelated.name:
                raise failure
            return real_symlink(source, destination, *args, **kwargs)

        monkeypatch.setattr(publish_module.os, "symlink", fail_symlink_copy)
    elif failure_point == "metadata":
        monkeypatch.setattr(
            publish_module,
            "_apply_live_root_metadata",
            lambda _transaction: (_ for _ in ()).throw(failure),
        )
    else:
        raise AssertionError(f"unknown failure point: {failure_point}")

    with pytest.raises(RowOnePublishError, match="staged publish failed before commit") as exc_info:
        publish_module.publish_latest_row_one_site(output, render=render)

    assert type(exc_info.value) is RowOnePublishError
    assert exc_info.value.__cause__ is failure
    assert _generated_site_bytes(output) == before_generated
    if failure_point == "copy_regular":
        assert unrelated is not None
        assert unrelated.read_bytes() == b"regular bytes\x00\n"
    elif failure_point == "copy_directory":
        assert unrelated is not None
        assert (unrelated / "nested.txt").read_bytes() == b"directory bytes\x00\n"
    elif failure_point == "copy_symlink":
        assert unrelated is not None
        assert external is not None
        assert unrelated.is_symlink()
        assert os.readlink(unrelated) == str(external)
        assert external.read_bytes() == b"external bytes\x00\n"
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_render_oserror_preserves_live_and_is_the_exact_direct_cause(
    tmp_path: Path,
) -> None:
    output = tmp_path / "site"
    output.mkdir()
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old", encoding="utf-8")
    old_index = (output / "index.html").read_bytes()
    failure = OSError("asset write failed")

    def fail_render(_stage: Path) -> types.SimpleNamespace:
        raise failure

    with pytest.raises(RowOnePublishError, match="staged publish failed before commit") as exc_info:
        publish_module.publish_latest_row_one_site(output, render=fail_render)

    assert type(exc_info.value) is RowOnePublishError
    assert exc_info.value.__cause__ is failure
    assert (output / "index.html").read_bytes() == old_index
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize(
    "validator_error", [ValueError("corrupt integrity"), OSError("validator io")]
)
def test_public_staged_validator_failure_exposes_underlying_exact_direct_cause(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    validator_error: BaseException,
) -> None:
    output = tmp_path / "site"
    output.mkdir()
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old", encoding="utf-8")
    old_index = (output / "index.html").read_bytes()
    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", lambda _path: None)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: (_ for _ in ()).throw(validator_error),
    )

    with pytest.raises(RowOnePublishError, match="staged publish failed before commit") as exc_info:
        publish_module.publish_latest_row_one_site(
            output,
            render=_render_valid_staged_site,
        )

    assert type(exc_info.value) is RowOnePublishError
    assert exc_info.value.__cause__ is validator_error
    assert (output / "index.html").read_bytes() == old_index
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_owner_write_failure_preserves_live_and_cleans_journal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "site"
    output.mkdir()
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old", encoding="utf-8")
    old_index = (output / "index.html").read_bytes()
    failure = OSError("owner write failed")
    monkeypatch.setattr(
        publish_module,
        "_write_owner_file",
        lambda _stage, _transaction: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module.publish_latest_row_one_site(
            output,
            render=_render_valid_staged_site,
        )

    assert exc_info.value.__cause__ is failure
    assert (output / "index.html").read_bytes() == old_index
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_live_root_metadata_failure_preserves_live_before_ready_phase(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "site"
    output.mkdir()
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old", encoding="utf-8")
    old_index = (output / "index.html").read_bytes()
    failure = OSError("metadata copy failed")
    _patch_published_validators(monkeypatch)
    monkeypatch.setattr(
        publish_module,
        "_apply_live_root_metadata",
        lambda _transaction: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module.publish_latest_row_one_site(
            output,
            render=_render_valid_staged_site,
        )

    assert exc_info.value.__cause__ is failure
    assert (output / "index.html").read_bytes() == old_index
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_first_publish_move_failure_leaves_no_live_or_owned_debris(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "site"
    failure = OSError("first publish move failed")
    _patch_published_validators(monkeypatch)
    monkeypatch.setattr(
        publish_module,
        "_move_publish_path",
        lambda _source, _destination: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module.publish_latest_row_one_site(
            output,
            render=_render_valid_staged_site,
        )

    assert exc_info.value.__cause__ is failure
    assert not output.exists()
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("control_type", [KeyboardInterrupt, SystemExit])
def test_public_precommit_control_flow_cleans_owned_state_and_reraises_unchanged(
    tmp_path: Path,
    control_type: type[BaseException],
) -> None:
    output = tmp_path / "site"
    output.mkdir()
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old", encoding="utf-8")
    control = control_type("stop")

    def stop_render(_stage: Path) -> types.SimpleNamespace:
        raise control

    with pytest.raises(control_type) as exc_info:
        publish_module.publish_latest_row_one_site(output, render=stop_render)

    assert exc_info.value is control
    assert (output / "index.html").read_text(encoding="utf-8") == "old"
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("control_type", [KeyboardInterrupt, SystemExit])
def test_public_first_publish_post_move_control_flow_rolls_back_and_reraises_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    control_type: type[BaseException],
) -> None:
    output = tmp_path / "site"
    control = control_type("stop after first-publish move")
    _patch_published_validators(monkeypatch)
    monkeypatch.setattr(
        publish_module,
        "_validate_published_row_one_site",
        lambda _transaction: (_ for _ in ()).throw(control),
    )

    with pytest.raises(control_type) as exc_info:
        publish_module.publish_latest_row_one_site(
            output,
            render=_render_valid_staged_site,
        )

    assert exc_info.value is control
    assert not output.exists()
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_callback_row_one_error_is_sanitized_without_stage_path_leak(
    tmp_path: Path,
) -> None:
    output = tmp_path / "site"
    captured_stage: list[Path] = []
    callback_error: list[RowOnePublishError] = []

    def fail_render(stage: Path) -> types.SimpleNamespace:
        captured_stage.append(stage)
        error = RowOnePublishError(f"callback exposed {stage}")
        callback_error.append(error)
        raise error

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module.publish_latest_row_one_site(output, render=fail_render)

    assert type(exc_info.value) is RowOnePublishError
    assert exc_info.value.__cause__ is callback_error[0]
    assert str(captured_stage[0]) not in str(exc_info.value)
    assert "row-one-stage" not in str(exc_info.value)
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_callback_base_publish_error_with_cause_remains_the_outer_direct_cause(
    tmp_path: Path,
) -> None:
    output = tmp_path / "site"
    captured_stage: list[Path] = []
    callback_errors: list[RowOnePublishError] = []
    underlying = ValueError("underlying callback failure")

    def fail_render(stage: Path) -> types.SimpleNamespace:
        captured_stage.append(stage)
        try:
            raise underlying
        except ValueError as exc:
            callback_error = RowOnePublishError(f"callback exposed {stage}")
            callback_errors.append(callback_error)
            raise callback_error from exc

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module.publish_latest_row_one_site(output, render=fail_render)

    assert type(exc_info.value) is RowOnePublishError
    assert exc_info.value.__cause__ is callback_errors[0]
    assert callback_errors[0].__cause__ is underlying
    assert str(captured_stage[0]) not in str(exc_info.value)
    assert "row-one-stage" not in str(exc_info.value)
    _assert_no_transaction_debris(output)


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize(
    "error_type",
    [
        RowOnePublishAmbiguousStateError,
        RowOnePublishRollbackError,
        RowOnePublishCleanupPendingError,
        RowOnePublishPreservedError,
        RowOnePublishRestoredError,
    ],
)
def test_public_state_bearing_errors_are_not_wrapped_or_cause_unwrapped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[RowOnePublishError],
) -> None:
    output = tmp_path / "site"
    underlying = ValueError("underlying")
    state_error = error_type("state paths retained")
    state_error.__cause__ = underlying
    _patch_published_validators(monkeypatch)
    monkeypatch.setattr(
        publish_module,
        "_commit_publish",
        lambda _transaction: (_ for _ in ()).throw(state_error),
    )

    with pytest.raises(error_type) as exc_info:
        publish_module.publish_latest_row_one_site(
            output,
            render=_render_valid_staged_site,
        )

    assert exc_info.value is state_error
    assert exc_info.value.__cause__ is underlying


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_public_postcommit_cleanup_failure_keeps_valid_new_live(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "site"
    output.mkdir()
    (output / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (output / "index.html").write_text("old", encoding="utf-8")
    _patch_published_validators(monkeypatch)
    monkeypatch.setattr(
        publish_module,
        "_remove_owned_backup_if_present",
        lambda _transaction: (_ for _ in ()).throw(OSError("cleanup failed")),
    )

    with pytest.raises(RowOnePublishCleanupPendingError) as exc_info:
        publish_module.publish_latest_row_one_site(
            output,
            render=lambda stage: _render_valid_staged_site(stage, index="new"),
        )

    assert (output / "index.html").read_text(encoding="utf-8") == "new"
    assert str(output) in str(exc_info.value)
    assert (output.parent / ".site.row-one-publish.json").exists()


def test_safe_directory_operations_supported_removes_legacy_three_operation_name() -> None:
    assert not hasattr(publish_module, "_DIRECTORY_FD_SUPPORTED")


def test_live_preflight_exports_exact_generated_children_contract() -> None:
    assert GENERATED_CHILDREN == (
        "index.html",
        ".row-one-site",
        "details",
        "assets",
        "data",
        "articles",
    )


def test_live_preflight_allows_missing_output_without_creating_it(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")

    publish_module._validate_live_publish_target(target)

    assert not target.physical_output.exists()


def test_live_preflight_rejects_existing_non_directory_without_mutation(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.physical_output.write_text("keep", encoding="utf-8")

    with pytest.raises(RowOnePublishError, match="not a directory"):
        publish_module._validate_live_publish_target(target)

    assert target.physical_output.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize(
    "generated_name",
    ("index.html", "details", "assets", "data", "articles"),
)
def test_live_preflight_rejects_generated_children_in_an_unmarked_output(
    tmp_path: Path,
    generated_name: str,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.physical_output.mkdir()
    generated = target.physical_output / generated_name
    if "." in generated_name:
        generated.write_text("keep", encoding="utf-8")
    else:
        generated.mkdir()

    with pytest.raises(RowOnePublishError, match="not marked"):
        publish_module._validate_live_publish_target(target)

    assert generated.lstat()


def test_live_preflight_allows_a_regular_marker_only_directory_unchanged(
    tmp_path: Path,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.physical_output.mkdir()
    marker = target.physical_output / ".row-one-site"
    marker.write_text("ROW ONE generated site\n", encoding="utf-8")
    original = marker.read_bytes()

    publish_module._validate_live_publish_target(target)

    assert marker.read_bytes() == original
    assert set(target.physical_output.iterdir()) == {marker}


def test_live_preflight_allows_unmarked_unrelated_only_directory_unchanged(
    tmp_path: Path,
) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.physical_output.mkdir()
    unrelated = target.physical_output / "keep.txt"
    unrelated.write_text("keep", encoding="utf-8")

    publish_module._validate_live_publish_target(target)

    assert unrelated.read_text(encoding="utf-8") == "keep"
    assert set(target.physical_output.iterdir()) == {unrelated}


def test_live_preflight_does_not_follow_a_nonregular_marker(tmp_path: Path) -> None:
    target = _resolve_publish_target(tmp_path / "site")
    target.physical_output.mkdir()
    outside = tmp_path / "outside-marker"
    outside.write_text("outside", encoding="utf-8")
    marker = target.physical_output / ".row-one-site"
    _symlink_to(marker, outside)
    (target.physical_output / "index.html").write_text("keep", encoding="utf-8")

    with pytest.raises(RowOnePublishError, match="not marked"):
        publish_module._validate_live_publish_target(target)

    assert marker.is_symlink()
    assert os.readlink(marker) == str(outside)
    assert outside.read_text(encoding="utf-8") == "outside"


def test_unrelated_copy_preserves_regular_files_and_nested_directories(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    stage = tmp_path / "stage"
    nested = source / "notes" / "archive"
    nested.mkdir(parents=True)
    stage.mkdir()
    regular = source / "keep.txt"
    regular.write_text("keep", encoding="utf-8")
    nested_file = nested / "item.txt"
    nested_file.write_text("nested", encoding="utf-8")
    regular.chmod(0o640)
    nested_file.chmod(0o604)
    os.utime(regular, ns=(1_700_000_000_123_456_789,) * 2)
    os.utime(nested_file, ns=(1_700_000_001_987_654_321,) * 2)
    expected_regular = regular.stat()
    expected_nested = nested_file.stat()
    for child_name in GENERATED_CHILDREN:
        child = source / child_name
        if "." in child_name:
            child.write_text("generated", encoding="utf-8")
        else:
            child.mkdir()
    _write_valid_owner_file(source, _transaction_fixture(tmp_path / "owner"))

    publish_module._copy_unrelated_children(source, stage)

    copied_regular = stage / "keep.txt"
    copied_nested = stage / "notes" / "archive" / "item.txt"
    assert copied_regular.read_text(encoding="utf-8") == "keep"
    assert copied_nested.read_text(encoding="utf-8") == "nested"
    assert stat.S_IMODE(copied_regular.stat().st_mode) == stat.S_IMODE(expected_regular.st_mode)
    assert stat.S_IMODE(copied_nested.stat().st_mode) == stat.S_IMODE(expected_nested.st_mode)
    assert copied_regular.stat().st_mtime_ns == expected_regular.st_mtime_ns
    assert copied_nested.stat().st_mtime_ns == expected_nested.st_mtime_ns
    assert not any((stage / child_name).exists() for child_name in GENERATED_CHILDREN)


def test_unrelated_copy_recreates_relative_dangling_and_external_symlink_targets_raw(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    stage = tmp_path / "stage"
    source.mkdir()
    stage.mkdir()
    (source / "internal.txt").write_text("internal", encoding="utf-8")
    external = tmp_path / "external.txt"
    external.write_text("external", encoding="utf-8")
    raw_targets = {
        "internal-link": "internal.txt",
        "dangling-link": "missing/target.txt",
        "external-link": str(external),
    }
    for name, raw_target in raw_targets.items():
        _symlink_to(source / name, Path(raw_target))

    publish_module._copy_unrelated_children(source, stage)

    for name, raw_target in raw_targets.items():
        copied = stage / name
        assert copied.is_symlink()
        assert os.readlink(copied) == raw_target
    assert external.read_text(encoding="utf-8") == "external"


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO files are unavailable")
def test_unrelated_copy_rejects_a_top_level_fifo_before_copying(tmp_path: Path) -> None:
    source = tmp_path / "source"
    stage = tmp_path / "stage"
    source.mkdir()
    stage.mkdir()
    (source / "keep.txt").write_text("keep", encoding="utf-8")
    fifo = source / "unsafe.fifo"
    _make_fifo(fifo)

    with pytest.raises(RowOnePublishError, match="special|unsafe|regular"):
        publish_module._copy_unrelated_children(source, stage)

    assert not (stage / "keep.txt").exists()
    assert stat.S_ISFIFO(fifo.lstat().st_mode)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO files are unavailable")
def test_unrelated_copy_rejects_a_nested_fifo_before_any_partial_stage_copy(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    stage = tmp_path / "stage"
    nested = source / "nested"
    nested.mkdir(parents=True)
    stage.mkdir()
    (source / "copy-first.txt").write_text("must not copy", encoding="utf-8")
    (stage / "existing.txt").write_text("existing", encoding="utf-8")
    fifo = nested / "unsafe.fifo"
    _make_fifo(fifo)

    with pytest.raises(RowOnePublishError, match="special|unsafe|regular"):
        publish_module._copy_unrelated_children(source, stage)

    assert set(path.name for path in stage.iterdir()) == {"existing.txt"}
    assert stat.S_ISFIFO(fifo.lstat().st_mode)


@pytest.mark.parametrize("kind", ["symlink", "directory", "fifo"])
def test_unrelated_copy_rejects_unsafe_owner_path_without_following_or_removing_it(
    tmp_path: Path,
    kind: str,
) -> None:
    if kind == "fifo" and not hasattr(os, "mkfifo"):
        pytest.skip("FIFO files are unavailable on this platform")
    source = tmp_path / "source"
    stage = tmp_path / "stage"
    owner_path = source / ROW_ONE_PUBLISH_OWNER_PATH
    owner_path.parent.mkdir(parents=True)
    stage.mkdir()
    outside = tmp_path / "outside-owner.json"
    outside.write_text("outside", encoding="utf-8")
    if kind == "symlink":
        _symlink_to(owner_path, outside)
    elif kind == "directory":
        owner_path.mkdir()
    else:
        _make_fifo(owner_path)
    original = owner_path.lstat()

    with pytest.raises(RowOnePublishAmbiguousStateError, match="owner"):
        publish_module._copy_unrelated_children(source, stage)

    assert owner_path.lstat().st_ino == original.st_ino
    assert outside.read_text(encoding="utf-8") == "outside"
    assert not any(stage.iterdir())


def test_root_metadata_is_a_noop_for_first_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path, create_live=False)
    transaction.stage_path.mkdir()

    def fail_copystat(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("copystat must not run for a first publish")

    monkeypatch.setattr(publish_module.shutil, "copystat", fail_copystat)

    publish_module._apply_live_root_metadata(transaction)


def test_root_metadata_is_applied_after_generated_writes_and_survives_stage_promotion(
    tmp_path: Path,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    live = transaction.target.physical_output
    live.chmod(0o751)
    os.utime(live, ns=(1_700_000_123_456_789_012,) * 2)
    expected = live.stat()
    transaction.stage_path.mkdir()
    (transaction.stage_path / "index.html").write_text("new", encoding="utf-8")

    publish_module._apply_live_root_metadata(transaction)
    live.rename(transaction.backup_path)
    transaction.stage_path.rename(live)

    observed = live.stat()
    assert stat.S_IMODE(observed.st_mode) == stat.S_IMODE(expected.st_mode)
    assert observed.st_mtime_ns == expected.st_mtime_ns


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_writer_emits_the_exact_sorted_contract(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    data_dir = transaction.stage_path / "data"
    assert stat.S_ISDIR(transaction.stage_path.lstat().st_mode)
    assert not any(transaction.stage_path.iterdir())
    assert not data_dir.exists()
    expected = {
        "contract_version": ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION,
        "physical_output": str(transaction.target.physical_output),
        "token": transaction.token,
    }

    publish_module._write_owner_file(transaction.stage_path, transaction)

    owner_path = transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH
    assert stat.S_ISDIR(data_dir.lstat().st_mode)
    assert owner_path.read_text(encoding="utf-8") == (
        json.dumps(expected, ensure_ascii=True, sort_keys=True) + "\n"
    )
    assert json.loads(owner_path.read_text(encoding="utf-8")) == expected


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_writer_rejects_an_existing_regular_owner_without_overwriting_it(
    tmp_path: Path,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    owner_path = transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH
    owner_path.parent.mkdir()
    original = b"existing owner bytes\n"
    owner_path.write_bytes(original)
    before = owner_path.stat()

    with pytest.raises(RowOnePublishAmbiguousStateError, match="owner path already exists"):
        publish_module._write_owner_file(transaction.stage_path, transaction)

    after = owner_path.stat()
    assert (after.st_dev, after.st_ino) == (before.st_dev, before.st_ino)
    assert owner_path.read_bytes() == original


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_writer_rejects_an_inode_swap_before_identity_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    data_dir = transaction.stage_path / "data"
    data_dir.mkdir()
    owner_path = transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH
    displaced_owner = owner_path.with_name(f"{owner_path.name}.displaced")
    external_owner = tmp_path / "external-owner.json"
    external_original = b"external owner bytes\n"
    external_owner.write_bytes(external_original)
    real_fstat = publish_module.os.fstat
    swaps: list[tuple[int, int]] = []

    def swap_owner_after_open(descriptor: int) -> os.stat_result:
        metadata = real_fstat(descriptor)
        if stat.S_ISREG(metadata.st_mode) and not swaps:
            owner_path.rename(displaced_owner)
            owner_path.write_bytes(external_owner.read_bytes())
            swaps.append((metadata.st_dev, metadata.st_ino))
        return metadata

    monkeypatch.setattr(publish_module.os, "fstat", swap_owner_after_open)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="owner identity changed"):
        publish_module._write_owner_file(transaction.stage_path, transaction)

    assert len(swaps) == 1
    assert displaced_owner.read_bytes() == b""
    assert external_owner.read_bytes() == external_original
    assert owner_path.read_bytes() == external_original


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_writer_preserves_identity_error_when_descriptor_close_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    data_dir = transaction.stage_path / "data"
    data_dir.mkdir(parents=True)
    owner_path = transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH
    external = tmp_path / "external-owner-sentinel.txt"
    external.write_bytes(b"external owner sentinel\n")
    opened_descriptors: list[int] = []
    owner_descriptors: list[int] = []
    owner_identity_calls = 0
    close_failure = OSError("owner descriptor close failure")
    real_open = os.open
    real_close = os.close
    real_identity = publish_module._identity

    def record_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            descriptor = real_open(path, flags, mode)
        else:
            descriptor = real_open(path, flags, mode, dir_fd=dir_fd)
        opened_descriptors.append(descriptor)
        if dir_fd is not None and os.fsdecode(path) == owner_path.name:
            owner_descriptors.append(descriptor)
        return descriptor

    def mismatch_owner_identity(metadata: os.stat_result) -> tuple[int, int]:
        nonlocal owner_identity_calls
        identity = real_identity(metadata)
        if owner_descriptors and stat.S_ISREG(metadata.st_mode):
            owner_identity_calls += 1
            if owner_identity_calls == 2:
                return identity[0], identity[1] + 1
        return identity

    def fail_owner_descriptor_close(descriptor: int) -> None:
        if descriptor in owner_descriptors:
            raise close_failure
        real_close(descriptor)

    monkeypatch.setattr(publish_module.os, "open", record_open)
    monkeypatch.setattr(publish_module, "_identity", mismatch_owner_identity)
    monkeypatch.setattr(publish_module.os, "close", fail_owner_descriptor_close)

    try:
        with pytest.raises(RowOnePublishAmbiguousStateError) as exc_info:
            publish_module._write_owner_file(transaction.stage_path, transaction)
    finally:
        for descriptor in opened_descriptors:
            try:
                real_close(descriptor)
            except OSError as exc:
                if exc.errno != errno.EBADF:
                    raise

    assert type(exc_info.value) is RowOnePublishAmbiguousStateError
    assert str(exc_info.value) == (
        f"ROW ONE publish owner identity changed while opening: {owner_path}"
    )
    notes = getattr(exc_info.value, "__notes__", ())
    assert len(notes) == 1
    assert "publish owner file close also failed" in notes[0]
    assert f"OSError: {close_failure}" in notes[0]
    _assert_file_descriptors_closed(opened_descriptors)
    assert owner_path.read_bytes() == b""
    assert external.read_bytes() == b"external owner sentinel\n"


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_writer_rejects_a_symlinked_data_directory_without_touching_external(
    tmp_path: Path,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    external_data = tmp_path / "external-data"
    external_data.mkdir()
    sentinel = external_data / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    data_link = transaction.stage_path / "data"
    _symlink_to(data_link, external_data, target_is_directory=True)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="data.*directory|directory.*data"):
        publish_module._write_owner_file(transaction.stage_path, transaction)

    assert data_link.is_symlink()
    assert os.readlink(data_link) == str(external_data)
    assert sentinel.read_text(encoding="utf-8") == "keep"
    assert not (external_data / ROW_ONE_PUBLISH_OWNER_PATH.name).exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_writer_rejects_a_symlinked_stage_without_touching_external(
    tmp_path: Path,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    external_stage = tmp_path / "external-stage"
    external_data = external_stage / "data"
    external_data.mkdir(parents=True)
    sentinel = external_data / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    _symlink_to(transaction.stage_path, external_stage, target_is_directory=True)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="stage.*directory|directory.*stage"):
        publish_module._write_owner_file(transaction.stage_path, transaction)

    assert transaction.stage_path.is_symlink()
    assert sentinel.read_text(encoding="utf-8") == "keep"
    assert not (external_data / ROW_ONE_PUBLISH_OWNER_PATH.name).exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_writer_rejects_data_replaced_after_creation_without_touching_external(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    external_data = tmp_path / "external-data"
    external_data.mkdir()
    real_mkdir = publish_module.os.mkdir
    replaced: list[Path] = []

    def replace_created_data(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> None:
        real_mkdir(path, mode, dir_fd=dir_fd)
        data_dir = transaction.stage_path / "data"
        data_dir.rmdir()
        _symlink_to(data_dir, external_data, target_is_directory=True)
        replaced.append(data_dir)

    monkeypatch.setattr(publish_module.os, "mkdir", replace_created_data)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="data.*directory|directory.*data"):
        publish_module._write_owner_file(transaction.stage_path, transaction)

    assert replaced == [transaction.stage_path / "data"]
    assert (transaction.stage_path / "data").is_symlink()
    assert not (external_data / ROW_ONE_PUBLISH_OWNER_PATH.name).exists()


def test_safe_directory_operations_unsupported_owner_writer_fails_before_creating_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    sentinel = external / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", False)

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module._write_owner_file(transaction.stage_path, transaction)

    _assert_safe_directory_handle_capability_error(exc_info)
    assert not any(transaction.stage_path.iterdir())
    assert not (transaction.stage_path / "data").exists()
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_safe_directory_operations_unsupported_owner_writer_avoids_full_path_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    data_dir = transaction.stage_path / "data"
    data_dir.mkdir()
    external_data = tmp_path / "external-data"
    external_data.mkdir()
    sentinel = external_data / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    swaps = _install_full_path_swap_spy(
        monkeypatch,
        final_path=transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH,
        directory=data_dir,
        external_directory=external_data,
    )
    monkeypatch.setattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", False)

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module._write_owner_file(transaction.stage_path, transaction)

    _assert_safe_directory_handle_capability_error(exc_info)
    assert swaps == []
    assert stat.S_ISDIR(data_dir.lstat().st_mode)
    assert sentinel.read_text(encoding="utf-8") == "keep"
    assert not (external_data / ROW_ONE_PUBLISH_OWNER_PATH.name).exists()


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_reader_returns_token_for_the_exact_contract(tmp_path: Path) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    _write_valid_owner_file(transaction.stage_path, transaction)

    assert publish_module._read_owner_token(transaction.stage_path) == transaction.token


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_reader_rejects_a_symlinked_data_directory_without_following_it(
    tmp_path: Path,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    external_root = tmp_path / "external-root"
    external_owner = _write_valid_owner_file(external_root, transaction)
    original = external_owner.read_bytes()
    data_link = transaction.stage_path / "data"
    _symlink_to(data_link, external_owner.parent, target_is_directory=True)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="data.*directory|directory.*data"):
        publish_module._read_owner_token(transaction.stage_path)

    assert data_link.is_symlink()
    assert external_owner.read_bytes() == original


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_reader_rejects_a_symlinked_stage_without_following_it(
    tmp_path: Path,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    external_stage = tmp_path / "external-stage"
    external_owner = _write_valid_owner_file(external_stage, transaction)
    original = external_owner.read_bytes()
    _symlink_to(transaction.stage_path, external_stage, target_is_directory=True)

    with pytest.raises(RowOnePublishAmbiguousStateError, match="stage.*directory|directory.*stage"):
        publish_module._read_owner_token(transaction.stage_path)

    assert transaction.stage_path.is_symlink()
    assert external_owner.read_bytes() == original


def test_safe_directory_operations_unsupported_owner_reader_avoids_full_path_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    owner_path = _write_valid_owner_file(transaction.stage_path, transaction)
    external_root = tmp_path / "external-root"
    external_owner = _write_valid_owner_file(external_root, transaction)
    external_original = external_owner.read_bytes()
    swaps = _install_full_path_swap_spy(
        monkeypatch,
        final_path=owner_path,
        directory=owner_path.parent,
        external_directory=external_owner.parent,
    )
    monkeypatch.setattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", False)

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module._read_owner_token(transaction.stage_path)

    _assert_safe_directory_handle_capability_error(exc_info)
    assert swaps == []
    assert stat.S_ISDIR(owner_path.parent.lstat().st_mode)
    assert external_owner.read_bytes() == external_original


@pytest.mark.parametrize(
    ("case", "overrides"),
    [
        ("extra key", {"extra": True}),
        ("wrong version", {"contract_version": "row-one-publish-owner/v0"}),
        ("relative physical output", {"physical_output": "site"}),
        ("unsafe token", {"token": "A" * 32}),
    ],
)
@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_reader_rejects_inexact_or_unsafe_contracts(
    tmp_path: Path,
    case: str,
    overrides: dict[str, object],
) -> None:
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    owner_path = _write_valid_owner_file(transaction.stage_path, transaction, **overrides)
    original = owner_path.read_bytes()

    with pytest.raises(RowOnePublishAmbiguousStateError, match="owner"):
        publish_module._read_owner_token(transaction.stage_path)

    assert case
    assert owner_path.read_bytes() == original


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize("document_kind", ["owner", "generated"])
@pytest.mark.parametrize("parser_failure", ["duplicate", "deep"])
def test_managed_json_parser_failures_preserve_bytes_and_close_descriptors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    document_kind: str,
    parser_failure: str,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    if document_kind == "owner":
        document_path = transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH
    else:
        document_path = transaction.stage_path / "data" / "edition.json"
    if parser_failure == "duplicate":
        if document_kind == "owner":
            raw = (
                "{"
                f'"contract_version": {json.dumps(ROW_ONE_PUBLISH_OWNER_CONTRACT_VERSION)}, '
                f'"physical_output": {json.dumps(str(transaction.target.physical_output))}, '
                f'"token": {json.dumps(transaction.token)}, '
                f'"token": {json.dumps("b" * 32)}'
                "}\n"
            ).encode()
        else:
            raw = b'{"stories": [], "stories": []}\n'
    else:
        depth = sys.getrecursionlimit() * 10
        raw = ('{"nested":' * depth + "null" + "}" * depth + "\n").encode()
    document_path.write_bytes(raw)
    original_identity = document_path.stat()
    opened_descriptors: list[tuple[int, tuple[int, int]]] = []
    real_open = publish_module.os.open

    def record_document_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            return real_open(path, flags, mode)
        descriptor = real_open(path, flags, mode, dir_fd=dir_fd)
        if os.fsdecode(path) == document_path.name:
            metadata = os.fstat(descriptor)
            opened_descriptors.append((descriptor, (metadata.st_dev, metadata.st_ino)))
        return descriptor

    monkeypatch.setattr(publish_module.os, "open", record_document_open)

    if document_kind == "owner":
        with pytest.raises(RowOnePublishAmbiguousStateError, match="owner"):
            publish_module._read_owner_token(transaction.stage_path)
    else:
        with pytest.raises(RowOnePublishError, match="edition"):
            publish_module._validate_staged_row_one_site(transaction, result)

    assert document_path.read_bytes() == raw
    after = document_path.stat()
    assert (after.st_dev, after.st_ino) == (original_identity.st_dev, original_identity.st_ino)
    assert [identity for _descriptor, identity in opened_descriptors] == [
        (original_identity.st_dev, original_identity.st_ino)
    ]
    _assert_file_descriptors_closed(
        [descriptor for descriptor, _identity_value in opened_descriptors]
    )


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_rejects_a_missing_owner_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    (transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH).unlink()
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    with pytest.raises(RowOnePublishAmbiguousStateError, match="owner.*missing"):
        publish_module._validate_staged_row_one_site(transaction, result)


@pytest.mark.parametrize("kind", ["symlink", "directory", "fifo"])
@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_owner_reader_rejects_nonregular_paths_without_following_or_mutating_them(
    tmp_path: Path,
    kind: str,
) -> None:
    if kind == "fifo" and not hasattr(os, "mkfifo"):
        pytest.skip("FIFO files are unavailable on this platform")
    transaction = _transaction_fixture(tmp_path)
    transaction.stage_path.mkdir()
    owner_path = transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH
    owner_path.parent.mkdir()
    outside = tmp_path / "outside-owner.json"
    outside.write_text("outside", encoding="utf-8")
    if kind == "symlink":
        _symlink_to(owner_path, outside)
    elif kind == "directory":
        owner_path.mkdir()
    else:
        _make_fifo(owner_path)
    original = owner_path.lstat()

    with pytest.raises(RowOnePublishAmbiguousStateError, match="owner"):
        publish_module._read_owner_token(transaction.stage_path)

    assert owner_path.lstat().st_ino == original.st_ino
    assert outside.read_text(encoding="utf-8") == "outside"


@pytest.mark.parametrize("missing_name", [".row-one-site", "index.html"])
@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_rejects_missing_public_marker_or_index(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    missing_name: str,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    (transaction.stage_path / missing_name).unlink()
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    with pytest.raises(RowOnePublishError, match=missing_name):
        publish_module._validate_staged_row_one_site(transaction, result)


@pytest.mark.parametrize("mismatch", ["output_dir", "index_path"])
def test_validate_staged_rejects_result_path_mismatches(
    tmp_path: Path,
    mismatch: str,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    setattr(result, mismatch, tmp_path / "wrong")

    with pytest.raises(RowOnePublishError, match=mismatch):
        publish_module._validate_staged_row_one_site(transaction, result)


@pytest.mark.parametrize("mismatch", ["token", "physical_output"])
@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_rejects_owner_identity_mismatches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mismatch: str,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    value = "b" * 32 if mismatch == "token" else str(tmp_path / "other-site")
    _write_valid_owner_file(transaction.stage_path, transaction, **{mismatch: value})
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    with pytest.raises(RowOnePublishAmbiguousStateError, match=mismatch.replace("_", " ")):
        publish_module._validate_staged_row_one_site(transaction, result)


@pytest.mark.parametrize("filename", ["edition.json", "manifest.json", "runtime.json"])
@pytest.mark.parametrize("raw", ["{malformed", "[]"])
@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_rejects_malformed_or_nonobject_disk_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    filename: str,
    raw: str,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    (transaction.stage_path / "data" / filename).write_text(raw, encoding="utf-8")
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    with pytest.raises(RowOnePublishError, match=filename.removesuffix(".json")):
        publish_module._validate_staged_row_one_site(transaction, result)


@pytest.mark.parametrize("state", ["missing", "symlink"])
@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_rejects_missing_or_unsafe_disk_json_without_following(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    state: str,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    edition_path = transaction.stage_path / "data" / "edition.json"
    edition_path.unlink()
    outside = tmp_path / "outside-edition.json"
    outside.write_text('{"stories": []}\n', encoding="utf-8")
    if state == "symlink":
        _symlink_to(edition_path, outside)
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **_kwargs: None,
    )

    with pytest.raises(RowOnePublishAmbiguousStateError, match="edition"):
        publish_module._validate_staged_row_one_site(transaction, result)

    if state == "symlink":
        assert edition_path.is_symlink()
    assert outside.read_text(encoding="utf-8") == '{"stories": []}\n'


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_json_reader_rejects_a_symlinked_direct_parent_without_following_it(
    tmp_path: Path,
) -> None:
    external_data = tmp_path / "external-data"
    external_data.mkdir()
    external_json = external_data / "edition.json"
    external_json.write_text('{"stories": []}\n', encoding="utf-8")
    original = external_json.read_bytes()
    data_link = tmp_path / "data-link"
    _symlink_to(data_link, external_data, target_is_directory=True)

    with pytest.raises(
        RowOnePublishAmbiguousStateError,
        match="parent.*directory|directory.*parent",
    ):
        publish_module._read_json_object(data_link / "edition.json", label="edition")

    assert data_link.is_symlink()
    assert external_json.read_bytes() == original


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_json_reader_rejects_a_symlinked_managed_root_before_child_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    external_root = tmp_path / "external-root"
    external_data = external_root / "data"
    external_data.mkdir(parents=True)
    external_json = external_data / "edition.json"
    external_json.write_text('{"stories": []}\n', encoding="utf-8")
    original = external_json.read_bytes()
    managed_root = tmp_path / "managed-root"
    _symlink_to(managed_root, external_root, target_is_directory=True)
    child_opens: list[str] = []
    real_open = publish_module.os.open

    def record_child_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is not None:
            child_opens.append(os.fsdecode(path))
            return real_open(path, flags, mode, dir_fd=dir_fd)
        return real_open(path, flags, mode)

    monkeypatch.setattr(publish_module.os, "open", record_child_open)

    with pytest.raises(
        RowOnePublishAmbiguousStateError,
        match="managed root.*directory|directory.*managed root",
    ):
        publish_module._read_json_object(managed_root / "data" / "edition.json", label="edition")

    assert child_opens == []
    assert managed_root.is_symlink()
    assert external_json.read_bytes() == original


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_json_reader_preserves_mapped_verification_error_when_close_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    managed_root = tmp_path / "managed-root"
    data_dir = managed_root / "data"
    data_dir.mkdir(parents=True)
    json_path = data_dir / "edition.json"
    original = b'{"stories": []}\n'
    json_path.write_bytes(original)
    opened_descriptors: list[int] = []
    json_descriptors: list[int] = []
    verification_injected = False
    verification_failure = OSError("JSON descriptor verification failure")
    close_failure = OSError("JSON descriptor close failure")
    real_open = os.open
    real_fstat = os.fstat
    real_close = os.close

    def record_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is None:
            descriptor = real_open(path, flags, mode)
        else:
            descriptor = real_open(path, flags, mode, dir_fd=dir_fd)
        opened_descriptors.append(descriptor)
        if dir_fd is not None and os.fsdecode(path) == json_path.name:
            json_descriptors.append(descriptor)
        return descriptor

    def fail_json_descriptor_verification(descriptor: int) -> os.stat_result:
        nonlocal verification_injected
        if descriptor in json_descriptors and not verification_injected:
            verification_injected = True
            raise verification_failure
        return real_fstat(descriptor)

    def fail_json_descriptor_close(descriptor: int) -> None:
        if descriptor in json_descriptors:
            raise close_failure
        real_close(descriptor)

    monkeypatch.setattr(publish_module.os, "open", record_open)
    monkeypatch.setattr(publish_module.os, "fstat", fail_json_descriptor_verification)
    monkeypatch.setattr(publish_module.os, "close", fail_json_descriptor_close)

    try:
        with pytest.raises(RowOnePublishAmbiguousStateError) as exc_info:
            publish_module._read_json_object(json_path, label="edition")
    finally:
        for descriptor in opened_descriptors:
            try:
                real_close(descriptor)
            except OSError as exc:
                if exc.errno != errno.EBADF:
                    raise

    assert type(exc_info.value) is RowOnePublishAmbiguousStateError
    assert str(exc_info.value) == f"ROW ONE edition cannot be read safely: {json_path}"
    assert exc_info.value.__cause__ is verification_failure
    notes = getattr(exc_info.value, "__notes__", ())
    assert len(notes) == 1
    assert "edition JSON descriptor close also failed" in notes[0]
    assert f"OSError: {close_failure}" in notes[0]
    _assert_file_descriptors_closed(opened_descriptors)
    assert json_path.read_bytes() == original


def test_safe_directory_operations_unsupported_json_reader_avoids_full_path_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    json_path = data_dir / "edition.json"
    json_path.write_text('{"source": "stage"}\n', encoding="utf-8")
    external_data = tmp_path / "external-data"
    external_data.mkdir()
    external_json = external_data / "edition.json"
    external_json.write_text('{"source": "external"}\n', encoding="utf-8")
    external_original = external_json.read_bytes()
    swaps = _install_full_path_swap_spy(
        monkeypatch,
        final_path=json_path,
        directory=data_dir,
        external_directory=external_data,
    )
    monkeypatch.setattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", False)

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module._read_json_object(json_path, label="edition")

    _assert_safe_directory_handle_capability_error(exc_info)
    assert swaps == []
    assert stat.S_ISDIR(data_dir.lstat().st_mode)
    assert external_json.read_bytes() == external_original


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_rejects_a_symlinked_data_ancestor_before_following_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    data_dir = transaction.stage_path / "data"
    external_data = tmp_path / "external-data"
    data_dir.rename(external_data)
    _symlink_to(data_dir, external_data, target_is_directory=True)
    original = {path.name: path.read_bytes() for path in external_data.iterdir() if path.is_file()}
    validation_calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **kwargs: validation_calls.append(kwargs),
    )

    with pytest.raises(RowOnePublishAmbiguousStateError, match="data.*directory|directory.*data"):
        publish_module._validate_staged_row_one_site(transaction, result)

    assert data_dir.is_symlink()
    assert validation_calls == []
    assert {
        path.name: path.read_bytes() for path in external_data.iterdir() if path.is_file()
    } == original


def test_safe_directory_operations_unsupported_staged_validation_fails_before_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    data_dir = transaction.stage_path / "data"
    external_data = tmp_path / "external-data"
    external_data.mkdir()
    for path in data_dir.iterdir():
        if path.is_file():
            (external_data / path.name).write_bytes(path.read_bytes())
    sentinel = external_data / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    external_original = {
        path.name: path.read_bytes() for path in external_data.iterdir() if path.is_file()
    }
    swaps = _install_full_path_swap_spy(
        monkeypatch,
        final_path=transaction.stage_path / ROW_ONE_PUBLISH_OWNER_PATH,
        directory=data_dir,
        external_directory=external_data,
    )
    integrity_calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        lambda **kwargs: integrity_calls.append(kwargs),
    )
    monkeypatch.setattr(publish_module, "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED", False)

    with pytest.raises(RowOnePublishError) as exc_info:
        publish_module._validate_staged_row_one_site(transaction, result)

    _assert_safe_directory_handle_capability_error(exc_info)
    assert swaps == []
    assert integrity_calls == []
    assert stat.S_ISDIR(data_dir.lstat().st_mode)
    assert {
        path.name: path.read_bytes() for path in external_data.iterdir() if path.is_file()
    } == external_original


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_passes_the_disk_edition_to_integrity_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    disk_edition = {"stories": [], "source": "disk"}
    _write_payload(transaction.stage_path / "data" / "edition.json", disk_edition)
    calls: list[dict[str, object]] = []

    def capture_validation(**kwargs: object) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        capture_validation,
    )

    publish_module._validate_staged_row_one_site(transaction, result)

    assert calls == [{"site_dir": transaction.stage_path, "edition": disk_edition}]
    assert result.edition != disk_edition


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_propagates_the_exact_unexpected_validator_oserror(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    failure = OSError("validator disk failure")

    def fail_validation(**_kwargs: object) -> None:
        raise failure

    monkeypatch.setattr(
        publish_module,
        "validate_row_one_generated_site_integrity",
        fail_validation,
    )

    with pytest.raises(OSError) as exc_info:
        publish_module._validate_staged_row_one_site(transaction, result)

    assert exc_info.value is failure


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
def test_validate_staged_propagates_the_exact_site_validator_oserror(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction, result = _staged_publish_fixture(tmp_path)
    failure = OSError("site validator disk failure")

    def fail_validation(_stage: Path) -> None:
        raise failure

    monkeypatch.setattr(publish_module, "validate_row_one_site_dir", fail_validation)

    with pytest.raises(OSError) as exc_info:
        publish_module._validate_staged_row_one_site(transaction, result)

    assert exc_info.value is failure
