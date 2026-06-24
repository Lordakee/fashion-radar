# Stage 191 Plan Rereview Prompt

Do a narrow rereview from the excerpts below. Do not read files or perform a
full project review. Answer only whether the previous Important findings are
resolved and whether the fixes introduced a new Critical or Important issue.

Previous Important findings:

1. Docs wording had to make `no demand proof` and
   `no platform coverage verification` satisfiable as contiguous phrases.
2. Report-level summary pluralization had to be explicit.
3. Brief item `title` mappings had to be explicit.

Updated plan/spec excerpts:

```text
Use this canonical scope sentence anywhere docs/tests require both scope
phrases contiguously: `It provides no demand proof and no platform coverage
verification.`

Every file in `DAILY_BRIEF_DOCS` must contain the exact sentence:
`It provides no demand proof and no platform coverage verification.`
```

```python
def _daily_brief_summary(
    *,
    tracked_count: int,
    candidate_count: int,
    source_caveat_count: int,
) -> str:
    return (
        "Local observed brief from configured sources and imported local signals: "
        f"{tracked_count} {_count_label(tracked_count, 'tracked signal', 'tracked signals')}, "
        f"{candidate_count} "
        f"{_count_label(candidate_count, 'candidate signal needing review', 'candidate signals needing review')}, "
        f"{source_caveat_count} "
        f"{_count_label(source_caveat_count, 'source caveat', 'source caveats')}. "
        "It provides no demand proof and no platform coverage verification."
    )


def _count_label(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural
```

```text
Use these explicit item title mappings:

- tracked entity items set `title=entity.entity_name`;
- candidate phrase items set `title=candidate.phrase`;
- source-health caveat items set `title=source.source_name`;
- collector-run caveat items set `title=run.source_name`.
```

```text
The updated plan also added `docs/trend-deltas.md` and
`tests/test_trend_deltas_docs.py`, docs parity for `Heat Narrative`, exact
first-run smoke fixture wording, and reason-code order assertions.
```

The plan's stated boundaries remain:

```text
No new CLI command, no LLM/external API, no source acquisition, no social search,
no compliance-review feature, and no trend/heat/dashboard contract mutation.
```

Return one coherent review body starting with:

```text
# Stage 191 Plan Rereview
```

Use these sections exactly:

- Critical
- Important
- Minor
- Verdict
