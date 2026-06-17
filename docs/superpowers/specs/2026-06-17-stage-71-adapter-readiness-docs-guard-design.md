# Stage 71 Adapter Readiness Docs Guard Design

## Goal

Add a focused docs drift guard that pins the documented relationship between
`external-tool-adapters` and `external-tool-readiness`.

## Context

`external-tool-adapters` is print-only. It now prints
`external-tool-readiness` as an optional local read-only preflight command in
adapter recommended command lists, but `external-tool-adapters` itself must not
run readiness or perform PATH lookup.

Existing docs tests verify the adapter registry is linked and bounded, but they
do not specifically pin this readiness-preflight wording. A future docs edit
could accidentally remove the discoverability guidance or imply that
`external-tool-adapters` executes readiness.

## Scope

In scope:

- Extend the existing adapter registry docs test in `tests/test_cli_docs.py`.
- Assert stable readiness-preflight concepts in the existing adapter docs.
- Keep the test section-scoped enough to avoid overfitting unrelated docs.
- Keep runtime behavior unchanged.
- Keep docs unchanged unless the new test exposes actual drift.

Out of scope:

- Runtime code changes.
- CLI output changes.
- Adapter registry command changes.
- Source/platform connectors, scraping, browser automation, platform APIs,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance-review product behavior.

## Design

Extend the existing
`test_external_tool_adapter_registry_docs_are_linked_and_bounded` loop with a
small readiness-preflight relationship phrase set:

```python
    readiness_preflight_terms = (
        "external-tool-readiness",
        "optional local read-only preflight command",
        "itself remains print-only",
        "does not run readiness or perform PATH lookup",
    )

    for text in (
        readme,
        import_doc,
        quality_doc,
        cli_reference,
        checklist,
        boundaries,
        architecture,
        agents,
        changelog,
    ):
        normalized = _normalized_text(text).casefold()
        assert "external-tool-adapters" in normalized
        assert "external social/community tool adapter registry" in normalized
        assert "local producer-discovery registry" in normalized
        for term in readiness_preflight_terms:
            assert term.casefold() in normalized
```

The test intentionally checks stable concepts rather than exact paragraphs.
It includes the upload checklist and changelog because those files already act
as release-review artifacts and should retain the readiness-preflight wording.

## Test Strategy

- Run the extended adapter docs test first and confirm it passes against
  existing docs.
- Run all docs tests.
- Run ruff check/format for `tests/test_cli_docs.py`.
- Run release hygiene, diff whitespace checks, and full pytest before commit.

## Acceptance Criteria

- `tests/test_cli_docs.py` has a focused guard pinning adapter readiness
  preflight discoverability and boundaries.
- The test covers `external-tool-readiness`, optional local read-only
  preflight wording, `external-tool-adapters` print-only behavior, no readiness
  execution, and no PATH lookup by adapters.
- Runtime code is unchanged.
- Docs are unchanged unless the new test reveals actual drift.
