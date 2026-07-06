# opencode Plan Review Prompt: Stage 311 Saved Text Digest

You are the fallback plan reviewer for `/home/ubuntu/fashion-radar` because
local Claude Code plan review hit a retryable upstream 524 timeout after
multiple attempts. Use read-only review. Do not edit files.

## Stage Goal

Add a ROW ONE generated-site detail-page saved text digest that organizes
locally saved article content into scan-first cards. This should move ROW ONE
beyond link/reader navigation by presenting existing saved article sidecar
content as a local, organized detail-page digest.

## Files To Review

- `docs/superpowers/specs/2026-07-06-stage-311-row-one-saved-text-digest-design.md`
- `docs/superpowers/plans/2026-07-06-stage-311-row-one-saved-text-digest-plan.md`

Do not inspect source files unless the plan text is impossible to evaluate
without them. Keep the review narrow and under 900 words.

## Required Boundaries

- Free/local-first.
- Generated-site presentation only.
- Use existing `RowOneLocalArticle.paragraphs`, optional aligned
  `paragraphs_zh`, and existing `content_sections`.
- Do not add source collection, scraping, browser automation, platform APIs,
  cookies, proxy, CAPTCHA, paywall bypass, LLM calls, translation services,
  image generation, or scheduling.
- Do not add compliance-review product features.
- Do not change `row-one-app/v7`, `data/edition.json`,
  `row-one-manifest/v1`, `row-one-runtime/v1`, JSON schemas, detail routes,
  or `#local-article-paragraph-N` anchors.
- Do not add a homepage coverage index in this stage; that is an explicit
  follow-up candidate.

## Prior Read-Only Review Notes Already Addressed

The plan was revised after read-only subagent findings:

- CSS selector assertions now match split `.local-article-digest-list {` and
  `.local-article-digest-link-list {` CSS blocks.
- Stage 310 map-slice tests now have an explicit update step because digest is
  inserted between map and reader.
- Read First keeps a nonblank takeaway body even if paragraph links are invalid.
- Source-map counts are specified as nonblank saved paragraph counts.
- Stage push wording clarifies this is a normal authorized stage push, not a
  release/GitHub-upload review.

## Review Questions

1. Is the stage objective coherent and aligned with the user goal of organizing
   local article information rather than only linking out?
2. Does the plan preserve these boundaries?
3. Are the proposed helpers and rendering contract technically feasible against
   the current code?
4. Are the TDD steps concrete enough for implementation?
5. Are any test assertions brittle, misleading, impossible, or inconsistent
   with current HTML/model behavior?
6. Does the plan accidentally create a schema/app-contract/status surface?
7. Should any Critical or Important issue be fixed before implementation?

## Expected Output

Return findings first, grouped by severity:

- Critical
- Important
- Minor

For each finding, include file/line references and explain why it matters.
If there are no Critical or Important findings, say so explicitly and state
whether the plan is approved for implementation.
