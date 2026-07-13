# Claude Code Stage 388 Plan Review

## Verdict

APPROVED after the recorded plan revisions.

## Scope Reviewed

- `docs/superpowers/specs/2026-07-13-release-documentation-consistency-design.md`
- `docs/superpowers/plans/2026-07-13-stage-388-release-documentation-consistency-plan.md`
- The current source-scope documentation, package-extra contract, changelog,
  and named documentation tests.

## Findings And Disposition

The initial review required a direct contract test for the normative
`AGENTS.md` Scope Boundaries statement. The revised plan adds a dedicated
`tests/test_agents_scope_docs.py` guard for the minimum core, the optional
`article` extra, Google News exclusion, social opt-in wording, and the absence
of the obsolete conflating sentence.

The review also required tests to scope changelog assertions to the current
`Unreleased` and `Added` subsection, rather than scanning the full changelog.
The revised plan now requires the Stage 386/387 names, homepage-only boundary,
existing saved local text/reference reuse, and explicit no-artifact/route/source
collection/scoring/app-contract statement inside that exact subsection.

The final plan proves all three source positions: Minimum Core excludes HTML,
sitemap, and social connectors; Optional Article-Extra Collection retains the
existing HTML/sitemap safeguards; and Opt-In retains explicit enablement and
the existing social limits. It also keeps official RSS in Minimum Core and adds
a separate Local Input And Community Handoff subsection so local inputs cannot
be misclassified as article-extra collectors.

## Final Assessment

No critical or important plan gap remains. The stage is documentation/test-only
and proposes no collector, dependency, schema, route, source-default, scoring,
scheduling, deployment, or social-connector behavior change.
