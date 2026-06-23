# Stage 183 Package Archive Entry Point Case Design

## Objective

Add a regression guard proving wheel `entry_points.txt` console-script names
remain case-sensitive.

## Background

The package archive checker reads wheel `entry_points.txt` with
`configparser.ConfigParser(interpolation=None)` and sets `parser.optionxform =
str` before parsing. That preserves the case of option keys. Without that line,
ConfigParser lowercases option names, and a malformed wheel containing
`Fashion-Radar = fashion_radar.cli:app` would be accepted as if it contained
the expected lowercase `fashion-radar = fashion_radar.cli:app`.

Stage 160 review notes recorded this as an optional future guard. The runtime
checker already appears to enforce the intended behavior, so this stage should
be test-only unless the new test exposes a real defect.

## Scope

In scope:

- Add one focused test in `tests/test_package_archives.py`.
- Build a wheel fixture whose `entry_points.txt` contains a case-mismatched
  console-script name.
- Assert the checker rejects the wheel as missing the expected lowercase
  console-script entry.
- Assert no traceback leaks.
- Add Stage 183 plan/review artifacts.

Out of scope:

- Runtime checker changes unless the test exposes a real defect.
- Changes to archive filenames, metadata expectations, required members,
  forbidden member checks, invalid UTF-8 behavior, sdist behavior, dependency
  files, or `uv.lock`.
- Source acquisition, scraping, platform APIs, monitoring, scheduling, ranking,
  demand proof, coverage verification, or compliance-review product features.

## Technical Approach

Reuse the existing `WHEEL_FILES`, `write_wheel`, `write_sdist`, and
`run_checker` helpers in `tests/test_package_archives.py`. Add the new test near
the existing `entry_points.txt` console-script validation tests.

The fixture should replace wheel `entry_points.txt` with:

```text
[console_scripts]
Fashion-Radar = fashion_radar.cli:app
```

Expected behavior:

- exit code is `1`;
- stderr contains
  `entry_points.txt is missing console_scripts entry: fashion-radar = fashion_radar.cli:app`;
- stderr does not contain `Traceback`.

## Acceptance Criteria

- The new test exists in `tests/test_package_archives.py`.
- The test fails if console-script name matching becomes case-insensitive.
- Focused package archive tests pass.
- Ruff check and format check pass for the touched test file.
- Full release gate remains clean before commit.
