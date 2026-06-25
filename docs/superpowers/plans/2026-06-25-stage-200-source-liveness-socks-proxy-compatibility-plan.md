# Stage 200 Source-Liveness SOCKS Proxy Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the core HTTP client and `source-liveness` usable in environments that already set standard SOCKS proxy environment variables, so future public-source liveness evidence is not blocked by a missing transport helper.

**Architecture:** Keep runtime HTTP behavior unchanged: `FashionHttpClient` continues to construct the default `httpx.Client`, which honors standard user/system proxy environment variables. Add the `httpx` SOCKS extra to the core runtime dependency set, lock the resulting `socksio` package with public uv settings, and add a no-network constructor regression test that proves SOCKS proxy environment variables no longer fail at client construction. Update docs to frame this as standard HTTP client compatibility, not managed proxy functionality.

**Tech Stack:** Python 3.11+, uv lockfile, httpx 0.28.1 with `socks` extra, socksio 1.x, pytest, ruff, local OpenCode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Scope Boundary

This stage closes a source-liveness evidence blocker in the `configured sources
-> HTTP client -> source-liveness` path. Stage 197 and the Stage 200 source
exploration both rely on source-liveness evidence for curated public-source
coverage. In this workspace, `ALL_PROXY` and `all_proxy` are set to
`socks5h://...`, and the current frozen environment lacks `socksio`, so
`httpx.Client(...)` raises:

```text
Using SOCKS proxy, but the 'socksio' package is not installed
```

The fix is dependency metadata and validation only. Do not add:

- proxy pools, proxy rotation, managed proxy configuration, scraping/crawling,
  browser automation, account/session/cookie/token behavior, CAPTCHA handling,
  access-control bypasses, paywall bypasses, platform APIs, source acquisition,
  demand proof, popularity/source ranking, platform coverage verification, or
  compliance-review product features
- per-source proxy config
- `trust_env=False`
- changes to source-liveness contracts, collector persistence, scoring, matcher,
  report generation, source packs, or starter source configs

Live source-liveness runs may be recorded as advisory evidence only. They must
not become release gates because source/network availability is variable.

## Files And Responsibilities

- Modify `pyproject.toml`: change the core runtime dependency from
  `httpx>=0.28.1` to `httpx[socks]>=0.28.1`.
- Modify `uv.lock`: regenerate with `UV_NO_CONFIG=1 uv lock`, expecting a narrow
  diff that adds `socksio` and records the `httpx` `socks` extra in project
  metadata.
- Modify `tests/test_http.py`: add a no-network regression test proving
  `FashionHttpClient(...)` constructs successfully when either `ALL_PROXY` or
  `all_proxy` is `socks5h://...`.
- Modify `tests/test_cli_docs.py`: pin the dependency mirror and README wording
  that describes the SOCKS transport helper without adding proxy-pool scope.
- Modify `docs/dependency-mirrors.md`: document that frozen installs include
  the SOCKS transport helper and mirror users should use the existing
  `UV_DEFAULT_INDEX=... uv sync --frozen --dev` flow rather than editing
  lockfiles or installing ad hoc dependencies.
- Modify `README.md`: add a short source-liveness note that proxy-configured
  environments should refresh from the committed lock/frozen install.
- Modify `CHANGELOG.md`: add Stage 200 under `[Unreleased] / ### Fixed`.
- Create review artifacts:
  - `docs/reviews/opencode-stage-200-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-200-plan-review.md`
  - `docs/reviews/opencode-stage-200-code-review-prompt.md`
  - `docs/reviews/opencode-stage-200-code-review.md`
  - `docs/reviews/opencode-stage-200-release-review-prompt.md`
  - `docs/reviews/opencode-stage-200-release-review.md`

Do not modify:

- `src/fashion_radar/utils/http.py`
- `src/fashion_radar/source_liveness.py`
- `configs/source-packs/*`
- `configs/sources.example.yaml`
- `src/fashion_radar/templates/configs/sources.example.yaml`
- matcher/scoring/report/source-pack runtime modules
- external/community/imported command surfaces

## Task 0: Create Plan Review Artifacts

**Files:**
- Create: `docs/reviews/opencode-stage-200-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-200-plan-review.md`

- [ ] **Step 1: Write the plan review prompt**

Create `docs/reviews/opencode-stage-200-plan-review-prompt.md` asking local
OpenCode to review:

- whether Stage 200 should prioritize SOCKS proxy compatibility before public
  RSS endpoint recovery and source expansion
- whether `httpx[socks]>=0.28.1` is the right dependency-level fix instead of
  `trust_env=False`, per-source proxy config, or source-liveness code changes
- whether the test proves the constructor failure without live network access
- whether the lockfile/mirror verification is sufficient
- whether docs wording avoids proxy-pool/scraping/source-acquisition scope drift
- whether the stage avoids source packs, starter configs, scoring, report,
  social connectors, and compliance-review product features

- [ ] **Step 2: Run plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-200-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-200-plan-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. If OpenCode finds Critical or
Important issues, update this plan, rerun review, and save a
`opencode-stage-200-plan-rereview.md` artifact before implementation.

## Task 1: Add SOCKS Constructor Regression

**Files:**
- Modify: `tests/test_http.py`

- [ ] **Step 1: Add failing test**

Add this test after `test_http_client_sends_user_agent_and_parses_json`:

```python
@pytest.mark.parametrize("proxy_env", ["ALL_PROXY", "all_proxy"])
def test_http_client_constructs_with_socks_proxy_env(
    monkeypatch: pytest.MonkeyPatch,
    proxy_env: str,
) -> None:
    for key in (
        "ALL_PROXY",
        "all_proxy",
        "HTTP_PROXY",
        "http_proxy",
        "HTTPS_PROXY",
        "https_proxy",
        "NO_PROXY",
        "no_proxy",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv(proxy_env, "socks5h://127.0.0.1:9")

    client = FashionHttpClient(HttpSourceSettings(per_domain_delay_seconds=0))
    client.close()
```

This test must not make a network request. It only proves default client
construction works when `httpx` observes SOCKS proxy environment variables.
`tests/test_source_liveness.py` uses fake clients and intentionally guards
against default network clients, so `tests/test_http.py` is the correct
RED/GREEN location for the constructor failure.

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_http.py::test_http_client_constructs_with_socks_proxy_env -q
```

Expected before dependency change: fail with an `ImportError` mentioning the
missing `socksio` package.

## Task 2: Add SOCKS Runtime Dependency

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`

- [ ] **Step 1: Update dependency metadata**

In `pyproject.toml`, change:

```toml
"httpx>=0.28.1",
```

to:

```toml
"httpx[socks]>=0.28.1",
```

- [ ] **Step 2: Regenerate lockfile without local uv config**

Run:

```bash
UV_NO_CONFIG=1 uv lock
```

Expected: `uv.lock` updates narrowly:

- `httpx` remains at the current compatible version unless uv has a resolver
  reason to change it
- a `socksio` package is added
- project metadata records the `httpx` `socks` extra
- no mirror/index URLs are written into `uv.lock`

- [ ] **Step 3: Sync from the locked dependency graph**

Run:

```bash
UV_NO_CONFIG=1 uv sync --locked --dev
```

Expected: the environment installs `socksio` from the lockfile.

- [ ] **Step 4: Run GREEN HTTP tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_http.py -q
ALL_PROXY=socks5h://127.0.0.1:9 all_proxy=socks5h://127.0.0.1:9 \
  uv --no-config run --frozen pytest tests/test_http.py -q
```

Expected: all tests pass in both normal and SOCKS-proxy-env runs.

- [ ] **Step 5: Check lockfile and mirror hygiene**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
git diff -- pyproject.toml uv.lock
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
```

Expected: lock check passes, the diff is dependency-scoped, and no mirror or
index config strings are present in `uv.lock`.

## Task 3: Update User-Facing Install And Liveness Notes

**Files:**
- Modify: `docs/dependency-mirrors.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add docs tests if existing coverage requires it**

Inspect `tests/test_cli_docs.py`, `tests/test_project_brief_docs.py`, and related
docs tests for sections that already pin dependency mirrors or source-liveness
wording. If they contain relevant assertions, update them first so they fail
until docs are changed. Do not add broad new docs tests unless an existing
parity test naturally owns this text.

- [ ] **Step 2: Update dependency mirror docs**

In `docs/dependency-mirrors.md`, add a short note near the locked/frozen install
guidance:

```markdown
The locked core install includes the HTTP client's SOCKS transport helper used
when a user's environment already sets standard SOCKS proxy variables. Keep
using the committed lockfile with your mirror (`UV_DEFAULT_INDEX=... uv sync
--frozen --dev`) instead of editing `uv.lock` or installing ad hoc packages.
```

Do not add mirror URLs to `uv.lock` or `pyproject.toml`.

- [ ] **Step 3: Update README source-liveness note**

Near the `source-liveness` usage section in `README.md`, add:

```markdown
In proxy-configured environments, refresh from the committed lockfile/frozen
install so the HTTP client's SOCKS transport helper is present. Fashion Radar
does not manage proxy pools or rotate proxies; it only uses the standard
environment observed by the HTTP client.
```

Keep nearby source-boundary wording intact.

- [ ] **Step 4: Update changelog**

Under `[Unreleased] / ### Fixed`, add:

```markdown
- Stage 200 declares the HTTP client's SOCKS transport helper in the locked
  core dependency graph so `source-liveness` and configured-source HTTP checks
  can construct clients in environments that already set standard SOCKS proxy
  variables, without adding proxy pools, scraping, source acquisition, ranking,
  coverage verification, social connectors, or compliance-review behavior.
```

- [ ] **Step 5: Run docs and package metadata checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_metadata.py tests/test_cli_docs.py tests/test_project_brief_docs.py -q
uv --no-config run --frozen ruff check tests/test_http.py
uv --no-config run --frozen ruff format --check tests/test_http.py
git diff --check
```

Expected: all pass.

## Task 4: Focused Regression And Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-200-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-200-code-review.md`

- [ ] **Step 1: Run focused regression**

Run:

```bash
uv --no-config run --frozen pytest tests/test_http.py tests/test_source_liveness.py -q
ALL_PROXY=socks5h://127.0.0.1:9 all_proxy=socks5h://127.0.0.1:9 \
  uv --no-config run --frozen pytest tests/test_http.py tests/test_source_liveness.py -q
uv --no-config run --frozen pytest tests/test_package_metadata.py tests/test_cli_docs.py tests/test_project_brief_docs.py -q
uv --no-config run --frozen ruff check pyproject.toml tests/test_http.py
uv --no-config run --frozen ruff format --check tests/test_http.py
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Run advisory source-liveness check**

Run:

```bash
uv --no-config run --frozen fashion-radar source-liveness \
  configs/source-packs/fashion-public.example.yaml --format json || true
```

Expected: the previous `ImportError` about missing `socksio` should not appear.
The command may still report source-level fetch failures if the proxy/network or
remote feeds are unavailable. Record this honestly in the code/release review
artifacts as advisory evidence only.

- [ ] **Step 3: Create code review prompt**

Create `docs/reviews/opencode-stage-200-code-review-prompt.md` asking OpenCode
to review:

- dependency metadata and lockfile diff scope
- SOCKS constructor regression test quality and no-network behavior
- mirror/lockfile hygiene
- docs wording around standard proxy environment compatibility
- no source-liveness contract, source pack, starter config, scraping,
  source-acquisition, ranking, social connector, or compliance-review drift

- [ ] **Step 4: Run local OpenCode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-200-code-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-200-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. Clean the review artifact of any
tool chatter before commit. Fix any Critical/Important findings and rerun a
`code-rereview` before release review.

## Task 5: Release Verification, Release Review, Commit, And Push

**Files:**
- Create: `docs/reviews/opencode-stage-200-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-200-release-review.md`
- Modify: any file needed to fix Critical or Important release findings

- [ ] **Step 1: Run release verification**

Run:

```bash
git status --short --untracked-files=all
git diff --check
UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- pyproject.toml || true
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
rm -rf "$tmp_build"
uv --no-config run --frozen pytest tests/ -q --tb=short
```

Expected: all pass. `pyproject.toml` and `uv.lock` are intentionally changed in
this stage; inspect their diff manually and ensure it is dependency-scoped.

- [ ] **Step 2: Run secret/local-artifact scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+" --glob '!uv.lock' --glob '!dist/**' --glob '!build/**' . || true
git status --short --untracked-files=all
```

Expected: no secret hits and no accidental local artifacts.

- [ ] **Step 3: Create and run local OpenCode release review**

Create `docs/reviews/opencode-stage-200-release-review-prompt.md` covering:

- final diff and dependency/lockfile scope
- verification command results
- mirror/secret/local artifact checks
- advisory source-liveness result
- package archive and installed metadata
- standard proxy compatibility wording
- no source-pack/source-liveness contract/social/scraping/ranking/demand-proof/
  coverage-verification/compliance-review expansion

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-200-release-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-200-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. Clean the review artifact before
commit. Fix any Critical/Important findings and rerun `release-rereview`.

- [ ] **Step 4: Check review artifact hygiene**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
rg -n "I'll|Let me|Now let me|→|✱|build ·|\\x1b|\\$ |Wrote|errored" docs/reviews/*stage-200*.md || true
```

Expected: release hygiene passes. Inspect any `rg` match before staging.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add \
  CHANGELOG.md \
  README.md \
  docs/dependency-mirrors.md \
  docs/reviews/opencode-stage-200-plan-review-prompt.md \
  docs/reviews/opencode-stage-200-plan-review.md \
  docs/reviews/opencode-stage-200-code-review-prompt.md \
  docs/reviews/opencode-stage-200-code-review.md \
  docs/reviews/opencode-stage-200-release-review-prompt.md \
  docs/reviews/opencode-stage-200-release-review.md \
  docs/superpowers/plans/2026-06-25-stage-200-source-liveness-socks-proxy-compatibility-plan.md \
  pyproject.toml \
  uv.lock \
  tests/test_cli_docs.py \
  tests/test_http.py
git commit -m "Stage 200: support SOCKS proxy source liveness"
git push origin main
```

Expected: push succeeds and `origin/main` points to the new commit.

## Handoff Summary Template

At node completion, report:

```markdown
Handoff Summary
- Repo status: branch, HEAD SHA, origin/main SHA, clean/dirty state.
- Verified commands: concise list with pass/fail status.
- Uncommitted files: exact `git status --short --untracked-files=all` result.
- Next step: Stage 201 public RSS endpoint liveness recovery, unless release
  review identifies a more urgent fix.
```
