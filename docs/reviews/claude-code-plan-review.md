# Claude Code Plan Review

Date: 2026-06-11

Status: Proceed with conditions.

Claude Code reviewed the project brief, design spec, implementation plan, and source-boundary notes before implementation.

## Critical Issues To Fix Before Coding

1. Google News RSS legal risk is insufficiently flagged.
   - Decision required: remove it from MVP or keep it disabled by default with explicit use-at-your-own-risk warnings.

2. Article extraction lacks robots.txt compliance.
   - Add explicit robots.txt checks before fetching pages.

3. Entity matching false positives are not sufficiently handled.
   - Add word-boundary matching, alias quality rules, and match confidence.

4. GDELT rate limiting is not specified.
   - Add configurable rate limits, exponential backoff, and retry limits.

5. Source attribution and copyright strategy is incomplete.
   - Store/display source URL and source name, avoid paywalls, display snippets only, and add attribution footer to reports.

## Important Issues

1. No data retention or cleanup strategy.
2. HTTP User-Agent header not specified.
3. Cross-source deduplication needs more than URL matching.
4. Timestamps need UTC normalization.
5. Streamlit dashboard should bind to localhost by default.
6. Entity YAML validation should catch duplicate aliases.
7. Repeated source failure circuit breaker is not defined.
8. Heat score formula needs fixture-based validation.

## Minor Issues

1. Add annotated entity configuration examples.
2. Specify pre-commit hooks.
3. Define logging strategy.
4. Add dashboard data staleness indicator.
5. Document lightweight schema migration strategy.
6. Add CLI helpful-error acceptance criteria.
7. Document expected scale limits.

## Recommendation

Claude Code recommends proceeding only after critical issues 1-5 are addressed in the plan.

