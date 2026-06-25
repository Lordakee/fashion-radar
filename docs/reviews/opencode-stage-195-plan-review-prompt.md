# Stage 195 Plan Review Prompt

Please review `/home/ubuntu/fashion-radar/docs/superpowers/plans/2026-06-25-stage-195-source-coverage-and-diacritics-plan.md`.

Context:

- Project goal: free-first local fashion trend radar for daily fashion news, celebrity styling, brands, designers, emerging brands, bags, shoes, and heat movement.
- Current v0.1.x core source boundary: RSS/Atom, RSSHub-compatible feeds when user accepts route terms, and GDELT Doc API metadata. Social platform scraping/connectors remain future experimental opt-ins and must not become core blockers.
- Cross-validated review identified these top product gaps after Stage 194:
  - bundled public source examples are too small;
  - deterministic matching does not fold diacritics;
  - review/process scope must stay right-sized and not create compliance-review product features.

Review questions:

1. Does the Stage 195 plan match the project objective and current source boundaries?
2. Is the technical approach for diacritic folding correct and low-risk for existing matching/hash/candidate behavior?
3. Is the curated public source expansion scoped safely and testable offline?
4. Are the tests specific enough to fail before implementation and pass after implementation?
5. Are there any critical or important issues that must be fixed before implementation?

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Concrete fixes required before implementation
