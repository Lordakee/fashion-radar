# Stage 48 Installed-Wheel First-Run Smoke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an installed-wheel mode to the deterministic first-run smoke and wire it into CI/release docs so packaged installs run the same local sample flow as source checkouts.

**Architecture:** Reuse `scripts/check_first_run_smoke.py` as the single smoke runner. Add an execution-mode flag that controls whether `repo_root/src` is prepended to `PYTHONPATH`; installed mode removes any inherited repo `src` entry and preflights the import origin so the smoke cannot silently pass by importing the source tree. Keep the deterministic CLI sequence, temporary runtime directories, checked-in example CSV, and default-artifact guard unchanged. CI and docs call the same script for source-checkout and installed-wheel confidence.

**Tech Stack:** Python stdlib, Typer CLI through `python -m fashion_radar`, pytest, GitHub Actions YAML, uv, ruff, Claude Code review with `--effort max`.

---

## Files

- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/github-upload-checklist.md`
- Modify: `README.md`
- Modify: `tests/test_cli_docs.py`
- Add: `docs/reviews/claude-code-stage-48-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-48-plan-review.md`
- Later add: `docs/reviews/claude-code-stage-48-release-review-prompt.md`
- Later add: `docs/reviews/claude-code-stage-48-release-review.md`

## Task 1: Installed Mode In Smoke Runner

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add failing tests for source vs installed PYTHONPATH behavior**

Add tests in `tests/test_first_run_smoke.py`:

```python
def test_command_environment_does_not_prepend_src_in_installed_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.setenv("PYTHONPATH", "/already/here")

    env = smoke.command_environment(context, source_checkout=False)

    assert env["PYTHONPATH"] == "/already/here"


def test_command_environment_leaves_pythonpath_absent_in_installed_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.delenv("PYTHONPATH", raising=False)

    env = smoke.command_environment(context, source_checkout=False)

    assert "PYTHONPATH" not in env
```

Add a contamination regression:

```python
def test_command_environment_removes_repo_src_from_installed_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    repo_src = str(tmp_path / "src")
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(["/before", repo_src, "/after"]))

    env = smoke.command_environment(context, source_checkout=False)

    assert env["PYTHONPATH"] == os.pathsep.join(["/before", "/after"])
```

Also update existing `test_command_environment_prepends_src_and_preserves_pythonpath`
and `test_command_environment_sets_pythonpath_when_absent` to call
`source_checkout=True` explicitly or rely on the default.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py::test_command_environment_does_not_prepend_src_in_installed_mode tests/test_first_run_smoke.py::test_command_environment_leaves_pythonpath_absent_in_installed_mode -q
```

Expected: fail because `command_environment()` does not accept `source_checkout`
and does not remove repo `src` in installed mode.

- [ ] **Step 3: Implement environment mode**

Update `scripts/check_first_run_smoke.py`:

```python
def command_environment(
    context: SmokeContext,
    base_env: Mapping[str, str] | None = None,
    *,
    source_checkout: bool = True,
) -> dict[str, str]:
    env = dict(os.environ if base_env is None else base_env)
    if not source_checkout:
        remove_pythonpath_entry(env, context.repo_root / "src")
        return env
    src_path = str(context.repo_root / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path if not existing_pythonpath else os.pathsep.join([src_path, existing_pythonpath])
    )
    return env
```

Add helper:

```python
def remove_pythonpath_entry(env: dict[str, str], entry: Path) -> None:
    pythonpath = env.get("PYTHONPATH")
    if not pythonpath:
        return

    target = entry.resolve()
    kept = [
        value
        for value in pythonpath.split(os.pathsep)
        if value and Path(value).resolve() != target
    ]
    if kept:
        env["PYTHONPATH"] = os.pathsep.join(kept)
    else:
        env.pop("PYTHONPATH", None)
```

Extend `SmokeContext`:

```python
@dataclass(frozen=True)
class SmokeContext:
    repo_root: Path
    python: str
    runtime_dir: Path
    config_dir: Path
    data_dir: Path
    reports_dir: Path
    exports_dir: Path
    source_checkout: bool = True
```

Update `run_cli()`:

```python
env=command_environment(context, source_checkout=context.source_checkout),
```

Update `build_context()` signature:

```python
def build_context(
    repo_root: Path,
    python: str,
    runtime_dir: Path,
    *,
    source_checkout: bool = True,
) -> SmokeContext:
    return SmokeContext(
        repo_root=repo_root,
        python=python,
        runtime_dir=runtime_dir,
        config_dir=runtime_dir / "config",
        data_dir=runtime_dir / "data",
        reports_dir=runtime_dir / "reports",
        exports_dir=runtime_dir / "exports",
        source_checkout=source_checkout,
    )
```

- [ ] **Step 4: Verify GREEN for environment tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py::test_command_environment_prepends_src_and_preserves_pythonpath tests/test_first_run_smoke.py::test_command_environment_sets_pythonpath_when_absent tests/test_first_run_smoke.py::test_command_environment_does_not_prepend_src_in_installed_mode tests/test_first_run_smoke.py::test_command_environment_leaves_pythonpath_absent_in_installed_mode -q
```

Expected: all selected tests pass.

## Task 2: CLI Flag, Import-Origin Preflight, And Command-Sequence Coverage

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add failing tests for `--installed` parsing and context construction**

Add tests:

```python
def test_parse_args_defaults_to_source_checkout() -> None:
    args = smoke.parse_args(["--repo-root", ".", "--python", "python-test"])

    assert args.repo_root == "."
    assert args.python == "python-test"
    assert args.installed is False


def test_parse_args_accepts_installed_mode() -> None:
    args = smoke.parse_args(["--repo-root", ".", "--python", "python-test", "--installed"])

    assert args.installed is True


def test_build_context_records_source_checkout_mode(tmp_path: Path) -> None:
    source_context = smoke.build_context(tmp_path, "python-test", tmp_path / "source")
    installed_context = smoke.build_context(
        tmp_path,
        "python-test",
        tmp_path / "installed",
        source_checkout=False,
    )

    assert source_context.source_checkout is True
    assert installed_context.source_checkout is False
```

Add preflight tests:

```python
def test_assert_installed_import_origin_rejects_repo_src_path(tmp_path: Path) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    source_file = tmp_path / "src" / "fashion_radar" / "__init__.py"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("", encoding="utf-8")

    with pytest.raises(smoke.SmokeError, match="source checkout"):
        smoke.assert_installed_import_origin(context, source_file)


def test_assert_installed_import_origin_allows_non_source_path(tmp_path: Path) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    installed_file = tmp_path / "venv" / "site-packages" / "fashion_radar" / "__init__.py"
    installed_file.parent.mkdir(parents=True)
    installed_file.write_text("", encoding="utf-8")

    smoke.assert_installed_import_origin(context, installed_file)
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py::test_parse_args_accepts_installed_mode tests/test_first_run_smoke.py::test_build_context_records_source_checkout_mode tests/test_first_run_smoke.py::test_assert_installed_import_origin_rejects_repo_src_path -q
```

Expected: fail before implementation.

- [ ] **Step 3: Implement `--installed` CLI flag**

Update `parse_args()`:

```python
parser.add_argument(
    "--installed",
    action="store_true",
    help=(
        "Run against the supplied installed Python environment without "
        "prepending repo_root/src to PYTHONPATH."
    ),
)
```

Update `main()`:

```python
context = build_context(
    repo_root,
    args.python,
    Path(temp_dir),
    source_checkout=not args.installed,
)
```

Add import-origin helper:

```python
def assert_installed_import_origin(context: SmokeContext, module_file: Path) -> None:
    source_root = (context.repo_root / "src").resolve()
    resolved_file = module_file.resolve()
    if resolved_file == source_root or source_root in resolved_file.parents:
        raise SmokeError(
            "Installed smoke imported fashion_radar from source checkout: "
            f"{resolved_file}"
        )
```

Add preflight runner:

```python
def installed_import_origin(context: SmokeContext) -> Path:
    command = [
        context.python,
        "-c",
        (
            "import fashion_radar, pathlib; "
            "print(pathlib.Path(fashion_radar.__file__).resolve())"
        ),
    ]
    completed = subprocess.run(
        command,
        cwd=context.repo_root,
        env=command_environment(context, source_checkout=False),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SmokeError(format_command_failure(command, completed))
    output = completed.stdout.strip()
    if not output:
        raise SmokeError("Installed smoke import-origin preflight returned no module path")
    return Path(output)
```

Call it before `run_smoke(context)` in `main()` when `args.installed`:

```python
if args.installed:
    assert_installed_import_origin(context, installed_import_origin(context))
```

- [ ] **Step 4: Update command sequence test to assert installed mode is preserved**

In `test_run_first_run_flow_uses_deterministic_local_command_sequence`, set:

```python
context = make_context(tmp_path, python=sys.executable)
```

as-is for source mode. Add a small separate test:

```python
def test_run_cli_uses_context_source_checkout_flag(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    captured_env = {}

    def fake_run(command, *, cwd, env, text, capture_output, check):
        captured_env.update(env)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(smoke.subprocess, "run", fake_run)
    monkeypatch.setenv("PYTHONPATH", "/already/here")

    smoke.run_cli(context, "--help")

    assert captured_env["PYTHONPATH"] == "/already/here"
```

Add a contamination assertion to that test or a separate test:

```python
monkeypatch.setenv(
    "PYTHONPATH",
    os.pathsep.join(["/already/here", str(tmp_path / "src")]),
)
smoke.run_cli(context, "--help")
assert captured_env["PYTHONPATH"] == "/already/here"
```

- [ ] **Step 5: Verify GREEN for smoke unit tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py -q
```

Expected: all smoke unit tests pass.

## Task 3: CI And Release Docs

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/github-upload-checklist.md`
- Modify: `README.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add failing docs/CI drift tests**

In `tests/test_cli_docs.py`, extend `test_first_run_smoke_command_is_documented_and_in_ci()`:

```python
installed_command = (
    '"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . '
    '--python "$tmp_env/venv/bin/python" --installed'
)
assert installed_command in ci_workflow
assert installed_command in checklist
```

In `test_readme_documents_manual_sample_flow_and_automated_smoke_boundary()`,
add terms:

```python
"source checkout",
"installed wheel",
"--installed",
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_first_run_smoke_command_is_documented_and_in_ci tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary -q
```

Expected: fail until docs/CI are updated.

- [ ] **Step 3: Update CI installed-wheel step**

In `.github/workflows/ci.yml`, after the installed `doctor` command and before
the template resource smoke, add:

```yaml
          "$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Keep the existing source-checkout first-run smoke step unchanged.

- [ ] **Step 4: Update upload checklist installed-wheel smoke**

In `docs/github-upload-checklist.md`, after installed `doctor`, add:

```bash
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Add one sentence that the installed-wheel smoke uses the built wheel's Python
environment and does not prepend `src/` to `PYTHONPATH`.

- [ ] **Step 5: Update README automated smoke wording**

Under `### Automated First-Run Smoke`, keep the source-checkout command and add:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Explain that source mode prepends `src/`, while installed mode intentionally
uses the installed package from the wheel.

- [ ] **Step 6: Verify docs/CI tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: tests pass.

## Task 4: Real Installed-Wheel Verification

**Files:**
- No source changes expected unless verification fails.

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
UV_NO_CONFIG=1 uv run ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py
```

Expected: all pass.

- [ ] **Step 2: Run installed-wheel smoke manually**

Run:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Expected: package archive check passes and installed smoke prints
`First-run sample smoke passed.`

- [ ] **Step 3: Run full release verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Expected: all pass and `uv.lock` remains unchanged.

## Task 5: Claude Code Release Review, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-48-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-48-release-review.md`

- [ ] **Step 1: Prepare release review prompt**

Write a concise embedded prompt containing:
- Stage 48 goal and non-goals;
- file list;
- implementation summary;
- verification evidence;
- request for Critical/Important/Minor findings;
- required approval line:
  `APPROVED FOR STAGE 48 COMMIT AND PUSH`.

- [ ] **Step 2: Run Claude Code release review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  -p "$(cat docs/reviews/claude-code-stage-48-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-48-release-review.md
```

Expected: no Critical/Important findings and approval line present.

- [ ] **Step 3: Fix any Critical/Important findings**

If Claude Code reports Critical or Important issues, fix them and rerun focused
and full verification plus the release review.

- [ ] **Step 4: Final verification**

Rerun:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

- [ ] **Step 5: Commit and push**

Commit:

```bash
git add .github/workflows/ci.yml README.md docs/github-upload-checklist.md \
  docs/reviews/claude-code-stage-48-*.md \
  docs/superpowers/specs/2026-06-15-stage-48-installed-wheel-first-run-smoke-design.md \
  docs/superpowers/plans/2026-06-15-stage-48-installed-wheel-first-run-smoke-plan.md \
  scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py
git commit -m "Add installed-wheel first-run smoke"
```

Push with the existing non-persistent token-header method. Do not write the
token into git config or the remote URL.

- [ ] **Step 6: Confirm GitHub Actions**

Poll the latest `main` Actions run through the GitHub REST API until it reaches
`completed success` for the new commit.

## Self-Review

Spec coverage:
- Installed mode: Task 1 and Task 2.
- CI/release docs: Task 3.
- Real installed wheel verification: Task 4.
- Review-gated commit/push: Task 5.

Placeholder scan:
- No `TBD`, `TODO`, or "similar to" placeholders remain.

Type/signature consistency:
- `SmokeContext.source_checkout`, `command_environment(..., source_checkout=...)`,
  `build_context(..., source_checkout=...)`, and `parse_args().installed` are
  consistently named across tasks.
