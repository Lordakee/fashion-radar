# OpenCode Stage 388 Plan Revision Review

## Verdict

APPROVED contingent on the applied plan revisions.

## Scope

OpenCode reviewed the Stage 388 design and plan after the primary Claude plan
review, in read-only mode with GLM 5.2 and the max variant.

## Accepted Revisions

- Add a direct `AGENTS.md` Scope Boundaries test because it is a touched
  normative surface.
- Scope the changelog test to the `Unreleased` `Added` subsection and preserve
  the existing saved-local-text/reference and homepage-only boundary language.
- Prove that Minimum Core excludes HTML, sitemap, and every social connector;
  prove the social connectors stay in the explicit-user-enablement Opt-In tier.
- Scope the CLI regression guard to the existing `collect` command entry.
- State which proposed guards are expected to be red and which existing guards
  are expected to be green before documentation edits.
- Remove the obsolete architecture literal, add the two new exact literals, and
  retain Markdown punctuation in the article-extra phrase.

## Verified Disposition

The final plan also separates official RSS from optional HTML/sitemap collection
and separates local input/community handoff documentation from connector tiers.
The current `Unreleased` section was independently verified to be empty before
the dated `0.1.0` heading, so the plan correctly creates one new `Added`
subsection there.

No runtime or connector behavior is included in the revised direction.
