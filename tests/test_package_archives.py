from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_package_archives.py"

spec = importlib.util.spec_from_file_location("check_package_archives", SCRIPT)
check_package_archives = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = check_package_archives
spec.loader.exec_module(check_package_archives)

EXPECTED_METADATA = check_package_archives.load_expected_project_metadata()
EXPECTED_ARCHIVE_BASE_NAME = check_package_archives.expected_archive_base_name(EXPECTED_METADATA)
EXPECTED_WHEEL_ARCHIVE_NAME = check_package_archives.expected_wheel_archive_name(EXPECTED_METADATA)
EXPECTED_SDIST_ARCHIVE_NAME = check_package_archives.expected_sdist_archive_name(EXPECTED_METADATA)
EXPECTED_SDIST_ROOT_DIR = check_package_archives.expected_sdist_root_dir(EXPECTED_METADATA)
EXPECTED_WHEEL_DIST_INFO_DIR = check_package_archives.expected_wheel_dist_info_dir(
    EXPECTED_METADATA
)

WHEEL_FILES = {
    "fashion_radar/cli.py": "",
    "fashion_radar/__main__.py": "",
    "fashion_radar/templates/daily_report.md": "",
    "fashion_radar/templates/configs/sources.example.yaml": "",
    "fashion_radar/templates/configs/entities.example.yaml": "",
    "fashion_radar/templates/configs/scoring.example.yaml": "",
    f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA": (
        "Metadata-Version: 2.4\n"
        f"Name: {EXPECTED_METADATA.name}\n"
        f"Version: {EXPECTED_METADATA.version}\n"
    ),
    f"{EXPECTED_WHEEL_DIST_INFO_DIR}/WHEEL": "Wheel-Version: 1.0\n",
    f"{EXPECTED_WHEEL_DIST_INFO_DIR}/RECORD": "",
    f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": (
        "[console_scripts]\n" + "\n".join(sorted(EXPECTED_METADATA.console_script_lines)) + "\n"
    ),
    f"{EXPECTED_WHEEL_DIST_INFO_DIR}/licenses/LICENSE": "MIT\n",
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
    "examples/community-signals.watchlist.example.csv",
    "examples/community-signal-profile.example.json",
    "examples/community-tool-handoff.example.csv",
    "examples/community-tool-handoff.example.json",
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
    "schemas/community-signals.schema.json",
    "scripts/check_first_run_smoke.py",
    "src/fashion_radar/cli.py",
    "src/fashion_radar/__main__.py",
    "src/fashion_radar/templates/daily_report.md",
    "src/fashion_radar/templates/configs/sources.example.yaml",
    "src/fashion_radar/templates/configs/entities.example.yaml",
    "src/fashion_radar/templates/configs/scoring.example.yaml",
]


def test_package_archive_fixture_metadata_matches_current_public_names() -> None:
    assert f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA" in WHEEL_FILES
    assert EXPECTED_METADATA.name == "fashion-radar"
    assert EXPECTED_METADATA.version == "0.1.0"
    assert EXPECTED_METADATA.console_script_lines == frozenset(
        {"fashion-radar = fashion_radar.cli:app"}
    )
    assert EXPECTED_ARCHIVE_BASE_NAME == "fashion_radar-0.1.0"
    assert EXPECTED_WHEEL_ARCHIVE_NAME == "fashion_radar-0.1.0-py3-none-any.whl"
    assert EXPECTED_SDIST_ARCHIVE_NAME == "fashion_radar-0.1.0.tar.gz"
    assert EXPECTED_SDIST_ROOT_DIR == "fashion_radar-0.1.0"
    assert EXPECTED_WHEEL_DIST_INFO_DIR == "fashion_radar-0.1.0.dist-info"


def test_expected_archive_metadata_is_derived_from_pyproject() -> None:
    metadata = check_package_archives.load_expected_project_metadata()

    assert metadata.name == EXPECTED_METADATA.name
    assert metadata.version == EXPECTED_METADATA.version
    assert metadata.console_script_lines == EXPECTED_METADATA.console_script_lines


def test_expected_archive_metadata_loader_uses_supplied_pyproject(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "\n".join(
            [
                "[project]",
                'name = "example-package"',
                'version = "9.8.7"',
                "[project.scripts]",
                'example-cli = "example.cli:app"',
                'example-admin = "example.admin:main"',
            ]
        ),
        encoding="utf-8",
    )

    metadata = check_package_archives.load_expected_project_metadata(pyproject)

    assert metadata.name == "example-package"
    assert metadata.version == "9.8.7"
    assert metadata.console_script_lines == frozenset(
        {
            "example-cli = example.cli:app",
            "example-admin = example.admin:main",
        }
    )


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
    filename: str = EXPECTED_WHEEL_ARCHIVE_NAME,
) -> Path:
    path = build_dir / filename
    archive_files = WHEEL_FILES if files is None else files

    with zipfile.ZipFile(path, "w") as archive:
        for archive_path, content in archive_files.items():
            archive.writestr(archive_path, content)

    return path


def write_sdist(
    build_dir: Path,
    *,
    files: list[str] | None = None,
    filename: str = EXPECTED_SDIST_ARCHIVE_NAME,
    root_dir: str = EXPECTED_SDIST_ROOT_DIR,
) -> Path:
    path = build_dir / filename
    archive_files = SDIST_FILES if files is None else files

    with tarfile.open(path, "w:gz") as archive:
        for relative_path in archive_files:
            data = b"fixture\n"
            info = tarfile.TarInfo(f"{root_dir}/{relative_path}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))

    return path


def write_sdist_with_raw_member(build_dir: Path, raw_member: str) -> Path:
    path = build_dir / EXPECTED_SDIST_ARCHIVE_NAME

    with tarfile.open(path, "w:gz") as archive:
        for relative_path in SDIST_FILES:
            data = b"fixture\n"
            info = tarfile.TarInfo(f"{EXPECTED_SDIST_ROOT_DIR}/{relative_path}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))

        data = b"unsafe\n"
        info = tarfile.TarInfo(raw_member)
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


def test_accepts_uv_build_gitignore_marker(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / ".gitignore").write_text("*\n", encoding="utf-8")

    result = run_checker(build_dir)

    assert result.returncode == 0
    assert result.stdout == "Package archives contain required files.\n"
    assert result.stderr == ""


def test_rejects_build_directory_with_unexpected_direct_file(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / "build.log").write_text("local build output\n", encoding="utf-8")

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "build directory contains unexpected direct child: build.log" in result.stderr
    assert "Traceback" not in result.stderr


def test_rejects_build_directory_with_unexpected_direct_directory(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / "metadata").mkdir()

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "build directory contains unexpected direct child: metadata" in result.stderr
    assert "Traceback" not in result.stderr


def test_reports_all_unexpected_build_directory_direct_children(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / "build.log").write_text("local build output\n", encoding="utf-8")
    (build_dir / "metadata").mkdir()

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "build directory contains unexpected direct child: build.log" in result.stderr
    assert "build directory contains unexpected direct child: metadata" in result.stderr
    assert result.stderr.index("build.log") < result.stderr.index("metadata")
    assert "Traceback" not in result.stderr


def test_allowed_gitignore_marker_does_not_hide_unexpected_direct_child(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / ".gitignore").write_text("*\n", encoding="utf-8")
    (build_dir / "build.log").write_text("local build output\n", encoding="utf-8")

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "build directory contains unexpected direct child: .gitignore" not in result.stderr
    assert "build directory contains unexpected direct child: build.log" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    ("wheel_filename", "sdist_filename", "expected_error"),
    [
        (
            "wrong_name-0.1.0-py3-none-any.whl",
            EXPECTED_SDIST_ARCHIVE_NAME,
            (
                "wheel archive filename mismatch: expected "
                f"{EXPECTED_WHEEL_ARCHIVE_NAME}, "
                "found wrong_name-0.1.0-py3-none-any.whl"
            ),
        ),
        (
            "fashion_radar-9.9.9-py3-none-any.whl",
            EXPECTED_SDIST_ARCHIVE_NAME,
            (
                "wheel archive filename mismatch: expected "
                f"{EXPECTED_WHEEL_ARCHIVE_NAME}, "
                "found fashion_radar-9.9.9-py3-none-any.whl"
            ),
        ),
        (
            EXPECTED_WHEEL_ARCHIVE_NAME,
            "wrong_name-0.1.0.tar.gz",
            (
                "sdist archive filename mismatch: expected "
                f"{EXPECTED_SDIST_ARCHIVE_NAME}, found wrong_name-0.1.0.tar.gz"
            ),
        ),
        (
            EXPECTED_WHEEL_ARCHIVE_NAME,
            "fashion_radar-9.9.9.tar.gz",
            (
                "sdist archive filename mismatch: expected "
                f"{EXPECTED_SDIST_ARCHIVE_NAME}, found fashion_radar-9.9.9.tar.gz"
            ),
        ),
    ],
)
def test_rejects_package_archives_with_mismatched_filenames(
    tmp_path: Path,
    wheel_filename: str,
    sdist_filename: str,
    expected_error: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir, filename=wheel_filename)
    write_sdist(build_dir, filename=sdist_filename)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert expected_error in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    "root_dir",
    [
        "wrong_name-0.1.0",
        "fashion_radar-9.9.9",
    ],
)
def test_rejects_sdist_with_mismatched_root_directory(
    tmp_path: Path,
    root_dir: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, root_dir=root_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive root directory mismatch: "
        f"expected {EXPECTED_SDIST_ROOT_DIR}, found {root_dir}"
    ) in result.stderr
    assert "sdist archive missing required file" not in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    ("unsafe_path", "expected_path"),
    [
        ("../outside.txt", "../outside.txt"),
        ("/absolute.txt", "/absolute.txt"),
        ("fashion_radar/../outside.txt", "fashion_radar/../outside.txt"),
        ("C:/outside.txt", "C:/outside.txt"),
        ("C:outside.txt", "C:outside.txt"),
        ("//server/share/outside.txt", "//server/share/outside.txt"),
        (r"fashion_radar\..\outside.txt", "fashion_radar/../outside.txt"),
    ],
)
def test_rejects_wheel_with_unsafe_archive_member_path(
    tmp_path: Path,
    unsafe_path: str,
    expected_path: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir, files=WHEEL_FILES | {unsafe_path: "unsafe\n"})
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (f"wheel archive contains unsafe archive member path: {expected_path}") in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    ("unsafe_path", "expected_path"),
    [
        ("../outside.txt", "../outside.txt"),
        ("/absolute.txt", "/absolute.txt"),
        ("fashion_radar-0.1.0/../outside.txt", "fashion_radar-0.1.0/../outside.txt"),
        ("C:/outside.txt", "C:/outside.txt"),
        ("C:outside.txt", "C:outside.txt"),
        ("//server/share/outside.txt", "//server/share/outside.txt"),
        (
            r"fashion_radar-0.1.0\..\outside.txt",
            "fashion_radar-0.1.0/../outside.txt",
        ),
    ],
)
def test_rejects_sdist_with_unsafe_archive_member_path(
    tmp_path: Path,
    unsafe_path: str,
    expected_path: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist_with_raw_member(build_dir, unsafe_path)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (f"sdist archive contains unsafe archive member path: {expected_path}") in result.stderr
    assert "Traceback" not in result.stderr


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


def wheel_files_with_dist_info_dir(dist_info_dir: str) -> dict[str, str]:
    return {
        (
            f"{dist_info_dir}/{path.split('/', 1)[1]}"
            if path.startswith(f"{EXPECTED_WHEEL_DIST_INFO_DIR}/")
            else path
        ): content
        for path, content in WHEEL_FILES.items()
    }


@pytest.mark.parametrize(
    "dist_info_dir",
    [
        "wrong_name-0.1.0.dist-info",
        "fashion_radar-9.9.9.dist-info",
    ],
)
def test_rejects_wheel_with_mismatched_dist_info_directory(
    tmp_path: Path,
    dist_info_dir: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir, files=wheel_files_with_dist_info_dir(dist_info_dir))
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "wheel archive dist-info directory mismatch: expected "
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}, found {dist_info_dir}"
    ) in result.stderr
    assert "Traceback" not in result.stderr


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


def test_rejects_sdist_without_community_signal_profile_example(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[
            path for path in SDIST_FILES if path != "examples/community-signal-profile.example.json"
        ],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive missing required file: examples/community-signal-profile.example.json"
    ) in result.stderr


def test_rejects_sdist_without_watchlist_community_signal_sample(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[
            path
            for path in SDIST_FILES
            if path != "examples/community-signals.watchlist.example.csv"
        ],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive missing required file: examples/community-signals.watchlist.example.csv"
    ) in result.stderr


def test_rejects_sdist_without_community_tool_handoff_csv_template(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[
            path for path in SDIST_FILES if path != "examples/community-tool-handoff.example.csv"
        ],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive missing required file: examples/community-tool-handoff.example.csv"
    ) in result.stderr


def test_rejects_sdist_without_community_tool_handoff_json_template(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[
            path for path in SDIST_FILES if path != "examples/community-tool-handoff.example.json"
        ],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive missing required file: examples/community-tool-handoff.example.json"
    ) in result.stderr


@pytest.mark.parametrize(
    "missing_path",
    [
        "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
        "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    ],
)
def test_rejects_sdist_without_community_tool_handoff_directory_example(
    tmp_path: Path,
    missing_path: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[path for path in SDIST_FILES if path != missing_path],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert f"sdist archive missing required file: {missing_path}" in result.stderr


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


def test_rejects_sdist_with_env_local(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + [".env.local"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "sdist archive contains forbidden release member: .env.local" in result.stderr


@pytest.mark.parametrize(
    "forbidden_path",
    [
        "docs/reviews/",
        "docs/reviews/opencode-stage-1-code-review.md",
        "docs/superpowers/",
        "docs/superpowers/plans/2026-06-20-stage-122-plan.md",
        "docs/superpowers/specs/2026-06-20-stage-122-design.md",
    ],
)
def test_rejects_sdist_with_internal_review_or_plan_artifacts(
    tmp_path: Path,
    forbidden_path: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + [forbidden_path])

    result = run_checker(build_dir)

    assert result.returncode == 1
    expected_path = forbidden_path.rstrip("/")
    assert f"sdist archive contains forbidden release member: {expected_path}" in result.stderr


def test_rejects_sdist_with_local_sqlite_database(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + ["data/fashion-radar.sqlite"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive contains forbidden release member: data/fashion-radar.sqlite"
        in result.stderr
    )


def test_rejects_sdist_with_database_sidecar_outside_local_state_dirs(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    forbidden_paths = ["runtime.sqlite-backup", "cache.db-bak"]
    write_sdist(build_dir, files=SDIST_FILES + forbidden_paths)

    result = run_checker(build_dir)

    assert result.returncode == 1
    for forbidden_path in forbidden_paths:
        assert f"sdist archive contains forbidden release member: {forbidden_path}" in result.stderr


def test_rejects_wheel_with_database_sidecar(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files=WHEEL_FILES | {"fashion_radar/runtime.sqlite-backup": ""},
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "wheel archive contains forbidden release member: fashion_radar/runtime.sqlite-backup"
    ) in result.stderr


def test_rejects_sdist_with_generated_report(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + ["reports/latest.json"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "sdist archive contains forbidden release member: reports/latest.json" in result.stderr


def test_rejects_sdist_with_generated_source_config(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + ["configs/sources.yaml"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "sdist archive contains forbidden release member: configs/sources.yaml" in result.stderr


def test_rejects_sdist_with_codegraph_database(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + [".codegraph/codegraph.db"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive contains forbidden release member: .codegraph/codegraph.db" in result.stderr
    )


def test_rejects_sdist_with_cookie_session_and_private_export_files(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    forbidden_paths = ["cookies.txt", "session.json", "private-source-export.csv"]
    write_sdist(build_dir, files=SDIST_FILES + forbidden_paths)

    result = run_checker(build_dir)

    assert result.returncode == 1
    for forbidden_path in forbidden_paths:
        assert f"sdist archive contains forbidden release member: {forbidden_path}" in result.stderr


def test_rejects_sdist_with_wildcard_cookie_session_and_private_export_files(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    forbidden_paths = [
        "cookies-chrome.txt",
        "cookies-prod.json",
        "session-prod.json",
        "private-export.csv",
        "xhs-private-export-2026.csv",
    ]
    write_sdist(build_dir, files=SDIST_FILES + forbidden_paths)

    result = run_checker(build_dir)

    assert result.returncode == 1
    for forbidden_path in forbidden_paths:
        assert f"sdist archive contains forbidden release member: {forbidden_path}" in result.stderr


def test_rejects_wheel_with_wildcard_cookie_session_or_private_export_file(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files=WHEEL_FILES
        | {
            "fashion_radar/cookies-chrome.txt": "",
            "fashion_radar/session-prod.json": "",
            "fashion_radar/private-export.csv": "",
        },
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "wheel archive contains forbidden release member: fashion_radar/cookies-chrome.txt"
    ) in result.stderr
    assert (
        "wheel archive contains forbidden release member: fashion_radar/session-prod.json"
    ) in result.stderr
    assert (
        "wheel archive contains forbidden release member: fashion_radar/private-export.csv"
    ) in result.stderr


def test_rejects_wheel_with_bytecode_cache(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files=WHEEL_FILES | {"fashion_radar/__pycache__/cli.cpython-311.pyc": ""},
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "wheel archive contains forbidden release member: "
        "fashion_radar/__pycache__/cli.cpython-311.pyc"
    ) in result.stderr


def test_sdist_allows_release_member_allowlist(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=SDIST_FILES
        + [".env.example", ".codegraph/.gitignore", "data/README.md", "reports/README.md"],
    )

    result = run_checker(build_dir)

    assert result.returncode == 0
    assert result.stdout == "Package archives contain required files.\n"
    assert result.stderr == ""


def test_rejects_sdist_with_local_credential_config_files(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    forbidden_paths = [".pypirc", "pip.conf", "pip.ini", "uv.toml", ".netrc", ".npmrc"]
    write_sdist(build_dir, files=SDIST_FILES + forbidden_paths)

    result = run_checker(build_dir)

    assert result.returncode == 1
    for forbidden_path in forbidden_paths:
        assert f"sdist archive contains forbidden release member: {forbidden_path}" in result.stderr


def test_rejects_wheel_metadata_without_project_name(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA": (
            f"Metadata-Version: 2.4\nVersion: {EXPECTED_METADATA.version}\n"
        )
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert f"METADATA is missing Name: {EXPECTED_METADATA.name}" in result.stderr


def test_rejects_wheel_metadata_without_project_version(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA": (
            f"Metadata-Version: 2.4\nName: {EXPECTED_METADATA.name}\n"
        )
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert f"METADATA is missing Version: {EXPECTED_METADATA.version}" in result.stderr


def test_rejects_wheel_entry_points_without_console_script(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": (
            "[console_scripts]\nother-command = fashion_radar.cli:app\n"
        )
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    for console_script_line in EXPECTED_METADATA.console_script_lines:
        assert f"entry_points.txt is missing {console_script_line}" in result.stderr
