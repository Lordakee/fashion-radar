#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

BINARY_SAMPLE_BYTES = 8192
SUCCESS_MESSAGE = "Release hygiene checks passed."

CREDENTIAL_FILENAMES = {
    ".netrc",
    ".npmrc",
    ".pypirc",
    "pip.conf",
    "pip.ini",
    "uv.toml",
}
LOCAL_SECRET_FILENAMES = {
    "cookies.json",
    "cookies.txt",
    "session.json",
    "storage-state.json",
}
LOCAL_SECRET_DIRNAMES = {
    "browser-profiles",
    "exports",
    "private-exports",
}
BUILD_ARTIFACT_DIRNAMES = {
    ".cache",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "build",
    "dist",
    "__pycache__",
}
GENERATED_CONFIG_PATHS = {
    "configs/entities.yaml",
    "configs/scoring.yaml",
    "configs/sources.yaml",
}
ALLOWED_LOCAL_STATE_PATHS = {
    "data/readme.md",
    "reports/readme.md",
}
ALLOWED_ENV_FILENAMES = {
    ".env.example",
}
ALLOWED_CODEGRAPH_PATHS = {
    ".codegraph/.gitignore",
}

GITHUB_TOKEN_PATTERNS = [
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82,255}\b"),
]
PEM_PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"
    r"[\s\S]*?"
    r"-----END [A-Z0-9 ]*PRIVATE KEY-----"
)
URL_USERINFO_PATTERN = re.compile(r"://([^/\s@]+)@")
UV_LOCK_PATH = "uv.lock"
PUBLIC_PYPI_REGISTRY_URL = "https://pypi.org/simple"
PUBLIC_PYPI_ARTIFACT_HOST = "files.pythonhosted.org"
UV_LOCK_REGISTRY_URL_PATTERN = re.compile(
    r'\bregistry\s*=\s*"(?P<url>https?://[^"]+)"',
    re.IGNORECASE,
)
UV_LOCK_ARTIFACT_URL_PATTERN = re.compile(
    r'\burl\s*=\s*"(?P<url>https?://[^"]+)"',
    re.IGNORECASE,
)
UV_LOCK_INDEX_MARKER_PATTERN = re.compile(
    r"\b(?P<marker>index-url|extra-index-url|find-links|default-index|extra-index)\b",
    re.IGNORECASE,
)
REVIEW_CAPTURE_MIN_STAGE = 159
REVIEW_CAPTURE_ARTIFACT_PATTERN = re.compile(
    r"^docs/reviews/"
    r"opencode-stage-(?P<stage>[0-9]+)-"
    r"(?:plan|code|release)-(?:review|rereview(?:-[0-9]+)?)\.md$"
)
NON_STAGE_OPENCODE_REVIEW_ARTIFACT_PATTERN = re.compile(
    r"^docs/reviews/opencode-(?!stage-[0-9]+-).+\.md$"
)
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\)|.)")
REVIEW_CAPTURE_TOOL_STATUS_PREFIXES = (
    "Review written to ",
    "Wrote ",
)
REVIEW_CAPTURE_PROCESS_PREFIXES = (
    "I'll ",
    "I will ",
    "Let me ",
    "Now let me ",
)
REVIEW_CAPTURE_TIMEOUT_STUB_PREFIXES = (
    "opencode plan review timed out",
    "opencode code review timed out",
    "opencode release review timed out",
)

SECRET_PATTERNS = [
    ("GitHub token", *GITHUB_TOKEN_PATTERNS),
    ("PEM private key", PEM_PRIVATE_KEY_PATTERN),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check repository release hygiene for local secrets and credentials.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Path inside the git repository to check. Defaults to the current directory.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    git_root, repo_error = find_git_root(args.repo_root)
    if repo_error is not None:
        print(repo_error, file=sys.stderr)
        return 1
    if git_root is None:
        print(f"not a git repository: {args.repo_root}", file=sys.stderr)
        return 1

    findings = collect_findings(git_root)
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1

    print(SUCCESS_MESSAGE)
    return 0


def find_git_root(repo_root: Path) -> tuple[Path | None, str | None]:
    repo_path = repo_root.resolve()
    if not repo_path.exists():
        return None, f"repository path does not exist: {repo_path}"
    if not repo_path.is_dir():
        return None, f"repository path is not a directory: {repo_path}"

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=repo_path,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return None, "git executable not found"

    if result.returncode != 0:
        return None, f"not a git repository: {repo_path}"

    return Path(result.stdout.strip()).resolve(), None


def collect_findings(repo_root: Path) -> list[str]:
    findings: list[str] = []

    tracked_paths, error = git_output_lines(repo_root, "ls-files")
    if error is not None:
        return [error]
    untracked_paths, error = git_output_lines(
        repo_root,
        "ls-files",
        "--others",
        "--exclude-standard",
    )
    if error is not None:
        return [error]

    findings.extend(find_forbidden_path_findings(tracked_paths, "tracked"))
    findings.extend(find_forbidden_path_findings(untracked_paths, "untracked"))
    findings.extend(find_uv_lock_hygiene_findings(repo_root, tracked_paths, "tracked"))
    findings.extend(find_uv_lock_hygiene_findings(repo_root, untracked_paths, "untracked"))
    findings.extend(find_secret_findings(repo_root, tracked_paths, "tracked"))
    findings.extend(find_secret_findings(repo_root, untracked_paths, "untracked"))
    findings.extend(find_review_capture_hygiene_findings(repo_root, tracked_paths, "tracked"))
    findings.extend(find_review_capture_hygiene_findings(repo_root, untracked_paths, "untracked"))
    findings.extend(find_remote_credential_findings(repo_root))
    findings.extend(find_extraheader_findings(repo_root))

    return findings


def git_output_lines(
    repo_root: Path,
    *args: str,
    allow_no_match: bool = False,
) -> tuple[list[str], str | None]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return [], "git executable not found"

    if result.returncode == 0:
        return result.stdout.splitlines(), None
    if allow_no_match and result.returncode == 1 and not result.stdout.strip():
        return [], None

    command = " ".join(("git", *args))
    detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
    return [], f"git command failed: {command}: {detail}"


def find_forbidden_path_findings(paths: list[str], path_status: str) -> list[str]:
    findings = []
    for path in paths:
        normalized = normalize_git_path(path)
        if normalized and is_forbidden_path(normalized):
            findings.append(f"forbidden {path_status} path: {normalized}")
    return findings


def normalize_git_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def is_forbidden_path(path: str) -> bool:
    lower_path = path.lower()
    if lower_path in ALLOWED_CODEGRAPH_PATHS or lower_path in ALLOWED_LOCAL_STATE_PATHS:
        return False
    if lower_path == ".codegraph" or lower_path.startswith(".codegraph/"):
        return True

    parts = PurePosixPath(lower_path).parts
    filename = parts[-1] if parts else lower_path

    if filename in CREDENTIAL_FILENAMES or filename in LOCAL_SECRET_FILENAMES:
        return True
    if is_local_secret_filename(filename):
        return True
    if any(part in LOCAL_SECRET_DIRNAMES for part in parts):
        return True
    if any(part in BUILD_ARTIFACT_DIRNAMES or part.endswith(".egg-info") for part in parts):
        return True
    if filename == ".env":
        return True
    if filename.startswith(".env.") and filename not in ALLOWED_ENV_FILENAMES:
        return True
    if lower_path in GENERATED_CONFIG_PATHS:
        return True
    if lower_path.startswith("data/") or lower_path.startswith("reports/"):
        return True
    if is_database_or_sidecar(filename):
        return True
    if filename.endswith((".pyc", ".pyo", ".pyd")):
        return True
    if filename.endswith((".pem", ".key")):
        return True

    return False


def is_local_secret_filename(filename: str) -> bool:
    return (
        re.match(r"cookies.*\.(?:txt|json)$", filename) is not None
        or re.match(r"session.*\.json$", filename) is not None
        or re.match(r"storage-state.*\.json$", filename) is not None
        or re.match(r".*private-export.*\.csv$", filename) is not None
        or re.match(r".*private-source-export.*\.csv$", filename) is not None
    )


def is_database_or_sidecar(filename: str) -> bool:
    return re.search(r"\.(?:sqlite3?|db)(?:-.+)?$", filename) is not None


def find_uv_lock_hygiene_findings(
    repo_root: Path,
    paths: list[str],
    path_status: str,
) -> list[str]:
    findings = []
    for path in paths:
        normalized = normalize_git_path(path)
        if normalized != UV_LOCK_PATH:
            continue

        file_path = safe_repo_path(repo_root, normalized)
        if file_path is None or file_path.is_symlink() or not file_path.is_file():
            continue

        text = read_text_if_not_binary(file_path)
        if text is None:
            continue

        findings.extend(uv_lock_text_findings(normalized, text, path_status))
    return findings


def uv_lock_text_findings(path: str, text: str, path_status: str) -> list[str]:
    findings = []
    prefix = f"forbidden mirror/private index in {path_status} file: {path}"

    for match in UV_LOCK_INDEX_MARKER_PATTERN.finditer(text):
        line_number = text.count("\n", 0, match.start()) + 1
        marker = match.group("marker")
        findings.append(f"{prefix}:{line_number}: {marker}: <redacted>")

    for match in UV_LOCK_REGISTRY_URL_PATTERN.finditer(text):
        url = match.group("url")
        if not is_public_pypi_registry_url(url):
            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(f"{prefix}:{line_number}: registry URL: <redacted>")

    for match in UV_LOCK_ARTIFACT_URL_PATTERN.finditer(text):
        url = match.group("url")
        if not is_public_pypi_artifact_url(url):
            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(f"{prefix}:{line_number}: artifact URL: <redacted>")

    return findings


def is_public_pypi_registry_url(url: str) -> bool:
    return url.rstrip("/") == PUBLIC_PYPI_REGISTRY_URL


def is_public_pypi_artifact_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname == PUBLIC_PYPI_ARTIFACT_HOST


def find_secret_findings(
    repo_root: Path,
    paths: list[str],
    path_status: str,
) -> list[str]:
    findings = []
    for path in paths:
        normalized = normalize_git_path(path)
        if not normalized:
            continue

        if path_status == "untracked" and (repo_root / normalized).is_symlink():
            continue

        file_path = safe_repo_path(repo_root, normalized)
        if file_path is None or file_path.is_symlink() or not file_path.is_file():
            continue

        text = read_text_if_not_binary(file_path)
        if text is None:
            continue

        for label, pattern in iter_secret_patterns():
            for match in pattern.finditer(text):
                line_number = text.count("\n", 0, match.start()) + 1
                findings.append(
                    f"forbidden secret in {path_status} file: "
                    f"{normalized}:{line_number}: {label}: <redacted>"
                )

    return findings


def iter_secret_patterns():
    for label, *patterns in SECRET_PATTERNS:
        for pattern in patterns:
            yield label, pattern


def safe_repo_path(repo_root: Path, relative_path: str) -> Path | None:
    candidate = (repo_root / relative_path).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError:
        return None
    return candidate


def read_text_if_not_binary(path: Path) -> str | None:
    try:
        with path.open("rb") as file:
            sample = file.read(BINARY_SAMPLE_BYTES)
            if is_binary_sample(sample):
                return None
            data = sample + file.read()
    except OSError:
        return None

    return data.decode("utf-8", errors="replace")


def is_binary_sample(sample: bytes) -> bool:
    return b"\0" in sample


def find_review_capture_hygiene_findings(
    repo_root: Path,
    paths: list[str],
    path_status: str,
) -> list[str]:
    findings = []
    for path in paths:
        normalized = normalize_git_path(path)
        if not normalized or not is_review_capture_artifact_path(normalized):
            continue

        file_path = safe_repo_path(repo_root, normalized)
        if file_path is None or file_path.is_symlink() or not file_path.is_file():
            continue

        text = read_text_if_not_binary(file_path)
        if text is None:
            continue

        findings.extend(
            review_capture_text_findings(
                normalized,
                text,
                path_status,
            )
        )
    return findings


def is_review_capture_artifact_path(path: str) -> bool:
    lower_path = path.lower()
    match = REVIEW_CAPTURE_ARTIFACT_PATTERN.fullmatch(lower_path)
    if match is not None:
        return int(match.group("stage")) >= REVIEW_CAPTURE_MIN_STAGE
    if lower_path.endswith("-prompt.md"):
        return False
    return NON_STAGE_OPENCODE_REVIEW_ARTIFACT_PATTERN.fullmatch(lower_path) is not None


def review_capture_text_findings(
    path: str,
    text: str,
    path_status: str,
) -> list[str]:
    prefix = f"forbidden review capture artifact in {path_status} file: {path}"
    if not text.strip():
        return [f"{prefix}: empty output"]

    findings = []
    first_nonblank: tuple[int, str] | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped and first_nonblank is None:
            first_nonblank = (line_number, stripped)
        if ANSI_ESCAPE_PATTERN.search(line):
            findings.append(f"{prefix}:{line_number}: ANSI escape sequence")
        if is_review_tool_status_line(stripped):
            findings.append(f"{prefix}:{line_number}: tool-status line")
        if has_review_tool_ui_marker(line):
            findings.append(f"{prefix}:{line_number}: tool UI marker")
        if is_review_timeout_stub_line(stripped):
            findings.append(f"{prefix}:{line_number}: timeout stub")

    if first_nonblank is not None:
        line_number, stripped = first_nonblank
        if is_review_process_chatter_start(stripped):
            findings.append(f"{prefix}:{line_number}: process chatter at start")

    return findings


def is_review_tool_status_line(line: str) -> bool:
    return (
        line == "Review complete"
        or line.startswith(("Review complete.", "Review complete:"))
        or any(line.startswith(prefix) for prefix in REVIEW_CAPTURE_TOOL_STATUS_PREFIXES)
    )


def has_review_tool_ui_marker(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith(("\u2192", "\u2731")) or stripped.startswith("build \u00b7")


def is_review_process_chatter_start(line: str) -> bool:
    return any(line.startswith(prefix) for prefix in REVIEW_CAPTURE_PROCESS_PREFIXES)


def is_review_timeout_stub_line(line: str) -> bool:
    lower_line = line.lower()
    return any(lower_line.startswith(prefix) for prefix in REVIEW_CAPTURE_TIMEOUT_STUB_PREFIXES)


def find_remote_credential_findings(repo_root: Path) -> list[str]:
    lines, error = git_output_lines(repo_root, "remote", "-v")
    if error is not None:
        return [error]

    findings = []
    seen_lines: set[str] = set()
    for line in lines:
        if line in seen_lines or not remote_line_has_credential(line):
            continue
        seen_lines.add(line)
        remote_name = line.split(None, 1)[0] if line.split(None, 1) else "unknown"
        findings.append(f"forbidden git remote credential: {remote_name}: <redacted>")
    return findings


def remote_line_has_credential(line: str) -> bool:
    if contains_github_token(line):
        return True

    match = URL_USERINFO_PATTERN.search(line)
    if match is None:
        return False

    userinfo = match.group(1)
    return ":" in userinfo or contains_github_token(userinfo)


def contains_github_token(text: str) -> bool:
    return any(pattern.search(text) for pattern in GITHUB_TOKEN_PATTERNS)


def find_extraheader_findings(repo_root: Path) -> list[str]:
    lines, error = git_output_lines(
        repo_root,
        "config",
        "--get-regexp",
        r"^http\..*\.extraheader$",
        allow_no_match=True,
    )
    if error is not None:
        return [error]

    findings = []
    for line in lines:
        key, value = split_config_line(line)
        if key and "authorization" in value.lower():
            findings.append(
                f"forbidden persistent git config: {key} contains authorization header: <redacted>"
            )
    return findings


def split_config_line(line: str) -> tuple[str, str]:
    parts = line.split(None, 1)
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


if __name__ == "__main__":
    raise SystemExit(main())
