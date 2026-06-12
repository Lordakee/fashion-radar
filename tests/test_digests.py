from __future__ import annotations

import json
import os
from email import policy
from email.parser import Parser
from pathlib import Path

import pytest

from fashion_radar.digests import (
    DigestLatestMode,
    DigestOptions,
    DigestResult,
    package_daily_digest,
    render_digest_summary,
    write_report_index,
)


def _write_daily_pair(reports_dir: Path, report_date: str) -> tuple[Path, Path]:
    markdown_path = reports_dir / f"fashion-radar-{report_date}.md"
    json_path = reports_dir / f"fashion-radar-{report_date}.json"
    markdown_path.write_text(f"# Fashion Radar {report_date}\n", encoding="utf-8")
    json_path.write_text(
        json.dumps({"metadata": {"report_date": f"{report_date}T00:00:00+00:00"}}),
        encoding="utf-8",
    )
    return markdown_path, json_path


def test_package_daily_digest_no_options_writes_nothing(tmp_path: Path) -> None:
    markdown_path, json_path = _write_daily_pair(tmp_path, "2026-06-12")

    result = package_daily_digest(
        markdown_path=markdown_path,
        json_path=json_path,
        reports_dir=tmp_path,
        options=DigestOptions(),
    )

    assert result == DigestResult()
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "fashion-radar-2026-06-12.json",
        "fashion-radar-2026-06-12.md",
    ]


def test_package_daily_digest_writes_latest_copies(tmp_path: Path) -> None:
    markdown_path, json_path = _write_daily_pair(tmp_path, "2026-06-12")

    result = package_daily_digest(
        markdown_path=markdown_path,
        json_path=json_path,
        reports_dir=tmp_path,
        options=DigestOptions(latest=DigestLatestMode.COPY),
    )

    assert result.latest_markdown_path == tmp_path / "latest.md"
    assert result.latest_json_path == tmp_path / "latest.json"
    assert (tmp_path / "latest.md").read_text(encoding="utf-8") == markdown_path.read_text(
        encoding="utf-8"
    )
    assert json.loads((tmp_path / "latest.json").read_text(encoding="utf-8")) == json.loads(
        json_path.read_text(encoding="utf-8")
    )
    assert not (tmp_path / "latest.md").is_symlink()
    assert not (tmp_path / "latest.json").is_symlink()


def test_package_daily_digest_writes_latest_symlinks(tmp_path: Path) -> None:
    if not hasattr(os, "symlink"):
        pytest.skip("symlink is unavailable on this platform")
    markdown_path, json_path = _write_daily_pair(tmp_path, "2026-06-12")

    result = package_daily_digest(
        markdown_path=markdown_path,
        json_path=json_path,
        reports_dir=tmp_path,
        options=DigestOptions(latest=DigestLatestMode.SYMLINK),
    )

    assert result.latest_markdown_path == tmp_path / "latest.md"
    assert result.latest_json_path == tmp_path / "latest.json"
    assert (tmp_path / "latest.md").is_symlink()
    assert (tmp_path / "latest.json").is_symlink()
    assert os.readlink(tmp_path / "latest.md") == "fashion-radar-2026-06-12.md"
    assert os.readlink(tmp_path / "latest.json") == "fashion-radar-2026-06-12.json"
    assert (tmp_path / "latest.md").read_text(encoding="utf-8") == markdown_path.read_text(
        encoding="utf-8"
    )
    assert json.loads((tmp_path / "latest.json").read_text(encoding="utf-8")) == json.loads(
        json_path.read_text(encoding="utf-8")
    )


def test_write_report_index_lists_date_stamped_pairs_descending(tmp_path: Path) -> None:
    _write_daily_pair(tmp_path, "2026-06-10")
    _write_daily_pair(tmp_path, "2026-06-12")
    _write_daily_pair(tmp_path, "2026-06-11")

    index_path = write_report_index(tmp_path)

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    assert payload == {
        "entries": [
            {
                "report_date": "2026-06-12",
                "markdown_path": "fashion-radar-2026-06-12.md",
                "json_path": "fashion-radar-2026-06-12.json",
            },
            {
                "report_date": "2026-06-11",
                "markdown_path": "fashion-radar-2026-06-11.md",
                "json_path": "fashion-radar-2026-06-11.json",
            },
            {
                "report_date": "2026-06-10",
                "markdown_path": "fashion-radar-2026-06-10.md",
                "json_path": "fashion-radar-2026-06-10.json",
            },
        ]
    }


def test_write_report_index_ignores_helper_and_malformed_files(tmp_path: Path) -> None:
    _write_daily_pair(tmp_path, "2026-06-12")
    (tmp_path / "latest.md").write_text("latest", encoding="utf-8")
    (tmp_path / "latest.json").write_text("{}", encoding="utf-8")
    (tmp_path / "report-index.json").write_text("{}", encoding="utf-8")
    (tmp_path / "fashion-radar-latest.json").write_text("{}", encoding="utf-8")
    (tmp_path / "fashion-radar-2026-99-99.md").write_text("bad", encoding="utf-8")
    (tmp_path / "fashion-radar-2026-99-99.json").write_text("{}", encoding="utf-8")
    (tmp_path / "fashion-radar-2026-06-13.json").write_text("{}", encoding="utf-8")
    (tmp_path / "fashion-radar-2026-06-14.md").write_text("directory json", encoding="utf-8")
    (tmp_path / "fashion-radar-2026-06-14.json").mkdir()
    (tmp_path / "fashion-radar-2026-06-15.md").mkdir()
    (tmp_path / "fashion-radar-2026-06-15.json").write_text("{}", encoding="utf-8")

    index_path = write_report_index(tmp_path)

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    assert payload == {
        "entries": [
            {
                "report_date": "2026-06-12",
                "markdown_path": "fashion-radar-2026-06-12.md",
                "json_path": "fashion-radar-2026-06-12.json",
            }
        ]
    }


def test_package_daily_digest_writes_local_eml_with_attachments(tmp_path: Path) -> None:
    markdown_path, json_path = _write_daily_pair(tmp_path, "2026-06-12")

    result = package_daily_digest(
        markdown_path=markdown_path,
        json_path=json_path,
        reports_dir=tmp_path,
        options=DigestOptions(write_eml=True),
    )

    assert result.eml_path == tmp_path / "fashion-radar-2026-06-12.eml"
    message = Parser(policy=policy.default).parsestr(result.eml_path.read_text(encoding="utf-8"))
    assert message["Subject"] == "Fashion Radar local report 2026-06-12"
    assert message["To"] is None
    assert message["Cc"] is None
    assert message["Bcc"] is None
    assert message["X-Fashion-Radar-Local-Digest"] == "true"
    assert (
        "Local observed fashion report" in message.get_body(preferencelist=("plain",)).get_content()
    )
    assert [attachment.get_filename() for attachment in message.iter_attachments()] == [
        "fashion-radar-2026-06-12.md",
        "fashion-radar-2026-06-12.json",
    ]


def test_render_digest_summary_uses_local_observed_wording(tmp_path: Path) -> None:
    markdown_path, json_path = _write_daily_pair(tmp_path, "2026-06-12")
    result = DigestResult(
        latest_markdown_path=tmp_path / "latest.md",
        latest_json_path=tmp_path / "latest.json",
        index_path=tmp_path / "report-index.json",
        eml_path=tmp_path / "fashion-radar-2026-06-12.eml",
    )

    summary = render_digest_summary(markdown_path, json_path, result)

    assert "Local observed fashion report is ready for review." in summary
    assert "configured source set" in summary
    assert "Review source attribution before sharing." in summary
    forbidden = [
        "social trends",
        "top social trend",
        "platform-wide",
        "market-wide",
        "verified demand",
        "complete social listening",
        "real-time social monitoring",
    ]
    assert all(term not in summary.lower() for term in forbidden)


def test_package_daily_digest_rejects_missing_report_files(tmp_path: Path) -> None:
    markdown_path = tmp_path / "fashion-radar-2026-06-12.md"
    json_path = tmp_path / "fashion-radar-2026-06-12.json"

    with pytest.raises(FileNotFoundError, match="report file does not exist"):
        package_daily_digest(
            markdown_path=markdown_path,
            json_path=json_path,
            reports_dir=tmp_path,
            options=DigestOptions(latest=DigestLatestMode.COPY),
        )


def test_package_daily_digest_rejects_non_daily_report_names(tmp_path: Path) -> None:
    markdown_path = tmp_path / "report.md"
    json_path = tmp_path / "report.json"
    markdown_path.write_text("# Report\n", encoding="utf-8")
    json_path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="daily report filename"):
        package_daily_digest(
            markdown_path=markdown_path,
            json_path=json_path,
            reports_dir=tmp_path,
            options=DigestOptions(latest=DigestLatestMode.COPY),
        )
