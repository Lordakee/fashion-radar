# Claude Code Stage 32 Release Review Prompt

You are reviewing the completed Stage 32 CI release hygiene changes for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release/code review only; do not edit files.
- Treat Critical and Important findings as blockers for commit and push.

## Goal

Stage 32 should align GitHub CI, contributor docs, PR/issue templates, and
upload smoke commands with Stage 31 release-gate lockfile and artifact hygiene.

## Approved Plan Evidence

- Stage 32 design:
  `docs/superpowers/specs/2026-06-14-stage-32-ci-release-hygiene-design.md`
- Stage 32 implementation plan:
  `docs/superpowers/plans/2026-06-14-stage-32-ci-release-hygiene-plan.md`
- Corrected plan approval:
  `docs/reviews/claude-code-stage-32-plan-rereview.md`

The first Stage 32 plan review artifact is intentionally retained as historical
audit evidence and documents an earlier Critical finding. The corrected plan was
approved in the rereview artifact above.

## Files To Review

- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `AGENTS.md`
- `README.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`
- `docs/release-gate-stage31.md`
- `docs/superpowers/specs/2026-06-14-stage-32-ci-release-hygiene-design.md`
- `docs/superpowers/plans/2026-06-14-stage-32-ci-release-hygiene-plan.md`
- `docs/reviews/claude-code-stage-32-*.md`

## Review Checklist

Check that:

- CI runs `UV_NO_CONFIG=1 uv lock --check` and
  `UV_NO_CONFIG=1 uv sync --locked --dev --check` before install.
- CI rejects mirror/index markers in `uv.lock`.
- CI installs with `UV_NO_CONFIG=1 uv sync --locked --dev`.
- CI builds to a temp directory, installs the wheel from that same temp
  directory, and does not use repository `dist/*.whl`.
- Contributor docs, PR template, issue template, agent instructions, and mirror
  docs use `UV_NO_CONFIG=1` for public lockfile checks.
- Local mirror install guidance remains mirror-backed and frozen.
- Upload checklist uses `uv run python -m zipfile` rather than bare
  `python -m zipfile`.
- `docs/release-gate-stage31.md` summarizes Stage 31 review artifacts without a
  stale partial explicit list.
- `CHANGELOG.md` accurately summarizes the Stage 32 hygiene change.
- There are no `uv.lock`, dependency, runtime code, source connector, scraping,
  crawling, platform automation, watcher, scheduler, source acquisition, source
  ranking, demand proof, platform coverage, secret, generated artifact, or
  build artifact changes implied by Stage 32.

## Verification Evidence

The following local commands have already exited `0` in this Stage 32 run:

```bash
python3 - <<'PY'
import re
from pathlib import Path

paths = [
    Path("AGENTS.md"),
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path(".github/pull_request_template.md"),
    Path(".github/ISSUE_TEMPLATE/bug_report.yml"),
    Path("docs/dependency-mirrors.md"),
    Path("docs/github-upload-checklist.md"),
    Path("docs/release-gate-stage31.md"),
]
missing = []
for path in paths:
    for _, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if "://" in target or target.startswith("#"):
            continue
        target_path = target.split("#", 1)[0]
        if target_path and not (path.parent / target_path).exists():
            missing.append(f"{path}: {target}")
if missing:
    raise SystemExit("\n".join(missing))
PY
rg -n 'UV_NO_CONFIG=1 uv lock --check|UV_NO_CONFIG=1 uv sync --locked --dev --check|tmp_build|dist/\*\.whl' .github/workflows/ci.yml
rg -n 'uv lock --check|uv sync --locked --dev|UV_NO_CONFIG=1|UV_DEFAULT_INDEX|python -m zipfile|dist/\*\.whl' AGENTS.md README.md CONTRIBUTING.md .github docs/dependency-mirrors.md docs/github-upload-checklist.md .github/workflows/ci.yml
git diff --check
git diff --cached --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

Test result:

```text
572 passed
```

CI-equivalent build smoke also exited `0` using this command shape:

```bash
tmp_build="$(mktemp -d)"
uv build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
tmp_run="$(mktemp -d)"
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/fashion-radar" init --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
"$tmp_env/venv/bin/fashion-radar" doctor --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
"$tmp_env/venv/bin/python" -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
tmp_dash="$(mktemp -d)"
uv venv "$tmp_dash/venv"
wheel_path="$(ls "$tmp_build"/*.whl | head -n 1)"
uv pip install --python "$tmp_dash/venv/bin/python" "${wheel_path}[dashboard]"
"$tmp_dash/venv/bin/python" -c "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
```

The diff-scoped boundary scan only matched negative boundary language in
`docs/release-gate-stage31.md`. Diff-scoped secret scanning returned no matches.
`git diff -- uv.lock` returned no diff.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the changes are acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 32 COMMIT AND PUSH
```
