# Stage 49 First-Run Onboarding Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tested first-run onboarding guide that tells GitHub users which checkout, wheel, manual sample, dashboard, and reset path to use.

**Architecture:** This is a docs-and-tests-only stage. `docs/first-run.md` becomes the canonical onboarding guide, README points users to it and keeps a compact chooser, and `docs/github-upload-checklist.md` keeps release-oriented smoke wording. `tests/test_cli_docs.py` prevents drift by asserting exact smoke commands, repo-local setup flags, expected report paths, dashboard command, reset guidance, and local-only smoke boundaries.

**Tech Stack:** Markdown, pytest, existing Typer `CliRunner` doc-smoke helpers, uv, ruff, Claude Code review with `--effort max`. No runtime dependencies or lockfile changes.

---

## Files

- Add: `docs/first-run.md`
- Modify: `README.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Add: `docs/reviews/claude-code-stage-49-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-49-plan-review.md`
- Later add: `docs/reviews/claude-code-stage-49-plan-rereview-prompt.md`
- Later add: `docs/reviews/claude-code-stage-49-plan-rereview.md`
- Later add: `docs/reviews/claude-code-stage-49-release-review-prompt.md`
- Later add: `docs/reviews/claude-code-stage-49-release-review.md`

## Task 1: Add First-Run Guide Drift Tests

**Files:**
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add failing test constants and include the guide in path scans**

Add `FIRST_RUN_DOC` beside the existing path constants:

```python
FIRST_RUN_DOC = ROOT / "docs" / "first-run.md"
```

Add the guide to `PATH_CONSISTENCY_DOCS`:

```python
ROOT / "docs" / "first-run.md",
```

This should initially fail because `docs/first-run.md` does not exist.

- [ ] **Step 2: Add a failing README link test**

Add:

```python
def test_readme_links_first_run_guide() -> None:
    text = _read(README)
    documentation = text.split("## Documentation", 1)[1].split("\n## ", 1)[0]

    assert FIRST_RUN_DOC.exists()
    assert "[docs/first-run.md](docs/first-run.md)" in text
    assert "[docs/first-run.md](docs/first-run.md)" in documentation
```

- [ ] **Step 3: Tighten smoke command docs test**

Update `test_first_run_smoke_command_is_documented_and_in_ci`:

```python
first_run_doc = _read(FIRST_RUN_DOC)
```

Then include `first_run_doc` in both command loops:

```python
for text in (checklist, ci_workflow, readme, first_run_doc):
    assert source_command in text
    assert "scripts/check_first_run_smoke.py" in text

for text in (checklist, ci_workflow, readme, first_run_doc):
    assert installed_command in text
```

- [ ] **Step 4: Add a failing guide content test**

Add:

```python
def _normalized_doc_text(path: Path) -> str:
    return " ".join(_read(path).split())


def test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries() -> None:
    text = _read(FIRST_RUN_DOC)
    normalized = _normalized_doc_text(FIRST_RUN_DOC)

    for term in (
        "Choose Your First Run",
        "Manual Repo-Local Sample Flow",
        'AS_OF="2026-06-13T12:00:00Z"',
        "examples/community-signals.example.csv",
        "community-candidates examples/community-signals.example.csv",
        "import-signals examples/community-signals.example.csv",
        "reports/fashion-radar-2026-06-13.md",
        "reports/fashion-radar-2026-06-13.json",
        "data/fashion-radar.sqlite",
        "configs/sources.yaml",
        "configs/entities.yaml",
        "configs/scoring.yaml",
        "Automated First-Run Smoke",
        "source checkout",
        "installed wheel",
        "--installed",
        "First-run sample smoke passed.",
        "should not create files under repo `data/` or `reports/`",
        "browser automation",
        "account login",
        "cookies/sessions",
        "source/platform connectors",
        "external services",
        "community-handoff-workflow",
        "community-signal-lint-dir",
        "community-candidates-dir",
        "import-signals-dir",
        "uv run fashion-radar dashboard --config-dir",
        "http://127.0.0.1:8501",
        "Reset The Repo-Local Sample",
        "keeps `data/README.md` and `reports/README.md`",
    ):
        assert term in text

    for term in (
        "temporary config, data, report, and export directories",
        "does not run live collection",
        "does not run `collect`, `run`, or `dashboard`",
    ):
        assert term in normalized
```

- [ ] **Step 5: Add failing first-run setup command flag test**

Add:

```python
def test_first_run_guide_setup_commands_use_repo_local_paths() -> None:
    setup_commands = [
        command
        for command in _fashion_radar_commands(FIRST_RUN_DOC)
        if (match := FASHION_RADAR_COMMAND_RE.search(command)) is not None
        and match.group("name") in {"init", "migrate-db", "doctor"}
    ]

    command_names = [
        FASHION_RADAR_COMMAND_RE.search(command).group("name")
        for command in setup_commands
    ]
    assert command_names == ["init", "migrate-db", "doctor"]

    for command in setup_commands:
        match = FASHION_RADAR_COMMAND_RE.search(command)
        assert match is not None
        command_name = match.group("name")
        assert '--data-dir "$PWD/data"' in command
        if command_name in {"init", "doctor"}:
            assert '--config-dir "$PWD/configs"' in command
            assert '--reports-dir "$PWD/reports"' in command
```

- [ ] **Step 6: Add failing first-run setup smoke test**

Add a helper:

```python
def _first_run_setup_commands() -> list[str]:
    return [
        command
        for command in _fashion_radar_commands(FIRST_RUN_DOC)
        if (match := FASHION_RADAR_COMMAND_RE.search(command)) is not None
        and match.group("name") in {"init", "migrate-db", "doctor"}
    ]
```

Refactor Step 5 to use the helper, then add:

```python
def test_first_run_guide_setup_commands_smoke(tmp_path: Path) -> None:
    for command in _first_run_setup_commands():
        parts = [part.replace("$PWD", str(tmp_path)) for part in shlex.split(command)]
        assert parts[:3] == ["uv", "run", "fashion-radar"]

        result = CliRunner().invoke(app, parts[3:])

        assert result.exit_code == 0, result.output
```

- [ ] **Step 7: Run focused tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: fail because `docs/first-run.md` is missing and README/checklist docs
do not yet contain the new required text.

## Task 2: Add The First-Run Guide

**Files:**
- Add: `docs/first-run.md`

- [ ] **Step 1: Create `docs/first-run.md`**

Add a guide with these sections:

```markdown
# First Run

## Choose Your First Run

| Goal | Run This Path | Writes Repo `data/` / `reports/`? |
| --- | --- | --- |
| Verify the source checkout without keeping sample output | Automated First-Run Smoke | No |
| Create inspectable sample output and dashboard data | Manual Repo-Local Sample Flow | Yes |
| Verify a built wheel before release | Installed-Wheel Smoke | No |
| Start over after a local experiment | Reset The Repo-Local Sample | Deletes selected local runtime files |

## Prepare A Source Checkout

...

## Manual Repo-Local Sample Flow

...

## Inspect The Sample In The Dashboard

...

## Automated First-Run Smoke

...

## Installed-Wheel Smoke

...

## Reset The Repo-Local Sample

...

## Boundary

...
```

Use the exact command blocks already present in README for:

```bash
uv run fashion-radar init --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
uv run fashion-radar migrate-db --data-dir "$PWD/data"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

```bash
AS_OF="2026-06-13T12:00:00Z"

uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$AS_OF"
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
test -s reports/fashion-radar-2026-06-13.md
test -s reports/fashion-radar-2026-06-13.json
```

Dashboard command:

```bash
uv sync --locked --dev --extra dashboard
uv run fashion-radar dashboard --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --host 127.0.0.1 --port 8501
```

Source smoke command:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Installed smoke command block:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

- [ ] **Step 2: Include exact expected artifacts and boundaries**

The guide must state the manual flow writes:

```text
configs/sources.yaml
configs/entities.yaml
configs/scoring.yaml
data/fashion-radar.sqlite
reports/fashion-radar-2026-06-13.md
reports/fashion-radar-2026-06-13.json
```

The guide must state automated smokes verify temporary reports and print:

```text
First-run sample smoke passed.
```

The guide must state, with wording that can survive line wrapping:

```markdown
Both automated smoke paths use temporary config, data, report, and export directories.
They should not create files under repo `data/` or `reports/`.
They do not run live collection, and do not run `collect`, `run`, or `dashboard`.
They do not run scheduler/monitoring commands, scraping/crawling, browser
automation, account login, cookies/sessions, source/platform connectors,
platform automation, or external services.
```

The guide must mention the directory-tail commands covered by the smoke:

```text
community-handoff-workflow
community-signal-lint-dir
community-candidates-dir
import-signals-dir
```

- [ ] **Step 3: Add reset guidance**

Add a reset section with cautious commands:

```bash
rm -f data/fashion-radar.sqlite data/fashion-radar.sqlite-wal data/fashion-radar.sqlite-shm
rm -f reports/fashion-radar-2026-06-13.md reports/fashion-radar-2026-06-13.json
rm -f configs/sources.yaml configs/entities.yaml configs/scoring.yaml
```

The text must say this deletes local experiment state, and keeps
`data/README.md` and `reports/README.md`. It must also warn users to review or
copy any edits to `configs/sources.yaml`, `configs/entities.yaml`, and
`configs/scoring.yaml` before deleting those files.

- [ ] **Step 4: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: the first-run guide tests still fail until README/checklist/CLI links
and wording are added.

## Task 3: Link And Tighten Public Docs

**Files:**
- Modify: `README.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Update README Quickstart chooser**

Under `## Quickstart`, add a compact chooser before dependency installation:

```markdown
Use [docs/first-run.md](docs/first-run.md) for the full onboarding path.

| Goal | Path |
| --- | --- |
| Verify the checkout without keeping sample output | Automated First-Run Smoke |
| Create repo-local sample output for inspection | Manual Repo-Local Sample Flow |
| Open the optional dashboard with sample data | Manual flow, then dashboard |
| Verify a wheel before release | Installed-wheel smoke |
```

Add the guide to the README Documentation list:

```markdown
- [docs/first-run.md](docs/first-run.md)
```

- [ ] **Step 2: Clarify README manual sample and dashboard next step**

In README's manual sample section, add:

```markdown
Prerequisite: run the `init`, `migrate-db`, and `doctor` block above first.
```

After the manual command block, add expected artifact text listing:

```text
configs/sources.yaml
configs/entities.yaml
configs/scoring.yaml
data/fashion-radar.sqlite
reports/fashion-radar-2026-06-13.md
reports/fashion-radar-2026-06-13.json
```

Add a short dashboard next-step note pointing to `docs/first-run.md` and
`http://127.0.0.1:8501`.

- [ ] **Step 3: Clarify README smoke purpose and output**

In README's automated smoke section, add that source and installed smokes print
`First-run sample smoke passed.`, verify temporary
`fashion-radar-2026-06-13.md/json`, and do not leave dashboard-inspectable
repo-local report files.

- [ ] **Step 4: Add README reset pointer**

Near the cleanup/report storage area, add:

```markdown
For a full sample reset, see [docs/first-run.md](docs/first-run.md#reset-the-repo-local-sample).
`clean-old-data` is retention pruning, not a full reset of generated configs or reports.
```

- [ ] **Step 5: Update CLI reference note**

Under `docs/cli-reference.md` Shared Path Options, add:

```markdown
For first-run onboarding, use [first-run.md](first-run.md) and keep
`--config-dir "$PWD/configs"`, `--data-dir "$PWD/data"`, and
`--reports-dir "$PWD/reports"` consistent through setup, import, match, report,
and dashboard commands. A report run with
`--as-of "2026-06-13T12:00:00Z"` writes
`reports/fashion-radar-2026-06-13.md` and
`reports/fashion-radar-2026-06-13.json`.
```

Also state that `scripts/check_first_run_smoke.py` is a checkout/release helper,
not a normal public `fashion-radar` CLI command.

- [ ] **Step 6: Update upload checklist smoke boundary**

In `docs/github-upload-checklist.md` Package Smoke, add:

```markdown
Both source-checkout and installed-wheel first-run smokes run local CLI commands
against checked-in sample files and temporary directories only. They do not run
`collect`, `run`, `dashboard`, scheduler/monitoring commands,
scraping/crawling, browser automation, account login, cookies/sessions,
source/platform connectors, platform automation, or external services.
```

Add expected success output:

```text
First-run sample smoke passed.
```

- [ ] **Step 7: Run focused tests and lint**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
```

Expected: all pass.

## Task 4: Release Verification And Review

**Files:**
- Add: `docs/reviews/claude-code-stage-49-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-49-release-review.md`

- [ ] **Step 1: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
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

- [ ] **Step 2: Create Claude Code release review prompt**

Write `docs/reviews/claude-code-stage-49-release-review-prompt.md` with:

```markdown
You are Claude Code performing the required Stage 49 release review for
/home/ubuntu/fashion-radar.

Use maximum reasoning. Do not browse the network. Do not modify files.

Stage 49 objective:
- Add a tested first-run onboarding guide and tighten public docs so new GitHub
  users can choose between source checkout smoke, installed-wheel smoke,
  manual repo-local sample output, dashboard inspection, and reset.

Changed files:
- docs/first-run.md
- README.md
- docs/cli-reference.md
- docs/github-upload-checklist.md
- tests/test_cli_docs.py
- docs/superpowers/specs/2026-06-16-stage-49-first-run-onboarding-guide-design.md
- docs/superpowers/plans/2026-06-16-stage-49-first-run-onboarding-guide-plan.md
- docs/reviews/claude-code-stage-49-plan-review*.md

Boundaries:
- Docs/tests only.
- No runtime code, dependency, lockfile, CI behavior, dashboard behavior,
  source/social connector, scraping/browser/account/session automation,
  external service, or compliance-review feature.

Verification evidence:
- [paste concise command results]

Please return Critical, Important, Minor issues, whether any issue blocks
commit/push, and if no Critical or Important issues remain include exactly:
APPROVED FOR STAGE 49 COMMIT AND PUSH
```

- [ ] **Step 3: Run Claude Code release review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  -p "$(cat docs/reviews/claude-code-stage-49-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-49-release-review.md
```

- [ ] **Step 4: Fix Critical/Important review issues**

If the review reports Critical or Important issues, fix them, rerun focused and
affected verification, and rerun Claude Code review until it includes:

```text
APPROVED FOR STAGE 49 COMMIT AND PUSH
```

- [ ] **Step 5: Commit, then push only when explicitly authorized**

Commit the reviewed Stage 49 changes:

Run:

```bash
git status --short --branch
git add docs/first-run.md README.md docs/cli-reference.md docs/github-upload-checklist.md tests/test_cli_docs.py docs/superpowers/specs/2026-06-16-stage-49-first-run-onboarding-guide-design.md docs/superpowers/plans/2026-06-16-stage-49-first-run-onboarding-guide-plan.md docs/reviews/claude-code-stage-49-plan-review-prompt.md docs/reviews/claude-code-stage-49-plan-review.md docs/reviews/claude-code-stage-49-plan-rereview-prompt.md docs/reviews/claude-code-stage-49-plan-rereview.md docs/reviews/claude-code-stage-49-release-review-prompt.md docs/reviews/claude-code-stage-49-release-review.md
git commit -m "Add first-run onboarding guide"
```

Push only when the active user has explicitly authorized pushing this repository
to GitHub. The current project owner has authorized it for this work. Use a
credential source stored outside the repository, never print the token, never
commit the token, and never store it in the remote URL or git config. If that
authorization is absent in a future run, stop after commit readiness and report
the verified commit state.

- [ ] **Step 6: Confirm GitHub Actions**

Run the GitHub REST API check for latest `main` run until completed:

```bash
TOKEN="$(cat /home/ubuntu/.config/fashion-radar/github-token)"
curl -fsS -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/Lordakee/fashion-radar/actions/runs?branch=main&per_page=1" \
  | python3 -c 'import json,sys; r=json.load(sys.stdin)["workflow_runs"][0]; print(r["id"], r["status"], r["conclusion"], r["head_sha"], r["html_url"])'
```

Expected: latest run for the pushed commit completes with `success`.
