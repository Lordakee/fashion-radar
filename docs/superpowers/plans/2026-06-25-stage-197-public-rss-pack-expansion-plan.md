# Stage 197 Public RSS Pack Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the optional public fashion source pack with a small curated set of currently reachable public RSS feeds for fashion editorial, business/luxury, celebrity style, and bag/product coverage.

**Architecture:** Keep the default compact `configs/sources.example.yaml` unchanged and update only the optional broader public source pack. Add only existing supported source types (`rss`), disable RSS article extraction for the new feeds, preserve conservative weights/tags, and regenerate docs examples from deterministic `source-pack-lint` output. Treat live source checks as advisory point-in-time evidence, not release-blocking verification.

**Tech Stack:** YAML source config, existing `source-pack-lint` and `source-liveness` CLIs, pytest docs guards, ruff, uv, no new dependencies.

---

## Scope Boundary

This stage must not add default source-pack changes, collectors, source types,
Google News RSS, Google Trends, social scraping, browser automation, platform
APIs, login/cookie/proxy behavior, source acquisition workflows, source ranking,
demand proof, platform-wide coverage claims, or compliance-review product
features.

Live feed checks may be recorded as advisory review evidence only. Blocking
verification must be deterministic and offline.

## Candidate RSS Evidence

These public RSS URLs returned HTTP 200 with XML/RSS content during Stage 197
planning on 2026-06-25:

- `https://www.vogue.com/feed/rss`
- `https://www.businessoffashion.com/arc/outboundfeeds/rss/`
- `https://www.redcarpet-fashionawards.com/feed/`
- `https://www.purseblog.com/feed/`

Rejected or deferred examples:

- Vogue Business guessed RSS endpoints returned 404.
- FashionNetwork RSS endpoints returned 403.
- Who What Wear RSS redirected to XML and was reachable, but this stage keeps
  the first expansion small and avoids adding a redirecting feed in the same
  node.
- Hypebeast RSS was reachable, but the current pack already has Highsnobiety
  for streetwear/culture; add Hypebeast only in a future streetwear-focused
  source-balance stage if needed.
- Elle, Harper's Bazaar, and Footwear News feeds were reachable, but this stage
  prefers a smaller product-fit set that directly covers business/luxury
  fashion, red-carpet styling, and bags/accessories. Footwear News also shares
  the `wwd.com` domain with `WWD`; it can be added in a future footwear-focused
  balance node if needed.

## Files And Responsibilities

- Modify `configs/source-packs/fashion-public.example.yaml`: add four RSS
  entries with `article.enabled: false`, explicit weights, and lane tags; update
  the top comment so Stage 197 additions do not inherit the Stage 7-only
  endpoint-check note.
- Modify `docs/source-packs.md`: update public-pack summary, Stage 197 source
  availability note, lint JSON example, and keep GDELT list unchanged unless
  YAML GDELT sources change.
- Modify `docs/source-pack-quality.md`: update table and JSON examples from
  current `source-pack-lint` output.
- Modify `CHANGELOG.md`: add a Stage 197 entry under `[Unreleased]`.
- Create Stage 197 review artifacts under `docs/reviews/`.

## Task 1: Expand Optional Public RSS Sources

**Files:**
- Modify: `configs/source-packs/fashion-public.example.yaml`

- [ ] **Step 1: Add RSS entries after existing RSS sources**

Add these entries after `WWD` and before the existing GDELT lanes:

```yaml
  - name: Vogue
    type: rss
    url: https://www.vogue.com/feed/rss
    enabled: true
    weight: 1.0
    tags: [fashion_media, runway, fashion_week, celebrity_style]
    article:
      enabled: false
  - name: Business of Fashion
    type: rss
    url: https://www.businessoffashion.com/arc/outboundfeeds/rss/
    enabled: true
    weight: 1.0
    tags: [trade_media, industry_news, designer_brands, luxury, retail, emerging_designers]
    article:
      enabled: false
  - name: Red Carpet Fashion Awards
    type: rss
    url: https://www.redcarpet-fashionawards.com/feed/
    enabled: true
    weight: 0.8
    tags: [celebrity_style, red_carpet, fashion_media]
    article:
      enabled: false
  - name: PurseBlog
    type: rss
    url: https://www.purseblog.com/feed/
    enabled: true
    weight: 0.8
    tags: [products, accessories, bags, handbags, luxury]
    article:
      enabled: false
```

Rationale:

- `Vogue` adds runway, designer, and fashion-editorial context.
- `Business of Fashion` adds industry, business/luxury, retail, designer-brand,
  and emerging-designer context through a working Arc RSS feed; the simpler
  `/rss/` guess returned 404 during planning.
- `Red Carpet Fashion Awards` adds direct red-carpet celebrity style coverage.
- `PurseBlog` adds focused bag/accessory/product coverage.

- [ ] **Step 2: Update the YAML header comment**

Replace the current Stage 7-only endpoint note with:

```yaml
# Original RSS endpoints were checked during Stage 7 planning on 2026-06-12.
# Vogue, Business of Fashion, Red Carpet Fashion Awards, and PurseBlog RSS
# endpoints were checked during Stage 197 planning on 2026-06-25. RSS
# availability can change. Treat this as a starter set, not an endorsement or
# availability guarantee.
```

- [ ] **Step 3: Verify source-pack lint**

Run:

```bash
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

Expected: no source-pack quality findings, `source_count` increases from `16`
to `20`, `type_counts` becomes `{"gdelt": 10, "rss": 10}`, and tag counts
reflect the four new RSS entries. The new `red_carpet`, `bags`, and `handbags`
tags are intentional free-form source-pack tags and are expected in regenerated
tag counts.

## Task 2: Synchronize Public Source-Pack Docs

**Files:**
- Modify: `docs/source-packs.md`
- Modify: `docs/source-pack-quality.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update `docs/source-packs.md` public-pack prose**

In `## Public Fashion Pack`, update the summary sentence so it mentions the
new RSS coverage without implying platform coverage or live availability:

```markdown
The expanded public pack keeps the RSS entries conservative, adds public RSS
feeds for runway/editorial, business/luxury fashion, red-carpet celebrity
style, and bag/accessory product signals, and keeps bounded GDELT lanes for
runway and fashion week, designer-brand momentum, retail and resale, footwear,
handbags and accessories, creative-director moves, and beauty/fashion crossover
signals inside the configured source set.
```

Keep the following boundary paragraph unchanged:

```markdown
It does not include Google News RSS, Google Trends, account-based source access,
browser automation, access-control bypasses, paywall bypass, or private data
collection.
```

- [ ] **Step 2: Regenerate `docs/source-packs.md` JSON example**

Run:

```bash
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

Replace the `Example JSON shape` block in `docs/source-packs.md` with the
command output. Preserve JSON indentation and the `findings: []` invariant.

- [ ] **Step 3: Update source availability note**

Replace the current source availability paragraph with:

```markdown
Original RSS endpoints were checked during Stage 7 planning on 2026-06-12.
Vogue, Business of Fashion, Red Carpet Fashion Awards, and PurseBlog RSS
endpoints were checked during Stage 197 planning on 2026-06-25. RSS
availability can change without notice. If a source fails, disable it or
replace it with a feed you have verified.
```

- [ ] **Step 4: Regenerate `docs/source-pack-quality.md` table and JSON samples**

Run:

```bash
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

Update the table sample and JSON sample to match exactly. The tests compare
these samples to runtime lint output.

- [ ] **Step 5: Add changelog entry**

Under `[Unreleased]`, add an `### Added` entry at the top of the existing
`### Added` list:

```markdown
- Stage 197 expands the optional public fashion source pack with four public
  RSS feeds for runway/editorial, business/luxury fashion, red-carpet celebrity
  style, and bag/accessory product signals, based on point-in-time RSS planning
  evidence. It does not change the compact default starter config, add
  social/platform connectors, scrape, automate browsers, bypass access
  controls, prove demand, rank sources, verify platform coverage, or add
  compliance-review product features.
```

## Task 3: Update Public Source-Pack CLI Count Test

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Update public-pack count assertions**

In `test_source_pack_lint_prints_json_for_public_pack()`, update:

```python
assert payload["source_count"] == 20
assert payload["type_counts"] == {"gdelt": 10, "rss": 10}
```

- [ ] **Step 2: Verify the focused CLI test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py::test_source_pack_lint_prints_json_for_public_pack -q
```

Expected: pass.

## Task 4: Focused Verification And Review

**Files:**
- Create: `docs/reviews/opencode-stage-197-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-197-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-197-code-review.md`
- Create: `docs/reviews/opencode-stage-197-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-197-release-review.md`

- [ ] **Step 1: Run focused deterministic checks**

Run:

```bash
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
uv --no-config run --frozen fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen pytest tests/test_source_liveness.py -q
uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_pack_lint or source_liveness"
uv --no-config run --frozen pytest tests/test_config.py -q -k "public_source_pack or google_news"
```

Expected: all deterministic checks pass. Do not make live `source-liveness`
blocking.

- [ ] **Step 2: Optional advisory liveness**

After strict source-pack lint passes, optionally run:

```bash
uv --no-config run --frozen fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml --format json || true
```

Record this only as advisory review evidence. Do not fail the stage solely
because a live upstream feed or GDELT lane changes during the run.

- [ ] **Step 3: Run local OpenCode code review**

Use the active local review engine:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-197-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-197-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. If the raw output contains process
chatter or tool status lines, rewrite the committed artifact as a clean,
coherent review body that preserves the verdict and findings.

- [ ] **Step 4: Run release verification**

Run:

```bash
uv --no-config run --frozen pytest tests/ -q --tb=short
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q
uv --no-config run --frozen ruff check tests/test_source_packs.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_source_liveness.py tests/test_cli.py
uv --no-config run --frozen ruff format --check tests/test_source_packs.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_source_liveness.py tests/test_cli.py
UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock pyproject.toml
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --check
```

Expected: all pass.

- [ ] **Step 5: Run local OpenCode release review**

Use:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-197-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-197-release-review.md
rm -f "$tmp_review"
```

Expected: `READY` with no Blocking findings. Clean the committed review artifact
if the raw output includes capture chatter.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short
git add configs/source-packs/fashion-public.example.yaml docs/source-packs.md docs/source-pack-quality.md CHANGELOG.md tests/test_cli.py docs/reviews/*stage-197*.md docs/superpowers/plans/2026-06-25-stage-197-public-rss-pack-expansion-plan.md
git commit -m "Stage 197: expand optional public RSS sources"
git push origin main
```

Expected: push succeeds and `origin/main` matches local `HEAD`.

## Self-Review Checklist

- [ ] The default compact starter config is unchanged.
- [ ] The optional public pack uses only existing `rss` and `gdelt` source types.
- [ ] New RSS feeds have `article.enabled: false`.
- [ ] Source-pack lint reports zero findings under `--strict`.
- [ ] Docs JSON/table samples match current runtime lint output.
- [ ] GDELT docs remain in YAML order if no GDELT lanes change.
- [ ] Live liveness is advisory only, not a release blocker.
- [ ] No social/platform connectors, scraping, browser automation, platform APIs,
  source acquisition workflow, demand proof, source ranking, coverage
  verification, or compliance-review product feature is added.
