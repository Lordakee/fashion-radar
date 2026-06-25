# Stage 201 Public RSS Endpoint Liveness Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize configured public RSS endpoints to current direct feed URLs so `source-liveness` and first-run collection avoid avoidable redirects or stale feed paths.

**Architecture:** This stage is config/docs/test only. It updates checked-in RSS URL literals in the public source pack and starter source config/template, pins those canonical URLs with deterministic tests, and records advisory live-liveness evidence without making network success a release gate. It does not change HTTP client code, collectors, source-liveness contracts, scoring, matching, reports, source acquisition, social connectors, proxy behavior, or compliance-review behavior.

**Tech Stack:** YAML source configs, Python 3.11+, pytest, uv, source-pack lint, local OpenCode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Core Product Gap

The `collect -> match -> report` pipeline depends on configured source URLs
being practical starter inputs. Stage 200 removed a local SOCKS dependency
blocker for liveness checks. Stage 201 closes the next small source-coverage
gap: several checked-in RSS URLs currently rely on redirects to the feed that
`source-liveness` and RSS collection actually parse. Recording the current
direct feed URLs reduces avoidable liveness noise and gives users cleaner
starter configs without adding new acquisition surfaces.

## Scope Boundary

This stage may update only checked-in RSS URL literals, related documentation,
tests that pin those literals, and review/plan artifacts.

Do not add:

- new source types, Google News RSS, RSSHub routes, social connectors, scraping,
  crawling, browser automation, platform APIs, account/session/cookie/token
  behavior, CAPTCHA handling, access-control bypasses, paywall bypasses,
  source acquisition, demand proof, ranking, platform coverage verification,
  proxy pools, proxy rotation, or compliance-review product features
- runtime code changes to HTTP client, collectors, source-liveness contracts,
  scoring, matching, reports, source-pack lint behavior, CLI command contracts,
  external/community/imported command surfaces, or dashboard behavior
- live network success as a hard release gate

Live endpoint probes and `source-liveness` runs may be recorded as advisory
evidence only. Deterministic tests are the release gate.

## Advisory Endpoint Evidence

On 2026-06-25, a short read-only probe with redirects enabled observed these
current direct RSS targets:

- Fashionista:
  `https://fashionista.com/.rss/feed/28e21eb8-20ac-4617-a448-e845081591ca.xml`
- Fashion Week Daily: `https://fashionweekdaily.com/feed/`
- The Industry Fashion: `https://www.theindustry.fashion/feed/`
- Highsnobiety: `https://www.highsnobiety.com/feeds/rss`
- WWD: `https://wwd.com/feed/`

The current checked-in pack already redirects successfully for these sources
at the time of probing, so this stage should be framed as direct endpoint
normalization and liveness-noise reduction, not as proof that sources will
remain live.

## Files And Responsibilities

- Create `docs/reviews/opencode-stage-201-plan-review-prompt.md`: plan review
  prompt for local OpenCode.
- Create `docs/reviews/opencode-stage-201-plan-review.md`: cleaned plan review
  result.
- Modify `tests/test_config.py`: add deterministic assertions that the starter
  config, packaged starter template, and public pack use current direct RSS
  endpoints for overlapping configured sources.
- Modify `configs/source-packs/fashion-public.example.yaml`: update direct RSS
  endpoint URLs and the availability comment.
- Modify `configs/sources.example.yaml`: update starter RSS URLs that overlap
  with the public pack.
- Modify `src/fashion_radar/templates/configs/sources.example.yaml`: keep the
  packaged starter template synchronized with `configs/sources.example.yaml`.
- Modify `docs/source-packs.md`: update Source Availability wording to mention
  Stage 201 direct endpoint normalization.
- Modify `tests/test_source_packs_docs.py`: pin the Stage 201 source
  availability wording.
- Modify `CHANGELOG.md`: add a Stage 201 fixed entry under `[Unreleased]`.
- Create `docs/reviews/opencode-stage-201-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-201-code-review.md`.
- Create `docs/reviews/opencode-stage-201-release-review-prompt.md`.
- Create `docs/reviews/opencode-stage-201-release-review.md`.

Do not modify:

- `src/fashion_radar/utils/http.py`
- `src/fashion_radar/source_liveness.py`
- `src/fashion_radar/collectors/*`
- matcher/scoring/report/dashboard modules
- source-pack lint implementation
- external/community/imported command modules
- `pyproject.toml` or `uv.lock`

## Expected Direct Endpoint Map

Use this exact map in tests and config updates:

```python
CANONICAL_PUBLIC_RSS_URLS = {
    "Fashionista": "https://fashionista.com/.rss/feed/28e21eb8-20ac-4617-a448-e845081591ca.xml",
    "Fashion Week Daily": "https://fashionweekdaily.com/feed/",
    "The Industry Fashion": "https://www.theindustry.fashion/feed/",
    "Highsnobiety": "https://www.highsnobiety.com/feeds/rss",
    "WWD": "https://wwd.com/feed/",
}
```

Starter configs contain only the overlapping RSS sources:

```python
CANONICAL_STARTER_RSS_URLS = {
    "Fashionista": "https://fashionista.com/.rss/feed/28e21eb8-20ac-4617-a448-e845081591ca.xml",
    "Fashion Week Daily": "https://fashionweekdaily.com/feed/",
}
```

## Task 0: Create Plan Review Artifacts

**Files:**
- Create: `docs/reviews/opencode-stage-201-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-201-plan-review.md`

- [ ] **Step 1: Write the plan review prompt**

Create `docs/reviews/opencode-stage-201-plan-review-prompt.md` asking local
OpenCode to review:

- whether direct RSS endpoint normalization is the right next stage after
  Stage 200
- whether the scope should include both public pack and starter/template URLs
  that overlap with the pack
- whether deterministic tests should pin exact URL literals before YAML edits
- whether live endpoint probes and `source-liveness` should remain advisory
- whether the plan avoids runtime code, source acquisition, ranking, coverage
  proof, social connectors, proxy pools, and compliance-review features
- whether release verification is sufficient without dependency changes

- [ ] **Step 2: Run plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-201-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-201-plan-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. If OpenCode reports Critical or
Important findings, update this plan and rerun with
`opencode-stage-201-plan-rereview-prompt.md` /
`opencode-stage-201-plan-rereview.md` before implementation.

## Task 1: Add Deterministic Direct Endpoint Tests

**Files:**
- Modify: `tests/test_config.py`
- Modify: `tests/test_stage1_hardening.py`

- [ ] **Step 1: Add helper functions and expected maps**

In `tests/test_config.py`, near the existing public source-pack tests, add:

```python
CANONICAL_PUBLIC_RSS_URLS = {
    "Fashionista": "https://fashionista.com/.rss/feed/28e21eb8-20ac-4617-a448-e845081591ca.xml",
    "Fashion Week Daily": "https://fashionweekdaily.com/feed/",
    "The Industry Fashion": "https://www.theindustry.fashion/feed/",
    "Highsnobiety": "https://www.highsnobiety.com/feeds/rss",
    "WWD": "https://wwd.com/feed/",
}

CANONICAL_STARTER_RSS_URLS = {
    "Fashionista": CANONICAL_PUBLIC_RSS_URLS["Fashionista"],
    "Fashion Week Daily": CANONICAL_PUBLIC_RSS_URLS["Fashion Week Daily"],
}


def rss_urls_by_source_name(path: Path) -> dict[str, str]:
    config = load_source_config(path)
    return {
        source.name: source.url
        for source in config.sources
        if source.type.value == "rss" and source.url is not None
    }
```

- [ ] **Step 2: Add failing tests**

Add these tests after `test_public_fashion_source_pack_loads`:

```python
def test_public_fashion_source_pack_uses_direct_rss_endpoints() -> None:
    urls_by_name = rss_urls_by_source_name(
        Path("configs/source-packs/fashion-public.example.yaml")
    )

    for source_name, expected_url in CANONICAL_PUBLIC_RSS_URLS.items():
        assert urls_by_name[source_name] == expected_url


def test_starter_source_configs_use_direct_rss_endpoints() -> None:
    for path in (
        Path("configs/sources.example.yaml"),
        Path("src/fashion_radar/templates/configs/sources.example.yaml"),
    ):
        urls_by_name = rss_urls_by_source_name(path)
        for source_name, expected_url in CANONICAL_STARTER_RSS_URLS.items():
            assert urls_by_name[source_name] == expected_url
```

- [ ] **Step 3: Add starter/template byte-identity guard**

`tests/test_stage1_hardening.py` already checks that root example configs match
packaged templates. This stage also adds a focused direct assertion so future
starter RSS URL edits cannot desynchronize the root starter and packaged
template. Add after `test_root_example_configs_match_packaged_templates`:

```python
def test_root_and_packaged_source_configs_stay_byte_identical() -> None:
    root = Path(__file__).resolve().parents[1] / "configs" / "sources.example.yaml"
    packaged = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "fashion_radar"
        / "templates"
        / "configs"
        / "sources.example.yaml"
    )

    assert root.read_text(encoding="utf-8") == packaged.read_text(encoding="utf-8")
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_config.py::test_public_fashion_source_pack_uses_direct_rss_endpoints \
  tests/test_config.py::test_starter_source_configs_use_direct_rss_endpoints \
  tests/test_stage1_hardening.py::test_root_and_packaged_source_configs_stay_byte_identical -q
```

Expected before YAML edits: the endpoint tests fail for the current redirected
or non-canonical URL literals, while the byte-identity guard passes.

## Task 2: Update RSS URL Literals

**Files:**
- Modify: `configs/source-packs/fashion-public.example.yaml`
- Modify: `configs/sources.example.yaml`
- Modify: `src/fashion_radar/templates/configs/sources.example.yaml`

- [ ] **Step 1: Update public pack URLs**

In `configs/source-packs/fashion-public.example.yaml`, change:

```yaml
url: https://fashionista.com/.rss/excerpt
url: https://fashionweekdaily.com/feed
url: https://www.theindustry.fashion/feed
url: https://www.highsnobiety.com/feed/
url: https://wwd.com/feed/rss
```

to:

```yaml
url: https://fashionista.com/.rss/feed/28e21eb8-20ac-4617-a448-e845081591ca.xml
url: https://fashionweekdaily.com/feed/
url: https://www.theindustry.fashion/feed/
url: https://www.highsnobiety.com/feeds/rss
url: https://wwd.com/feed/
```

- [ ] **Step 2: Update public pack availability comment**

At the top of `configs/source-packs/fashion-public.example.yaml`, update the
availability comment to include:

```yaml
# Fashionista, Fashion Week Daily, The Industry Fashion, Highsnobiety, and WWD
# direct RSS endpoints were normalized during Stage 201 planning on 2026-06-25.
```

Keep the existing note that RSS availability can change and the pack is a
starter set.

- [ ] **Step 3: Update root starter config URLs**

In `configs/sources.example.yaml`, change the Fashionista and Fashion Week
Daily URLs to:

```yaml
url: https://fashionista.com/.rss/feed/28e21eb8-20ac-4617-a448-e845081591ca.xml
url: https://fashionweekdaily.com/feed/
```

- [ ] **Step 4: Sync the packaged starter template byte-for-byte**

Run:

```bash
cp configs/sources.example.yaml src/fashion_radar/templates/configs/sources.example.yaml
cmp -s configs/sources.example.yaml src/fashion_radar/templates/configs/sources.example.yaml
```

Expected: `cmp -s` exits 0.

Do not change starter source membership, GDELT queries, weights, tags, HTTP
settings, article settings, or health settings.

- [ ] **Step 5: Run GREEN config tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_config.py tests/test_stage1_hardening.py -q
```

Expected: all config tests pass.

## Task 3: Update Source-Pack Docs And Changelog

**Files:**
- Modify: `tests/test_source_packs_docs.py`
- Modify: `docs/source-packs.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add failing docs wording test**

In `tests/test_source_packs_docs.py`, add:

```python
def test_source_packs_docs_record_stage_201_direct_endpoint_refresh() -> None:
    section = _section(_read_source_packs_doc(), "Source Availability")
    normalized = _normalized(section)

    for phrase in (
        "stage 201 planning on 2026-06-25",
        "direct rss endpoints",
        "fashionista",
        "fashion week daily",
        "the industry fashion",
        "highsnobiety",
        "wwd",
        "availability can change without notice",
    ):
        assert phrase in normalized
```

- [ ] **Step 2: Run RED docs test**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_source_packs_docs.py::test_source_packs_docs_record_stage_201_direct_endpoint_refresh -q
```

Expected before docs update: fail because Stage 201 wording is absent.

- [ ] **Step 3: Update `docs/source-packs.md`**

In the `## Source Availability` section, replace the existing availability
paragraph with:

```markdown
Original RSS endpoints were checked during Stage 7 planning on 2026-06-12.
Vogue, Business of Fashion, Red Carpet Fashion Awards, and PurseBlog RSS
endpoints were checked during Stage 197 planning on 2026-06-25. Fashionista,
Fashion Week Daily, The Industry Fashion, Highsnobiety, and WWD direct RSS
endpoints were normalized during Stage 201 planning on 2026-06-25. RSS
availability can change without notice. If a source fails, disable it or
replace it with a feed you have verified.
```

- [ ] **Step 4: Update `CHANGELOG.md`**

Under `[Unreleased] / ### Fixed`, add:

```markdown
- Stage 201 normalizes Fashionista, Fashion Week Daily, The Industry Fashion,
  Highsnobiety, and WWD public RSS URLs to current direct feed endpoints in the
  optional public source pack, and keeps starter source configs aligned without
  adding collectors, source acquisition, ranking, social connectors, proxy
  pools, or compliance-review behavior.
```

- [ ] **Step 5: Run docs checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py -q
```

Expected: all selected docs tests pass.

## Task 4: Focused Verification And Advisory Liveness

**Files:**
- No source edits expected.

- [ ] **Step 1: Run source-pack lint**

Run:

```bash
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

Expected: the public source pack remains lint-clean.

- [ ] **Step 2: Run focused tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_config.py \
  tests/test_stage1_hardening.py \
  tests/test_source_packs.py \
  tests/test_source_packs_docs.py \
  tests/test_source_pack_quality_docs.py \
  tests/test_source_liveness.py -q
```

Expected: all selected tests pass.

- [ ] **Step 3: Run advisory live liveness**

Run:

```bash
uv --no-config run --frozen fashion-radar source-liveness \
  configs/source-packs/fashion-public.example.yaml --format json > /tmp/stage201-source-liveness.json || true
uv --no-config run --frozen python - <<'PY'
import json
from pathlib import Path

payload = json.loads(Path("/tmp/stage201-source-liveness.json").read_text())
print(
    f"live={payload['live_count']} degraded={payload['degraded_count']} "
    f"empty={payload['empty_count']} failed={payload['failed_count']} "
    f"errors={payload['error_count']}"
)
for result in payload["results"]:
    if result["source_name"] in {
        "Fashionista",
        "Fashion Week Daily",
        "The Industry Fashion",
        "Highsnobiety",
        "WWD",
    }:
        print(
            result["source_name"],
            result["status"],
            result["records_seen"],
            result["target"],
            result["message"],
        )
PY
```

Expected: record current evidence honestly. Failures here are advisory and
should not block release unless they reveal a deterministic config mistake.

## Task 5: Code Review, Release Review, Commit, Push

**Files:**
- Create: `docs/reviews/opencode-stage-201-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-201-code-review.md`
- Create: `docs/reviews/opencode-stage-201-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-201-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-201-code-review-prompt.md` asking local
OpenCode to review the Stage 201 diff for:

- exact canonical URL test coverage
- public pack and starter/template alignment, including byte-identity
- docs/changelog accuracy
- no runtime code, dependency, source acquisition, ranking, social connector,
  proxy-pool, or compliance-review scope creep
- focused verification sufficiency before release review

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-201-code-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-201-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. Clean the review artifact before
commit. Fix any Critical/Important findings and rerun with code-rereview
artifacts.

- [ ] **Step 3: Run release verification**

Run:

```bash
git status --short --untracked-files=all
git diff --check
UV_NO_CONFIG=1 uv lock --check
git diff --name-only -- pyproject.toml uv.lock
cmp -s configs/sources.example.yaml src/fashion_radar/templates/configs/sources.example.yaml
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
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+" --glob '!uv.lock' --glob '!dist/**' --glob '!build/**' . || true
```

Expected: all deterministic gates pass, secret scan returns no matches, and
`pyproject.toml` / `uv.lock` remain unchanged.

- [ ] **Step 4: Create and run release review**

Create `docs/reviews/opencode-stage-201-release-review-prompt.md` summarizing
the final diff, code review result, deterministic verification, advisory live
liveness summary, and unchanged dependency graph. Then run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-201-release-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-201-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. Clean the review artifact before
commit. Fix any Critical/Important findings and rerun with release-rereview
artifacts.

- [ ] **Step 5: Final review hygiene**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
rg -n "I'll|I will|Let me|Now let me|→|✱|build ·|\\x1b|\\$ |Wrote|Review complete|Review written|errored" docs/reviews/*stage-201*.md || true
```

Expected: release hygiene passes. Inspect and clean any review artifact noise
before staging.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add \
  CHANGELOG.md \
  configs/source-packs/fashion-public.example.yaml \
  configs/sources.example.yaml \
  docs/source-packs.md \
  docs/reviews/opencode-stage-201-plan-review-prompt.md \
  docs/reviews/opencode-stage-201-plan-review.md \
  docs/reviews/opencode-stage-201-code-review-prompt.md \
  docs/reviews/opencode-stage-201-code-review.md \
  docs/reviews/opencode-stage-201-release-review-prompt.md \
  docs/reviews/opencode-stage-201-release-review.md \
  docs/superpowers/plans/2026-06-25-stage-201-public-rss-endpoint-liveness-recovery-plan.md \
  src/fashion_radar/templates/configs/sources.example.yaml \
  tests/test_config.py \
  tests/test_stage1_hardening.py \
  tests/test_source_packs_docs.py
git commit -m "Stage 201: refresh public RSS endpoints"
git push origin main
```

Expected: push succeeds and `origin/main` points to the new commit.

## Handoff Summary Template

After push, report:

- repo status: branch, `HEAD`, `origin/main`, clean/dirty status
- verified commands: exact commands and pass/fail summaries
- uncommitted files: exact `git status --short --untracked-files=all` output
- next step: recommended Stage 202 direction
