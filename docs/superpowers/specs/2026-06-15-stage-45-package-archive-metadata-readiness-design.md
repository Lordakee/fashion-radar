# Stage 45 Package Archive And Metadata Readiness Design

## Goal

Make the GitHub-ready package surface explicit and testable: public package
metadata should identify the project correctly, both wheel and sdist archives
should be checked for release-critical files, and installed-package smoke checks
should cover both the console script and module entrypoint.

## Scope

In scope:

- Add public package metadata to `pyproject.toml`: keywords, classifiers, and
  project URLs for the GitHub repository, documentation, issues, changelog, and
  security policy.
- Add a local archive inspection script that checks one built wheel and one
  built sdist in a supplied build directory.
- Require wheel checks for the CLI module, module entrypoint, packaged
  templates, dist-info metadata, console entry point, and bundled license file.
- Require sdist checks for public-readiness files: README, license, security,
  contribution/conduct docs, changelog, upload checklist, key documentation,
  config/source/entity examples, community signal examples, schema, and package
  source entrypoints.
- Update CI package smoke to run the archive inspection script after
  `uv build`.
- Update the GitHub upload checklist so humans run the same archive inspection
  script and also smoke `python -m fashion_radar --help` from the installed
  wheel environment.
- Add tests that guard package metadata, the archive inspection script, and
  CI/checklist package-smoke drift.
- Record Stage 45 Claude Code plan and release review artifacts.

Out of scope:

- PyPI publishing, GitHub release creation, artifact upload, or remote
  configuration changes.
- Dependency additions, dependency upgrades, lockfile changes, package version
  bumps, or dashboard/runtime feature changes.
- Source connectors, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, source acquisition, schedulers,
  watchers, monitors, or external services.
- Any compliance-review feature inside the tool.
- Exhaustive archive assertions for every tracked file. The checks should cover
  release-critical public files only, so future docs can move without excessive
  maintenance cost.

## Design

`pyproject.toml` currently has functional but thin metadata. Stage 45 should
keep the package name, version, dependencies, build backend, and script entry
point unchanged, while adding public metadata that GitHub and future package
consumers can use:

- `keywords` for fashion trend monitoring, local-first use, RSS/GDELT, and
  community signals.
- `classifiers` for alpha maturity, console environment, MIT license, Python
  3.11/3.12, operating-system independence, and relevant indexing/news/text
  processing topics.
- `[project.urls]` pointing to the existing GitHub repository and repository
  docs. These URLs must not claim PyPI publication.

Create `scripts/check_package_archives.py` as a dependency-free Python script.
It should accept a build output directory, find exactly one wheel and one
`.tar.gz` sdist, inspect them with `zipfile` and `tarfile`, normalize the sdist
root directory prefix, and exit non-zero with a clear missing-file message when
required files are absent. It should use pattern checks for dynamic dist-info
paths such as `fashion_radar-0.1.0.dist-info/METADATA` and exact normalized
paths for package and sdist contents.

The required wheel checks should include:

```text
fashion_radar/cli.py
fashion_radar/__main__.py
fashion_radar/templates/daily_report.md
fashion_radar/templates/configs/sources.example.yaml
fashion_radar/templates/configs/entities.example.yaml
fashion_radar/templates/configs/scoring.example.yaml
*.dist-info/METADATA
*.dist-info/WHEEL
*.dist-info/entry_points.txt
*.dist-info/licenses/LICENSE
```

The required sdist checks should include:

```text
README.md
LICENSE
SECURITY.md
CODE_OF_CONDUCT.md
CONTRIBUTING.md
CHANGELOG.md
pyproject.toml
docs/cli-reference.md
docs/github-upload-checklist.md
docs/source-boundaries.md
docs/dependency-mirrors.md
docs/community-signal-import.md
docs/source-packs.md
docs/entity-packs.md
configs/sources.example.yaml
configs/entities.example.yaml
configs/scoring.example.yaml
configs/source-packs/fashion-public.example.yaml
configs/entity-packs/fashion-watchlist.example.yaml
examples/community-signals.example.csv
examples/community-signals.example.json
schemas/community-signals.schema.json
src/fashion_radar/cli.py
src/fashion_radar/__main__.py
src/fashion_radar/templates/daily_report.md
src/fashion_radar/templates/configs/sources.example.yaml
src/fashion_radar/templates/configs/entities.example.yaml
src/fashion_radar/templates/configs/scoring.example.yaml
```

Update `.github/workflows/ci.yml` to replace the inline wheel-template-only
archive check with:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
```

Keep the existing installed wheel smoke, and add:

```bash
"$tmp_env/venv/bin/python" -m fashion_radar --help
```

Update `docs/github-upload-checklist.md` to use the same archive inspection
command and the same module-entrypoint smoke. The checklist can keep the broad
installed command help loop because it is stronger than CI's shorter smoke.

Update `README.md` near Quickstart to distinguish source-checkout setup from
package archive readiness. It should explain that `uv sync --locked --dev` is
for development from a checkout, and the upload checklist builds and smokes a
local wheel without claiming PyPI availability.

## Verification

Focused RED/GREEN checks:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_metadata.py -q
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py -q
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_package_archive_smoke_command_is_documented_and_in_ci -q
```

Archive smoke:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
```

Release checks:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_metadata.py tests/test_package_archives.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run ruff check scripts/check_package_archives.py tests/test_package_metadata.py tests/test_package_archives.py tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check scripts/check_package_archives.py tests/test_package_metadata.py tests/test_package_archives.py tests/test_cli_docs.py
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```
