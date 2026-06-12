# Claude Code Stage 15 Plan Rereview Prompt

You are rereviewing the Stage 15 plan for Fashion Radar after fixes to the first
plan review. Run this as a read-only planning review. Do not edit files, do not
commit, do not call the network, do not run collectors, do not create
directories, do not open SQLite, and do not execute platform/social/community
tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-15-plan-rereview-prompt.md
```

## Files To Review

- `docs/superpowers/specs/2026-06-12-stage-15-entity-pack-quality-design.md`
- `docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md`
- First review record:
  `docs/reviews/claude-code-stage-15-plan-review.md`

## Fixes Made After First Review

- Removed the design goal wording that framed the linter as preparation for
  future community-signal imports.
- Tightened matcher semantics in the design: `context_terms` are not universal,
  effective non-product safe aliases bypass context, and product entities with
  `parent_brand` ignore `safe_single_word`.
- Added explicit alias-gate classification pseudocode to the implementation
  plan:
  - product with `parent_brand`: parent/context gated, safe flag ignored;
  - non-product safe single/common alias with reason: safe alias, not context
    gated;
  - non-product single/common alias without effective safe reason: context
    required;
  - ordinary multi-word alias: accepted without context.
- Added explicit test requirements for matcher-contract edge cases.
- Clarified that the repository watchlist smoke test permits advisory warnings.
- Clarified that `product_missing_parent_brand` is a precision recommendation
  for named branded products, not a validity failure.
- Added raw-YAML-to-validated-entity index correlation guidance for omitted
  default diagnostics.
- Added broader documentation boundary inspection terms.

## Review Focus

Please verify whether the previous Critical/Important findings are resolved and
whether the plan is now safe to implement. Also check that the revised plan still
does not add or document:

- social/platform connectors, platform search, remote community ingestion, or
  automated social collection;
- web scraping, crawler development, browser automation, account automation, or
  source-acquisition workflows;
- login cookies, session files, browser profiles, tokens, proxy pools,
  fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall bypass;
- official or unofficial social platform APIs;
- instructions for obtaining platform/community exports;
- current-hotness claims, platform-wide claims, social-wide claims, market-wide
  trend proof, verified demand outside configured local signals, real-time
  monitoring, or top social trend rankings;
- DB migrations, source-health changes, collector changes, dashboard changes,
  report semantics changes, matcher behavior changes, or scoring algorithm
  changes;
- product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## Response Format

Start with one of:

- `Approved for Stage 15 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
