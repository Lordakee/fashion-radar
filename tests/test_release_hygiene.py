from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_release_hygiene.py"

GITHUB_TOKEN = "ghp_" + ("a" * 36)
CREDENTIAL_FILENAMES = [
    ".pypirc",
    "pip.conf",
    "pip.ini",
    "uv.toml",
    ".netrc",
    ".npmrc",
]
HIGH_RISK_LOCAL_PATHS = [
    "data/fashion-radar.sqlite",
    "reports/latest.json",
    "configs/sources.yaml",
    "configs/entities.yaml",
    "configs/scoring.yaml",
    "session.json",
    "storage-state.json",
    "browser-profiles/default/state.json",
    "private-source-export.csv",
    "private-exports/signals.csv",
    "exports/raw.csv",
    "secrets.pem",
    "deploy.key",
]
TRACKED_BUILD_ARTIFACT_PATHS = [
    "build/lib/fashion_radar.py",
    "dist/fashion-radar.tar.gz",
    ".pytest_cache/v/cache/nodeids",
    ".ruff_cache/0.12.0/123456",
    ".venv/bin/python",
    "src/fashion_radar.egg-info/PKG-INFO",
    "pkg/__pycache__/module.cpython-311.pyc",
]
WILDCARD_LOCAL_SECRET_PATHS = [
    "cookies-chrome.txt",
    "cookies-prod.json",
    "session-prod.json",
    "storage-state-prod.json",
    "private-export.csv",
    "xhs-private-export-2026.csv",
]
CLEAN_REVIEW_ARTIFACT = """## Verdict

No critical findings. No important findings.

## Critical
None.

## Important
None.
"""


def run_checker(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    )


def init_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    git(repo_root, "init")
    git(repo_root, "config", "user.email", "tests@example.invalid")
    git(repo_root, "config", "user.name", "Release Hygiene Tests")
    write_tracked(repo_root, "README.md", "# Fixture\n")
    git(repo_root, "commit", "-m", "initial")
    return repo_root


def write_file(repo_root: Path, relative_path: str, content: str = "fixture\n") -> Path:
    path = repo_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_tracked(
    repo_root: Path,
    relative_path: str,
    content: str = "fixture\n",
    *,
    force: bool = False,
) -> Path:
    path = write_file(repo_root, relative_path, content)
    if force:
        git(repo_root, "add", "-f", relative_path)
    else:
        git(repo_root, "add", relative_path)
    return path


def load_checker_module():
    spec = importlib.util.spec_from_file_location("check_release_hygiene", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_clean_temp_repo_passes(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_stage_159_review_artifact_with_clean_body_passes(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        CLEAN_REVIEW_ARTIFACT,
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_stage_159_review_artifact_with_tool_status_line_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        "## Verdict\n\nWrote docs/reviews/opencode-stage-159-code-review.md\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-code-review.md:3: tool-status line"
    ) in result.stderr


def test_stage_159_review_artifact_with_review_completed_prose_passes(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        "## Verdict\n\nReview completed on 2026-06-23 with no blocking findings.\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_stage_159_review_artifact_prompt_with_tool_status_example_is_ignored(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review-prompt.md",
        "Review this stage. Reject output containing Wrote lines.\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_stage_158_legacy_review_artifact_is_not_rechecked(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-158-code-review.md",
        "## Verdict\n\nWrote docs/reviews/opencode-stage-158-code-review.md\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_untracked_stage_159_review_artifact_with_ansi_escape_fails(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_file(
        repo_root,
        "docs/reviews/opencode-stage-159-release-review.md",
        "## Verdict\n\n\x1b[32mApproved\x1b[0m\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in untracked file: "
        "docs/reviews/opencode-stage-159-release-review.md:3: ANSI escape sequence"
    ) in result.stderr


def test_stage_159_review_artifact_with_process_chatter_start_fails(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-plan-review.md",
        "I'll inspect the repository first.\n\n## Verdict\nNo blocking findings.\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-plan-review.md:1: process chatter at start"
    ) in result.stderr


def test_stage_159_review_artifact_with_tool_ui_marker_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-release-rereview.md",
        "## Verdict\n\nbuild \u00b7 running\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-release-rereview.md:3: tool UI marker"
    ) in result.stderr


def test_stage_159_review_artifact_with_inline_arrow_prose_passes(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        "## Verdict\n\n- `pytest -q` \u2192 1300 passed\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_non_stage_opencode_review_artifact_with_capture_noise_fails(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-full-project-review.md",
        "I'll inspect the repository first.\n\n\x1b[32mApproved\x1b[0m\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-full-project-review.md:1: process chatter at start"
    ) in result.stderr
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-full-project-review.md:3: ANSI escape sequence"
    ) in result.stderr


def test_stage_159_review_artifact_with_timeout_stub_fails(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        (
            "# Stage 159 Code Review\n\n"
            "opencode code review timed out after 600 seconds. "
            "No partial output was captured as approval.\n"
        ),
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-code-review.md:3: timeout stub"
    ) in result.stderr


def test_non_stage_opencode_review_artifact_with_clean_body_passes(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-full-project-review.md",
        "# Full Project Review\n\n## Critical\n\nNone.\n\n## Important\n\nNone.\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_stage_159_review_artifact_with_empty_output_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-release-review.md",
        "   \n\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-release-review.md: empty output"
    ) in result.stderr


def test_stage_159_numbered_rereview_artifact_is_checked(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-rereview-2.md",
        "## Verdict\n\nWrote docs/reviews/opencode-stage-159-code-rereview-2.md\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-code-rereview-2.md:3: tool-status line"
    ) in result.stderr


def test_tracked_env_local_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, ".env.local", "SECRET=value\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "forbidden tracked path: .env.local" in result.stderr


def test_tracked_codegraph_gitignore_is_allowed_but_database_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, ".codegraph/.gitignore", "*\n!.gitignore\n")
    write_tracked(repo_root, ".codegraph/codegraph.db", "not really sqlite\n", force=True)

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert "forbidden tracked path: .codegraph/codegraph.db" in result.stderr
    assert "forbidden tracked path: .codegraph/.gitignore" not in result.stderr


def test_tracked_data_and_reports_readmes_are_allowed(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, "data/README.md", "local data placeholder\n")
    write_tracked(repo_root, "reports/README.md", "local reports placeholder\n")

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_unignored_local_cookies_file_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_file(repo_root, "cookies.txt", "sessionid=value\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "forbidden untracked path: cookies.txt" in result.stderr


@pytest.mark.parametrize("path", HIGH_RISK_LOCAL_PATHS)
def test_tracked_high_risk_local_paths_are_rejected(
    tmp_path: Path,
    path: str,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, path, "local artifact\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert f"forbidden tracked path: {path}" in result.stderr


@pytest.mark.parametrize("path", TRACKED_BUILD_ARTIFACT_PATHS)
def test_tracked_build_cache_and_bytecode_paths_are_rejected(
    tmp_path: Path,
    path: str,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, path, "local artifact\n", force=True)

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert f"forbidden tracked path: {path}" in result.stderr


@pytest.mark.parametrize("path", WILDCARD_LOCAL_SECRET_PATHS)
def test_tracked_wildcard_local_secret_paths_are_rejected(
    tmp_path: Path,
    path: str,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, path, "local artifact\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert f"forbidden tracked path: {path}" in result.stderr


@pytest.mark.parametrize("path", HIGH_RISK_LOCAL_PATHS)
def test_untracked_high_risk_local_paths_are_rejected(
    tmp_path: Path,
    path: str,
) -> None:
    repo_root = init_repo(tmp_path)
    write_file(repo_root, path, "local artifact\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert f"forbidden untracked path: {path}" in result.stderr


@pytest.mark.parametrize("path", WILDCARD_LOCAL_SECRET_PATHS)
def test_untracked_wildcard_local_secret_paths_are_rejected(
    tmp_path: Path,
    path: str,
) -> None:
    repo_root = init_repo(tmp_path)
    write_file(repo_root, path, "local artifact\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert f"forbidden untracked path: {path}" in result.stderr


def test_tracked_file_with_valid_github_token_is_redacted_and_reports_line(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, "README.md", f"# Fixture\nleaked = {GITHUB_TOKEN}\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert "forbidden secret in tracked file: README.md:2: GitHub token" in result.stderr
    assert GITHUB_TOKEN not in result.stderr
    assert "<redacted>" in result.stderr


def test_untracked_file_with_valid_github_token_is_redacted_and_reports_line(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_file(repo_root, "notes.md", f"# Scratch\nleaked = {GITHUB_TOKEN}\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert "forbidden secret in untracked file: notes.md:2: GitHub token" in result.stderr
    assert GITHUB_TOKEN not in result.stderr
    assert "<redacted>" in result.stderr


def test_untracked_symlink_target_is_not_scanned_for_secret(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, ".gitignore", "ignored-secret.txt\n")
    git(repo_root, "commit", "-m", "ignore secret fixture")
    write_file(repo_root, "ignored-secret.txt", f"leaked = {GITHUB_TOKEN}\n")
    symlink = repo_root / "notes.md"
    try:
        symlink.symlink_to("ignored-secret.txt")
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink unavailable: {exc}")

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_prefix_only_github_token_examples_do_not_fail(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, "docs/github-token-examples.md", "Do not paste a ghp_ token.\n")
    write_tracked(repo_root, "tests/test_token_docs.py", 'EXAMPLE_PREFIX = "ghp_"\n')

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_persistent_remote_url_with_token_like_value_fails_redacted(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    token = "ghp_" + ("b" * 36)
    git(repo_root, "remote", "add", "origin", f"https://{token}@github.com/acme/widgets.git")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert "forbidden git remote credential: origin" in result.stderr
    assert token not in result.stderr
    assert "<redacted>" in result.stderr


def test_persistent_http_extraheader_authorization_config_fails_redacted(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    token = "ghp_" + ("c" * 36)
    header = f"AUTHORIZATION: bearer {token}"
    git(repo_root, "config", "http.https://github.com/.extraheader", header)

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden persistent git config: "
        "http.https://github.com/.extraheader contains authorization header"
    ) in result.stderr
    assert header not in result.stderr
    assert token not in result.stderr


def test_outside_git_repo_exits_cleanly_without_traceback(tmp_path: Path) -> None:
    repo_root = tmp_path / "not-a-repo"
    repo_root.mkdir()

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "not a git repository:" in result.stderr
    assert "Traceback" not in result.stderr


def test_current_repository_tracked_file_list_has_no_forbidden_tracked_paths() -> None:
    checker = load_checker_module()
    result = git(REPO_ROOT, "ls-files")
    tracked_paths = result.stdout.splitlines()

    assert checker.find_forbidden_path_findings(tracked_paths, "tracked") == []


def test_current_repository_tracked_review_artifacts_have_no_capture_findings() -> None:
    checker = load_checker_module()
    result = git(REPO_ROOT, "ls-files", "docs/reviews")
    tracked_paths = result.stdout.splitlines()

    assert (
        checker.find_review_capture_hygiene_findings(
            REPO_ROOT,
            tracked_paths,
            "tracked",
        )
        == []
    )


@pytest.mark.parametrize("filename", CREDENTIAL_FILENAMES)
def test_tracked_credential_config_filenames_are_rejected(
    tmp_path: Path,
    filename: str,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, filename, "secret=value\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert f"forbidden tracked path: {filename}" in result.stderr


@pytest.mark.parametrize("filename", CREDENTIAL_FILENAMES)
def test_untracked_credential_config_filenames_are_rejected(
    tmp_path: Path,
    filename: str,
) -> None:
    repo_root = init_repo(tmp_path)
    write_file(repo_root, filename, "secret=value\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert f"forbidden untracked path: {filename}" in result.stderr
