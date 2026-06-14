# Stage 35 Public Launch Contact Design

## Goal

Make the repository's public security and conduct reporting paths actionable
before public GitHub launch.

## Scope

Stage 35 is a release hygiene and repository settings node. It does not add
runtime features.

In scope:

- Enable or verify GitHub private vulnerability reporting for the repository.
- Update `SECURITY.md` so sensitive security reports have a concrete private
  GitHub reporting path.
- Update `CODE_OF_CONDUCT.md` so conduct reports have a concrete GitHub issue
  path that can be moderated by maintainers.
- Add an issue template for public conduct/moderation contact that warns users
  not to include secrets or sensitive security details.
- Align CI package smoke with the release checklist's explicit wheel
  content assertion for packaged templates.
- If the GitHub repository is still private, perform the public launch visibility
  switch only after local verification, private-repo push, CI success, and
  public-release scans.
- Add Stage 35 plan/review artifacts.

Out of scope:

- Runtime code changes.
- Dependency or `uv.lock` changes.
- Source connectors, scraping, crawling, browser automation, login/cookie
  flows, watchers, schedulers, source acquisition, source ranking, demand proof,
  or platform coverage verification.
- Publishing a PyPI package or uploading build artifacts.

## Design

### Security Reporting Path

Use GitHub private vulnerability reporting as the concrete security channel.
This avoids publishing a personal email address and keeps sensitive reports out
of public issues. `SECURITY.md` should instruct users to use the repository's
Security tab and explicitly tell them not to put sensitive details in public
issues.

The GitHub repository should have `private_vulnerability_reporting` enabled via
the repository security settings or the dedicated GitHub REST API endpoint:
`GET`/`PUT /repos/{owner}/{repo}/private-vulnerability-reporting`.

GitHub documents private vulnerability reporting as a feature for public
repositories. The current private repository state can make the dedicated
endpoint unavailable, so Stage 35 treats the public visibility switch and PVR
enablement as one release operation after the private repository commit has
already passed local and GitHub Actions verification.

Only an unambiguous `{"enabled": true}` response from the dedicated check
endpoint counts as verification. If private vulnerability reporting cannot be
verified as enabled immediately after the repository is made public, Stage 35
must attempt to restore the repository to private visibility and stop. The
launch path then requires either repository-admin access to enable the GitHub
setting or a different concrete private reporting channel.

### Conduct Reporting Path

Use a dedicated GitHub issue template for conduct/moderation contact. GitHub
issues are public by default, so the template must tell users to avoid secrets,
private security details, private source exports, local databases, generated
reports, and doxxing material. For highly sensitive matters, it should direct
users to open a minimal moderation-contact issue and wait for maintainer
instructions.

This is not as private as a dedicated email address, but it is concrete and
actionable for a small pre-1.0 open source project without exposing a personal
mailbox.

### CI Package Smoke Alignment

Add a wheel archive content assertion in CI after `uv build --out-dir
"$tmp_build"` that verifies every required packaged template/config path:

```bash
uv run python - "$tmp_build"/*.whl <<'PY'
import sys
import zipfile

expected = {
    "fashion_radar/templates/daily_report.md",
    "fashion_radar/templates/configs/sources.example.yaml",
    "fashion_radar/templates/configs/entities.example.yaml",
    "fashion_radar/templates/configs/scoring.example.yaml",
}
with zipfile.ZipFile(sys.argv[1]) as wheel:
    names = set(wheel.namelist())
missing = sorted(expected - names)
if missing:
    raise SystemExit("Missing wheel template files: " + ", ".join(missing))
print("Wheel template files present:", ", ".join(sorted(expected)))
PY
```

This makes CI evidence match `docs/github-upload-checklist.md` while still using
`/tmp` build artifacts.

## Verification

Local verification should include:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --cached --check
```

Repository settings verification should query GitHub and confirm private
vulnerability reporting is enabled.

After push, poll the GitHub Actions run for the new commit and confirm it
succeeds.
