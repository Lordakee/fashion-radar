# Stage 160 Wheel Entry Points Console Scripts Design

## Objective

Make the package archive checker validate that expected wheel entry points are
present under the `[console_scripts]` group in `entry_points.txt`.

## Current Gap

`scripts/check_package_archives.py` currently reads wheel `entry_points.txt` as
plain stripped lines. This means the checker accepts an expected console script
line even if it appears under the wrong entry-point group, for example:

```ini
[gui_scripts]
fashion-radar = fashion_radar.cli:app
```

That line exists, but it does not prove the wheel exposes the intended command
line executable.

## Scope

In scope:

- Parse wheel `entry_points.txt` as INI-style metadata.
- Require the expected project scripts under exactly `[console_scripts]`.
- Preserve no-traceback behavior for malformed `entry_points.txt`.
- Keep the change inside the package archive release gate.

Out of scope:

- No runtime CLI changes.
- No package metadata rewrites beyond archive-checker validation logic.
- No wheel building changes.
- No social platform connectors, scraping, browser automation, platform APIs,
  login/cookie/token behavior, monitoring, scheduling, source acquisition,
  demand proof, ranking, coverage verification, or compliance-review product
  features.
- No broad release-hygiene or first-run smoke changes.

## Architecture

Replace line-membership validation in `validate_wheel_entry_points(...)` with a
small section-aware parser:

1. Read `{dist_info_dir}/entry_points.txt`.
2. Parse it with `configparser.ConfigParser(interpolation=None)`.
3. Set `parser.optionxform = str` before parsing so script names remain
   case-preserving.
4. Require a `[console_scripts]` section.
5. For each expected script line derived from `[project.scripts]`, split the
   expected `name = target` line into script name and target, then require:
   - the script name exists in `parser["console_scripts"]`;
   - the target exactly matches the expected target.

The checker should return deterministic error strings instead of raising
tracebacks if `entry_points.txt` is malformed.

## Tech Stack

- Python standard library: `configparser`, `zipfile`, existing helpers.
- Existing archive checker script.
- Existing pytest module `tests/test_package_archives.py`.
- Local opencode plan/code/release review with
  `zhipuai-coding-plan/glm-5.2 --variant max`.
- `uv --no-config run --frozen` for tests and lint.

## Implementation Method

Use test-first changes:

1. Add a RED test where `fashion-radar = fashion_radar.cli:app` is placed under
   `[gui_scripts]`. It should fail before implementation because the current
   checker accepts the line anywhere.
2. Update the existing missing-console-script assertion to the new
   section-aware error message.
3. Add a wrong-target test to prove the checker validates the target, not just
   the script name.
4. Implement section-aware parsing in `scripts/check_package_archives.py`.
5. Run focused package archive tests, build archive smoke, code review, full
   release gate, release review, commit, and push.

## Expected Behavior

Wrong group should fail:

```ini
[gui_scripts]
fashion-radar = fashion_radar.cli:app
```

Expected error:

```text
entry_points.txt is missing console_scripts entry: fashion-radar = fashion_radar.cli:app
```

Wrong target should fail:

```ini
[console_scripts]
fashion-radar = fashion_radar.other:app
```

Expected error:

```text
entry_points.txt console_scripts entry mismatch: expected fashion-radar = fashion_radar.cli:app, found fashion-radar = fashion_radar.other:app
```

Malformed entry points should fail without a traceback:

```text
fashion-radar = fashion_radar.cli:app
```

Expected error starts with:

```text
entry_points.txt is invalid:
```

## Risks

- `ConfigParser` lowercases option names by default; `optionxform = str` must be
  set before `read_string(...)`.
- Wheel entry-point metadata is INI-like. `interpolation=None` avoids accidental
  interpolation behavior.
- Error wording changes will require updating the existing missing-script test.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "entry_points"
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
rm -rf "$tmp_build"
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```
