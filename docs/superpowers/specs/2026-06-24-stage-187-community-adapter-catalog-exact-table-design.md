# Stage 187 Community Adapter Catalog Exact Table Guard Design

## Objective

Strengthen the community signal documentation guard so both community docs must
contain exactly the current external social/community adapter catalog table.

## Background

Stage 181 added `Known adapter ids` tables to
`docs/community-signal-import.md` and `docs/community-signal-quality.md`, and
added a registry-derived docs parity test in
`tests/test_external_tool_contract_parity.py`. That test derives each expected
adapter row from `build_external_tool_adapter_registry(...)`, but it only
checks that each current row is present as a substring.

The Stage 181 release review recorded the remaining gap: a stale but
well-formed extra row could remain after an adapter is removed, or the table
could drift in order, while the current substring guard still passes. This
stage closes that gap by asserting the extracted table block equals the live
registry-derived table.

## Scope

In scope:

- Update `tests/test_external_tool_contract_parity.py` only.
- Add a helper that extracts the `Known adapter ids` Markdown table from a
  community doc.
- Add a focused exact-table test for both community docs.
- Prove the new guard catches a stale extra row with a temporary mutation
  during verification, then revert that mutation before commit.
- Add Stage 187 plan and review artifacts.

Out of scope:

- Runtime source changes.
- Documentation content changes unless the exact-table test exposes real drift.
- CLI command changes.
- New connectors, source acquisition, scraping, browser automation, platform
  APIs, login/cookie/token behavior, monitoring, scheduling, demand proof,
  ranking, platform coverage verification, or compliance-review product
  features.
- Dependency, lockfile, source-pack, entity-pack, package archive, first-run
  smoke, or release hygiene behavior changes.

## Technical Approach

Add this test-local table extractor near `_adapter_catalog_doc_row(...)`:

```python
def _known_adapter_catalog_doc_table(text: str) -> list[str]:
    lines = text.splitlines()

    assert lines.count("Known adapter ids:") == 1
    marker_index = lines.index("Known adapter ids:")
    assert lines[marker_index + 1] == ""

    table_lines: list[str] = []
    for line in lines[marker_index + 2 :]:
        if not line.startswith("|"):
            break
        table_lines.append(line)

    return table_lines
```

Add a new exact-table test:

```python
def test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table(
    registry,
) -> None:
    expected_table = [
        "| Adapter id | Display/source name | Platform label | Format | Pattern |",
        "| --- | --- | --- | --- | --- |",
        *[_adapter_catalog_doc_row(adapter) for adapter in registry.adapters],
    ]

    for doc_path in COMMUNITY_SIGNAL_EXTERNAL_TOOL_DOCS:
        actual_table = _known_adapter_catalog_doc_table(
            doc_path.read_text(encoding="utf-8")
        )

        assert actual_table == expected_table, doc_path.relative_to(ROOT)
```

The helper intentionally requires exactly one `Known adapter ids:` marker, pins
the blank line before the table, and extracts only the contiguous Markdown table
after the marker. The assertion compares header, separator, row order, current
row set, and absence of stale extra rows in one check.

Because the current docs are expected to already be correct, the RED proof is a
temporary mutation: add a stale row such as
`| `removed_adapter` | Removed Adapter | `community` | `json` | `*.json` |`
to one guarded doc table, run the exact-table test and observe failure, then
remove the temporary row and observe GREEN.

## Acceptance Criteria

- The new exact-table test fails if either community doc table contains a stale
  extra row.
- The new exact-table test fails if either community doc table has rows out of
  registry order.
- The new exact-table test still derives current adapter rows from the live
  registry fixture rather than duplicating adapter constants.
- Existing advisory wording coverage remains intact.
- No runtime source files are changed.
- Focused external-tool contract parity tests pass.
- Ruff check and format check pass for `tests/test_external_tool_contract_parity.py`.
- Full release gate remains clean before commit.
