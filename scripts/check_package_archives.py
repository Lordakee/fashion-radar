#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from collections.abc import Iterable
from email.parser import Parser
from pathlib import Path

PROJECT_NAME = "fashion-radar"
PROJECT_VERSION = "0.1.0"
ENTRY_POINT = "fashion-radar = fashion_radar.cli:app"

WHEEL_REQUIRED_PATHS = [
    "fashion_radar/cli.py",
    "fashion_radar/__main__.py",
    "fashion_radar/templates/daily_report.md",
    "fashion_radar/templates/configs/sources.example.yaml",
    "fashion_radar/templates/configs/entities.example.yaml",
    "fashion_radar/templates/configs/scoring.example.yaml",
]

WHEEL_REQUIRED_DIST_INFO_PATHS = [
    "METADATA",
    "WHEEL",
    "RECORD",
    "entry_points.txt",
    "licenses/LICENSE",
]

SDIST_REQUIRED_PATHS = [
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

FORBIDDEN_RELEASE_MEMBER_ALLOWLIST = {
    ".env.example",
    ".codegraph/.gitignore",
    "data/README.md",
    "reports/README.md",
}

FORBIDDEN_RELEASE_GENERATED_CONFIGS = {
    "configs/sources.yaml",
    "configs/entities.yaml",
    "configs/scoring.yaml",
}

FORBIDDEN_RELEASE_EXACT_NAMES = {
    ".netrc",
    ".npmrc",
    ".pypirc",
    "cookies.json",
    "cookies.txt",
    "pip.conf",
    "pip.ini",
    "session.json",
    "storage-state.json",
    "uv.toml",
}

FORBIDDEN_RELEASE_EXACT_DIR_NAMES = {
    ".cache",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "browser-profiles",
    "build",
    "dist",
    "exports",
    "private-exports",
    "__pycache__",
}

FORBIDDEN_RELEASE_SUFFIXES = (
    ".key",
    ".pem",
    ".pyc",
    ".pyd",
    ".pyo",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Fashion Radar wheel and sdist archive contents.",
    )
    parser.add_argument(
        "build_dir",
        type=Path,
        help="Directory containing exactly one wheel and one sdist archive.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_dir = args.build_dir

    errors = validate_build_dir(build_dir)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Package archives contain required files.")
    return 0


def validate_build_dir(build_dir: Path) -> list[str]:
    if not build_dir.is_dir():
        return [f"build directory does not exist: {build_dir}"]

    wheel_path, wheel_errors = select_single_archive(build_dir, "*.whl", "wheel")
    sdist_path, sdist_errors = select_single_archive(build_dir, "*.tar.gz", "sdist")
    errors = wheel_errors + sdist_errors
    if errors:
        return errors

    if wheel_path is None or sdist_path is None:
        return ["internal archive selection error"]

    return validate_wheel(wheel_path) + validate_sdist(sdist_path)


def select_single_archive(
    build_dir: Path, pattern: str, label: str
) -> tuple[Path | None, list[str]]:
    archives = sorted(path for path in build_dir.glob(pattern) if path.is_file())
    if not archives:
        return None, [f"missing {label} archive ({pattern})"]
    if len(archives) > 1:
        archive_names = ", ".join(path.name for path in archives)
        return None, [
            f"expected exactly one {label} archive ({pattern}), "
            f"found {len(archives)}: {archive_names}"
        ]
    return archives[0], []


def validate_wheel(wheel_path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(wheel_path) as archive:
            paths = clean_archive_paths(archive.namelist())
            errors = missing_required_paths(
                paths,
                exact_paths=WHEEL_REQUIRED_PATHS,
                archive_label="wheel archive",
            )
            errors.extend(forbidden_release_member_errors(paths, "wheel archive"))
            dist_info_dir, dist_info_errors = select_wheel_dist_info_dir(paths)
            errors.extend(dist_info_errors)
            if dist_info_dir is not None:
                errors.extend(validate_wheel_dist_info_files(paths, dist_info_dir))
                if f"{dist_info_dir}/METADATA" in paths:
                    errors.extend(validate_wheel_metadata(archive, dist_info_dir))
                if f"{dist_info_dir}/entry_points.txt" in paths:
                    errors.extend(validate_wheel_entry_points(archive, dist_info_dir))
            return errors
    except zipfile.BadZipFile as exc:
        return [f"could not read wheel archive {wheel_path.name}: {exc}"]


def select_wheel_dist_info_dir(paths: set[str]) -> tuple[str | None, list[str]]:
    dist_info_dirs = {
        path.split("/", 1)[0]
        for path in paths
        if "/" in path and path.split("/", 1)[0].endswith(".dist-info")
    }
    if len(dist_info_dirs) != 1:
        dirs = ", ".join(sorted(dist_info_dirs)) or "none"
        return None, [
            f"wheel archive must contain exactly one top-level .dist-info directory; found {dirs}"
        ]
    return dist_info_dirs.pop(), []


def validate_wheel_dist_info_files(paths: set[str], dist_info_dir: str) -> list[str]:
    errors = []
    for relative_path in WHEEL_REQUIRED_DIST_INFO_PATHS:
        archive_path = f"{dist_info_dir}/{relative_path}"
        if archive_path not in paths:
            errors.append(f"wheel dist-info missing required file: {relative_path}")
    return errors


def validate_wheel_metadata(archive: zipfile.ZipFile, dist_info_dir: str) -> list[str]:
    metadata_path = f"{dist_info_dir}/METADATA"
    metadata = read_zip_text(archive, metadata_path)
    parsed_metadata = Parser().parsestr(metadata)
    errors = []
    if parsed_metadata.get("Name") != PROJECT_NAME:
        errors.append(f"METADATA is missing Name: {PROJECT_NAME}")
    if parsed_metadata.get("Version") != PROJECT_VERSION:
        errors.append(f"METADATA is missing Version: {PROJECT_VERSION}")
    return errors


def validate_wheel_entry_points(archive: zipfile.ZipFile, dist_info_dir: str) -> list[str]:
    entry_points_path = f"{dist_info_dir}/entry_points.txt"
    entry_points = read_zip_text(archive, entry_points_path)
    entry_point_lines = {line.strip() for line in entry_points.splitlines()}
    if ENTRY_POINT not in entry_point_lines:
        return [f"entry_points.txt is missing {ENTRY_POINT}"]
    return []


def read_zip_text(archive: zipfile.ZipFile, path: str) -> str:
    return archive.read(path).decode("utf-8")


def validate_sdist(sdist_path: Path) -> list[str]:
    try:
        with tarfile.open(sdist_path, "r:gz") as archive:
            paths = normalize_sdist_paths(member.name for member in archive.getmembers())
    except tarfile.TarError as exc:
        return [f"could not read sdist archive {sdist_path.name}: {exc}"]

    errors = missing_required_paths(
        paths,
        exact_paths=SDIST_REQUIRED_PATHS,
        archive_label="sdist archive",
    )
    errors.extend(forbidden_release_member_errors(paths, "sdist archive"))
    return errors


def clean_archive_paths(paths: Iterable[object]) -> set[str]:
    cleaned_paths = [clean_archive_path(path) for path in paths]
    return {path for path in cleaned_paths if path}


def normalize_sdist_paths(paths: Iterable[str]) -> set[str]:
    cleaned_paths = [clean_archive_path(path) for path in paths]
    cleaned_paths = [path for path in cleaned_paths if path]
    if not cleaned_paths:
        return set()

    roots = {path.split("/", 1)[0] for path in cleaned_paths if "/" in path}
    if len(roots) != 1:
        return set(cleaned_paths)

    root = roots.pop()
    if not all(path == root or path.startswith(f"{root}/") for path in cleaned_paths):
        return set(cleaned_paths)

    return {
        path.removeprefix(f"{root}/")
        for path in cleaned_paths
        if path != root and path.removeprefix(f"{root}/")
    }


def clean_archive_path(path: object) -> str:
    normalized = str(path).replace("\\", "/").rstrip("/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized == ".":
        return ""
    return normalized


def forbidden_release_member_errors(paths: set[str], archive_label: str) -> list[str]:
    return [
        f"{archive_label} contains forbidden release member: {path}"
        for path in sorted(paths)
        if is_forbidden_release_member(path)
    ]


def is_forbidden_release_member(path: str) -> bool:
    path = clean_archive_path(path)
    if not path or path in FORBIDDEN_RELEASE_MEMBER_ALLOWLIST:
        return False

    lower_path = path.lower()
    lower_parts = lower_path.split("/")
    lower_name = lower_parts[-1]

    if any(part == ".env" or part.startswith(".env.") for part in lower_parts):
        return True

    if any(part.endswith(".egg-info") for part in lower_parts):
        return True

    if any(part in FORBIDDEN_RELEASE_EXACT_DIR_NAMES for part in lower_parts):
        return True

    if lower_name in FORBIDDEN_RELEASE_EXACT_NAMES:
        return True

    if is_forbidden_local_secret_name(lower_name):
        return True

    if lower_path in FORBIDDEN_RELEASE_GENERATED_CONFIGS:
        return True

    if lower_parts[0] in {".codegraph", "data", "reports"}:
        return True

    return lower_name.endswith(FORBIDDEN_RELEASE_SUFFIXES) or is_database_or_sidecar(lower_name)


def is_forbidden_local_secret_name(filename: str) -> bool:
    return (
        re.match(r"cookies.*\.(?:txt|json)$", filename) is not None
        or re.match(r"session.*\.json$", filename) is not None
        or re.match(r"storage-state.*\.json$", filename) is not None
        or re.match(r".*private-export.*\.csv$", filename) is not None
        or re.match(r".*private-source-export.*\.csv$", filename) is not None
    )


def is_database_or_sidecar(filename: str) -> bool:
    return re.search(r"\.(?:sqlite3?|db)(?:-.+)?$", filename) is not None


def missing_required_paths(
    paths: set[str],
    *,
    exact_paths: list[str],
    archive_label: str,
) -> list[str]:
    errors = []
    for required_path in exact_paths:
        if required_path not in paths:
            errors.append(f"{archive_label} missing required file: {required_path}")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
