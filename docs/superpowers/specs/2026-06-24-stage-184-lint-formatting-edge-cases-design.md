# Stage 184 Lint Formatting Edge Cases Design

## Objective

Add direct regression coverage for `format_count_label(...)` across non-error
nouns, caller-shaped multi-word labels, identical singular/plural labels, and
an irregular plural.

## Background

`format_count_label(count, singular, plural)` is now shared by multiple
human-readable lint renderers. Current direct tests cover only the
`error/errors` pair for `0`, `1`, and `2`. A previous review note recorded that
the helper could use broader coverage once shared more widely.

The implementation already uses a simple contract: singular is used only when
`count == 1`; all other counts use the plural label. This stage should be
test-only unless the new test exposes a real defect.

## Scope

In scope:

- Add one focused parametrized test in `tests/test_lint_formatting.py`.
- Cover varied singular/plural label pairs.
- Cover labels used by current renderers, such as `import-ready row` and
  `valid file`.
- Cover identical singular/plural labels such as `info`.
- Cover an irregular plural pair to prove the helper uses caller-supplied
  labels instead of deriving plurals mechanically.
- Add Stage 184 plan/review artifacts.

Out of scope:

- Runtime helper changes unless the new test exposes a real defect.
- Changes to lint renderers, package archive tests, smoke scripts, docs,
  dependencies, or `uv.lock`.
- Source acquisition, scraping, platform APIs, monitoring, scheduling, ranking,
  demand proof, coverage verification, or compliance-review product features.

## Technical Approach

Replace the existing parametrized `format_count_label` direct test with a wider
test named `test_format_count_label_uses_supplied_label_for_count`:

```python
@pytest.mark.parametrize(
    ("count", "singular", "plural", "expected"),
    [
        (0, "error", "errors", "0 errors"),
        (1, "error", "errors", "1 error"),
        (2, "error", "errors", "2 errors"),
        (1, "import-ready row", "import-ready rows", "1 import-ready row"),
        (2, "import-ready row", "import-ready rows", "2 import-ready rows"),
        (0, "valid file", "valid files", "0 valid files"),
        (2, "info", "info", "2 info"),
        (2, "analysis", "analyses", "2 analyses"),
    ],
)
def test_format_count_label_uses_supplied_label_for_count(
    count: int,
    singular: str,
    plural: str,
    expected: str,
) -> None:
    assert format_count_label(count, singular, plural) == expected
```

Leave existing `format_finding_counts(...)` tests unchanged.

## Acceptance Criteria

- The direct `format_count_label(...)` parametrized test covers the existing
  `error/errors` cases plus caller-shaped and irregular labels.
- The test fails if `format_count_label(...)` ignores supplied labels or uses
  singular for any count other than exactly `1`.
- Focused lint formatting tests pass.
- Ruff check and format check pass for the touched test file.
- Full release gate remains clean before commit.
