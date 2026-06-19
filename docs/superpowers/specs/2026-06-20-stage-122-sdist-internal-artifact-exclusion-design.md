# Stage 122 Sdist Internal Artifact Exclusion Design

## Objective

Keep source distributions focused on public release material by excluding
internal agent review and implementation-planning artifacts from the sdist, and
make the package archive checker fail if those paths appear in any release
archive.

## Problem

A fresh package build currently passes `scripts/check_package_archives.py`, but
the sdist includes historical files under:

- `docs/reviews/`
- `docs/superpowers/`

Those files are useful repository-local development records, but they are not
runtime code, public user docs, config examples, schemas, or release examples.
Shipping them makes the release archive noisy and makes package consumers pull
internal process history that is unrelated to using Fashion Radar.

## Scope

In scope:

- Add Hatch sdist exclusions for `docs/reviews/**` and `docs/superpowers/**`.
- Add package checker coverage that rejects those directories if they appear in
  a wheel or sdist.
- Add tests proving the checker rejects internal review/plan members.
- Add tests pinning the Hatch sdist exclusions.
- Verify an actual local build no longer contains either directory.

Out of scope:

- No runtime behavior changes.
- No CLI behavior changes.
- No source acquisition changes.
- No scraping, browser automation, platform API, connector, monitoring,
  scheduling, demand proof, ranking, or coverage verification features.
- No dependency additions.
- No mirror URL policy changes in this stage.
- No deletion or renaming of existing repository-local review or plan artifacts.

## Architecture

The stage uses two layers:

1. Build-time exclusion in `pyproject.toml`, so normal Hatch sdists omit the
   internal directories.
2. Release-gate validation in `scripts/check_package_archives.py`, so an
   accidentally produced archive fails if it contains those paths.

The checker-level guard is intentionally shared by wheel and sdist validation
through the existing `forbidden_release_member_errors()` path. Wheels should
not include these docs today, but applying the same guard to both archive types
keeps the release boundary simple.

## Tech Stack

- Python 3.11
- Hatchling build configuration in `pyproject.toml`
- Standard library `tarfile` and `zipfile` archive validation
- `pytest` for regression tests
- `uv --no-config run --frozen ...` for verification commands

## Files

- Modify `pyproject.toml`
  - Add `[tool.hatch.build.targets.sdist]` with excludes for internal review
    and superpowers artifacts.
- Modify `scripts/check_package_archives.py`
  - Add internal release artifact path prefixes.
  - Reject paths equal to, or under, those prefixes.
- Modify `tests/test_package_archives.py`
  - Add a regression test for sdist members under `docs/reviews/` and
    `docs/superpowers/`.
- Modify `tests/test_package_metadata.py`
  - Add a regression test for the Hatch sdist excludes.

## Expected Behavior

After implementation:

- A synthetic sdist with `docs/reviews/opencode-stage-1-code-review.md` fails
  archive validation.
- A synthetic sdist with `docs/superpowers/plans/stage-plan.md` fails archive
  validation.
- A synthetic sdist with `docs/superpowers/specs/stage-design.md` fails archive
  validation.
- `pyproject.toml` contains the sdist exclude entries:
  - `/docs/reviews/**`
  - `/docs/superpowers/**`
- A real local `uv build` sdist has no members matching
  `/docs/reviews/` or `/docs/superpowers/` after root-prefix normalization.
- Required public docs, checked-in examples, schemas, and package source files
  remain required by `scripts/check_package_archives.py`.

## Risks

- Hatch glob syntax must be verified with a real build, not only with static
  tests. The release gate includes a real build and archive member scan.
- The checker should reject exact directory entries as well as child files. The
  implementation should treat both `docs/reviews` and `docs/reviews/...` as
  forbidden.
- Required public docs must stay in `SDIST_REQUIRED_PATHS`; this stage must not
  remove public docs or examples from the release archive.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py tests/test_package_metadata.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py tests/test_package_metadata.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py tests/test_package_metadata.py
```

Real archive verification:

```bash
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
if tar -tzf "$tmp_build"/*.tar.gz | grep -E '/docs/(reviews|superpowers)(/|$)'; then
  exit 1
fi
rm -rf "$tmp_build"
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
```
