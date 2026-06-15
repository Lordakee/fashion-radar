from __future__ import annotations

import io
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_package_archives.py"

WHEEL_FILES = {
    "fashion_radar/cli.py": "",
    "fashion_radar/__main__.py": "",
    "fashion_radar/templates/daily_report.md": "",
    "fashion_radar/templates/configs/sources.example.yaml": "",
    "fashion_radar/templates/configs/entities.example.yaml": "",
    "fashion_radar/templates/configs/scoring.example.yaml": "",
    "fashion_radar-0.1.0.dist-info/METADATA": (
        "Metadata-Version: 2.4\nName: fashion-radar\nVersion: 0.1.0\n"
    ),
    "fashion_radar-0.1.0.dist-info/WHEEL": "Wheel-Version: 1.0\n",
    "fashion_radar-0.1.0.dist-info/RECORD": "",
    "fashion_radar-0.1.0.dist-info/entry_points.txt": (
        "[console_scripts]\nfashion-radar = fashion_radar.cli:app\n"
    ),
    "fashion_radar-0.1.0.dist-info/licenses/LICENSE": "MIT\n",
}

SDIST_FILES = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "docs/cli-reference.md",
    "docs/github-upload-checklist.md",
    "docs/source-boundaries.md",
    "docs/dependency-mirrors.md",
    "docs/community-signal-import.md",
    "docs/source-packs.md",
    "docs/entity-packs.md",
    "configs/sources.example.yaml",
    "configs/entities.example.yaml",
    "configs/scoring.example.yaml",
    "configs/source-packs/fashion-public.example.yaml",
    "configs/entity-packs/fashion-watchlist.example.yaml",
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
    "schemas/community-signals.schema.json",
    "src/fashion_radar/cli.py",
    "src/fashion_radar/__main__.py",
    "src/fashion_radar/templates/daily_report.md",
    "src/fashion_radar/templates/configs/sources.example.yaml",
    "src/fashion_radar/templates/configs/entities.example.yaml",
    "src/fashion_radar/templates/configs/scoring.example.yaml",
]


def run_checker(build_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(build_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_wheel(
    build_dir: Path,
    *,
    files: dict[str, str] | None = None,
) -> Path:
    path = build_dir / "fashion_radar-0.1.0-py3-none-any.whl"
    archive_files = WHEEL_FILES if files is None else files

    with zipfile.ZipFile(path, "w") as archive:
        for archive_path, content in archive_files.items():
            archive.writestr(archive_path, content)

    return path


def write_sdist(build_dir: Path, *, files: list[str] | None = None) -> Path:
    path = build_dir / "fashion_radar-0.1.0.tar.gz"
    archive_files = SDIST_FILES if files is None else files

    with tarfile.open(path, "w:gz") as archive:
        for relative_path in archive_files:
            data = b"fixture\n"
            info = tarfile.TarInfo(f"fashion_radar-0.1.0/{relative_path}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))

    return path


def test_accepts_archives_with_required_files_and_metadata(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 0
    assert result.stdout == "Package archives contain required files.\n"
    assert result.stderr == ""


def test_rejects_build_directory_without_wheel(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "missing wheel archive (*.whl)" in result.stderr


def test_rejects_build_directory_without_sdist(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "missing sdist archive (*.tar.gz)" in result.stderr


def test_rejects_wheel_without_required_package_file(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files={
            path: content
            for path, content in WHEEL_FILES.items()
            if path != "fashion_radar/__main__.py"
        },
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "wheel archive missing required file: fashion_radar/__main__.py" in result.stderr


def test_rejects_wheel_without_record_file(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files={
            path: content for path, content in WHEEL_FILES.items() if not path.endswith("/RECORD")
        },
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "wheel dist-info missing required file: RECORD" in result.stderr


def test_rejects_wheel_without_metadata_file_without_traceback(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files={
            path: content for path, content in WHEEL_FILES.items() if not path.endswith("/METADATA")
        },
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "wheel dist-info missing required file: METADATA" in result.stderr
    assert "Traceback" not in result.stderr


def test_rejects_wheel_without_entry_points_file_without_traceback(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files={
            path: content
            for path, content in WHEEL_FILES.items()
            if not path.endswith("/entry_points.txt")
        },
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "wheel dist-info missing required file: entry_points.txt" in result.stderr
    assert "Traceback" not in result.stderr


def test_rejects_nested_wheel_dist_info_directory(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files={
            (f"nested/{path}" if ".dist-info/" in path else path): content
            for path, content in WHEEL_FILES.items()
        },
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "wheel archive must contain exactly one top-level .dist-info directory" in result.stderr


def test_rejects_multiple_wheel_dist_info_directories(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        "other-0.1.0.dist-info/METADATA": "Metadata-Version: 2.4\nName: other\nVersion: 0.1.0\n",
        "other-0.1.0.dist-info/WHEEL": "Wheel-Version: 1.0\n",
        "other-0.1.0.dist-info/RECORD": "",
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "wheel archive must contain exactly one top-level .dist-info directory" in result.stderr


def test_rejects_split_wheel_dist_info_files(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files={
            (
                "other-0.1.0.dist-info/entry_points.txt"
                if path.endswith("/entry_points.txt")
                else path
            ): content
            for path, content in WHEEL_FILES.items()
        },
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "wheel archive must contain exactly one top-level .dist-info directory" in result.stderr


def test_rejects_sdist_without_public_readiness_doc(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[path for path in SDIST_FILES if path != "docs/source-boundaries.md"],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "sdist archive missing required file: docs/source-boundaries.md" in result.stderr


def test_rejects_sdist_without_packaged_template_config(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[
            path
            for path in SDIST_FILES
            if path != "src/fashion_radar/templates/configs/entities.example.yaml"
        ],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive missing required file: "
        "src/fashion_radar/templates/configs/entities.example.yaml"
    ) in result.stderr


def test_rejects_wheel_metadata_without_project_name(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        "fashion_radar-0.1.0.dist-info/METADATA": ("Metadata-Version: 2.4\nVersion: 0.1.0\n")
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "METADATA is missing Name: fashion-radar" in result.stderr


def test_rejects_wheel_metadata_without_project_version(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        "fashion_radar-0.1.0.dist-info/METADATA": ("Metadata-Version: 2.4\nName: fashion-radar\n")
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "METADATA is missing Version: 0.1.0" in result.stderr


def test_rejects_wheel_entry_points_without_console_script(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        "fashion_radar-0.1.0.dist-info/entry_points.txt": (
            "[console_scripts]\nother-command = fashion_radar.cli:app\n"
        )
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "entry_points.txt is missing fashion-radar = fashion_radar.cli:app" in result.stderr
