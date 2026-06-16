# External Tool Handoff Templates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add sanitized importable external tool handoff templates and make them discoverable through existing community producer contracts without adding a new CLI command or any platform collection behavior.

**Architecture:** Keep the existing schema and runtime commands as the source of truth. Add static CSV/JSON example files, expose those paths through the existing producer profile and derived handoff manifest, and strengthen tests/docs/package checks so the examples remain sanitized, importable, packaged, and local-only.

**Tech Stack:** Python 3.11+, pytest, Typer `CliRunner`, Pydantic profile/manifest models, existing package archive checker, Markdown docs. No new dependencies.

---

## File Structure

- Create `examples/community-tool-handoff.example.csv`
  - Importable synthetic CSV template for external user-controlled tools.
- Create `examples/community-tool-handoff.example.json`
  - Importable synthetic JSON template using the existing `{ "items": [...] }`
    envelope.
- Modify `src/fashion_radar/community_signal_profile.py`
  - Add the new example paths to `COMMUNITY_SIGNAL_EXAMPLE_PATHS`.
- Modify `examples/community-signal-profile.example.json`
  - Regenerate deterministic producer profile output.
- Modify tests:
  - `tests/test_community_signal_lint.py`
  - `tests/test_community_signal_import_contract.py`
  - `tests/test_community_signal_profile.py`
  - `tests/test_community_handoff_manifest.py`
  - `tests/test_cli.py`
  - `tests/test_package_archives.py`
  - `tests/test_cli_docs.py`
- Modify archive checker:
  - `scripts/check_package_archives.py`
- Modify docs:
  - `README.md`
  - `docs/community-signal-import.md`
  - `docs/source-boundaries.md`
  - `docs/architecture.md`
  - `docs/github-upload-checklist.md`
  - `AGENTS.md`
  - `CHANGELOG.md`
- Add review records:
  - `docs/reviews/opencode-stage-54-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-54-plan-review.md`
  - opencode release review prompt/result after implementation.

### Task 1: Add External Tool Template Examples

**Files:**
- Create: `examples/community-tool-handoff.example.csv`
- Create: `examples/community-tool-handoff.example.json`
- Modify: `src/fashion_radar/community_signal_profile.py`
- Modify: `examples/community-signal-profile.example.json`

- [ ] **Step 1: Create sanitized CSV template**

Create `examples/community-tool-handoff.example.csv`:

```csv
url,title,published_at,summary,source_name,platform,source_weight,collected_at
https://example.com/community-tool/the-row-bag-signal,The Row bag observed signal,2026-06-12T10:00:00Z,Synthetic sanitized observation about The Row bag interest from a user-controlled tool,External Community Tool,community,1.2,2026-06-12T10:15:00Z
https://example.com/community-tool/silver-flat-shoe,Silver flat shoe observed signal,2026-06-12T11:00:00Z,Synthetic sanitized observation about silver flats and footwear styling from a user-controlled tool,External Community Tool,community,1.1,2026-06-12T11:10:00Z
```

- [ ] **Step 2: Create sanitized JSON template**

Create `examples/community-tool-handoff.example.json`:

```json
{
  "items": [
    {
      "url": "https://example.com/community-tool/ballet-flat-signal",
      "title": "Ballet flat observed signal",
      "published_at": "2026-06-12T12:00:00Z",
      "summary": "Synthetic sanitized observation about ballet flats from a user-controlled tool.",
      "source_name": "External Community Tool",
      "platform": "community",
      "source_weight": 1.2,
      "collected_at": "2026-06-12T12:10:00Z"
    },
    {
      "url": "https://example.com/community-tool/red-knitwear-signal",
      "title": "Red knitwear observed signal",
      "published_at": "2026-06-12T13:00:00Z",
      "summary": "Synthetic sanitized observation about red knitwear interest from a user-controlled tool.",
      "source_name": "External Community Tool",
      "platform": "community",
      "source_weight": 1.1,
      "collected_at": "2026-06-12T13:20:00Z"
    }
  ]
}
```

- [ ] **Step 3: Update profile example paths**

In `src/fashion_radar/community_signal_profile.py`, change:

```python
COMMUNITY_SIGNAL_EXAMPLE_PATHS = [
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
]
```

to:

```python
COMMUNITY_SIGNAL_EXAMPLE_PATHS = [
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
    "examples/community-tool-handoff.example.csv",
    "examples/community-tool-handoff.example.json",
]
```

- [ ] **Step 4: Regenerate profile example JSON**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python - <<'PY'
from pathlib import Path
from fashion_radar.community_signal_profile import build_community_signal_profile
Path("examples/community-signal-profile.example.json").write_text(
    build_community_signal_profile().model_dump_json(indent=2) + "\n",
    encoding="utf-8",
)
PY
```

Expected: `examples/community-signal-profile.example.json` updates only in
`example_paths`.

### Task 2: Add Template Contract Tests

**Files:**
- Modify: `tests/test_community_signal_lint.py`
- Modify: `tests/test_community_signal_import_contract.py`
- Modify: `tests/test_community_signal_profile.py`
- Modify: `tests/test_community_handoff_manifest.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add shared template paths in import contract tests**

In `tests/test_community_signal_import_contract.py`, add:

```python
TOOL_CSV_TEMPLATE = ROOT / "examples" / "community-tool-handoff.example.csv"
TOOL_JSON_TEMPLATE = ROOT / "examples" / "community-tool-handoff.example.json"
IMPORTABLE_COMMUNITY_EXAMPLES = [
    (CSV_EXAMPLE, "csv"),
    (JSON_EXAMPLE, "json"),
    (TOOL_CSV_TEMPLATE, "csv"),
    (TOOL_JSON_TEMPLATE, "json"),
]
```

- [ ] **Step 2: Extend allowed-field and lint tests**

Update `test_community_examples_use_same_allowed_contract_fields` to iterate
over `IMPORTABLE_COMMUNITY_EXAMPLES` and assert every CSV header or JSON item
key is within the schema property set.

Update `test_community_signal_linter_accepts_repository_examples` to iterate
over `IMPORTABLE_COMMUNITY_EXAMPLES` and assert each result is ok with no
findings.

- [ ] **Step 3: Extend dry-run import test**

Update `test_import_signals_dry_run_validates_community_examples_without_artifacts`
so it invokes `import-signals --dry-run` for all four importable examples and
asserts each command exits 0 and prints `Validated 2 manual signal rows`.

- [ ] **Step 4: Add lint template coverage**

In `tests/test_community_signal_lint.py`, add constants for the two new template
paths and a parameterized test:

```python
TOOL_CSV_TEMPLATE = ROOT / "examples" / "community-tool-handoff.example.csv"
TOOL_JSON_TEMPLATE = ROOT / "examples" / "community-tool-handoff.example.json"


@pytest.mark.parametrize(
    ("path", "input_format"),
    [
        (CSV_EXAMPLE, "csv"),
        (JSON_EXAMPLE, "json"),
        (TOOL_CSV_TEMPLATE, "csv"),
        (TOOL_JSON_TEMPLATE, "json"),
    ],
)
def test_repository_community_handoff_templates_lint_cleanly(
    path: Path,
    input_format: str,
) -> None:
    result = lint_community_signal_file(path, input_format=input_format)

    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.valid_row_count == 2
```

- [ ] **Step 5: Update profile tests**

In `tests/test_community_signal_profile.py`, update exact `example_paths`
assertions to include the two new paths.

Add a test:

```python
def test_profile_importable_example_paths_exist_and_lint_cleanly() -> None:
    profile = build_community_signal_profile()

    for relative_path in profile.example_paths:
        path = ROOT / relative_path
        assert path.exists()
        input_format = "csv" if path.suffix == ".csv" else "json"
        result = lint_community_signal_file(path, input_format=input_format)
        assert result.ok is True
        assert result.findings == []
```

- [ ] **Step 6: Update manifest and CLI JSON assertions**

Update expected `example_paths` in:

- `tests/test_community_handoff_manifest.py`
- `tests/test_cli.py::test_community_signal_profile_prints_json`
- `tests/test_cli.py::test_community_handoff_manifest_command_prints_json_with_stable_keys`

Expected list:

```python
[
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
    "examples/community-tool-handoff.example.csv",
    "examples/community-tool-handoff.example.json",
]
```

- [ ] **Step 7: Run targeted contract tests**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_handoff_manifest_command_prints_json_with_stable_keys -q
```

Expected: all selected tests pass.

### Task 3: Package Archive And Documentation Drift

**Files:**
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`
- Modify: `tests/test_cli_docs.py`
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add package archive requirements**

Add these paths to `SDIST_REQUIRED_PATHS` in
`scripts/check_package_archives.py` and to `SDIST_FILES` in
`tests/test_package_archives.py`:

```python
"examples/community-tool-handoff.example.csv",
"examples/community-tool-handoff.example.json",
```

- [ ] **Step 2: Add package archive missing-template regression**

In `tests/test_package_archives.py`, add:

```python
def test_rejects_sdist_without_external_tool_handoff_template(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[
            path
            for path in SDIST_FILES
            if path != "examples/community-tool-handoff.example.csv"
        ],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive missing required file: "
        "examples/community-tool-handoff.example.csv"
    ) in result.stderr
```

- [ ] **Step 3: Add docs drift test**

In `tests/test_cli_docs.py`, add a test near the community signal docs tests:

```python
def test_external_tool_handoff_template_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    normalized_docs = [
        " ".join(text.lower().replace("-", " ").split())
        for text in (readme, import_doc, boundaries, architecture)
    ]

    for text in (readme, import_doc, checklist):
        assert "examples/community-tool-handoff.example.csv" in text
        assert "examples/community-tool-handoff.example.json" in text
    for normalized in normalized_docs:
        assert "external tool handoff template" in normalized
        assert "sanitized csv/json" in normalized
    for text in (readme, import_doc, boundaries, architecture):
        assert "sanitized CSV/JSON" in text
    for text in (readme, import_doc, boundaries):
        normalized = " ".join(text.lower().replace("-", " ").split())
        assert "not an integration layer for platform collection" in normalized or (
            "does not add platform connectors" in normalized
        )
```

- [ ] **Step 4: Update community import docs**

In `docs/community-signal-import.md`:

- Add the two new template paths under `Contract Files`.
- Add a new `## External Tool Handoff Template` section after `Directory
  Manifest` and before `Required Fields`.
- State the producer/consumer sequence:
  profile, optional manifest, external tool writes files, lint, preview,
  dry-run import, import after validation, post-import review.
- State it does not add connectors, scraping, browser automation, platform API
  clients, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, compliance review, legal review, or approval UI.

- [ ] **Step 5: Update public and maintainer docs**

Update:

- `README.md`: add a compact local file handoff template note around the
  existing external community tools section.
- `docs/source-boundaries.md`: add an explicit external tool handoff template
  boundary paragraph or README requirement bullet.
- `docs/architecture.md`: add one sentence under Manual Import.
- `docs/github-upload-checklist.md`: add a template package/readiness checklist
  item.
- `AGENTS.md`: add a maintainer guardrail for future external community tool
  handoff work.
- `CHANGELOG.md`: add an Unreleased bullet.

- [ ] **Step 6: Run targeted package/docs tests**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py tests/test_cli_docs.py -q
```

Expected: all selected tests pass.

### Task 4: Verification, Review, Commit, And Upload

**Files:**
- Add: `docs/reviews/opencode-stage-54-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-54-release-review.md`
- Modify if needed: files changed by Tasks 1-3 only.

- [ ] **Step 1: Run full verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock
```

Expected: each command exits 0.

- [ ] **Step 2: Run release hygiene and smoke checks**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Expected: each command exits 0.

- [ ] **Step 3: Request local opencode release review**

Create `docs/reviews/opencode-stage-54-release-review-prompt.md` with:

```markdown
Review Stage 54 external tool handoff templates in `/home/ubuntu/fashion-radar`.

Focus on:
- whether the new examples are sanitized, importable, synthetic, and limited to
  existing schema fields;
- whether profile/manifest discoverability is correctly updated without adding
  a new CLI command;
- whether package archive checks require the new templates;
- whether docs describe a local file handoff template without implying platform
  collection, source acquisition, scraping, browser automation, platform APIs,
  monitoring, scheduling, compliance review, demand proof, ranking, or coverage
  verification;
- whether `uv.lock` is unchanged.

Report Critical, Important, and Minor findings. Treat Critical/Important as
blocking.
```

Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-54-release-review-prompt.md)" > docs/reviews/opencode-stage-54-release-review.md
```

Expected: no Critical or Important findings remain.

- [ ] **Step 4: Commit and upload**

Run:

```bash
git status --short
git add examples/community-tool-handoff.example.csv examples/community-tool-handoff.example.json src/fashion_radar/community_signal_profile.py examples/community-signal-profile.example.json tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_cli.py scripts/check_package_archives.py tests/test_package_archives.py tests/test_cli_docs.py README.md docs/community-signal-import.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md AGENTS.md CHANGELOG.md docs/superpowers/specs/2026-06-16-stage-54-external-tool-handoff-templates-design.md docs/superpowers/plans/2026-06-16-stage-54-external-tool-handoff-templates-plan.md docs/reviews/opencode-stage-54-plan-review-prompt.md docs/reviews/opencode-stage-54-plan-review.md docs/reviews/opencode-stage-54-release-review-prompt.md docs/reviews/opencode-stage-54-release-review.md
git commit -m "Add external tool handoff templates"
```

Upload to `origin/main`. If normal `git push` fails due authentication/TLS,
use the saved token with the GitHub Git Data API, verify the remote tree matches
the local tree, fetch the remote commit, and align local `main`/`origin/main` to
the API-created commit.

- [ ] **Step 5: Confirm GitHub Actions**

Use GitHub API or CLI to confirm the workflow run for the uploaded commit
completes successfully.
