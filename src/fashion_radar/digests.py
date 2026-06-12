from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass, replace
from datetime import date
from email.message import EmailMessage
from enum import StrEnum
from pathlib import Path


class DigestLatestMode(StrEnum):
    NONE = "none"
    COPY = "copy"
    SYMLINK = "symlink"


@dataclass(frozen=True)
class DigestOptions:
    latest: DigestLatestMode = DigestLatestMode.NONE
    write_index: bool = False
    write_eml: bool = False
    print_summary: bool = False


@dataclass(frozen=True)
class DigestResult:
    latest_markdown_path: Path | None = None
    latest_json_path: Path | None = None
    index_path: Path | None = None
    eml_path: Path | None = None
    summary_text: str | None = None


_DAILY_REPORT_PATTERN = re.compile(
    r"^fashion-radar-(?P<report_date>\d{4}-\d{2}-\d{2})\.(?P<extension>md|json)$"
)


def package_daily_digest(
    *,
    markdown_path: Path,
    json_path: Path,
    reports_dir: Path,
    options: DigestOptions,
) -> DigestResult:
    markdown_path = Path(markdown_path)
    json_path = Path(json_path)
    reports_dir = Path(reports_dir)
    _validate_report_file_exists(markdown_path)
    _validate_report_file_exists(json_path)
    _report_date_from_pair(markdown_path, json_path)

    latest_markdown_path: Path | None = None
    latest_json_path: Path | None = None
    latest_mode = DigestLatestMode(options.latest)
    if latest_mode != DigestLatestMode.NONE:
        latest_markdown_path, latest_json_path = write_latest_artifacts(
            markdown_path=markdown_path,
            json_path=json_path,
            reports_dir=reports_dir,
            mode=latest_mode,
        )

    index_path = write_report_index(reports_dir) if options.write_index else None
    eml_path = (
        write_eml_digest(markdown_path=markdown_path, json_path=json_path, reports_dir=reports_dir)
        if options.write_eml
        else None
    )
    result = DigestResult(
        latest_markdown_path=latest_markdown_path,
        latest_json_path=latest_json_path,
        index_path=index_path,
        eml_path=eml_path,
    )
    if options.print_summary:
        result = replace(
            result,
            summary_text=render_digest_summary(markdown_path, json_path, result),
        )
    return result


def write_latest_artifacts(
    *,
    markdown_path: Path,
    json_path: Path,
    reports_dir: Path,
    mode: DigestLatestMode,
) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    latest_markdown_path = reports_dir / "latest.md"
    latest_json_path = reports_dir / "latest.json"
    latest_mode = DigestLatestMode(mode)
    if latest_mode == DigestLatestMode.NONE:
        return latest_markdown_path, latest_json_path
    if latest_mode == DigestLatestMode.COPY:
        _atomic_copy(markdown_path, latest_markdown_path)
        _atomic_copy(json_path, latest_json_path)
    elif latest_mode == DigestLatestMode.SYMLINK:
        _replace_relative_symlink(markdown_path, latest_markdown_path)
        _replace_relative_symlink(json_path, latest_json_path)
    else:
        raise ValueError(f"unsupported digest latest mode: {mode}")
    return latest_markdown_path, latest_json_path


def write_report_index(reports_dir: Path) -> Path:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for markdown_path in reports_dir.glob("fashion-radar-*.md"):
        parsed_markdown = _parse_daily_report_path(markdown_path)
        if parsed_markdown is None:
            continue
        if not markdown_path.is_file():
            continue
        report_date, _extension = parsed_markdown
        json_path = reports_dir / f"fashion-radar-{report_date.isoformat()}.json"
        parsed_json = _parse_daily_report_path(json_path)
        if parsed_json is None or not json_path.is_file():
            continue
        json_date, _json_extension = parsed_json
        if json_date != report_date:
            continue
        entries.append(
            {
                "report_date": report_date.isoformat(),
                "markdown_path": markdown_path.name,
                "json_path": json_path.name,
            }
        )

    entries.sort(key=lambda entry: entry["report_date"], reverse=True)
    index_path = reports_dir / "report-index.json"
    _atomic_write_text(
        index_path,
        json.dumps({"entries": entries}, indent=2) + "\n",
    )
    return index_path


def write_eml_digest(*, markdown_path: Path, json_path: Path, reports_dir: Path) -> Path:
    report_date = _report_date_from_pair(markdown_path, json_path)
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    message = EmailMessage()
    message["Subject"] = f"Fashion Radar local report {report_date.isoformat()}"
    message["X-Fashion-Radar-Local-Digest"] = "true"
    message.set_content(_eml_body(markdown_path=markdown_path, json_path=json_path))
    message.add_attachment(
        markdown_path.read_text(encoding="utf-8"),
        subtype="markdown",
        filename=markdown_path.name,
    )
    message.add_attachment(
        json_path.read_text(encoding="utf-8"),
        subtype="json",
        filename=json_path.name,
    )
    eml_path = reports_dir / f"fashion-radar-{report_date.isoformat()}.eml"
    _atomic_write_text(eml_path, message.as_string())
    return eml_path


def render_digest_summary(
    markdown_path: Path,
    json_path: Path,
    result: DigestResult,
) -> str:
    lines = [
        "Local observed fashion report is ready for review.",
        "Signals are observed within this configured source set and imported local signals.",
        f"Markdown report: {markdown_path}",
        f"JSON report: {json_path}",
    ]
    if result.latest_markdown_path is not None:
        lines.append(f"Latest Markdown: {result.latest_markdown_path}")
    if result.latest_json_path is not None:
        lines.append(f"Latest JSON: {result.latest_json_path}")
    if result.index_path is not None:
        lines.append(f"Report index: {result.index_path}")
    if result.eml_path is not None:
        lines.append(f"Local EML digest: {result.eml_path}")
    lines.append("Review source attribution before sharing.")
    return "\n".join(lines)


def _eml_body(*, markdown_path: Path, json_path: Path) -> str:
    return "\n".join(
        [
            "Local observed fashion report is ready for review.",
            "Signals are observed within this configured source set and imported local signals.",
            "",
            f"Markdown report: {markdown_path.name}",
            f"JSON report: {json_path.name}",
            "",
            "This .eml file was written locally and was not sent by Fashion Radar.",
            "Review source attribution before sharing.",
            "",
        ]
    )


def _report_date_from_pair(markdown_path: Path, json_path: Path) -> date:
    parsed_markdown = _parse_daily_report_path(markdown_path)
    parsed_json = _parse_daily_report_path(json_path)
    if parsed_markdown is None or parsed_json is None:
        raise ValueError("daily report filename must match fashion-radar-YYYY-MM-DD.md/json")
    markdown_date, markdown_extension = parsed_markdown
    json_date, json_extension = parsed_json
    if markdown_extension != "md" or json_extension != "json" or markdown_date != json_date:
        raise ValueError("Markdown and JSON daily report filenames must share one date")
    return markdown_date


def _parse_daily_report_path(path: Path) -> tuple[date, str] | None:
    match = _DAILY_REPORT_PATTERN.fullmatch(path.name)
    if match is None:
        return None
    try:
        report_date = date.fromisoformat(match.group("report_date"))
    except ValueError:
        return None
    return report_date, match.group("extension")


def _validate_report_file_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"report file does not exist: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"report path is not a file: {path}")


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = _temporary_sibling(path)
    try:
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_file = tempfile.NamedTemporaryFile(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
        delete=False,
    )
    temp_path = Path(temp_file.name)
    temp_file.close()
    try:
        shutil.copyfile(source, temp_path)
        temp_path.replace(destination)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _replace_relative_symlink(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = _temporary_sibling(destination)
    if temp_path.exists() or temp_path.is_symlink():
        temp_path.unlink()
    try:
        os.symlink(os.path.relpath(source, start=destination.parent), temp_path)
        temp_path.replace(destination)
    finally:
        if temp_path.exists() or temp_path.is_symlink():
            temp_path.unlink()


def _temporary_sibling(path: Path) -> Path:
    handle = tempfile.NamedTemporaryFile(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temp_path = Path(handle.name)
    handle.close()
    return temp_path
